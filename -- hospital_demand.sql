-- Hospital Demand

SELECT HospitalID, COUNT(*) AS Requests
FROM Recipients
GROUP BY HospitalID
ORDER BY Requests DESC;