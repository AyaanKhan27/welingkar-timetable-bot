import os
import re
from playwright.sync_api import sync_playwright


WEWORLD_URL = "https://weworld.welingkar.org/home.htm"


def login(page, username, password):
    print("Opening WeWorld...")

    page.goto(WEWORLD_URL, wait_until="domcontentloaded", timeout=60000)

    print("Logging in...")

    # Username
    page.locator('input[name="j_username"]').fill(username)

    # Password
    page.locator('input[name="j_password"]').fill(password)

    # Click Login
    page.get_by_role("button", name="Login").click()

    # Wait for dashboard
    page.wait_for_load_state("domcontentloaded", timeout=60000)

    # Give the page a little time to load dashboard content
    page.wait_for_timeout(3000)

    print(f"Logged in successfully.")
    print(f"Current URL: {page.url}")
    print(f"Page title: {page.title()}")


def find_schedule_table(page):
    print("Searching for today's schedule table...")

    tables = page.locator("table")
    table_count = tables.count()

    print(f"Found {table_count} tables on the page.")

    time_pattern = re.compile(
        r"\d{1,2}:\d{2}\s*(AM|PM)",
        re.IGNORECASE
    )

    room_keywords = [
        "class room",
        "classroom",
        "logica",
        "nirvana"
    ]

    for i in range(table_count):
        table = tables.nth(i)

        try:
            table_text = table.inner_text(timeout=5000)
        except Exception:
            continue

        has_time = bool(time_pattern.search(table_text))
        has_room = any(
            keyword in table_text.lower()
            for keyword in room_keywords
        )

        if has_time and has_room:
            print(f"Schedule table found: table #{i + 1}")
            return table

    return None


def extract_schedule(table):
    print("Extracting timetable...")

    rows = table.locator("tr")
    row_count = rows.count()

    raw_rows = []

    for i in range(row_count):
        row = rows.nth(i)

        cells = row.locator("th, td")
        cell_count = cells.count()

        values = []

        for j in range(cell_count):
            value = cells.nth(j).inner_text().strip()
            values.append(value)

        if values:
            raw_rows.append(values)

    print("Raw timetable rows:")
    for row in raw_rows:
        print(row)

    # Expected structure:
    #
    # Row 1 = timings
    # Row 2 = subjects
    # Row 3 = rooms
    #
    # Example:
    # [
    #   ["12:30 PM-02:30 PM", "03:00 PM-05:00 PM",
    #    "10:00 AM-12:00 PM", "07:15 AM-08:30 AM"],
    #
    #   ["PTI", "PTI", "EWM", "Yoga"],
    #
    #   ["Class Room 410", "Class Room 410",
    #    "Logica 401", "Nirvana 402"]
    # ]

    if len(raw_rows) < 3:
        raise Exception("Could not identify timetable rows.")

    timings = raw_rows[0]
    subjects = raw_rows[1]
    rooms = raw_rows[2]

    schedule = []

    item_count = min(
        len(timings),
        len(subjects),
        len(rooms)
    )

    for i in range(item_count):

        timing = timings[i].strip()
        subject = subjects[i].strip()
        room = rooms[i].strip()

        # Ignore empty columns
        if not timing or not subject:
            continue

        schedule.append({
            "time": timing,
            "subject": subject,
            "room": room
        })

    return schedule


def get_start_time(time_string):
    """
    Extract the starting time from something like:

    12:30 PM-02:30 PM
    07:15 AM-08:30 AM
    """

    match = re.search(
        r"(\d{1,2}):(\d{2})\s*(AM|PM)",
        time_string,
        re.IGNORECASE
    )

    if not match:
        return 9999

    hour = int(match.group(1))
    minute = int(match.group(2))
    period = match.group(3).upper()

    # Convert to 24-hour format
    if period == "AM":
        if hour == 12:
            hour = 0
    else:
        if hour != 12:
            hour += 12

    return hour * 60 + minute


def sort_schedule(schedule):
    print("Sorting timetable chronologically...")

    return sorted(
        schedule,
        key=lambda item: get_start_time(item["time"])
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

    username = os.environ.get("WEWORLD_USERNAME")
    password = os.environ.get("WEWORLD_PASSWORD")

    if not username:
        raise Exception(
            "WEWORLD_USERNAME environment variable is missing."
        )

    if not password:
        raise Exception(
            "WEWORLD_PASSWORD environment variable is missing."
        )

    print("========================================")
    print("      WELINGKAR TIMETABLE GENERATOR")
    print("========================================")

    with sync_playwright() as p:

        browser = p.chromium.launch(
            headless=True
        )

        page = browser.new_page()

        try:

            # --------------------------------
            # LOGIN
            # --------------------------------

            login(
                page,
                username,
                password
            )

            # --------------------------------
            # FIND SCHEDULE TABLE
            # --------------------------------

            table = find_schedule_table(page)

            if table is None:

                print(
                    "\n❌ Schedule table could not be found."
                )

                raise Exception(
                    "Schedule table could not be found."
                )

            # --------------------------------
            # EXTRACT SCHEDULE
            # --------------------------------

            schedule = extract_schedule(table)

            if not schedule:

                raise Exception(
                    "No classes were found in the schedule."
                )

            # --------------------------------
            # SORT CHRONOLOGICALLY
            # --------------------------------

            schedule = sort_schedule(schedule)

            # --------------------------------
            # DISPLAY FINAL SCHEDULE
            # --------------------------------

            print("\n========== FINAL SCHEDULE ==========")

            for item in schedule:

                print(
                    f"{item['time']} | "
                    f"{item['subject']} | "
                    f"{item['room']}"
                )

            # --------------------------------
            # CREATE WHATSAPP MESSAGE
            # --------------------------------

            whatsapp_message = format_whatsapp_message(
                schedule
            )

            print(
                "\n========== WHATSAPP MESSAGE =========="
            )

            print(whatsapp_message)

            print(
                "\n========================================"
            )
            print("Timetable generation completed.")
            print("========================================")

        finally:

            browser.close()


if __name__ == "__main__":
    main()
