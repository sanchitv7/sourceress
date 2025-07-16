"""
Barebones LinkedIn OAuth-like authentication for MVP.

This module provides a simple session-based authentication flow:
1. One-time browser login saves session cookies
2. Future runs reuse saved session (no re-login needed)
3. Modular design for easy UI integration later
"""

from __future__ import annotations

import pickle
import time
from pathlib import Path
from typing import Optional

import undetected_chromedriver as uc
from loguru import logger
from selenium.webdriver.common.by import By


class LinkedInAuthenticator:
    """Manages LinkedIn authentication using session persistence."""
    
    def __init__(self, session_file: Path = Path(".linkedin_session")):
        """Initialize authenticator with session file path."""
        self.session_file = session_file
        self.driver: Optional[uc.Chrome] = None
    
    def has_valid_session(self) -> bool:
        """Check if we have a saved session file."""
        return self.session_file.exists()
    
    def authenticate(self) -> None:
        """One-time authentication flow - opens browser for manual login."""
        logger.info("Starting LinkedIn authentication flow...")
        
        # Create browser instance
        options = uc.ChromeOptions()
        options.add_argument("--window-size=800,600")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        self.driver = uc.Chrome(options=options)
        
        try:
            # Navigate to LinkedIn login
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for user to complete login
            logger.info("Please complete LinkedIn login in the browser window...")
            self._wait_for_login_completion()
            
            # Save session cookies
            cookies = self.driver.get_cookies()
            with open(self.session_file, 'wb') as f:
                pickle.dump(cookies, f)
            
            logger.info("✅ Authentication successful! Session saved.")
            
        finally:
            if self.driver:
                self.driver.quit()
                self.driver = None
    
    def get_authenticated_driver(self) -> uc.Chrome:
        """Get an authenticated Chrome driver using saved session."""
        if not self.has_valid_session():
            raise ValueError("No saved session found. Run authenticate() first.")
        
        # Create new driver instance
        options = uc.ChromeOptions()
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        self.driver = uc.Chrome(options=options)
        
        # Load saved cookies
        self.driver.get("https://www.linkedin.com")
        
        with open(self.session_file, 'rb') as f:
            cookies = pickle.load(f)
        
        for cookie in cookies:
            try:
                self.driver.add_cookie(cookie)
            except Exception as e:
                logger.debug(f"Failed to add cookie: {e}")
        
        # Refresh to apply cookies
        self.driver.refresh()
        time.sleep(2)
        
        logger.info("✅ Using saved LinkedIn session")
        # Detach driver from this authenticator instance to prevent
        # __del__ from closing it prematurely. Caller is responsible for
        # quitting the driver.
        driver_to_return = self.driver
        self.driver = None  # Avoid auto-quit in __del__
        return driver_to_return
    
    def _wait_for_login_completion(self) -> None:
        """Wait for user to complete LinkedIn login."""
        max_wait = 300  # 5 minutes
        wait_time = 0
        
        logger.info("Waiting for login completion (max 5 minutes)...")
        
        while wait_time < max_wait:
            try:
                if self.driver is None:
                    raise RuntimeError("Driver is not initialized")
                
                current_url = self.driver.current_url
                
                # Check if we're successfully logged in
                if "linkedin.com/feed" in current_url or "linkedin.com/in/" in current_url:
                    return
                
                # Check if login form is gone (might be on 2FA page)
                login_forms = self.driver.find_elements(By.ID, "username")
                if not login_forms and "login" not in current_url:
                    return
                
                time.sleep(2)
                wait_time += 2
                
            except Exception:
                time.sleep(2)
                wait_time += 2
        
        raise TimeoutError("Login timeout - please complete login within 5 minutes")
    
    def clear_session(self) -> None:
        """Clear saved session (forces re-authentication)."""
        if self.session_file.exists():
            self.session_file.unlink()
            logger.info("Session cleared")
    
    def __del__(self):
        """Cleanup driver on destruction."""
        if self.driver:
            try:
                self.driver.quit()
            except:  # noqa: E722
                pass


# Convenience functions for easy usage
def authenticate_linkedin() -> None:
    """One-time setup: authenticate with LinkedIn."""
    auth = LinkedInAuthenticator()
    auth.authenticate()


def get_linkedin_driver() -> uc.Chrome:
    """Get authenticated LinkedIn driver (uses saved session)."""
    auth = LinkedInAuthenticator()
    return auth.get_authenticated_driver()


def is_linkedin_authenticated() -> bool:
    """Check if LinkedIn session exists."""
    auth = LinkedInAuthenticator()
    return auth.has_valid_session()
