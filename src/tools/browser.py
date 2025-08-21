"""
Browser automation tools using Playwright.
Provides web browsing and automation capabilities.
"""

import asyncio
from typing import Tuple, List
from playwright.async_api import async_playwright, Browser, Playwright
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from langchain.agents import Tool


async def playwright_tools() -> Tuple[List[Tool], Browser, Playwright]:
    """
    Initialize Playwright browser tools.
    
    Returns:
        Tuple containing tools list, browser instance, and playwright instance
    """
    try:
        playwright = await async_playwright().start()
        browser = await playwright.chromium.launch(headless=False)
        toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
        tools = toolkit.get_tools()
        
        return tools, browser, playwright
    except Exception as e:
        raise RuntimeError(f"Failed to initialize Playwright tools: {e}")


async def cleanup_browser(browser: Browser, playwright: Playwright) -> None:
    """
    Clean up browser and playwright resources.
    
    Args:
        browser: Browser instance to close
        playwright: Playwright instance to stop
    """
    try:
        if browser:
            await browser.close()
        if playwright:
            await playwright.stop()
    except Exception as e:
        # Log error but don't raise to prevent cleanup failures
        print(f"Warning: Error during browser cleanup: {e}")
