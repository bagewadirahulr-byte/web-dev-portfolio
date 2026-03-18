"""
💰 Personal Expense Tracker
A feature-rich command-line expense tracker built with Python's standard library only.
"""

import json
import csv
import os
from datetime import datetime

# Get absolute path to the data file in the same directory as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(BASE_DIR, "expenses.json")
CATEGORIES = ["Food", "Transport", "Shopping", "Health", "Entertainment", "Utilities", "Other"]
DIVIDER = "═" * 50


# ─────────────────────────────────────────────────
#  Data helpers
# ─────────────────────────────────────────────────

def load_expenses() -> list:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return []


def save_expenses(expenses: list) -> None:
    with open(DATA_FILE, "w") as f:
        json.dump(expenses, f, indent=2)


def next_id(expenses: list) -> int:
    return max((e["id"] for e in expenses), default=0) + 1


# ─────────────────────────────────────────────────
#  Display helpers
# ─────────────────────────────────────────────────

def print_header() -> None:
    os.system("cls" if os.name == "nt" else "clear")
    print(DIVIDER)
    print("        💰 Personal Expense Tracker")
    print(DIVIDER)
    print()


def print_menu() -> None:
    print("  MENU")
    print("  1. Add Expense")
    print("  2. View All Expenses")
    print("  3. Category Summary")
    print("  4. Delete Expense")
    print("  5. Export to CSV")
    print("  0. Exit")
    print()


def print_table(expenses: list) -> None:
    if not expenses:
        print("  No expenses recorded yet.\n")
        return

    col_widths = {"id": 4, "date": 12, "category": 14, "description": 28, "amount": 10}

    header = (
        f"  {'ID':<{col_widths['id']}} "
        f"{'Date':<{col_widths['date']}} "
        f"{'Category':<{col_widths['category']}} "
        f"{'Description':<{col_widths['description']}} "
        f"{'Amount':>{col_widths['amount']}}"
    )
    sep = "  " + "-" * (sum(col_widths.values()) + len(col_widths) - 1)

    print(sep)
    print(header)
    print(sep)
    total = 0.0
    for e in expenses:
        print(
            f"  {e['id']:<{col_widths['id']}} "
            f"{e['date']:<{col_widths['date']}} "
            f"{e['category']:<{col_widths['category']}} "
            f"{e['description']:<{col_widths['description']}} "
            f"₹{e['amount']:>{col_widths['amount'] - 1},.2f}"
        )
        total += e["amount"]
    print(sep)
    print(f"  {'TOTAL':<{col_widths['id'] + col_widths['date'] + col_widths['category'] + col_widths['description'] + 3}} ₹{total:>{col_widths['amount'] - 1},.2f}")
    print()


# ─────────────────────────────────────────────────
#  Actions
# ─────────────────────────────────────────────────

def add_expense(expenses: list) -> None:
    print_header()
    print("  ➕  ADD EXPENSE\n")

    description = input("  Description : ").strip()
    if not description:
        print("\n  ❌  Description cannot be empty.")
        input("\n  Press Enter to continue...")
        return

    # Amount
    while True:
        amount_str = input("  Amount (₹)  : ").strip()
        try:
            amount = float(amount_str)
            if amount <= 0:
                raise ValueError
            break
        except ValueError:
            print("  ⚠️  Please enter a valid positive number.")

    # Date
    while True:
        date_str = input("  Date [YYYY-MM-DD] (Enter for today): ").strip()
        if not date_str:
            date_str = datetime.today().strftime("%Y-%m-%d")
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            break
        except ValueError:
            print("  ⚠️  Invalid date format. Use YYYY-MM-DD.")

    # Category
    print("\n  Categories:")
    for i, cat in enumerate(CATEGORIES, 1):
        print(f"    {i}. {cat}")
    while True:
        cat_input = input(f"  Choose category [1-{len(CATEGORIES)}]: ").strip()
        try:
            cat_idx = int(cat_input) - 1
            if 0 <= cat_idx < len(CATEGORIES):
                category = CATEGORIES[cat_idx]
                break
            raise ValueError
        except ValueError:
            print(f"  ⚠️  Enter a number between 1 and {len(CATEGORIES)}.")

    expense = {
        "id": next_id(expenses),
        "description": description,
        "amount": round(amount, 2),
        "date": date_str,
        "category": category,
    }
    expenses.append(expense)
    save_expenses(expenses)
    print(f"\n  ✅  Expense added! (ID: {expense['id']})")
    input("\n  Press Enter to continue...")


def view_expenses(expenses: list) -> None:
    print_header()
    print("  📋  ALL EXPENSES\n")
    print_table(expenses)
    input("  Press Enter to continue...")


def category_summary(expenses: list) -> None:
    print_header()
    print("  📊  CATEGORY SUMMARY\n")

    if not expenses:
        print("  No expenses recorded yet.\n")
        input("  Press Enter to continue...")
        return

    totals: dict[str, float] = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0.0) + e["amount"]

    grand_total = sum(totals.values())
    max_amount = max(totals.values())
    bar_max = 30  # characters

    print(f"  {'Category':<16} {'Amount':>12}  {'% ':>6}  Chart")
    print("  " + "-" * 65)
    for cat, amt in sorted(totals.items(), key=lambda x: x[1], reverse=True):
        pct = (amt / grand_total * 100) if grand_total else 0
        bar_len = int((amt / max_amount) * bar_max) if max_amount else 0
        bar = "█" * bar_len
        print(f"  {cat:<16} ₹{amt:>11,.2f}  {pct:>5.1f}%  {bar}")

    print("  " + "-" * 65)
    print(f"  {'TOTAL':<16} ₹{grand_total:>11,.2f}  100.0%")
    print()
    input("  Press Enter to continue...")


def delete_expense(expenses: list) -> None:
    print_header()
    print("  🗑️   DELETE EXPENSE\n")
    print_table(expenses)

    if not expenses:
        input("  Press Enter to continue...")
        return

    id_str = input("  Enter ID to delete (or 0 to cancel): ").strip()
    try:
        expense_id = int(id_str)
    except ValueError:
        print("\n  ❌  Invalid ID.")
        input("\n  Press Enter to continue...")
        return

    if expense_id == 0:
        return

    original_count = len(expenses)
    updated = [e for e in expenses if e["id"] != expense_id]

    if len(updated) == original_count:
        print(f"\n  ❌  No expense found with ID {expense_id}.")
    else:
        save_expenses(updated)
        expenses.clear()
        expenses.extend(updated)
        print(f"\n  ✅  Expense ID {expense_id} deleted.")

    input("\n  Press Enter to continue...")


def export_csv(expenses: list) -> None:
    print_header()
    print("  📤  EXPORT TO CSV\n")

    if not expenses:
        print("  No expenses to export.\n")
        input("  Press Enter to continue...")
        return

    filename = f"expenses_{datetime.today().strftime('%Y%m%d_%H%M%S')}.csv"
    fieldnames = ["id", "date", "category", "description", "amount"]

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(expenses)

    print(f"  ✅  Exported {len(expenses)} expense(s) to '{filename}'")
    input("\n  Press Enter to continue...")


# ─────────────────────────────────────────────────
#  Main loop
# ─────────────────────────────────────────────────

def main() -> None:
    expenses = load_expenses()

    while True:
        print_header()
        print_menu()
        choice = input("  Enter choice: ").strip()

        if choice == "1":
            add_expense(expenses)
        elif choice == "2":
            view_expenses(expenses)
        elif choice == "3":
            category_summary(expenses)
        elif choice == "4":
            delete_expense(expenses)
        elif choice == "5":
            export_csv(expenses)
        elif choice == "0":
            print("\n  👋  Goodbye!\n")
            break
        else:
            input("\n  ⚠️  Invalid choice. Press Enter to try again...")


if __name__ == "__main__":
    main()
