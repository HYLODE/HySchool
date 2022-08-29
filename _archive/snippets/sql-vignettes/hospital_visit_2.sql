-- Example script 2 of 3

-- 1. Simply pull hospital visits 
-- 2. Add in hospital numbers (MRN) and handle patient merges (THIS ONE)
-- 3. Add in patient demographics

-- Starting out with hospital visits
-- but now picking up the current MRN 
-- which may or may not be the one attached to the record 
-- (i.e. handles merges etc)

SELECT
   vo.hospital_visit_id
  ,vo.encounter
  ,vo.admission_time
  ,vo.arrival_method
  ,vo.presentation_time
  ,vo.discharge_time
  ,vo.discharge_disposition
  -- original MRN
  ,original_mrn.mrn AS original_mrn
  -- live MRN
  ,live_mrn.mrn AS live_mrn

-- start from hospital visits
FROM star.hospital_visit vo
-- get original mrn
INNER JOIN star.mrn original_mrn ON vo.mrn_id = original_mrn.mrn_id
-- get mrn to live mapping 
INNER JOIN star.mrn_to_live mtl ON vo.mrn_id = mtl.mrn_id 
-- get live mrn 
INNER JOIN star.mrn live_mrn ON mtl.live_mrn_id = live_mrn.mrn_id 

WHERE 
      -- hospital visits within the last 12 hours
      vo.presentation_time > NOW() - '12 HOURS'::INTERVAL	
      -- emergencies
  AND vo.patient_class = 'EMERGENCY'
      -- attending via ambulance
  AND vo.arrival_method = 'Ambulance'
      -- sort descending
ORDER BY vo.presentation_time DESC
; 