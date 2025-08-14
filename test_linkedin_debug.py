from sourceress.utils.scraping import search_linkedin
from sourceress.utils.linkedin_auth import get_linkedin_driver
from selenium.webdriver.common.by import By
import time

def debug_linkedin_structure():
    print("🔍 Debugging LinkedIn HTML structure...")
    
    try:
        driver = get_linkedin_driver()
        driver.get("https://www.linkedin.com/search/results/people/?keywords=python%20developer")
        time.sleep(5)
        
        # Find the first few profile cards
        profile_cards = driver.find_elements(By.CSS_SELECTOR, "div.entity-result")
        
        print(f"Found {len(profile_cards)} profile cards")
        
        for i, card in enumerate(profile_cards[:3]):
            print(f"\n--- Profile Card {i+1} ---")
            
            # Try to find name
            try:
                name_elem = card.find_element(By.CSS_SELECTOR, "span.entity-result__title-text a")
                name = name_elem.text.strip()
                print(f"Name: '{name}'")
            except:
                print("Name: Not found")
            
            # Try to find title
            try:
                title_elem = card.find_element(By.CSS_SELECTOR, "div.entity-result__primary-subtitle")
                title = title_elem.text.strip()
                print(f"Title: '{title}'")
            except:
                print("Title: Not found")
            
            # Try to find location
            try:
                loc_elem = card.find_element(By.CSS_SELECTOR, "div.entity-result__secondary-subtitle")
                location = loc_elem.text.strip()
                print(f"Location: '{location}'")
            except:
                print("Location: Not found")
            
            # Print all text content for debugging
            print(f"All text: '{card.text[:200]}...'")
        
        driver.quit()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_linkedin_structure()
