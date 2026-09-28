from playwright.sync_api import sync_playwright


WEWORLD_URL = "https://weworld.welingkar.org/home.htm"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        print("Opening WeWorld...")
        page.goto(WEWORLD_URL, wait_until="networkidle")

        print("Page title:", page.title())
        print("Current URL:", page.url)

        browser.close()


if __name__ == "__main__":
    main()
