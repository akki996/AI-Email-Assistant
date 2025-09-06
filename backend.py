import requests
import json
import os
from typing import Dict, Any

class EmailClassifier:
    def __init__(self, model_url="http://localhost:11434"):
        """Initialize the email classifier with Llama via Ollama"""
        self.model_url = model_url
        self.model_name = "llama3.2:3b"  # Using Llama 3.2 3B model
    
    def classify_email(self, sender: str, subject: str, body: str) -> Dict[str, Any]:
        """
        Classify an email into category and priority using Llama
        
        Args:
            sender: Email sender address
            subject: Email subject line
            body: Email body content
            
        Returns:
            Dictionary with category, priority, and reasoning
        """
        
        # Try to use Llama via Ollama API, fallback to rule-based
        try:
            return self._classify_with_llama(sender, subject, body)
        except Exception as e:
            print(f"Llama classification failed: {e}")
            print("Falling back to rule-based classification")
            return self._classify_rule_based(sender, subject, body)
    
    def _classify_with_llama(self, sender: str, subject: str, body: str) -> Dict[str, Any]:
        """Classify email using Llama model"""
        
        prompt = f"""
        Analyze the following email and classify it into a category and priority level.

        Email Details:
        From: {sender}
        Subject: {subject}
        Body: {body}

        Categories to choose from:
        - technical_support: Issues with software, bugs, errors, login problems
        - billing: Payment issues, charges, refunds, pricing questions
        - account: Account verification, access issues, account management
        - integration: API questions, third-party integrations, CRM connections
        - general: General inquiries, questions not fitting other categories

        Priority levels:
        - high: Urgent issues, system down, critical problems
        - medium: Important issues that need attention but not critical
        - low: General questions, non-urgent requests

        Respond in JSON format only:
        {{
            "category": "category_name",
            "priority": "priority_level",
            "reasoning": "Brief explanation of why this classification was chosen"
        }}
        """

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "top_p": 0.9
            }
        }

        try:
            response = requests.post(
                f"{self.model_url}/api/generate",
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '')
                
                # Try to extract JSON from response
                try:
                    # Find JSON in the response
                    start_idx = response_text.find('{')
                    end_idx = response_text.rfind('}') + 1
                    if start_idx != -1 and end_idx > start_idx:
                        json_str = response_text[start_idx:end_idx]
                        classification = json.loads(json_str)
                        
                        # Validate the response
                        if all(key in classification for key in ['category', 'priority', 'reasoning']):
                            return classification
                
                except json.JSONDecodeError:
                    pass
            
            # If we get here, something went wrong with the API response
            raise Exception("Invalid response from Llama API")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Ollama: {e}")
    
    def _classify_rule_based(self, sender: str, subject: str, body: str) -> Dict[str, Any]:
        """Fallback rule-based classification"""
        category = self._determine_category(subject, body)
        priority = self._determine_priority(subject, body)
        reasoning = self._generate_reasoning(category, priority, subject, body)
        
        return {
            "category": category,
            "priority": priority,
            "reasoning": reasoning
        }
    
    def _determine_category(self, subject: str, body: str) -> str:
        """Determine email category based on keywords"""
        text = (subject + " " + body).lower()
        
        # Define category keywords
        categories = {
            "technical_support": ["error", "bug", "not working", "broken", "issue", "problem", "unable", "cannot", "can't", "reset", "password", "login", "access"],
            "billing": ["billing", "charge", "payment", "refund", "invoice", "cost", "price", "pricing", "charged"],
            "account": ["account", "verification", "verify", "blocked"],
            "integration": ["api", "integration", "crm", "third-party"],
            "general": ["help", "support", "question", "query", "understand"]
        }
        
        # Score each category
        scores = {}
        for category, keywords in categories.items():
            score = sum(1 for keyword in keywords if keyword in text)
            scores[category] = score
        
        # Return category with highest score, default to general
        if max(scores.values()) > 0:
            return max(scores, key=scores.get)
        return "general"
    
    def _determine_priority(self, subject: str, body: str) -> str:
        """Determine email priority based on keywords"""
        text = (subject + " " + body).lower()
        
        # High priority keywords
        high_priority_keywords = ["urgent", "critical", "immediate", "emergency", "down", "outage", "cannot access", "completely inaccessible", "servers are down"]
        medium_priority_keywords = ["help", "support", "issue", "problem", "error", "unable"]
        
        for keyword in high_priority_keywords:
            if keyword in text:
                return "high"
        
        for keyword in medium_priority_keywords:
            if keyword in text:
                return "medium"
        
        return "low"
    
    def _generate_reasoning(self, category: str, priority: str, subject: str, body: str) -> str:
        """Generate reasoning for classification"""
        text = (subject + " " + body).lower()
        
        reasoning_parts = []
        
        # Category reasoning
        if "error" in text or "issue" in text or "problem" in text:
            reasoning_parts.append("Contains technical issue keywords")
        if "billing" in text or "charge" in text or "payment" in text:
            reasoning_parts.append("Contains billing-related terms")
        if "account" in text or "verification" in text or "login" in text:
            reasoning_parts.append("Contains account-related terms")
        if "api" in text or "integration" in text:
            reasoning_parts.append("Contains integration-related terms")
        
        # Priority reasoning
        if priority == "high":
            reasoning_parts.append("Contains urgent/critical keywords")
        elif priority == "medium":
            reasoning_parts.append("Contains support-related keywords")
        
        if not reasoning_parts:
            reasoning_parts.append("General inquiry based on content analysis")
        
        return f"Classified as {category} with {priority} priority. " + "; ".join(reasoning_parts) + "."


class ResponseGenerator:
    def __init__(self, model_url="http://localhost:11434"):
        """Initialize the response generator with Llama via Ollama"""
        self.model_url = model_url
        self.model_name = "llama3.2:3b"
    
    def generate_response(self, sender: str, subject: str, body: str, category: str, tone: str = "professional") -> str:
        """
        Generate an email response using Llama
        
        Args:
            sender: Original sender email
            subject: Original email subject
            body: Original email body
            category: Email category from classification
            tone: Response tone (professional, friendly, formal, casual)
            
        Returns:
            Generated email response
        """
        
        # Try to use Llama, fallback to templates
        try:
            return self._generate_with_llama(sender, subject, body, category, tone)
        except Exception as e:
            print(f"Llama response generation failed: {e}")
            print("Falling back to template-based responses")
            return self._generate_template_response(sender, subject, body, category, tone)
    
    def _generate_with_llama(self, sender: str, subject: str, body: str, category: str, tone: str) -> str:
        """Generate response using Llama model"""
        
        sender_name = sender.split('@')[0].replace('.', ' ').title()
        
        prompt = f"""
        Generate a customer service email response for the following email:

        Original Email:
        From: {sender}
        Subject: {subject}
        Body: {body}

        Email Category: {category}
        Required Tone: {tone}

        Guidelines:
        - Address the customer by name: {sender_name}
        - Use a {tone} tone throughout
        - Acknowledge their concern specifically
        - Provide helpful next steps or solutions
        - Keep it concise but complete
        - End with appropriate contact information
        - Don't include subject line, just the email body

        Generate only the email response text:
        """

        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9
            }
        }

        try:
            response = requests.post(
                f"{self.model_url}/api/generate",
                json=payload,
                timeout=45
            )
            
            if response.status_code == 200:
                result = response.json()
                response_text = result.get('response', '').strip()
                
                if response_text:
                    return response_text
            
            raise Exception("Invalid response from Llama API")
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to connect to Ollama: {e}")
    
    def _generate_template_response(self, sender: str, subject: str, body: str, category: str, tone: str) -> str:
        """Fallback template-based response generation"""
        
        # Extract sender name from email
        sender_name = sender.split('@')[0].replace('.', ' ').title()
        
        # Greeting based on tone
        greetings = {
            "professional": f"Dear {sender_name},",
            "friendly": f"Hi {sender_name}!",
            "formal": f"Dear {sender_name},",
            "casual": f"Hey {sender_name},"
        }
        
        # Response templates by category
        templates = {
            "technical_support": {
                "professional": "Thank you for reaching out regarding the technical issue you're experiencing. I understand how frustrating this must be. Our technical team will investigate this matter promptly and provide you with a resolution within 24 hours.",
                "friendly": "Thanks for letting us know about this issue! I totally understand how annoying technical problems can be. Our team is on it and we'll get this sorted out for you ASAP.",
                "formal": "We acknowledge receipt of your technical support request. Our engineering team will conduct a thorough investigation and provide you with a comprehensive solution within one business day.",
                "casual": "Got it! Thanks for the heads up about this issue. Our tech team will take a look and get back to you soon."
            },
            "billing": {
                "professional": "Thank you for contacting us about your billing inquiry. I will personally review your account and ensure any discrepancies are resolved immediately. You can expect a follow-up within 2 business hours.",
                "friendly": "Thanks for reaching out about your billing question! I'll take a look at your account right away and make sure everything is sorted out for you.",
                "formal": "We have received your billing inquiry and will conduct a comprehensive review of your account. Any necessary adjustments will be processed within 2 business hours.",
                "casual": "Hey! Thanks for the message about billing. I'll check your account and fix any issues right away."
            },
            "account": {
                "professional": "Thank you for your account-related inquiry. I will assist you in resolving this matter promptly. Please allow me to review your account details and provide you with the necessary steps to resolve this issue.",
                "friendly": "Thanks for reaching out about your account! I'm here to help you get everything sorted out. Let me look into this for you.",
                "formal": "We acknowledge your account verification request. Our security team will review your account and provide the necessary assistance within 4 business hours.",
                "casual": "Hey! No worries about the account issue - I'll help you get it sorted out quickly."
            },
            "integration": {
                "professional": "Thank you for your inquiry about our integration capabilities. I would be happy to provide you with detailed information about our API and CRM integration options. Our technical sales team will contact you within 24 hours.",
                "friendly": "Thanks for asking about our integrations! We have some great API and CRM options that I think you'll love. I'll have our tech team reach out with all the details.",
                "formal": "We appreciate your interest in our integration solutions. Our technical team will provide you with comprehensive documentation and integration options within one business day.",
                "casual": "Cool question about integrations! We've got some solid API options. I'll have the team send over the details soon."
            },
            "general": {
                "professional": "Thank you for reaching out to us. I have received your inquiry and will ensure you receive the appropriate assistance. Our team will respond with detailed information within 24 hours.",
                "friendly": "Thanks for getting in touch! I've got your message and will make sure you get the help you need.",
                "formal": "We acknowledge receipt of your inquiry. Our customer service team will provide you with a comprehensive response within one business day.",
                "casual": "Hey! Thanks for reaching out. I'll make sure you get the info you need."
            }
        }
        
        # Closing based on tone
        closings = {
            "professional": "Best regards,\nCustomer Support Team",
            "friendly": "Cheers!\nThe Support Team",
            "formal": "Sincerely,\nCustomer Service Department",
            "casual": "Talk soon!\nSupport Team"
        }
        
        # Build response
        greeting = greetings.get(tone, greetings["professional"])
        content = templates.get(category, templates["general"]).get(tone, templates["general"]["professional"])
        closing = closings.get(tone, closings["professional"])
        
        response = f"{greeting}\n\n{content}\n\nIf you have any additional questions, please don't hesitate to reach out.\n\n{closing}"
        
        return response
