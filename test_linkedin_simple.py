import asyncio
from sourceress.utils.scraping import search_linkedin_async

async def test_linkedin_simple():
    print("🔍 Testing LinkedIn scraping with simple query...")
    
    try:
        # Test with a very simple query
        simple_query = "python developer"
        print(f"Searching for: '{simple_query}'")
        
        profiles = await search_linkedin_async(simple_query, max_results=5)
        
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
    asyncio.run(test_linkedin_simple())
