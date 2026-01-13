-- all contaminated blood units

SELECT UnitID, DonorID, BloodGroup, ExpiryDate
FROM Blood_Inventory
WHERE QualityStatus = 'Contaminated';

-- unsafe donors

SELECT DonorID, Result
FROM Tests
WHERE Result = 'Unsafe';