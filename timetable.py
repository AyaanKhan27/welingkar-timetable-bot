import os
import re
from playwright.sync_api import sync_playwright


WEWORLD_URL = "https://weworld.welingkar.org/home.htm"


def login(page, username, password):

    print("Opening WeWorld...")

    page.goto(
        WEWORLD_URL,
        wait_until="networkidle",
        timeout=60000
    )

    print("Login page:", page.url)

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


def find_schedule_table(page):

    print("\nSearching for schedule table...")

    tables = page.locator("table")

    print("Total tables found:", tables.count())

    for i in range(tables.count()):

        table = tables.nth(i)

        try:
            text = table.inner_text().strip()

            # A schedule table should contain
            # both a time and a classroom/subject.
            has_time = bool(
                re.search(
                    r"\d{1,2}:\d{2}\s*(AM|PM)",
                    text,
                    re.IGNORECASE
                )
            )

            has_room = (
                "Class Room" in text
                or "Classroom" in text
                or "Logic" in text
                or "Nirvana" in text
            )

            if has_time and has_room:

                print(
                    f"Potential schedule table found: #{i}"
                )

                print("\nTABLE TEXT:")
                print(text)

                return table

        except Exception as e:

            print(
                f"Could not inspect table {i}: {e}"
            )

    return None


def extract_schedule(table):

    print("\nExtracting timetable...")

    rows = table.locator("tr")

    print("Rows found:", rows.count())

    all_rows = []

    for i in range(rows.count()):

        cells = rows.nth(i).locator("th, td")

        row_data = []

        for j in range(cells.count()):

            value = cells.nth(j).inner_text().strip()

            # Normalize whitespace
            value = re.sub(
                r"\s+",
                " ",
                value
            )

            row_data.append(value)

        if row_data:
            all_rows.append(row_data)

    print("\nRAW TABLE DATA:")

    for row in all_rows:
        print(row)

    if len(all_rows) < 3:

        raise Exception(
            "Schedule table does not contain "
            "the expected 3 rows."
        )

    times = all_rows[0]
    subjects = all_rows[1]
    rooms = all_rows[2]

    schedule = []

    number_of_classes = min(
        len(times),
        len(subjects),
        len(rooms)
    )

    for i in range(number_of_classes):

        if not times[i]:
            continue

        schedule.append({
            "time": times[i],
            "subject": subjects[i],
            "room": rooms[i]
        })

    return schedule


def sort_schedule(schedule):

    def get_start_time(item):

        match = re.search(
            r"(\d{1,2}):(\d{2})\s*(AM|PM)",
            item["time"],
            re.IGNORECASE
        )

        if not match:
            return 9999

        hour = int(match.group(1))
        minute = int(match.group(2))
        period = match.group(3).upper()

        if period == "AM":

            if hour == 12:
                hour = 0

        else:

            if hour != 12:
                hour += 12

        return hour * 60 + minute

    return sorted(
        schedule,
        key=get_start_time
    )


def format_whatsapp_message(schedule):

    message = "📚 *TODAY'S CLASS SCHEDULE*\n\n"

    for item in schedule:

        message += (
            f"🕐 *{item['time']}*\n"
            f"📖 {item['subject']}\n"
            f"🏫 {item['room']}\n\n"
        )

    return message.strip()


def main():

    username = os.environ["WEWORLD_USERNAME"]
    password = os.environ["WEWORLD_PASSWORD"]

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        # Login
        login(
            page,
            username,
            password
        )

        # Find timetable
        table = find_schedule_table(page)

        if table is None:

            print(
                "\n❌ Schedule table could not be found."
            )

            browser.close()
            return

        # Extract
        schedule = extract_schedule(table)

        # Sort chronologically
        schedule = sort_schedule(schedule)

        print("\n========== FINAL SCHEDULE ==========")

        for item in schedule:

            print(
                f"{item['time']} | "
                f"{item['subject']} | "
                f"{item['room']}"
            )

        # Format WhatsApp message
        message = format_whatsapp_message(
            schedule
        )

        print(
            "\n========== WHATSAPP MESSAGE =========="
        )

        print(message)

        browser.close()


if __name__ == "__main__":
    main()
