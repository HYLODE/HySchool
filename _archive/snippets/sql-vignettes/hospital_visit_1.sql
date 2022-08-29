-- Example script 1 of 3

-- 1. Simply pull hospital visits (THIS ONE)
-- 2. Add in hospital numbers (MRN) and handle patient merges
-- 3. Add in patient demographics

-- Starting out with hospital visits


SELECT
   vo.hospital_visit_id
  ,vo.encounter
  -- admission to hospital
  ,vo.admission_time
  ,vo.arrival_method
  ,vo.presentation_time
  -- discharge from hospital
  -- NB: Outpatients have admission events but not discharge events
  ,vo.discharge_time
  ,vo.discharge_disposition

-- start from hospital visits
FROM star.hospital_visit vo
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