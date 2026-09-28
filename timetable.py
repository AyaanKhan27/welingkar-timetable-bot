import os
from playwright.sync_api import sync_playwright


WEWORLD_URL = "https://weworld.welingkar.org/home.htm"


def main():

    username = os.environ["WEWORLD_USERNAME"]
    password = os.environ["WEWORLD_PASSWORD"]

    with sync_playwright() as p:

        browser = p.chromium.launch(headless=True)

        page = browser.new_page()

        # -------------------------
        # LOGIN
        # -------------------------

        print("Opening WeWorld...")

        page.goto(
            WEWORLD_URL,
            wait_until="networkidle",
            timeout=60000
        )

        page.locator(
            'input[name="j_username"]'
        ).fill(username)

        page.locator(
            'input[name="j_password"]'
        ).fill(password)

        page.get_by_role(
            "button",
            name="Login"
        ).click()

        page.wait_for_timeout(5000)

        print("Logged in.")
        print("Dashboard URL:", page.url)

        # -------------------------
        # FIND TODAY'S SCHEDULE
        # -------------------------

        print("\nSearching for TODAY'S SCHEDULE...")

        schedule_heading = page.get_by_text(
            "TODAY'S SCHEDULE",
            exact=False
        )

        print(
            "Schedule heading count:",
            schedule_heading.count()
        )

        if schedule_heading.count() == 0:
            print("❌ Could not find Today's Schedule")
            browser.close()
            return

        heading = schedule_heading.first

        print("✅ Today's Schedule found.")

        # -------------------------
        # INSPECT PARENT ELEMENTS
        # -------------------------

        print("\n--- PARENT STRUCTURE ---")

        current = heading

        for level in range(6):

            try:

                tag = current.evaluate(
                    "(el) => el.tagName"
                )

                classes = current.get_attribute(
                    "class"
                )

                element_id = current.get_attribute(
                    "id"
                )

                print(
                    f"Level {level}: "
                    f"TAG={tag}, "
                    f"ID={element_id}, "
                    f"CLASS={classes}"
                )

                current = current.locator("..")

            except Exception as e:

                print(
                    "Could not inspect level:",
                    e
                )

                break

        # -------------------------
        # INSPECT NEARBY TABLES
        # -------------------------

        print("\n--- TABLES ON PAGE ---")

        tables = page.locator("table")

        print(
            "Number of tables:",
            tables.count()
        )

        for i in range(tables.count()):

            table = tables.nth(i)

            try:

                text = table.inner_text()

                if any(
                    keyword in text.upper()
                    for keyword in [
                        "TODAY'S SCHEDULE",
                        "PTI",
                        "EWM",
                        "YOGA",
                        "CLASS ROOM"
                    ]
                ):

                    print(
                        f"\n*** POSSIBLE SCHEDULE TABLE {i} ***"
                    )

                    print(text)

                    print(
                        "\nHTML:"
                    )

                    print(
                        table.evaluate(
                            "(el) => el.outerHTML"
                        )[:15000]
                    )

            except Exception as e:

                print(
                    f"Could not inspect table {i}:",
                    e
                )

        browser.close()


if __name__ == "__main__":
    main()
