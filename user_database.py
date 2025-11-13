import json
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging
from auth import AuthManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserDatabase:
    """Manages user accounts and authentication data"""

    def __init__(self, db_file: str = "users.json"):
        self.db_file = db_file
        self.auth_manager = AuthManager()
        self.users = self._load_database()

    def _load_database(self) -> List[Dict]:
        """Load users from JSON file"""
        try:
            if os.path.exists(self.db_file):
                with open(self.db_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, list):
                        return data
                    elif isinstance(data, dict) and 'users' in data:
                        return data['users']
                    else:
                        logger.warning(f"Invalid database format in {self.db_file}, starting fresh")
                        return []
            else:
                logger.info(f"User database file {self.db_file} not found, starting fresh")
                return []
        except Exception as e:
            logger.error(f"Error loading user database: {e}, starting with empty database")
            return []

    def _save_database(self):
        """Save users to JSON file"""
        try:
            # Create backup before saving
            if os.path.exists(self.db_file):
                backup_file = f"{self.db_file}.backup"
                with open(self.db_file, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())

            # Save current data
            with open(self.db_file, 'w', encoding='utf-8') as f:
                json.dump(self.users, f, indent=2, ensure_ascii=False)

            logger.debug(f"User database saved successfully with {len(self.users)} users")

        except Exception as e:
            logger.error(f"Error saving user database: {e}")

    def create_user(self, username: str, email: str, password: str, full_name: str = "") -> tuple[bool, str]:
        """
        Create a new user account
        Returns (success, message)
        """
        try:
            # Validate username
            is_valid, error_msg = self.auth_manager.validate_username(username)
            if not is_valid:
                return False, error_msg

            # Validate email
            is_valid, error_msg = self.auth_manager.validate_email(email)
            if not is_valid:
                return False, error_msg

            # Validate password
            is_valid, error_msg = self.auth_manager.validate_password_strength(password)
            if not is_valid:
                return False, error_msg

            # Check if username already exists
            if self.get_user_by_username(username):
                return False, "Username already exists"

            # Check if email already exists
            if self.get_user_by_email(email):
                return False, "Email already registered"

            # Create password hash
            password_data = self.auth_manager.create_password_hash(password)

            # Create user object
            user = {
                'username': username,
                'email': email,
                'full_name': full_name,
                'password_salt': password_data['salt'],
                'password_hash': password_data['hash'],
                'created_at': datetime.now().isoformat(),
                'last_login': None,
                'is_active': True,
                'role': 'user'  # Default role
            }

            # Add to users list
            self.users.append(user)

            # Save to file
            self._save_database()

            logger.info(f"User created successfully: {username}")
            return True, "Account created successfully"

        except Exception as e:
            logger.error(f"Error creating user: {e}")
            return False, f"Error creating account: {str(e)}"

    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """
        Authenticate a user with username and password
        Returns user data if successful, None otherwise
        """
        try:
            user = self.get_user_by_username(username)

            if not user:
                logger.warning(f"Authentication failed: User not found - {username}")
                return None

            if not user.get('is_active', True):
                logger.warning(f"Authentication failed: User inactive - {username}")
                return None

            # Verify password
            is_valid = self.auth_manager.verify_password(
                password,
                user['password_salt'],
                user['password_hash']
            )

            if is_valid:
                # Update last login
                self.update_last_login(username)
                logger.info(f"User authenticated successfully: {username}")

                # Return user data without sensitive information
                user_data = {
                    'username': user['username'],
                    'email': user['email'],
                    'full_name': user.get('full_name', ''),
                    'role': user.get('role', 'user'),
                    'created_at': user.get('created_at', '')
                }
                return user_data
            else:
                logger.warning(f"Authentication failed: Invalid password - {username}")
                return None

        except Exception as e:
            logger.error(f"Error authenticating user: {e}")
            return None

    def get_user_by_username(self, username: str) -> Optional[Dict]:
        """Get user by username"""
        for user in self.users:
            if user.get('username') == username:
                return user
        return None

    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """Get user by email"""
        for user in self.users:
            if user.get('email') == email:
                return user
        return None

    def update_last_login(self, username: str) -> bool:
        """Update the last login timestamp for a user"""
        try:
            for user in self.users:
                if user.get('username') == username:
                    user['last_login'] = datetime.now().isoformat()
                    self._save_database()
                    return True
            return False
        except Exception as e:
            logger.error(f"Error updating last login: {e}")
            return False

    def get_all_users(self) -> List[Dict]:
        """Get all users (without sensitive information)"""
        try:
            return [{
                'username': u['username'],
                'email': u['email'],
                'full_name': u.get('full_name', ''),
                'created_at': u.get('created_at', ''),
                'last_login': u.get('last_login', ''),
                'is_active': u.get('is_active', True),
                'role': u.get('role', 'user')
            } for u in self.users]
        except Exception as e:
            logger.error(f"Error retrieving users: {e}")
            return []

    def deactivate_user(self, username: str) -> bool:
        """Deactivate a user account"""
        try:
            for user in self.users:
                if user.get('username') == username:
                    user['is_active'] = False
                    self._save_database()
                    logger.info(f"User deactivated: {username}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error deactivating user: {e}")
            return False

    def activate_user(self, username: str) -> bool:
        """Activate a user account"""
        try:
            for user in self.users:
                if user.get('username') == username:
                    user['is_active'] = True
                    self._save_database()
                    logger.info(f"User activated: {username}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error activating user: {e}")
            return False

    def change_password(self, username: str, old_password: str, new_password: str) -> tuple[bool, str]:
        """Change user password"""
        try:
            user = self.get_user_by_username(username)

            if not user:
                return False, "User not found"

            # Verify old password
            is_valid = self.auth_manager.verify_password(
                old_password,
                user['password_salt'],
                user['password_hash']
            )

            if not is_valid:
                return False, "Current password is incorrect"

            # Validate new password
            is_valid, error_msg = self.auth_manager.validate_password_strength(new_password)
            if not is_valid:
                return False, error_msg

            # Create new password hash
            password_data = self.auth_manager.create_password_hash(new_password)

            # Update user
            user['password_salt'] = password_data['salt']
            user['password_hash'] = password_data['hash']

            self._save_database()
            logger.info(f"Password changed successfully for user: {username}")
            return True, "Password changed successfully"

        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False, f"Error changing password: {str(e)}"

    def get_user_count(self) -> int:
        """Get total number of users"""
        return len(self.users)

    def get_active_user_count(self) -> int:
        """Get number of active users"""
        return len([u for u in self.users if u.get('is_active', True)])
