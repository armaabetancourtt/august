import pytest

from august.econometrics.real_values import inflation_adjusted_value, real_return


def test_inflation_adjusted_value():
    assert inflation_adjusted_value(120, 100, 120) == pytest.approx(100)


def test_real_return_uses_fisher_relation():
    assert real_return(0.10, 0.05) == pytest.approx((1.10 / 1.05) - 1)
