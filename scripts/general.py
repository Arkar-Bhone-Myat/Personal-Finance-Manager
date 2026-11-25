from datetime import datetime,tzinfo

EXPENSE_CATEGORIES = [
        "Housing",
        "Food and Dining",
        "Transportation",
        "Shopping",
        "Bills and Utilities",
        "Health and Wellness",
        "Entertainment and Subscriptions",
        "Travel",
        "Savings and goals",
        "Other",
    ]
INCOME_CATEGORIES = [
        "Salary",
        "Freelance / Side Income",
        "Investments",
        "Gift / Refunds",
        "Other income",
    ]
BUDGET_CATEGORIES = {
    "Housing": "A roof over your head. Peace of mind.",
    "Food and Dining": "Groceries, good meals, and coffee breaks.",
    "Transportation": "Everyday journeys, accounted for.",
    "Shopping": "A few more treats than planned.",
    "Bills and Utilities": "Keeping the lights on and bills on time.",
    "Health and Wellness": "Caring for your body and mind.",
    "Entertainment and Subscriptions": "Fun, media, and recurring memberships.",
    "Travel": "Trips, getaways, and new places.",
    "Savings and goals": "Setting aside money for what's next.",
    "Other": "For everything in between.",
}

def get_month_year(transactions: list[dict], date_format: str = "%y-%m-%d") -> list[str]:
    return [
        datetime.strptime(tx["date"].strip(), date_format).strftime("%B %Y")
        for tx in transactions
    ]

def get_next_tx_id(data: list[dict], prefix: str = "tx", width: int = 4) -> str:
    """Return the next ID like 'tx_004' based on existing data."""
    max_num = 0
    expected_prefix = f"{prefix}_"

    for record in data:
        record_id = record.get("id")
        if isinstance(record_id, str) and record_id.startswith(expected_prefix):
            suffix = record_id.removeprefix(expected_prefix)
            if suffix.isdigit():
                max_num = max(max_num, int(suffix))

    return f"{prefix}_{max_num + 1:0{width}d}"

def get_current_date_yy_mm_dd() -> str:
    """Return the current local date formatted as 'yy-mm-dd'."""
    now = datetime.now()
    return f"{now:%y-%m-%d}"

def has_non_empty_string_values(data: dict) -> bool:
    """Return False if any value in the dictionary is an empty string, else True."""
    return not any(value == "" for value in data.values())

def get_current_month_year():
    now = datetime.now()
    return f"{now:%B %Y}"

def get_current_upper_month_and_date(tz: tzinfo | None = None) -> str:

    now = datetime.now(tz)
    month = now.strftime("%B").capitalize()
    day = now.day

    return f"{month} {day}"

if __name__ == "__main__":
    print(get_current_month_year())