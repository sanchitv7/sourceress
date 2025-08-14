from sourceress.utils.scraping import search_linkedin

def test_real_titles():
    print("🔍 Testing what LinkedIn actually shows for titles...")
    
    try:
        profiles = search_linkedin("python developer", max_results=3)
        
        print(f"✅ Found {len(profiles)} profiles")
        
        if profiles:
            print("\n📋 Raw LinkedIn data:")
            for i, profile in enumerate(profiles, 1):
                name = profile.get('name', '').strip()
                title = profile.get('title', '').strip()
                location = profile.get('location', '').strip()
                url = profile.get('linkedin_url', '')
                
                print(f"\n{i}. Raw data from LinkedIn:")
                print(f"   Name: '{name}'")
                print(f"   Title: '{title}'")
                print(f"   Location: '{location}'")
                print(f"   URL: {url}")
                
                # Show the actual text content
                print(f"   Raw title text: '{title}'")
                
        else:
            print("❌ No profiles found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_real_titles()
