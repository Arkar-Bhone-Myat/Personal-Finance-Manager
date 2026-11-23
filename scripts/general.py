from datetime import datetime

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