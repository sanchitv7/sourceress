from sourceress.utils.scraping import search_linkedin

def test_profile_extraction():
    print("🔍 Testing LinkedIn profile data extraction...")
    
    try:
        # Test with a simple query to get profiles
        query = "python developer"
        print(f"Searching for: '{query}'")
        
        profiles = search_linkedin(query, max_results=5)
        
        print(f"✅ Found {len(profiles)} profiles")
        
        if profiles:
            print("\n📋 Profile data analysis:")
            for i, profile in enumerate(profiles, 1):
                name = profile.get('name', '').strip()
                title = profile.get('title', '').strip()
                location = profile.get('location', '').strip()
                url = profile.get('linkedin_url', '')
                
                print(f"\n{i}. Profile:")
                print(f"   Name: '{name}' (length: {len(name)})")
                print(f"   Title: '{title}' (length: {len(title)})")
                print(f"   Location: '{location}' (length: {len(location)})")
                print(f"   URL: {url}")
                
                # Analyze the data quality
                if not name:
                    print("   ⚠️  Name is empty")
                if not title:
                    print("   ⚠️  Title is empty")
                if not location:
                    print("   ⚠️  Location is empty")
                if name and title and location:
                    print("   ✅ All fields populated")
        else:
            print("❌ No profiles found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_profile_extraction()
