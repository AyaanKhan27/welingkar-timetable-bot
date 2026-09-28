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

        print("Login page:", page.url)

        # -------------------------
        # FILL LOGIN FORM
        # -------------------------

        print("Entering username...")

        page.locator(
            'input[name="j_username"]'
        ).fill(username)

        print("Entering password...")

        page.locator(
            'input[name="j_password"]'
        ).fill(password)

        print("Credentials entered.")

        # -------------------------
        # CLICK LOGIN
        # -------------------------

        print("Clicking Login...")

        page.get_by_role(
            "button",
            name="Login"
        ).click()

        # Give the portal time to process login
        page.wait_for_timeout(5000)

        print("\n========== LOGIN RESULT ==========")

        print("Current URL:")
        print(page.url)

        print("\nPage title:")
        print(page.title())

        print("\nPage text:")

        text = page.locator("body").inner_text()

        print(text[:12000])

        # -------------------------
        # CHECK WHETHER STILL ON LOGIN
        # -------------------------

        username_field = page.locator(
            'input[name="j_username"]'
        )

        if username_field.count() > 0 and username_field.is_visible():

            print("\n❌ LOGIN APPEARS TO HAVE FAILED.")

        else:

            print("\n✅ LOGIN PAGE IS NO LONGER VISIBLE.")

        browser.close()


if __name__ == "__main__":
    main()
