import os
from playwright.sync_api import sync_playwright


WEWORLD_URL = "https://weworld.welingkar.org/home.htm"


def inspect_frame(frame):
    print("\n========================================")
    print("FRAME URL:", frame.url)
    print("========================================")

    try:
        inputs = frame.locator("input")
        count = inputs.count()

        print("INPUT COUNT:", count)

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

    except Exception as e:
        print("Could not inspect inputs:", e)


def main():

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

        print("\nPAGE URL:")
        print(page.url)

        print("\nPAGE TITLE:")
        print(page.title())

        print("\nNUMBER OF FRAMES:")
        print(len(page.frames))

        for frame in page.frames:
            inspect_frame(frame)

        print("\n\n--- PAGE TEXT ---")

        try:
            print(page.locator("body").inner_text()[:10000])
        except Exception as e:
            print("Could not read body:", e)

        browser.close()


if __name__ == "__main__":
    main()
