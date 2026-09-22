from august.fraud.decision import decide_transaction, expected_fraud_loss


def test_expected_loss():
    assert expected_fraud_loss(0.87, 8400) == 7308


def test_high_risk_is_blocked():
    result = decide_transaction(0.91, 46000)
    assert result["recommended_action"] == "BLOCK"
