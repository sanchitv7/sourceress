from sourceress.utils.scraping import search_linkedin

def test_boolean_queries():
    print("🔍 Testing different boolean query formats...")
    
    # Test different query formats
    queries = [
        "python developer",  # Simple
        '"python developer"',  # Quoted
        '"python developer" AND "django"',  # Basic AND
        '"python developer" AND (python OR django)',  # AND with OR group
        'python developer AND django',  # No quotes
    ]
    
    for i, query in enumerate(queries, 1):
        print(f"\n{i}. Testing: '{query}'")
        try:
            profiles = search_linkedin(query, max_results=5)
            print(f"   Found: {len(profiles)} profiles")
            
            if profiles:
                for j, profile in enumerate(profiles[:2]):
                    name = profile.get('name', 'Unknown').strip()
                    title = profile.get('title', 'Unknown').strip()
                    if name and name != 'Unknown':
                        print(f"   - {name}: {title}")
        except Exception as e:
            print(f"   Error: {e}")

if __name__ == "__main__":
    test_boolean_queries()
