from sourceress.utils.linkedin_api import fetch_profiles

def test_fetch_profiles():
    print("🔍 Testing fetch_profiles function directly...")
    
    try:
        # Test with the same optimized query
        query = "Senior Python Developer python django"
        print(f"Query: '{query}'")
        
        profiles = fetch_profiles(query, limit=10)
        
        print(f"✅ Found {len(profiles)} profiles")
        
        if profiles:
            print("\n📋 Sample profiles:")
            for i, profile in enumerate(profiles[:3]):
                print(f"  {i+1}. {profile.name}")
                print(f"     Title: {profile.title}")
                print(f"     Location: {profile.location}")
                print(f"     URL: {profile.linkedin_url}")
                print()
        else:
            print("❌ No profiles found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_fetch_profiles()
