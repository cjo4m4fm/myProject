import random
import asyncio
from playwright.async_api import async_playwright, TimeoutError
from playwright_stealth import stealth_async
import nest_asyncio

nest_asyncio.apply()

# URL of the Amazon product page
AMAZON_URL = "https://www.amazon.com/dp/B00VH84L5E?psc=1"

async def get_amazon_reviews(url):
    """
    Fetches and parses reviews from an Amazon product page using Playwright's Async API.
    """
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Create a new context for a clean session (clears cookies)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = await context.new_page()
        await stealth_async(page)
        try:
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)

            try:
                # Try to click the button if it appears
                await page.locator('text="Continue shopping"').click(timeout=5000)
                print("Intermediate page detected. Clicked 'Continue shopping'.")
            except TimeoutError:
                # This is expected if we land directly on the product page
                print("No intermediate page detected, proceeding.")

            # Simulate human-like scrolling
            print("Scrolling down to load reviews...")
            for i in range(random.randint(3, 6)):
                await page.evaluate(f"window.scrollBy(0, {random.randint(500, 1000)})")

            # Wait for the review section to load
            await page.wait_for_selector('[data-hook="review-body"]', timeout=30000)

            review_elements = await page.query_selector_all('[data-hook="review-body"]')

            if review_elements:
                print("Found reviews:")
                for i, review_element in enumerate(review_elements, 1):
                    print(f"Review {i}: {await review_element.inner_text()}")
            else:
                print("No reviews found on the page.")

        except Exception as e:
            print(f"An error occurred: {e}")
            await page.screenshot(path="error_screenshot.png")
            print("Screenshot saved to error_screenshot.png")
        finally:
            await context.close() # Close context to ensure clean session
            await browser.close()

if __name__ == "__main__":
    asyncio.run(get_amazon_reviews(AMAZON_URL))
