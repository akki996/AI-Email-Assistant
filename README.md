<img width="1728" height="932" alt="Screenshot 2025-09-06 at 10 13 53 AM" src="https://github.com/user-attachments/assets/b0f8837e-7723-4825-a12a-10fbeb5b707f" /><img width="1728" height="1037" alt="Screenshot 2025-09-06 at 10 11 40 AM" src="https://github.com/user-attachments/assets/57b7f978-c08a-4013-855c-94df74eae4d5" /># AI Email Assistant

An intelligent email classification and response generation system built with Streamlit and Llama.

## Features

- **Email Classification**: Automatically categorize emails into different types (technical support, billing, account issues, etc.)
- **Priority Detection**: Determine email priority levels (high, medium, low)
- **Response Generation**: Generate automated responses with customizable tones
- **Analytics Dashboard**: Analyze email patterns and distributions
- **Sample Data**: Includes sample emails for testing
- **Llama Integration**: Uses Llama 3.2 via Ollama for intelligent processing

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Install and Setup Ollama (for Llama model)

**Install Ollama:**
- Visit [ollama.ai](https://ollama.ai) and download Ollama for your system
- Or install via command line:
  ```bash
  # macOS
  curl -fsSL https://ollama.ai/install.sh | sh
  
  # Linux
  curl -fsSL https://ollama.ai/install.sh | sh
  ```

**Download Llama model:**
```bash
ollama pull llama3.2:3b
```

**Start Ollama server:**
```bash
ollama serve
```

### 3. Run the Application
```bash
streamlit run app.py
```

### 4. Access the Application
- Open your browser and go to `http://localhost:8501`

## Model Options

The application supports two modes:

1. **Llama Mode** (recommended): Uses Llama 3.2 for intelligent classification and response generation
2. **Fallback Mode**: Uses rule-based classification and template responses if Llama is unavailable

The system automatically falls back to rule-based processing if Ollama is not running.

## Usage

### Email Classification
- Choose between manual input or sample emails
- View automated classification results with reasoning

### Response Generation
- Input the original email details
- Select response tone (professional, friendly, formal, casual)
- Generate and copy automated responses

### Analytics
- Analyze all sample emails at once
- View category and priority distributions
- See sender patterns and detailed results

## File Structure

- `app.py` - Main Streamlit application
- `backend.py` - Email classification and response generation logic
- `sample_emails.csv` - Sample email data for testing
- `requirements.txt` - Python dependencies
- `README.md` - This file

## Customization

### Adding New Categories
Edit the `categories` dictionary in `backend.py` to add new email categories and keywords.

### Modifying Response Templates
Update the `templates` dictionary in `backend.py` to customize automated responses.

### Integrating OpenAI
Uncomment the OpenAI API calls in `backend.py` and add your API key to use AI-powered classification and response generation.

## Sample Data

The `sample_emails.csv` file contains 20 sample emails covering various scenarios:
- Technical support requests
- Billing inquiries
- Account verification issues
- Integration questions
- General queries

## Future Enhancements

- Integration with actual email providers (Gmail, Outlook)
- Machine learning model training on historical data
- Advanced sentiment analysis
- Multi-language support
- Email thread analysis
- Automated response scheduling


## Output Screenshorts
<img width="1728" height="1037" alt="Screenshot 2025-09-06 at 10 11 40 AM" src="https://github.com/user-attachments/assets/5ff9b197-9ce4-4b9b-82da-b532bdb151f4" />

<img width="1728" height="932" alt="Screenshot 2025-09-06 at 10 13 53 AM" src="https://github.com/user-attachments/assets/a22c419f-d5db-43f7-94b0-97198997791e" />




