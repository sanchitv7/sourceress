#!/usr/bin/env python3
"""Test script for LinkedIn scraping functionality with enhanced authentication."""

import sys
from pathlib import Path

# Add src to path so we can import sourceress modules
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from sourceress.utils.scraping import test_linkedin_search, search_linkedin
from sourceress.utils.linkedin_auth import is_linkedin_authenticated, LinkedInAuthenticator


def test_scraping_integration():
    """Test the integration between authentication and scraping."""
    print("🔍 Testing LinkedIn Scraping Integration")
    print("=" * 50)
    
    # Check if authentication is available
    if not is_linkedin_authenticated():
        print("❌ No LinkedIn session found!")
        print("This test will demonstrate the auto-authentication feature.")
        return False
    
    print("✅ LinkedIn session found")
    
    # Test the scraping functionality
    print("\n🚀 Testing LinkedIn search...")
    try:
        success = test_linkedin_search()
        
        if success:
            print("✅ LinkedIn scraping test PASSED!")
            return True
        else:
            print("❌ LinkedIn scraping test FAILED!")
            return False
            
    except Exception as e:
        print(f"❌ LinkedIn scraping test FAILED with error: {e}")
        return False


def test_manual_search():
    """Interactive test for manual LinkedIn search."""
    print("\n🔍 Manual LinkedIn Search Test")
    print("=" * 50)
    
    # Get search query from user
    query = input("Enter search query (e.g., 'python developer remote'): ").strip()
    
    if not query:
        print("No query provided, using default: 'python developer'")
        query = "python developer"
    
    # Get max results
    try:
        max_results = int(input("Max results (default 5): ") or "5")
    except ValueError:
        max_results = 5
    
    # Ask about auto-authentication
    auto_auth = input("Enable auto-authentication? (y/n, default n): ").lower().strip() == 'y'
    
    print(f"\n🚀 Searching for: '{query}' (max {max_results} results)")
    print(f"Auto-authentication: {'enabled' if auto_auth else 'disabled'}")
    
    try:
        profiles = search_linkedin(query, max_results, auto_authenticate=auto_auth)
        
        if profiles:
            print(f"✅ Found {len(profiles)} profiles:")
            print("-" * 60)
            
            for i, profile in enumerate(profiles, 1):
                print(f"{i}. {profile['name']}")
                print(f"   Title: {profile['title']}")
                print(f"   Location: {profile['location']}")
                print(f"   LinkedIn: {profile['linkedin_url']}")
                if profile['summary']:
                    print(f"   Summary: {profile['summary'][:100]}...")
                print()
            
            return True
        else:
            print("❌ No profiles found")
            return False
            
    except Exception as e:
        print(f"❌ Search failed: {e}")
        return False


def test_auto_authentication():
    """Test the auto-authentication feature."""
    print("\n🔍 Auto-Authentication Test")
    print("=" * 50)
    
    # Clear existing session to test auto-authentication
    auth = LinkedInAuthenticator()
    if auth.has_valid_session():
        response = input("Clear existing session to test auto-authentication? (y/n): ").lower().strip()
        if response == 'y':
            auth.clear_session()
            print("✅ Session cleared")
        else:
            print("Keeping existing session - auto-authentication test skipped")
            return
    
    print("\n🚀 Testing auto-authentication...")
    print("This will open a browser window for LinkedIn login.")
    
    try:
        # Test search with auto-authentication
        profiles = search_linkedin("python developer", max_results=3, auto_authenticate=True)
        
        if profiles:
            print(f"✅ Auto-authentication test PASSED! Found {len(profiles)} profiles")
            for profile in profiles:
                print(f"  - {profile['name']} | {profile['title']}")
            return True
        else:
            print("❌ Auto-authentication test FAILED! No profiles found")
            return False
            
    except Exception as e:
        print(f"❌ Auto-authentication test FAILED! Error: {e}")
        return False


def test_session_validation():
    """Test session validation during scraping."""
    print("\n🔍 Session Validation Test")
    print("=" * 50)
    
    if not is_linkedin_authenticated():
        print("❌ No LinkedIn session found! Cannot test session validation.")
        return False
    
    print("This test demonstrates how the scraper handles expired sessions.")
    print("The scraper will check if the session is still valid during searches.")
    
    try:
        # Test with a simple search
        profiles = search_linkedin("software engineer", max_results=2)
        
        if profiles:
            print("✅ Session validation test PASSED! Session is valid.")
            print(f"Found {len(profiles)} profiles:")
            for profile in profiles:
                print(f"  - {profile['name']} | {profile['title']}")
            return True
        else:
            print("⚠️  Session validation test: No profiles found (might be valid but no results)")
            return True
            
    except Exception as e:
        print(f"❌ Session validation test FAILED! Error: {e}")
        return False


def main():
    """Run enhanced scraping tests."""
    print("🔍 Enhanced LinkedIn Scraping Test Suite")
    print("=" * 60)
    
    try:
        # Test 1: Basic integration test
        print("TEST 1: Basic Integration")
        integration_success = test_scraping_integration()
        
        # Test 2: Session validation test
        print("\nTEST 2: Session Validation")
        test_session_validation()
        
        # Test 3: Manual search test
        if integration_success:
            response = input("\nDo you want to test manual search? (y/n): ").lower().strip()
            if response == 'y':
                print("\nTEST 3: Manual Search")
                test_manual_search()
        
        # Test 4: Auto-authentication test
        response = input("\nDo you want to test auto-authentication? (y/n): ").lower().strip()
        if response == 'y':
            print("\nTEST 4: Auto-Authentication")
            test_auto_authentication()
        
        print("\n🎉 Enhanced scraping test suite completed!")
        
    except KeyboardInterrupt:
        print("\n\n⏹️  Test suite interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")


if __name__ == "__main__":
    main() 