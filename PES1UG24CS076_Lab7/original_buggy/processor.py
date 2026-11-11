"""
Lab 7 - ORIGINAL (BUGGY) version of the ATM application from Lab 6
(atm_withdrawal.py renamed to processor.py).

The three functions are unchanged from Lab 6. Only the demo block at the
bottom was added so that `python processor.py` prints visible output.
"""

DAILY_LIMIT = {"savings": 25000, "current": 50000}


def withdraw(balance, amount, account_type, own_bank):
    if account_type not in DAILY_LIMIT:
        raise ValueError("unknown account")
    if amount <= 0 or amount % 100 != 0:
        raise ValueError("invalid amount")
    if amount > DAILY_LIMIT[account_type]:
        return "limit exceeded"
    fee = 0
    if not own_bank:
        fee = 20
        if amount > 10000:
            fee += 10
    if amount + fee > balance:
        return "insufficient funds"
    return balance - amount - fee


def pin_check(entered, actual, attempts):
    if attempts >= 3:
        return "card blocked"
    if entered == actual:
        return "ok"
    if attempts == 2:
        return "card blocked"
    return "retry"


def note_breakup(amount):
    if amount % 100 != 0:
        raise ValueError("invalid amount")
    notes_500 = amount // 500
    remaining = amount % 500
    if remaining >= 200:
        notes_200 = remaining // 200
        remaining = remaining % 200
    else:
        notes_200 = 0
    return notes_500, notes_200, remaining // 100


# --------------------------------------------------------------------------
# Demo: run each call and print either the result or the exception raised.
# --------------------------------------------------------------------------
def _try(label, func, *args):
    call = f"{label}({', '.join(repr(a) for a in args)})"
    try:
        result = func(*args)
        print(f"{call:<52} -> {result!r}")
    except Exception as exc:  # noqa: BLE001 - demo only
        print(f"{call:<52} -> {type(exc).__name__}: {exc}")


if __name__ == "__main__":
    print("=== withdraw ===")
    _try("withdraw", withdraw, 5000, 1000, "savings", True)
    _try("withdraw", withdraw, 5000, 1000, "savings", False)
    _try("withdraw", withdraw, 5000, 1000, "salary", True)
    _try("withdraw", withdraw, None, 1000, "savings", True)
    _try("withdraw", withdraw, 5000, None, "savings", True)
    _try("withdraw", withdraw, 5000, 1000, ["savings"], True)
    _try("withdraw", withdraw, float("nan"), 1000, "savings", True)
    _try("withdraw", withdraw, -500, 100, "savings", True)
    _try("withdraw", withdraw, 5000, 1000.0, "savings", True)
    _try("withdraw", withdraw, 5000, 1000, "savings", None)

    print("\n=== pin_check ===")
    _try("pin_check", pin_check, 1234, 1234, 0)
    _try("pin_check", pin_check, 1111, 1234, 2)
    _try("pin_check", pin_check, None, None, 0)
    _try("pin_check", pin_check, True, 1, 0)
    _try("pin_check", pin_check, 1234, 1234, None)
    _try("pin_check", pin_check, 1111, 1234, -5)

    print("\n=== note_breakup ===")
    _try("note_breakup", note_breakup, 1200)
    _try("note_breakup", note_breakup, 150)
    _try("note_breakup", note_breakup, None)
    _try("note_breakup", note_breakup, -100)
    _try("note_breakup", note_breakup, 100.0)
    _try("note_breakup", note_breakup, False)
