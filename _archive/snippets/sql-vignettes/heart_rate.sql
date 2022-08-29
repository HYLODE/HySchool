-- Example script showing how to work with a time series of heart rate


SELECT
  -- observation details
   ob.visit_observation_id
  ,ob.hospital_visit_id
  ,ob.observation_datetime

  --,ob.visit_observation_type_id
  --,ot.id_in_application

  -- label nicely
  ,CASE 
--     WHEN ot.id_in_application = '10' THEN 'SpO2'
--     WHEN ot.id_in_application = '5' THEN 'BP'
--     WHEN ot.id_in_application = '3040109304' THEN 'Oxygen'
--     WHEN ot.id_in_application = '6' THEN 'Temp'
     WHEN ot.id_in_application = '8' THEN 'Pulse'
--    WHEN ot.id_in_application = '9' THEN 'Resp'
--     WHEN ot.id_in_application = '6466' THEN 'AVPU'

  END AS vital

  ,ob.value_as_real
  ,ob.value_as_text
  ,ob.unit 
  
FROM
  star.visit_observation ob
-- observation look-up
LEFT JOIN
  star.visit_observation_type ot
  on ob.visit_observation_type_id = ot.visit_observation_type_id

WHERE
ob.observation_datetime > NOW() - '24 HOURS'::INTERVAL	
AND
ot.id_in_application in 

  (
--   '10'            --'SpO2'                  -- 602063230
--   ,'5'            --'BP'                    -- 602063234
--   ,'3040109304'   --'Room Air or Oxygen'    -- 602063268
--   ,'6'            --'Temp'                  -- 602063248
  '8'            --'Pulse'                 -- 602063237
--   ,'9'            --'Resp'                  -- 602063257
--   ,'6466'         -- Level of consciousness
)
ORDER BY ob.observation_datetime DESC, ob.hospital_visit_id
;