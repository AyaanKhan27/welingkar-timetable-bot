import os
from playwright.sync_api import sync_playwright


WEWORLD_URL = "https://weworld.welingkar.org/home.htm"


def main():
    username = os.environ["WEWORLD_USERNAME"]
    password = os.environ["WEWORLD_PASSWORD"]

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        print("Opening WeWorld...")
        page.goto(
            WEWORLD_URL,
            wait_until="networkidle",
            timeout=60000
        )

        print("Initial URL:", page.url)
        print("Initial title:", page.title())

        # -------------------------
        # LOGIN
        # -------------------------

        print("\nLogging into WeWorld...")

        page.locator("#j_username").fill(username)
        page.locator("#j_password").fill(password)

        page.get_by_role(
            "button",
            name="Login"
        ).click()

        # Wait for navigation / dashboard
        page.wait_for_load_state(
            "networkidle",
            timeout=60000
        )

        print("\n--- AFTER LOGIN ---")
        print("URL:", page.url)
        print("Title:", page.title())

        # -------------------------
        # BASIC LOGIN CHECK
        # -------------------------

        if page.locator("#j_username").count() > 0:
            print("WARNING: Login page is still visible.")
            print("Login may have failed.")
        else:
            print("Login page no longer visible.")
            print("Login may have succeeded.")

        # Print visible page text for us to inspect
        text = page.locator("body").inner_text()

        print("\n--- PAGE TEXT ---")
        print(text[:12000])

        browser.close()


if __name__ == "__main__":
    main()
