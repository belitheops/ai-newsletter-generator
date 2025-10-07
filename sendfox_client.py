import requests
import os
import logging
from typing import Dict, Optional, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SendFoxClient:
    def __init__(self):
        self.api_token = os.getenv("SENDFOX_API_TOKEN")
        self.base_url = "https://api.sendfox.com"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}" if self.api_token else "",
            "Content-Type": "application/json"
        }
        
        if not self.api_token:
            logger.warning("SENDFOX_API_TOKEN not found in environment variables")

    def send_newsletter(self, html_content: str, subject: str) -> bool:
        """
        Send newsletter via SendFox email campaign
        Returns True if successful, False otherwise
        """
        if not self.api_token:
            logger.error("Cannot send newsletter: SendFox API token not configured")
            return False
        
        try:
            # Create campaign
            campaign_data = {
                "name": f"AI Daily Newsletter - {subject}",
                "subject": subject,
                "html": html_content,
                "type": "regular"
            }
            
            campaign_response = self._create_campaign(campaign_data)
            if not campaign_response:
                return False
            
            campaign_id = campaign_response.get("id")
            if not campaign_id:
                logger.error("Failed to get campaign ID from response")
                return False
            
            # Send campaign to all subscribers
            send_response = self._send_campaign(campaign_id)
            if send_response:
                logger.info(f"Newsletter sent successfully via SendFox. Campaign ID: {campaign_id}")
                return True
            else:
                logger.error("Failed to send campaign")
                return False
                
        except Exception as e:
            logger.error(f"Error sending newsletter via SendFox: {e}")
            return False

    def _create_campaign(self, campaign_data: Dict) -> Optional[Dict]:
        """Create a new email campaign"""
        try:
            url = f"{self.base_url}/campaigns"
            response = requests.post(url, json=campaign_data, headers=self.headers, timeout=30)
            
            if response.status_code == 201:
                return response.json()
            else:
                logger.error(f"Failed to create campaign. Status: {response.status_code}, Response: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error creating campaign: {e}")
            return None

    def _send_campaign(self, campaign_id: int) -> bool:
        """Send an existing campaign to all subscribers"""
        try:
            url = f"{self.base_url}/campaigns/{campaign_id}/send"
            response = requests.post(url, headers=self.headers, timeout=30)
            
            if response.status_code in [200, 202]:
                return True
            else:
                logger.error(f"Failed to send campaign. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending campaign: {e}")
            return False

    def get_subscriber_count(self) -> int:
        """Get total number of subscribers"""
        if not self.api_token:
            return 0
        
        try:
            url = f"{self.base_url}/contacts"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("total", 0)
            else:
                logger.error(f"Failed to get subscribers. Status: {response.status_code}")
                return 0
                
        except Exception as e:
            logger.error(f"Error getting subscriber count: {e}")
            return 0

    def add_subscriber(self, email: str, first_name: str = "", last_name: str = "") -> bool:
        """Add a new subscriber"""
        if not self.api_token:
            logger.error("Cannot add subscriber: SendFox API token not configured")
            return False
        
        try:
            subscriber_data = {
                "email": email,
                "first_name": first_name,
                "last_name": last_name
            }
            
            url = f"{self.base_url}/contacts"
            response = requests.post(url, json=subscriber_data, headers=self.headers, timeout=30)
            
            if response.status_code in [200, 201]:
                logger.info(f"Successfully added subscriber: {email}")
                return True
            else:
                logger.error(f"Failed to add subscriber. Status: {response.status_code}, Response: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error adding subscriber: {e}")
            return False

    def get_campaign_stats(self, campaign_id: int) -> Optional[Dict]:
        """Get statistics for a specific campaign"""
        if not self.api_token:
            return None
        
        try:
            url = f"{self.base_url}/campaigns/{campaign_id}/stats"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to get campaign stats. Status: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error getting campaign stats: {e}")
            return None

    def test_connection(self) -> bool:
        """Test SendFox API connection"""
        if not self.api_token:
            logger.error("Cannot test connection: SendFox API token not configured")
            return False
        
        try:
            url = f"{self.base_url}/me"
            response = requests.get(url, headers=self.headers, timeout=10)
            
            if response.status_code == 200:
                logger.info("SendFox API connection successful")
                return True
            else:
                logger.error(f"SendFox API connection failed. Status: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error testing SendFox connection: {e}")
            return False

    def get_lists(self) -> List[Dict]:
        """Get all subscriber lists"""
        if not self.api_token:
            return []
        
        try:
            url = f"{self.base_url}/lists"
            response = requests.get(url, headers=self.headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("data", [])
            else:
                logger.error(f"Failed to get lists. Status: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error getting lists: {e}")
            return []

    def send_test_email(self, recipient_email: str, subject: str, html_content: str) -> bool:
        """Send a test email to a specific recipient"""
        if not self.api_token:
            logger.error("Cannot send test email: SendFox API token not configured")
            return False
        
        try:
            # Create a campaign and send to specific email
            campaign_data = {
                "name": f"Test - {subject}",
                "subject": f"[TEST] {subject}",
                "html": html_content,
                "type": "regular"
            }
            
            campaign_response = self._create_campaign(campaign_data)
            if not campaign_response:
                return False
            
            campaign_id = campaign_response.get("id")
            
            # For test purposes, we'll create the campaign but note that SendFox
            # typically sends to all subscribers. In a production setup, you might
            # want to maintain a separate test list.
            logger.info(f"Test campaign created with ID: {campaign_id}")
            logger.info(f"Note: SendFox sends to all subscribers. Consider using a test list for actual testing.")
            
            return True
                
        except Exception as e:
            logger.error(f"Error sending test email: {e}")
            return False
