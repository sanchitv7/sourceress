from sourceress.utils.scraping import search_linkedin

def test_optimized_query():
    print("🔍 Testing optimized LinkedIn query...")
    
    # Test the optimized query that the LinkedInSourcer would generate
    optimized_query = "Senior Python Developer Django FastAPI"
    print(f"Optimized query: '{optimized_query}'")
    
    try:
        profiles = search_linkedin(optimized_query, max_results=10)
        
        print(f"✅ Found {len(profiles)} profiles")
        
        if profiles:
            print("\n📋 Sample profiles:")
            for i, profile in enumerate(profiles[:5]):
                name = profile.get('name', 'Unknown').strip()
                title = profile.get('title', 'Unknown').strip()
                location = profile.get('location', 'Unknown').strip()
                
                if name and name != 'Unknown':
                    print(f"  {i+1}. {name}")
                    print(f"     Title: {title}")
                    print(f"     Location: {location}")
                    print()
        else:
            print("❌ No profiles found")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_optimized_query()
