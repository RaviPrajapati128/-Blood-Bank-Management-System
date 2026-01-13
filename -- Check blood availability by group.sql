-- Check blood availability by group:

SELECT BloodGroup, COUNT(BloodGroup) AS AvailableUnits
FROM Blood_Inventory
WHERE QualityStatus = 'Good' 
GROUP BY BloodGroup;