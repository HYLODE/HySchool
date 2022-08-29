-- Example script showing how to work with labs

-- Let's go looking for patients with possible septic shock 
-- defined by high blood lactate (measured near patient machines)

SELECT
   m.lab_result_id
  ,mo.hospital_visit_id
  ,m.result_last_modified_time
  ,m.value_as_real
  ,m.units
  ,m.abnormal_flag
  ,m.comment

FROM 
star.lab_result m
-- join onto the order table to pick up the patient and visit identifiers
INNER JOIN star.lab_order mo ON m.lab_order_id = mo.lab_order_id

WHERE
-- just blood lactate
m.lab_test_definition_id = 141462274
AND
-- in the last 3 hours
m.result_last_modified_time > NOW() - '3 HOURS'::INTERVAL
ORDER BY m.result_last_modified_time DESC