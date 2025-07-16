#!/usr/bin/env python3
"""Test script for LinkedIn authentication using the new session-based approach."""

import sys
import time
from pathlib import Path

# Add src to path so we can import sourceress modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sourceress.utils.linkedin_auth import (
    LinkedInAuthenticator,
    authenticate_linkedin,
    get_linkedin_driver,
    is_linkedin_authenticated,
)


def test_authentication_flow():
    """Test the LinkedIn authentication flow."""
    print("🔍 Testing LinkedIn Authentication Flow")
    print("=" * 50)
    
    # Initialize authenticator
    auth = LinkedInAuthenticator()
    
    # Check if we already have a session
    if auth.has_valid_session():
        print("✅ Found existing LinkedIn session")
        
        # Test using the saved session
        print("\n🚀 Testing saved session...")
        try:
            driver = auth.get_authenticated_driver()
            
            # Navigate to LinkedIn feed to test authentication
            driver.get("https://www.linkedin.com/feed/")
            time.sleep(3)
            
            current_url = driver.current_url
            print(f"Current URL: {current_url}")
            
            if "linkedin.com/feed" in current_url or "linkedin.com/in/" in current_url:
                print("✅ LinkedIn authentication test PASSED!")
                print("Successfully accessed LinkedIn feed with saved session.")
            else:
                print("⚠️  LinkedIn authentication test FAILED!")
                print("Could not access LinkedIn feed - session may be expired.")
                print("Try clearing the session and re-authenticating.")
            
            driver.quit()
            
        except Exception as e:
            print(f"❌ Error testing saved session: {e}")
            print("Session may be invalid. Try clearing and re-authenticating.")
    
    else:
        print("❌ No saved LinkedIn session found")
        print("\nTo authenticate with LinkedIn:")
        print("1. Run: python -c \"from sourceress.utils.linkedin_auth import authenticate_linkedin; authenticate_linkedin()\"")
        print("2. Complete the login in the browser window that opens")
        print("3. Wait for the session to be saved")
        print("4. Run this test again")


def test_convenience_functions():
    """Test the convenience functions for LinkedIn authentication."""
    print("\n🔍 Testing Convenience Functions")
    print("=" * 50)
    
    # Test session check
    session_exists = is_linkedin_authenticated()
    print(f"Session exists: {session_exists}")
    
    if session_exists:
        print("\n🚀 Testing get_linkedin_driver() convenience function...")
        try:
            driver = get_linkedin_driver()
            
            # Quick test
            driver.get("https://www.linkedin.com/")
            time.sleep(2)
            
            title = driver.title
            print(f"Page title: {title}")
            
            if "LinkedIn" in title:
                print("✅ Convenience function test PASSED!")
            else:
                print("⚠️  Convenience function test FAILED!")
            
            driver.quit()
            
        except Exception as e:
            print(f"❌ Error with convenience function: {e}")
    
    else:
        print("❌ No session available for convenience function test")


def test_manual_authentication():
    """Interactive test for manual authentication."""
    print("\n🔍 Manual Authentication Test")
    print("=" * 50)
    
    response = input("Do you want to test manual authentication? (y/n): ").lower().strip()
    
    if response == 'y':
        print("\n🚀 Starting manual authentication...")
        print("This will open a browser window for LinkedIn login.")
        
        try:
            # Clear any existing session first
            auth = LinkedInAuthenticator()
            auth.clear_session()
            
            # Authenticate
            authenticate_linkedin()
            
            print("✅ Manual authentication completed!")
            
            # Test the new session
            test_authentication_flow()
            
        except Exception as e:
            print(f"❌ Manual authentication failed: {e}")
    
    else:
        print("Skipping manual authentication test.")


def main():
    """Run all LinkedIn authentication tests."""
    print("🔍 LinkedIn Authentication Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Check existing session
        test_authentication_flow()
        
        # Test 2: Test convenience functions
        test_convenience_functions()
        
        # Test 3: Optional manual authentication
        test_manual_authentication()
        
        print("\n🎉 Test suite completed!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test suite interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")


if __name__ == "__main__":
    main() 