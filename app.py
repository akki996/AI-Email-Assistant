import streamlit as st
import pandas as pd
from backend import EmailClassifier, ResponseGenerator
import os

# Page configuration
st.set_page_config(
    page_title="AI Email Assistant",
    page_icon="📧",
    layout="wide"
)

# Initialize session state
if 'classifier' not in st.session_state:
    st.session_state.classifier = EmailClassifier()
if 'response_generator' not in st.session_state:
    st.session_state.response_generator = ResponseGenerator()

st.title("📧 AI Email Assistant")
st.markdown("Classify emails and generate automated responses using Llama")

# Sidebar for configuration
st.sidebar.header("Configuration")

# Load sample emails
@st.cache_data
def load_sample_emails():
    csv_path = "/Users/ptupili/Desktop/Ai-email-assistant-starter-repo/sample_emails.csv"
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path)
    return pd.DataFrame()

# Main content
tab1, tab2, tab3 = st.tabs(["📨 Email Classification", "🤖 Response Generation", "📊 Analytics"])

with tab1:
    st.header("Email Classification")
    
    # Input methods
    input_method = st.radio("Choose input method:", ["Manual Input", "Sample Emails"])
    
    if input_method == "Manual Input":
        sender = st.text_input("Sender Email:")
        subject = st.text_input("Subject:")
        body = st.text_area("Email Body:", height=150)
        
        if st.button("Classify Email"):
            if sender and subject and body:
                with st.spinner("Classifying email..."):
                    result = st.session_state.classifier.classify_email(sender, subject, body)
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Category", result['category'])
                with col2:
                    st.metric("Priority", result['priority'])
                
                st.write("**Reasoning:**", result['reasoning'])
            else:
                st.warning("Please fill in all fields")
    
    else:  # Sample Emails
        df = load_sample_emails()
        if not df.empty:
            st.subheader("Sample Emails")
            
            # Email selection
            email_index = st.selectbox(
                "Select an email to classify:",
                range(len(df)),
                format_func=lambda x: f"{df.iloc[x]['sender']} - {df.iloc[x]['subject'][:50]}..."
            )
            
            selected_email = df.iloc[email_index]
            
            # Display selected email
            st.write("**From:**", selected_email['sender'])
            st.write("**Subject:**", selected_email['subject'])
            st.write("**Body:**", selected_email['body'])
            st.write("**Date:**", selected_email['sent_date'])
            
            if st.button("Classify Selected Email"):
                with st.spinner("Classifying email..."):
                    result = st.session_state.classifier.classify_email(
                        selected_email['sender'],
                        selected_email['subject'],
                        selected_email['body']
                    )
                
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Category", result['category'])
                with col2:
                    st.metric("Priority", result['priority'])
                
                st.write("**Reasoning:**", result['reasoning'])
        else:
            st.error("No sample emails found")

with tab2:
    st.header("Response Generation")
    
    # Input for response generation
    response_sender = st.text_input("Original Sender:", key="resp_sender")
    response_subject = st.text_input("Original Subject:", key="resp_subject")
    response_body = st.text_area("Original Email Body:", height=150, key="resp_body")
    
    # Response tone selection
    tone = st.selectbox("Response Tone:", ["professional", "friendly", "formal", "casual"])
    
    if st.button("Generate Response"):
        if response_sender and response_subject and response_body:
            with st.spinner("Generating response..."):
                # First classify the email
                classification = st.session_state.classifier.classify_email(
                    response_sender, response_subject, response_body
                )
                
                # Generate response
                response = st.session_state.response_generator.generate_response(
                    response_sender, response_subject, response_body, 
                    classification['category'], tone
                )
            
            st.subheader("Generated Response")
            st.text_area("Response:", value=response, height=200, key="generated_response")
            
            # Copy to clipboard button
            if st.button("📋 Copy Response"):
                st.success("Response copied to clipboard!")
        else:
            st.warning("Please fill in all fields")

with tab3:
    st.header("Email Analytics")
    
    df = load_sample_emails()
    if not df.empty:
        # Classify all emails for analytics
        if st.button("Analyze All Emails"):
            with st.spinner("Analyzing emails..."):
                results = []
                progress_bar = st.progress(0)
                
                for i, (_, row) in enumerate(df.iterrows()):
                    result = st.session_state.classifier.classify_email(
                        row['sender'], row['subject'], row['body']
                    )
                    results.append({
                        'sender': row['sender'],
                        'subject': row['subject'][:50] + "...",
                        'category': result['category'],
                        'priority': result['priority'],
                        'date': row['sent_date']
                    })
                    progress_bar.progress((i + 1) / len(df))
                
                results_df = pd.DataFrame(results)
                
                # Display analytics
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("Category Distribution")
                    category_counts = results_df['category'].value_counts()
                    st.bar_chart(category_counts)
                
                with col2:
                    st.subheader("Priority Distribution")
                    priority_counts = results_df['priority'].value_counts()
                    st.bar_chart(priority_counts)
                
                # Sender analysis
                st.subheader("Emails by Sender")
                sender_counts = results_df['sender'].value_counts()
                st.bar_chart(sender_counts)
                
                # Detailed results table
                st.subheader("Detailed Results")
                st.dataframe(results_df)
    else:
        st.error("No sample emails found for analysis")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit and Llama")