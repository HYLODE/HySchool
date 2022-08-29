-- Example script 
-- to pick out patients currently in A&E resus or majors

SELECT
   vd.location_visit_id
  ,vd.hospital_visit_id
  ,vd.location_id
  -- ugly HL7 location string 
  ,lo.location_string
  -- time admitted to that bed/theatre/scan etc.
  ,vd.admission_time
  -- time discharged from that bed
  ,vd.discharge_time

FROM star.location_visit vd
-- location label
INNER JOIN star.location lo ON vd.location_id = lo.location_id
WHERE 
-- last few hours
vd.admission_time > NOW() - '12 HOURS'::INTERVAL	
-- just CURRENT patients
AND
vd.discharge_time IS NULL
-- filter out just ED and Resus or Majors
AND
-- unpacking the HL7 string formatted as 
-- Department^Ward^Bed string
SPLIT_PART(lo.location_string,'^',1) = 'ED'
AND
SPLIT_PART(lo.location_string,'^',2) ~ '(RESUS|MAJORS)'
-- sort
ORDER BY lo.location_string
;
