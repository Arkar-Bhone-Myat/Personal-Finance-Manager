"""JSON storage interface stubs for the Penny personal finance application.

This module defines the function signatures and docstrings for reading and
writing transaction, savings goal, budget, and recurring item records stored in
the ``data/`` directory.
"""
from pathlib import Path
import json
from typing import Any

DATA_DIR = Path("data")


def load_json(filename: str, default: Any) -> Any:
    path = DATA_DIR / filename

    try:
        with path.open("r" , encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(filename: str, data: Any) -> None:

    path = DATA_DIR / filename

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
    
    


# ---------------------------------------------------------------------------
# Transactions (transactions.json)
# ---------------------------------------------------------------------------


def get_transactions() -> list[dict[str, Any]]:

    return load_json(DATA_DIR / "transactions.json", [])


def save_transactions(transactions: list[dict[str, Any]]) -> None:

    save_json(DATA_DIR / "transactions.json", transactions)
 


def add_transaction(transaction: dict[str, Any]) -> None:

    current_transactions = get_transactions()
    current_transactions.append(transaction)
    save_json(DATA_DIR / "transactions.json",current_transactions)



def delete_transaction(tx_id: str) -> bool:

    current_transactions = get_transactions()

    for transaction in current_transactions:
        if transaction["id"] == tx_id:
            current_transactions.remove(transaction)
            save_json(DATA_DIR / "transactions.json", current_transactions)
            return True
        
    return False




# ---------------------------------------------------------------------------
# Goals (goals.json)
# ---------------------------------------------------------------------------


def get_goals() -> list[dict[str, Any]]:
    """Load and return all savings goal records from ``goals.json``.

    Returns:
        A list of goal dictionaries, defaulting to ``[]`` if missing.
    """
    pass


def save_goals(goals: list[dict[str, Any]]) -> None:
    """Overwrite ``goals.json`` with the provided list of savings goals.

    Args:
        goals: Full list of savings goal dictionaries to persist.
    """
    pass


def update_goal_progress(goal_id: str, new_amount: float) -> bool:
    """Update the saved amount for a specific goal in ``goals.json``.

    Finds the goal matching ``goal_id``, updates its ``current_amount`` to
    ``new_amount``, and saves the updated goals list back to ``goals.json``.

    Args:
        goal_id: Unique identifier of the savings goal to update.
        new_amount: Updated ``current_amount`` value (``>= 0``).

    Returns:
        ``True`` if the goal was found and updated, ``False`` otherwise.
    """
    pass


# ---------------------------------------------------------------------------
# Budgets (budgets.json)
# ---------------------------------------------------------------------------


def get_budgets() -> dict[str, Any]:
    """Load and return the budget configuration from ``budgets.json``.

    Returns:
        A dictionary containing ``initial_balance``, ``monthly_budget``, and
        per-category limits under ``categories``.
    """
    pass


def save_budgets(budgets: dict[str, Any]) -> None:
    """Save the updated budget configuration dictionary to ``budgets.json``.

    Args:
        budgets: Budget dictionary with ``initial_balance``, ``monthly_budget``,
            and ``categories`` mapping.
    """
    pass


# ---------------------------------------------------------------------------
# Recurring Items (recurring.json)
# ---------------------------------------------------------------------------


def get_recurring_items() -> list[dict[str, Any]]:
    """Load and return all recurring bills and income from ``recurring.json``.

    Returns:
        A list of recurring item dictionaries, defaulting to ``[]`` if missing.
    """
    pass


def save_recurring_items(items: list[dict[str, Any]]) -> None:
    """Overwrite ``recurring.json`` with the provided recurring items list.

    Args:
        items: Full list of recurring item dictionaries to persist.
    """
    pass

if __name__ == "__main__":
    pass