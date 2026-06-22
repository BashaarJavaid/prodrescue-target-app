"""Tests for the payment processor.

`test_charge_none_raises` fails on the buggy code (raises AttributeError instead
of PaymentError) and passes once ProdRescue patches in the None-guard.
"""
import pytest

from payments.processor import Order, PaymentError, build_request, charge


def test_charge_valid():
    assert charge(Order(total=10.0)) == 1000


def test_charge_rounds_down():
    assert charge(Order(total=9.999)) == 999


def test_charge_none_raises():
    with pytest.raises(PaymentError):
        charge(None)


def test_build_request_missing_currency_defaults():
    # A payload without 'currency' must not raise; it should default gracefully.
    req = build_request({"amount": 5})
    assert req.get("currency")
