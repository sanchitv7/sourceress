from sourceress.utils.scraping import search_linkedin

def test_linkedin_direct():
    print("🔍 Testing LinkedIn scraping directly (no async wrapper)...")
    
    try:
        # Test with a very simple query
        simple_query = "python developer"
        print(f"Searching for: '{simple_query}'")
        
        profiles = search_linkedin(simple_query, max_results=5)
        
        print(f"✅ Found {len(profiles)} profiles")
        
        if profiles:
            print("\n📋 Sample profiles:")
            for i, profile in enumerate(profiles[:3]):
                print(f"  {i+1}. {profile.get('name', 'Unknown')}")
                print(f"     Title: {profile.get('title', 'Unknown')}")
                print(f"     Location: {profile.get('location', 'Unknown')}")
                print()
        else:
            print("❌ No profiles found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_linkedin_direct()
