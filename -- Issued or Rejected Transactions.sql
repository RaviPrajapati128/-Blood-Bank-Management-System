-- Issued or Rejected Transactions

SELECT Status, COUNT(*) AS Count
FROM Transactions
GROUP BY Status;