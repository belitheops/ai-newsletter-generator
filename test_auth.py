#!/usr/bin/env python3
"""Test script for authentication system"""

from user_database import UserDatabase
from auth import AuthManager
import os

def test_auth_system():
    """Test the authentication system"""

    # Use a test database file
    test_db_file = "test_users.json"

    # Clean up any existing test database
    if os.path.exists(test_db_file):
        os.remove(test_db_file)

    print("Testing Authentication System")
    print("=" * 50)

    # Initialize database
    user_db = UserDatabase(db_file=test_db_file)
    print("✓ User database initialized")

    # Test 1: Create a new user
    print("\nTest 1: Creating new user...")
    success, message = user_db.create_user(
        username="testuser",
        email="test@example.com",
        password="TestPass123",
        full_name="Test User"
    )
    print(f"  Result: {message}")
    assert success, "Failed to create user"
    print("✓ User created successfully")

    # Test 2: Duplicate username should fail
    print("\nTest 2: Testing duplicate username...")
    success, message = user_db.create_user(
        username="testuser",
        email="another@example.com",
        password="TestPass456"
    )
    print(f"  Result: {message}")
    assert not success, "Should not allow duplicate username"
    print("✓ Duplicate username correctly rejected")

    # Test 3: Weak password should fail
    print("\nTest 3: Testing weak password...")
    success, message = user_db.create_user(
        username="weakuser",
        email="weak@example.com",
        password="weak"
    )
    print(f"  Result: {message}")
    assert not success, "Should not allow weak password"
    print("✓ Weak password correctly rejected")

    # Test 4: Authenticate with correct credentials
    print("\nTest 4: Testing authentication with correct credentials...")
    user_data = user_db.authenticate_user("testuser", "TestPass123")
    assert user_data is not None, "Authentication should succeed"
    assert user_data['username'] == "testuser"
    assert user_data['email'] == "test@example.com"
    print(f"✓ Authentication successful: {user_data['username']}")

    # Test 5: Authenticate with wrong password
    print("\nTest 5: Testing authentication with wrong password...")
    user_data = user_db.authenticate_user("testuser", "WrongPass123")
    assert user_data is None, "Authentication should fail with wrong password"
    print("✓ Wrong password correctly rejected")

    # Test 6: Authenticate non-existent user
    print("\nTest 6: Testing authentication with non-existent user...")
    user_data = user_db.authenticate_user("nonexistent", "TestPass123")
    assert user_data is None, "Authentication should fail for non-existent user"
    print("✓ Non-existent user correctly rejected")

    # Test 7: Create another user
    print("\nTest 7: Creating second user...")
    success, message = user_db.create_user(
        username="admin",
        email="admin@example.com",
        password="AdminPass123"
    )
    assert success, "Failed to create second user"
    print("✓ Second user created successfully")

    # Test 8: Check user count
    print("\nTest 8: Checking user count...")
    user_count = user_db.get_user_count()
    print(f"  Total users: {user_count}")
    assert user_count == 2, "Should have 2 users"
    print("✓ User count is correct")

    # Test 9: Change password
    print("\nTest 9: Testing password change...")
    success, message = user_db.change_password("testuser", "TestPass123", "NewPass456")
    assert success, "Password change should succeed"
    print(f"  Result: {message}")

    # Verify new password works
    user_data = user_db.authenticate_user("testuser", "NewPass456")
    assert user_data is not None, "Should authenticate with new password"
    print("✓ Password changed successfully")

    # Test 10: Deactivate user
    print("\nTest 10: Testing user deactivation...")
    success = user_db.deactivate_user("testuser")
    assert success, "User deactivation should succeed"

    # Try to authenticate deactivated user
    user_data = user_db.authenticate_user("testuser", "NewPass456")
    assert user_data is None, "Deactivated user should not be able to login"
    print("✓ User deactivated successfully")

    # Test 11: Reactivate user
    print("\nTest 11: Testing user reactivation...")
    success = user_db.activate_user("testuser")
    assert success, "User activation should succeed"

    # Try to authenticate reactivated user
    user_data = user_db.authenticate_user("testuser", "NewPass456")
    assert user_data is not None, "Reactivated user should be able to login"
    print("✓ User reactivated successfully")

    # Clean up test database
    if os.path.exists(test_db_file):
        os.remove(test_db_file)
    if os.path.exists(f"{test_db_file}.backup"):
        os.remove(f"{test_db_file}.backup")

    print("\n" + "=" * 50)
    print("All tests passed! ✓")
    print("Authentication system is working correctly.")

if __name__ == "__main__":
    try:
        test_auth_system()
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
