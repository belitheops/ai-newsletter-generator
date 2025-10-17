import resend
import os
import logging
import requests
from typing import Dict, Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ResendClient:
    def __init__(self):
        """Initialize Resend client with API key from Replit connector or environment"""
        self.api_key = None
        self.from_email = None
        self._initialize_credentials()
        
        if self.api_key:
            resend.api_key = self.api_key
            logger.info("Resend client initialized successfully")
        else:
            logger.warning("Resend API key not configured")

    def _initialize_credentials(self):
        """Get credentials from Replit connector or environment variables"""
        try:
            # Try to get credentials from Replit connector
            hostname = os.getenv('REPLIT_CONNECTORS_HOSTNAME')
            repl_identity = os.getenv('REPL_IDENTITY')
            web_repl_renewal = os.getenv('WEB_REPL_RENEWAL')
            
            # Determine X_REPLIT_TOKEN
            x_replit_token = None
            if repl_identity:
                x_replit_token = f'repl {repl_identity}'
            elif web_repl_renewal:
                x_replit_token = f'depl {web_repl_renewal}'
            
            if hostname and x_replit_token:
                # Fetch connection settings from Replit connector
                url = f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=resend'
                headers = {
                    'Accept': 'application/json',
                    'X_REPLIT_TOKEN': x_replit_token
                }
                
                response = requests.get(url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    if items and len(items) > 0:
                        settings = items[0].get('settings', {})
                        self.api_key = settings.get('api_key')
                        self.from_email = settings.get('from_email')
                        logger.info("Loaded Resend credentials from Replit connector")
                        return
            
        except Exception as e:
            logger.warning(f"Could not load credentials from Replit connector: {e}")
        
        # Fallback to environment variables
        self.api_key = os.getenv('RESEND_API_KEY')
        self.from_email = os.getenv('RESEND_FROM_EMAIL', 'newsletter@yourdomain.com')
        
        if self.api_key:
            logger.info("Loaded Resend credentials from environment variables")

    def send_newsletter(self, html_content: str, subject: str, to_emails: Optional[List[str]] = None) -> bool:
        """
        Send newsletter via Resend
        
        Args:
            html_content: HTML content of the newsletter
            subject: Email subject line
            to_emails: List of recipient emails (optional, defaults to test email)
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_key:
            logger.error("Cannot send newsletter: Resend API key not configured")
            return False
        
        if not self.from_email:
            logger.error("Cannot send newsletter: From email not configured")
            return False
        
        # Default to a test recipient if none provided
        if not to_emails:
            to_emails = ['test@example.com']
        
        try:
            params: resend.Emails.SendParams = {
                "from": self.from_email,
                "to": to_emails,
                "subject": subject,
                "html": html_content,
            }
            
            email = resend.Emails.send(params)
            
            if email:
                logger.info(f"Newsletter sent successfully via Resend to {len(to_emails)} recipients")
                return True
            else:
                logger.error("Failed to send newsletter via Resend")
                return False
                
        except Exception as e:
            logger.error(f"Error sending newsletter via Resend: {e}")
            return False

    def send_to_list(self, html_content: str, subject: str, list_id: Optional[str] = None) -> bool:
        """
        Send newsletter to a contact list
        Note: Resend doesn't have built-in list management like SendFox,
        so this would need to be implemented separately with your own contact management
        
        Args:
            html_content: HTML content of the newsletter
            subject: Email subject line
            list_id: List/audience identifier (placeholder for future implementation)
            
        Returns:
            True if successful, False otherwise
        """
        logger.warning("List management not implemented. Use send_newsletter with explicit to_emails.")
        return False

    def send_test_email(self, recipient_email: str, subject: str, html_content: str) -> bool:
        """
        Send a test email to a specific recipient
        
        Args:
            recipient_email: Email address to send test to
            subject: Email subject line
            html_content: HTML content of the email
            
        Returns:
            True if successful, False otherwise
        """
        if not self.api_key or not self.from_email:
            logger.error("Cannot send test email: Resend not configured")
            return False
        
        try:
            params: resend.Emails.SendParams = {
                "from": self.from_email,
                "to": [recipient_email],
                "subject": f"[TEST] {subject}",
                "html": html_content,
            }
            
            email = resend.Emails.send(params)
            
            if email:
                logger.info(f"Test email sent successfully to {recipient_email}")
                return True
            else:
                logger.error("Failed to send test email")
                return False
                
        except Exception as e:
            logger.error(f"Error sending test email: {e}")
            return False

    def test_connection(self) -> bool:
        """
        Test Resend API connection by attempting to send a simple email
        
        Returns:
            True if connection is working, False otherwise
        """
        if not self.api_key:
            logger.error("Cannot test connection: Resend API key not configured")
            return False
        
        if not self.from_email:
            logger.error("Cannot test connection: From email not configured")
            return False
        
        try:
            # Try sending a simple test (to a verified test address)
            # Note: Resend requires verified domains/emails
            params: resend.Emails.SendParams = {
                "from": self.from_email,
                "to": ["delivered@resend.dev"],  # Resend's test email
                "subject": "Connection Test",
                "html": "<p>Testing Resend connection</p>",
            }
            
            email = resend.Emails.send(params)
            
            if email:
                logger.info("Resend API connection successful")
                return True
            else:
                logger.error("Resend API connection failed")
                return False
                
        except Exception as e:
            logger.error(f"Error testing Resend connection: {e}")
            return False

    def get_status(self) -> Dict:
        """
        Get status information about the Resend connection
        
        Returns:
            Dictionary with status information
        """
        return {
            'configured': bool(self.api_key),
            'from_email': self.from_email if self.from_email else 'Not configured',
            'ready': bool(self.api_key and self.from_email)
        }
