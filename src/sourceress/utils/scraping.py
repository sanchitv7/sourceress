# sourceress/src/sourceress/utils/scraping.py

"""LinkedIn scraping utilities using undetected_chromedriver for consistency with authentication."""

from __future__ import annotations

import asyncio
import random
import time
from typing import Any, List
from urllib.parse import quote

from loguru import logger
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from .linkedin_auth import get_linkedin_driver, is_linkedin_authenticated, authenticate_linkedin

# New stable selector for people-search result cards (June-2025)
PROFILE_CARD = "div.entity-result"
PROFILE_LINK = "a[data-test-app-aware-link][href*='/in/']"


def search_linkedin(query: str, max_results: int = 50, auto_authenticate: bool = False) -> List[dict[str, Any]]:
    """Search LinkedIn and return profile dictionaries using authenticated session.

    Args:
        query: Search query string.
        max_results: Maximum number of profiles to return.
        auto_authenticate: If True, automatically authenticate if no session exists.

    Returns:
        A list of dicts with profile data.
    """
    logger.info(f"Searching LinkedIn for: {query} (max {max_results} results)")
    
    # Check authentication status
    if not is_linkedin_authenticated():
        if auto_authenticate:
            logger.info("No LinkedIn session found. Starting authentication flow...")
            authenticate_linkedin()
        else:
            raise ValueError(
                "No LinkedIn session found. Please authenticate first:\n"
                "1. Run: python tests/test_linkedin_auth.py\n"
                "2. Or call search_linkedin() with auto_authenticate=True"
            )
    
    # Get authenticated driver from linkedin_auth
    driver = get_linkedin_driver()
    
    try:
        # Navigate to LinkedIn People Search
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={quote(query)}"
        logger.info(f"Navigating to: {search_url}")
        driver.get(search_url)
        
        # Check if we're still authenticated (session might have expired)
        if _is_signed_out(driver):
            logger.warning("LinkedIn session appears to have expired")
            if auto_authenticate:
                logger.info("Attempting to re-authenticate...")
                driver.quit()
                authenticate_linkedin()
                driver = get_linkedin_driver()
                driver.get(search_url)
            else:
                raise ValueError(
                    "LinkedIn session expired. Please re-authenticate:\n"
                    "1. Run: python tests/test_linkedin_auth.py\n"
                    "2. Or call search_linkedin() with auto_authenticate=True"
                )
        
        # Wait for search results to render – poll until at least one result
        # element is present. LinkedIn sometimes loads results lazily so we
        # use a lambda with a longer timeout instead of a static locator.
        def _results_present(d):
            return len(d.find_elements(By.CSS_SELECTOR, PROFILE_LINK)) > 0

        try:
            WebDriverWait(driver, 20).until(_results_present)
        except Exception as wait_err:  # TimeoutException or others
            logger.warning(f"Results did not appear within timeout: {wait_err}. Continuing anyway.")
        
        # Debug: log number of cards detected right after wait
        initial_count = len(driver.find_elements(By.CSS_SELECTOR, PROFILE_LINK))
        logger.debug(f"Initial profile card count: {initial_count}")
            
        # Random delay to appear more human
        time.sleep(random.uniform(2, 4))
        
        profiles = []
        seen_links: set[str] = set()
        
        # Scroll and collect profiles
        while len(profiles) < max_results:
            profile_anchors = driver.find_elements(By.CSS_SELECTOR, PROFILE_LINK)
            
            for anchor in profile_anchors:
                href = anchor.get_attribute("href")
                if not href or href in seen_links:
                    continue
                seen_links.add(href)
                
                # Extract name from the anchor
                name = anchor.text.strip() or anchor.get_attribute("innerText") or ""
                
                # Find the parent container for additional data
                try:
                    container = anchor.find_element(By.XPATH, "ancestor::div[contains(@class,'entity-result') or contains(@class,'search-result') or contains(@class,'reusable-search__result-container')]")
                except Exception:
                    container = None
                
                title = ""
                location = ""
                
                if container:
                    # Try multiple selectors for title (LinkedIn changes these frequently)
                    title_selectors = [
                        "div.t-14.t-black.t-normal",
                        "div.t-14.t-normal.t-black",
                        "div.entity-result__primary-subtitle",
                        "div.search-result__info",
                        "span.entity-result__title-text",
                        "div.t-14"
                    ]
                    
                    for selector in title_selectors:
                        try:
                            title_elem = container.find_element(By.CSS_SELECTOR, selector)
                            title = title_elem.text.strip()
                            if title and title != name:  # Avoid using name as title
                                break
                        except Exception:
                            continue
                    
                    # Try multiple selectors for location
                    location_selectors = [
                        "div.t-14.t-normal.t-black--light",
                        "div.entity-result__secondary-subtitle",
                        "div.search-result__location",
                        "div.t-14.t-normal"
                    ]
                    
                    for selector in location_selectors:
                        try:
                            loc_elem = container.find_element(By.CSS_SELECTOR, selector)
                            location = loc_elem.text.strip()
                            if location and location != title and location != name:
                                break
                        except Exception:
                            continue
                
                # Use the data as LinkedIn provides it (no hardcoded assumptions)
                # LinkedIn search results show limited info - that's normal
                if name and len(name) > 1:
                    profiles.append({
                        "name": name,
                        "linkedin_url": href.split("?")[0],
                        "title": title,
                        "location": location,
                        "summary": "",
                        "skills": [],
                    })
                    logger.debug(f"Collected: {name} - {title}")
                
                if len(profiles) >= max_results:
                    break
            
            if len(profiles) >= max_results:
                break
            
            # Scroll furtherbit
            driver.execute_script("window.scrollBy(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2, 4))
            # loop continues
            # stop if scrolling didn't add new anchors
            new_count = len(driver.find_elements(By.CSS_SELECTOR, PROFILE_LINK))
            if new_count == len(seen_links):
                logger.info("Reached end of results")
                break
        
        logger.info(f"Successfully collected {len(profiles)} profiles")
        return profiles[:max_results]
        
    except Exception as e:
        logger.error(f"LinkedIn search failed: {e}")
        return []

    finally:
        driver.quit()


def _is_signed_out(driver) -> bool:
    """Check if the current page indicates we're signed out.
    
    Args:
        driver: Selenium WebDriver instance
    
    Returns:
        True if signed out, False if still authenticated
    """
    try:
        # Check for sign-in elements
        sign_in_buttons = driver.find_elements(By.CSS_SELECTOR, "a[href*='login'], button[data-tracking-control-name='public_profile_v3_web_login_button']")
        sign_in_text = driver.find_elements(By.XPATH, "//*[contains(text(), 'Sign in')]")
        
        # Check for authentication challenge
        auth_challenge = driver.find_elements(By.CSS_SELECTOR, "div[data-test-id='challenge-page']")
        
        # Check current URL
        current_url = driver.current_url
        is_login_page = "login" in current_url or "authwall" in current_url
        
        logger.debug(f"Sign-in check: buttons={len(sign_in_buttons)}, text={len(sign_in_text)}, challenge={len(auth_challenge)}, login_page={is_login_page}")
        
        return len(sign_in_buttons) > 0 or len(sign_in_text) > 0 or len(auth_challenge) > 0 or is_login_page
        
    except Exception as e:
        logger.debug(f"Error checking sign-out status: {e}")
        return False
        

def _extract_profile_data(container) -> dict[str, Any] | None:
    """Extract profile data from a LinkedIn search result container.
    
    Args:
        container: Selenium WebElement containing profile data
        
    Returns:
        Dictionary with profile data or None if extraction fails
    """
    try:
        # Extract name
        name_elem = container.find_element(By.CSS_SELECTOR, "span.entity-result__title-text a")
        name = name_elem.text.strip() if name_elem else "Unknown"
        
        # Extract LinkedIn URL
        linkedin_url = name_elem.get_attribute("href") if name_elem else ""
        
        # Extract title/headline
        try:
            title_elem = container.find_element(By.CSS_SELECTOR, "div.entity-result__primary-subtitle")
            title = title_elem.text.strip() if title_elem else "Unknown"
        except NoSuchElementException:
            title = "Unknown"
        
        # Extract location
        try:
            location_elem = container.find_element(By.CSS_SELECTOR, "div.entity-result__secondary-subtitle")
            location = location_elem.text.strip() if location_elem else "Unknown"
        except NoSuchElementException:
            location = "Unknown"
        
        # Extract summary/snippet if available
        try:
            summary_elem = container.find_element(By.CSS_SELECTOR, "p.entity-result__summary")
            summary = summary_elem.text.strip() if summary_elem else ""
        except NoSuchElementException:
            summary = ""
        
        # Return structured profile data
        return {
            "name": name,
            "linkedin_url": linkedin_url,
            "title": title,
            "location": location,
            "summary": summary,
            "skills": [],  # Will be populated if we visit individual profiles
        }
                    
    except Exception as e:
        logger.warning(f"Failed to extract profile data from container: {e}")
        return None


def enrich_profile(profile_url: str, auto_authenticate: bool = False) -> dict[str, Any]:
    """Enrich a profile by visiting its individual page.
    
    Args:
        profile_url: LinkedIn profile URL
        auto_authenticate: If True, automatically authenticate if no session exists.
    
    Returns:
        Dictionary with enriched profile data
    """
    logger.info(f"Enriching profile: {profile_url}")
    
    # Check authentication status
    if not is_linkedin_authenticated():
        if auto_authenticate:
            logger.info("No LinkedIn session found. Starting authentication flow...")
            authenticate_linkedin()
        else:
            raise ValueError(
                "No LinkedIn session found. Please authenticate first:\n"
                "1. Run: python tests/test_linkedin_auth.py\n"
                "2. Or call enrich_profile() with auto_authenticate=True"
            )
    
    # Get authenticated driver
    driver = get_linkedin_driver()
    
    try:
        # Navigate to profile page
        driver.get(profile_url)
        
        # Check if we're still authenticated
        if _is_signed_out(driver):
            logger.warning("LinkedIn session appears to have expired")
            if auto_authenticate:
                logger.info("Attempting to re-authenticate...")
                driver.quit()
                authenticate_linkedin()
                driver = get_linkedin_driver()
                driver.get(profile_url)
            else:
                raise ValueError(
                    "LinkedIn session expired. Please re-authenticate:\n"
                    "1. Run: python tests/test_linkedin_auth.py\n"
                    "2. Or call enrich_profile() with auto_authenticate=True"
                )
        
        # Wait for profile to load
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "pv-text-details__left-panel"))
        )
        
        # Random delay
        time.sleep(random.uniform(2, 4))
        
        # Extract detailed profile information
        profile_data = {
            "linkedin_url": profile_url,
            "name": _extract_profile_name(driver),
            "title": _extract_profile_title(driver),
            "location": _extract_profile_location(driver),
            "summary": _extract_profile_summary(driver),
            "skills": _extract_profile_skills(driver),
            "experience": _extract_profile_experience(driver),
        }
        
        logger.info(f"Successfully enriched profile for: {profile_data['name']}")
        return profile_data
        
    except Exception as e:
        logger.error(f"Failed to enrich profile {profile_url}: {e}")
        return {"linkedin_url": profile_url, "error": str(e)}
    
    finally:
        driver.quit()


def _extract_profile_name(driver) -> str:
    """Extract name from profile page."""
    try:
        name_elem = driver.find_element(By.CSS_SELECTOR, "h1.text-heading-xlarge")
        return name_elem.text.strip()
    except NoSuchElementException:
        return "Unknown"


def _extract_profile_title(driver) -> str:
    """Extract title/headline from profile page."""
    try:
        title_elem = driver.find_element(By.CSS_SELECTOR, "div.text-body-medium")
        return title_elem.text.strip()
    except NoSuchElementException:
        return "Unknown"


def _extract_profile_location(driver) -> str:
    """Extract location from profile page."""
    try:
        location_elem = driver.find_element(By.CSS_SELECTOR, "span.text-body-small.inline")
        return location_elem.text.strip()
    except NoSuchElementException:
        return "Unknown"


def _extract_profile_summary(driver) -> str:
    """Extract summary/about section from profile page."""
    try:
        summary_elem = driver.find_element(By.CSS_SELECTOR, "div.pv-shared-text-with-see-more")
        return summary_elem.text.strip()
    except NoSuchElementException:
        return ""


def _extract_profile_skills(driver) -> List[str]:
    """Extract skills from profile page."""
    try:
        skills_elements = driver.find_elements(By.CSS_SELECTOR, "span.pv-skill-category-entity__name")
        return [skill.text.strip() for skill in skills_elements[:10]]  # Limit to top 10
    except NoSuchElementException:
        return []


def _extract_profile_experience(driver) -> List[dict[str, str]]:
    """Extract experience entries from profile page."""
    try:
        experience_elements = driver.find_elements(By.CSS_SELECTOR, "div.pv-entity__summary-info")
        experiences = []
        
        for exp_elem in experience_elements[:5]:  # Limit to top 5
            try:
                title_elem = exp_elem.find_element(By.CSS_SELECTOR, "h3")
                company_elem = exp_elem.find_element(By.CSS_SELECTOR, "p.pv-entity__secondary-title")
                
                experiences.append({
                    "title": title_elem.text.strip(),
                    "company": company_elem.text.strip(),
                })
            except NoSuchElementException:
                continue
        
        return experiences
    except NoSuchElementException:
        return []


def test_linkedin_search() -> bool:
    """Test LinkedIn search functionality.
    
    Returns:
        True if search successful, False otherwise.
    """
    logger.info("Testing LinkedIn search functionality...")
    
    try:
        # Test search with a simple query
        profiles = search_linkedin("python developer", max_results=5)
        
        if profiles:
            logger.info(f"✅ LinkedIn search test PASSED! Found {len(profiles)} profiles")
            for profile in profiles:
                logger.info(f"  - {profile['name']} | {profile['title']} | {profile['location']}")
            return True
        else:
            logger.error("❌ LinkedIn search test FAILED! No profiles found")
            return False
                
    except Exception as e:
        logger.error(f"❌ LinkedIn search test FAILED! Error: {e}")
        return False


# Async wrapper for compatibility (if needed)
async def search_linkedin_async(query: str, max_results: int = 50, auto_authenticate: bool = False) -> List[dict[str, Any]]:
    """Async wrapper for LinkedIn search."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, search_linkedin, query, max_results, auto_authenticate)


async def enrich_profile_async(profile_url: str, auto_authenticate: bool = False) -> dict[str, Any]:
    """Async wrapper for profile enrichment."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, enrich_profile, profile_url, auto_authenticate)
