"""
Lab 7 - Hypothesis fuzz tests for processor.py (withdraw, pin_check, note_breakup).

Three kinds of properties are checked for every function:
  1. NO-CRASH   : for ANY input the function either returns a well-formed result
                  or raises ValueError. Any other exception (TypeError, ...) or a
                  malformed result (e.g. float nan) is a bug.
  2. REJECTION  : clearly invalid input must raise ValueError.
  3. INVARIANTS : for valid input the result must satisfy the business rules.

Run:  pytest test_processor.py      (or: python -m pytest test_processor.py)
"""
import pytest
from hypothesis import given, settings, assume, strategies as st

from processor import withdraw, pin_check, note_breakup, DAILY_LIMIT

SETTINGS = settings(max_examples=300, deadline=None)

# ---------------------------------------------------------------------------
# Strategies
# ---------------------------------------------------------------------------
# "Anything": every kind of value a caller could wrongly pass in.
anything = st.one_of(
    st.none(),
    st.booleans(),
    st.integers(),
    st.floats(),                                   # includes nan, inf, -inf
    st.text(),
    st.binary(),
    st.lists(st.integers()),                       # unhashable
    st.dictionaries(st.text(), st.integers()),     # unhashable
)

# Valid values
valid_account = st.sampled_from(sorted(DAILY_LIMIT))
valid_amount = st.integers(min_value=1, max_value=600).map(lambda k: k * 100)
valid_balance = st.integers(min_value=0, max_value=10_000_000)
valid_pin = st.integers(min_value=0, max_value=9999)
valid_attempts = st.integers(min_value=0, max_value=10)
valid_notes_amount = st.integers(min_value=0, max_value=10_000).map(lambda k: k * 100)


def mixed(valid):
    """Mostly-valid values with the odd garbage value mixed in (reaches deeper code)."""
    return st.one_of(valid, valid, anything)


def is_real_int(x):
    return isinstance(x, int) and not isinstance(x, bool)


def check_only_value_error(func, *args):
    """Call func; allow ValueError, fail on any other exception. Return result or None."""
    try:
        return func(*args)
    except ValueError:
        return None
    except Exception as exc:  # noqa: BLE001
        pytest.fail(f"{func.__name__}{args!r} crashed with {type(exc).__name__}: {exc}")


# ===========================================================================
# withdraw
# ===========================================================================
@SETTINGS
@given(balance=mixed(valid_balance), amount=mixed(valid_amount),
       account=mixed(valid_account), own_bank=mixed(st.booleans()))
def test_withdraw_never_crashes(balance, amount, account, own_bank):
    """Any input -> ValueError or a well-formed result (never TypeError, never nan)."""
    result = check_only_value_error(withdraw, balance, amount, account, own_bank)
    if result is not None:
        assert is_real_int(result) or result in ("limit exceeded", "insufficient funds"), \
            f"malformed result {result!r}"


@SETTINGS
@given(account=anything, balance=valid_balance, amount=valid_amount, own_bank=st.booleans())
def test_withdraw_rejects_bad_account_type(account, balance, amount, own_bank):
    assume(not (isinstance(account, str) and account in DAILY_LIMIT))
    with pytest.raises(ValueError):
        withdraw(balance, amount, account, own_bank)


@SETTINGS
@given(
    amount=st.one_of(
        st.integers().filter(lambda x: x <= 0 or x % 100 != 0),
        st.floats(), st.text(), st.none(), st.booleans(), st.lists(st.integers())),
    balance=valid_balance, account=valid_account, own_bank=st.booleans())
def test_withdraw_rejects_bad_amount(amount, balance, account, own_bank):
    """Zero, negative, non-multiple of 100, floats (incl. 100.0 / nan / inf), None, bool, str."""
    with pytest.raises(ValueError):
        withdraw(balance, amount, account, own_bank)


@SETTINGS
@given(
    balance=st.one_of(st.integers(max_value=-1), st.floats(), st.text(),
                      st.none(), st.booleans(), st.lists(st.integers())),
    amount=valid_amount, account=valid_account, own_bank=st.booleans())
def test_withdraw_rejects_bad_balance(balance, amount, account, own_bank):
    """Negative, float/nan, None, bool, str balances must be rejected."""
    with pytest.raises(ValueError):
        withdraw(balance, amount, account, own_bank)


@SETTINGS
@given(own_bank=st.one_of(st.none(), st.integers(), st.floats(), st.text(),
                          st.lists(st.integers())),
       balance=valid_balance, amount=valid_amount, account=valid_account)
def test_withdraw_rejects_non_bool_own_bank(own_bank, balance, amount, account):
    with pytest.raises(ValueError):
        withdraw(balance, amount, account, own_bank)


@SETTINGS
@given(balance=valid_balance, amount=valid_amount, account=valid_account, own_bank=st.booleans())
def test_withdraw_invariants(balance, amount, account, own_bank):
    result = withdraw(balance, amount, account, own_bank)
    if amount > DAILY_LIMIT[account]:
        assert result == "limit exceeded"
    elif isinstance(result, str):
        assert result == "insufficient funds"
        assert balance < amount + (0 if own_bank else 20)   # even the cheapest fee failed
    else:
        assert is_real_int(result)
        assert 0 <= result <= balance - amount               # money never created
        fee = balance - amount - result
        if own_bank:
            assert fee == 0                                  # own bank is free
        else:
            assert fee == (30 if amount > 10000 else 20)     # other-bank fee tiers


# ===========================================================================
# pin_check
# ===========================================================================
@SETTINGS
@given(entered=mixed(valid_pin), actual=mixed(valid_pin), attempts=mixed(valid_attempts))
def test_pin_check_never_crashes(entered, actual, attempts):
    result = check_only_value_error(pin_check, entered, actual, attempts)
    if result is not None:
        assert result in ("ok", "retry", "card blocked")


@SETTINGS
@given(entered=st.one_of(st.none(), st.booleans(), st.floats(), st.text(),
                         st.integers(max_value=-1), st.integers(min_value=10_000),
                         st.lists(st.integers())),
       actual=valid_pin, attempts=valid_attempts)
def test_pin_check_rejects_bad_entered_pin(entered, actual, attempts):
    with pytest.raises(ValueError):
        pin_check(entered, actual, attempts)


@SETTINGS
@given(actual=st.one_of(st.none(), st.booleans(), st.floats(), st.text(),
                        st.integers(max_value=-1), st.integers(min_value=10_000),
                        st.lists(st.integers())),
       entered=valid_pin, attempts=valid_attempts)
def test_pin_check_rejects_bad_stored_pin(actual, entered, attempts):
    """Regression: pin_check(None, None, 0) used to return 'ok' (empty PIN matched)."""
    with pytest.raises(ValueError):
        pin_check(entered, actual, attempts)


@SETTINGS
@given(attempts=st.one_of(st.integers(max_value=-1), st.none(), st.floats(),
                          st.text(), st.booleans(), st.lists(st.integers())),
       entered=valid_pin, actual=valid_pin)
def test_pin_check_rejects_bad_attempts(attempts, entered, actual):
    with pytest.raises(ValueError):
        pin_check(entered, actual, attempts)


@SETTINGS
@given(entered=valid_pin, actual=valid_pin, attempts=valid_attempts)
def test_pin_check_invariants(entered, actual, attempts):
    result = pin_check(entered, actual, attempts)
    if attempts >= 3:
        assert result == "card blocked"          # blocked card never opens, even with right PIN
    elif entered == actual:
        assert result == "ok"
    elif attempts == 2:
        assert result == "card blocked"          # third wrong try blocks the card
    else:
        assert result == "retry"


# ===========================================================================
# note_breakup
# ===========================================================================
@SETTINGS
@given(amount=mixed(valid_notes_amount))
def test_note_breakup_never_crashes(amount):
    result = check_only_value_error(note_breakup, amount)
    if result is not None:
        assert isinstance(result, tuple) and len(result) == 3
        assert all(is_real_int(n) and n >= 0 for n in result), f"bad note counts {result!r}"


@SETTINGS
@given(amount=st.one_of(
    st.integers().filter(lambda x: x < 0 or x % 100 != 0),
    st.floats(), st.text(), st.none(), st.booleans(), st.lists(st.integers())))
def test_note_breakup_rejects_bad_amount(amount):
    """Negative amounts, non-multiples of 100, floats (incl. 100.0), None, bool, str."""
    with pytest.raises(ValueError):
        note_breakup(amount)


@SETTINGS
@given(amount=valid_notes_amount)
def test_note_breakup_invariants(amount):
    n500, n200, n100 = note_breakup(amount)
    assert n500 >= 0 and n200 >= 0 and n100 >= 0
    assert 500 * n500 + 200 * n200 + 100 * n100 == amount   # totals add up exactly
    assert n200 <= 2 and n100 <= 1                           # greedy split: remainder < 500
