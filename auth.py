import json
import hashlib
import os
import secrets
from datetime import datetime
from typing import Optional, Dict, List
import shutil

class AuthManager:
    def __init__(self, users_file: str = "users.json"):
        self.users_file = users_file
        self._ensure_users_file()
    
    def _ensure_users_file(self):
        if not os.path.exists(self.users_file):
            default_data = {
                "users": [],
                "created_at": datetime.now().isoformat()
            }
            with open(self.users_file, 'w') as f:
                json.dump(default_data, f, indent=2)
    
    def _load_users(self) -> Dict:
        try:
            with open(self.users_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading users: {e}")
            return {"users": [], "created_at": datetime.now().isoformat()}
    
    def _save_users(self, data: Dict):
        try:
            backup_file = f"{self.users_file}.backup"
            if os.path.exists(self.users_file):
                shutil.copy2(self.users_file, backup_file)
            
            with open(self.users_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving users: {e}")
            raise
    
    def _hash_password(self, password: str, salt: Optional[bytes] = None) -> tuple[str, str]:
        if salt is None:
            salt = secrets.token_bytes(32)
        
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt,
            iterations=100000
        )
        
        return password_hash.hex(), salt.hex()
    
    def _verify_password(self, password: str, stored_hash: str, stored_salt: str) -> bool:
        salt = bytes.fromhex(stored_salt)
        password_hash, _ = self._hash_password(password, salt)
        return password_hash == stored_hash
    
    def create_user(self, username: str, password: str, email: str = "", full_name: str = "") -> tuple[bool, str]:
        if not username or not password:
            return False, "Username and password are required"
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters"
        
        if len(password) < 6:
            return False, "Password must be at least 6 characters"
        
        data = self._load_users()
        
        if any(user['username'].lower() == username.lower() for user in data['users']):
            return False, "Username already exists"
        
        if email and any(user.get('email', '').lower() == email.lower() for user in data['users'] if user.get('email')):
            return False, "Email already registered"
        
        password_hash, salt = self._hash_password(password)
        
        user = {
            "username": username,
            "password_hash": password_hash,
            "password_salt": salt,
            "email": email,
            "full_name": full_name,
            "created_at": datetime.now().isoformat(),
            "last_login": None,
            "is_active": True
        }
        
        data['users'].append(user)
        self._save_users(data)
        
        return True, "User created successfully"
    
    def verify_user(self, username: str, password: str) -> tuple[bool, Optional[Dict]]:
        if not username or not password:
            return False, None
        
        data = self._load_users()
        
        for user in data['users']:
            if user['username'].lower() == username.lower():
                if not user.get('is_active', True):
                    return False, None
                
                stored_hash = user.get('password_hash', '')
                stored_salt = user.get('password_salt', '')
                
                if not stored_salt:
                    return False, None
                
                if self._verify_password(password, stored_hash, stored_salt):
                    user['last_login'] = datetime.now().isoformat()
                    self._save_users(data)
                    
                    user_info = {
                        "username": user['username'],
                        "email": user.get('email', ''),
                        "full_name": user.get('full_name', ''),
                        "created_at": user.get('created_at', ''),
                        "last_login": user.get('last_login', '')
                    }
                    return True, user_info
                else:
                    return False, None
        
        return False, None
    
    def change_password(self, username: str, old_password: str, new_password: str) -> tuple[bool, str]:
        if len(new_password) < 6:
            return False, "New password must be at least 6 characters"
        
        verified, user_info = self.verify_user(username, old_password)
        if not verified:
            return False, "Current password is incorrect"
        
        data = self._load_users()
        for user in data['users']:
            if user['username'].lower() == username.lower():
                password_hash, salt = self._hash_password(new_password)
                user['password_hash'] = password_hash
                user['password_salt'] = salt
                self._save_users(data)
                return True, "Password changed successfully"
        
        return False, "User not found"
    
    def get_user(self, username: str) -> Optional[Dict]:
        data = self._load_users()
        for user in data['users']:
            if user['username'].lower() == username.lower():
                return {
                    "username": user['username'],
                    "email": user.get('email', ''),
                    "full_name": user.get('full_name', ''),
                    "created_at": user.get('created_at', ''),
                    "last_login": user.get('last_login', ''),
                    "is_active": user.get('is_active', True)
                }
        return None
    
    def update_user(self, username: str, email: Optional[str] = None, full_name: Optional[str] = None) -> tuple[bool, str]:
        data = self._load_users()
        
        for user in data['users']:
            if user['username'].lower() == username.lower():
                if email is not None:
                    if email and any(u.get('email', '').lower() == email.lower() and u['username'].lower() != username.lower() for u in data['users']):
                        return False, "Email already registered to another user"
                    user['email'] = email
                
                if full_name is not None:
                    user['full_name'] = full_name
                
                self._save_users(data)
                return True, "Profile updated successfully"
        
        return False, "User not found"
    
    def get_all_users(self) -> List[Dict]:
        data = self._load_users()
        return [
            {
                "username": user['username'],
                "email": user.get('email', ''),
                "full_name": user.get('full_name', ''),
                "created_at": user.get('created_at', ''),
                "last_login": user.get('last_login', ''),
                "is_active": user.get('is_active', True)
            }
            for user in data['users']
        ]
    
    def user_exists(self, username: str) -> bool:
        data = self._load_users()
        return any(user['username'].lower() == username.lower() for user in data['users'])
    
    def get_user_count(self) -> int:
        data = self._load_users()
        return len(data['users'])
