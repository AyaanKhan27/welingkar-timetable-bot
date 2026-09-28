from playwright.sync_api import sync_playwright


WEWORLD_URL = "https://weworld.welingkar.org/home.htm"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Opening WeWorld...")
        page.goto(WEWORLD_URL, wait_until="networkidle")

        print("\n--- PAGE INFORMATION ---")
        print("Title:", page.title())
        print("URL:", page.url)

        print("\n--- INPUT FIELDS ---")

        inputs = page.locator("input")
        count = inputs.count()

        print("Number of inputs:", count)

        for i in range(count):
            element = inputs.nth(i)

            print(f"\nInput {i + 1}")

            for attribute in [
                "type",
                "name",
                "id",
                "placeholder",
                "autocomplete",
            ]:
                try:
                    print(
                        f"{attribute}:",
                        element.get_attribute(attribute)
                    )
                except Exception:
                    pass

        print("\n--- BUTTONS ---")

        buttons = page.locator("button, input[type='submit']")
        count = buttons.count()

        print("Number of buttons:", count)

        for i in range(count):
            element = buttons.nth(i)

            print(
                f"Button {i + 1}:",
                element.inner_text() if element.evaluate(
                    "(el) => el.tagName === 'BUTTON'"
                ) else element.get_attribute("value")
            )

        browser.close()


if __name__ == "__main__":
    main()
