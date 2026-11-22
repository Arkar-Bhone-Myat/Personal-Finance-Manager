"""JSON storage interface stubs for the Penny personal finance application.

This module defines the function signatures and docstrings for reading and
writing transaction, savings goal, budget, and recurring item records stored in
the ``data/`` directory.
"""
from pathlib import Path
import json
from typing import Any


def load_json(filename: str, default: Any) -> Any:
    path = Path(filename)

    try:
        with path.open("r" , encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


def save_json(filename: str, data: Any) -> None:

    path = Path(filename)

    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)
    
    


# ---------------------------------------------------------------------------
# Transactions (transactions.json)
# ---------------------------------------------------------------------------


def get_transactions() -> list[dict[str, Any]]:
    """Load and return all transaction records from ``transactions.json``.

    Returns:
        A list of transaction dictionaries, defaulting to ``[]`` if missing.
    """
    pass


def save_transactions(transactions: list[dict[str, Any]]) -> None:
    """Overwrite ``transactions.json`` with the provided transaction list.

    Args:
        transactions: Full list of transaction dictionaries to persist.
    """
    pass


def add_transaction(transaction: dict[str, Any]) -> None:
    """Append a single transaction record and save ``transactions.json``.

    Loads existing transactions, appends ``transaction`` to the list, and
    writes the updated list back to ``transactions.json``.

    Args:
        transaction: Transaction dictionary containing ``id``, ``merchant``,
            ``category``, ``date`` (``YYYY-MM-DD``), ``amount`` (``>= 0``), and
            ``type`` (``"income"`` or ``"expense"``).
    """
    pass


def delete_transaction(tx_id: str) -> bool:
    """Remove a transaction by ID and save ``transactions.json``.

    Loads existing transactions, filters out the record matching ``tx_id``,
    and writes the remaining list back to ``transactions.json``.

    Args:
        tx_id: Unique identifier of the transaction to remove.

    Returns:
        ``True`` if a matching transaction was removed, ``False`` otherwise.
    """
    pass


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