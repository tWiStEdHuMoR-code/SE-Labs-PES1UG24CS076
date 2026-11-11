"""
Lab 7 - FIXED version of the ATM application (Lab 6: atm_withdrawal.py).

Hardening done after fuzz testing with Hypothesis:
  * every argument is type- and range-checked before it is used
  * every invalid input raises ValueError (never TypeError / silent garbage)
  * bool is NOT accepted where a number is expected (True == 1 in Python)
  * float / NaN / inf are rejected where whole numbers are required
Business rules (limits, fees, 3-attempt PIN lock, note split) are unchanged,
so all the Lab 6 tests still pass.
"""

DAILY_LIMIT = {"savings": 25000, "current": 50000}
MAX_PIN = 9999


def _is_int(value):
    """True only for real integers (bool is a subclass of int, so exclude it)."""
    return isinstance(value, int) and not isinstance(value, bool)


def _is_pin(value):
    return _is_int(value) and 0 <= value <= MAX_PIN


def withdraw(balance, amount, account_type, own_bank):
    # --- input validation -------------------------------------------------
    if not isinstance(account_type, str) or account_type not in DAILY_LIMIT:
        raise ValueError("unknown account")
    if not _is_int(amount) or amount <= 0 or amount % 100 != 0:
        raise ValueError("invalid amount")
    if not _is_int(balance) or balance < 0:
        raise ValueError("invalid balance")
    if not isinstance(own_bank, bool):
        raise ValueError("invalid own_bank flag")

    # --- business logic (unchanged) ---------------------------------------
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
    # --- input validation -------------------------------------------------
    if not _is_int(attempts) or attempts < 0:
        raise ValueError("invalid attempts")
    if not _is_pin(entered):
        raise ValueError("invalid entered pin")
    if not _is_pin(actual):
        raise ValueError("invalid actual pin")

    # --- business logic (unchanged) ---------------------------------------
    if attempts >= 3:
        return "card blocked"
    if entered == actual:
        return "ok"
    if attempts == 2:
        return "card blocked"
    return "retry"


def note_breakup(amount):
    # --- input validation -------------------------------------------------
    if not _is_int(amount) or amount < 0 or amount % 100 != 0:
        raise ValueError("invalid amount")

    # --- business logic (unchanged) ---------------------------------------
    notes_500 = amount // 500
    remaining = amount % 500
    if remaining >= 200:
        notes_200 = remaining // 200
        remaining = remaining % 200
    else:
        notes_200 = 0
    return notes_500, notes_200, remaining // 100


# --------------------------------------------------------------------------
# Demo: identical calls to the original version, so the outputs can be compared
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
