"""JSON storage interface stubs for the Penny personal finance application.

This module defines the function signatures and docstrings for reading and
writing transaction, savings goal, budget, and recurring item records stored in
the ``data/`` directory.
"""
from pathlib import Path
import json
from typing import Any


def load_json(filename: str, default: Any) -> Any:
    """Load JSON data from a file.

    Args:
        filename: Path to the JSON file.
        default: Value to return if the file is missing or invalid.

    Returns:
        The parsed JSON data, or ``default``.
    """
    path = Path(filename)

    try:
        with path.open("r" , encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(filename: str, data: Any) -> None:
    """Write data to a JSON file.

    Args:
        filename: Path to the JSON file.
        data: Python data to serialize as JSON.
    """

    path = Path(filename)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
    
    


# ---------------------------------------------------------------------------
# Transactions (transactions.json)
# ---------------------------------------------------------------------------


def get_transactions() -> list[dict[str, Any]]:
    """Load and return all transactions from ``data/transactions.json``.

    Returns:
        A list of transaction dictionaries, or an empty list if the file
        is missing or invalid.
    """

    return load_json("data/transactions.json", [])


def save_transactions(transactions: list[dict[str, Any]]) -> None:
    """Save the full transaction list to ``data/transactions.json``.

    Args:
        transactions: Transaction dictionaries to save.
    """
    save_json("data/transactions.json", transactions)
 


def add_transaction(transaction: dict[str, Any]) -> None:
    """Add one transaction and save the updated list.

    Args:
        transaction: Transaction dictionary to add.
    """
    current_transactions = get_transactions()
    current_transactions.append(transaction)
    save_json("data/transactions.json",current_transactions)



def delete_transaction(tx_id: str) -> bool:
    """Delete a transaction by ID and save the updated list.

    Args:
        tx_id: ID of the transaction to remove.

    Returns:
        ``True`` if a transaction was removed, otherwise ``False``.
    """
    current_transactions = get_transactions()

    for transaction in current_transactions:
        if transaction["id"] == tx_id:
            current_transactions.remove(transaction)
            save_transactions(current_transactions)
            return True
        
    return False




# ---------------------------------------------------------------------------
# Goals (goals.json)
# ---------------------------------------------------------------------------


def get_goals() -> list[dict[str, Any]]:
    """Load and return all savings goals from ``data/goals.json``.

    Returns:
        A list of goal dictionaries, or an empty list if the file is missing
        or contains invalid JSON.
    """

    return load_json("data/goals.json", [])  


def save_goals(goals: list[dict[str, Any]]) -> None:
    """Save the full goals list to ``data/goals.json``.

    Args:
        goals: Goal dictionaries to save.
    """

    save_json("data/goals.json", goals)


def add_goals(goals: dict[str, Any]) -> None:
    """Add one goal and save the updated list.

    Args:
        goals: Goal dictionary to add.
    """
    current_goals = get_goals()
    current_goals.append(goals)
    save_goals(current_goals)


def update_goal_progress(goal_id: str, new_amount: float) -> bool:
    """Set the saved amount for a goal and save the updated goals list.

    Args:
        goal_id: ID of the goal to update.
        new_amount: New saved amount; must not be negative.

    Returns:
        ``True`` if the goal was found and updated, otherwise ``False``.

    Raises:
        ValueError: If ``new_amount`` is negative.
    """
    
    current_goals = get_goals()

    if new_amount < 0 :
        raise ValueError("Invalid amount for goal")

    for goal in current_goals:
        if goal["id"] == goal_id:
            goal["current_amount"] = new_amount
            save_goals(current_goals)
            return True
    return False


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