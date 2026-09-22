SELECT
    transaction_id,
    fraud_probability,
    transaction_amount,
    fraud_probability * transaction_amount AS expected_fraud_loss,
    CASE
        WHEN fraud_probability >= 0.80 THEN 'BLOCK'
        WHEN fraud_probability >= 0.25
          AND fraud_probability * transaction_amount > 40 THEN 'REVIEW'
        ELSE 'APPROVE'
    END AS recommended_action
FROM scored_transactions
ORDER BY expected_fraud_loss DESC;
