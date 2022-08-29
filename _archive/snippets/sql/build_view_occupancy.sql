-- Steve Harris
-- Created 23 Nov 2020

-- LOG

-- 23 Nov
-- I wish to be able to report occupancy in realtime; suggesting that by
-- running cumulative sum within a ward and treating an admission time as a +1
-- and a discharge time as a -1 should do it
-- ---------------------------------
-- now try and put this all together

-- 2021-05-21
-- corrected from star_a to star
-- changed target schema to icu_audit






SET search_path to star, public;

DROP VIEW IF EXISTS icu_audit.occupancy;

CREATE OR REPLACE VIEW icu_audit.occupancy AS
WITH
loc AS (
SELECT
     location_id
    ,location_string
    ,SPLIT_PART(location_string,'^',1) ward
FROM star_a.location
WHERE SPLIT_PART(location_string,'^',3) != 'null'
),
wide AS (
SELECT 
     vd.hospital_visit_id
    ,vd.location_visit_id
    ,vd.location_id
    ,vd.admission_time bed_in
    ,vd.discharge_time bed_dc
    ,v.admission_time hosp_in
    ,v.discharge_time hosp_dc
    ,loc.location_string
    ,loc.ward
    ,LAG(loc.ward,1) OVER (
        PARTITION BY vd.hospital_visit_id
        ORDER BY vd.admission_time ASC
        ) ward_lag1
FROM star_a.location_visit vd
JOIN loc ON vd.location_id = loc.location_id
JOIN star_a.hospital_visit v ON vd.hospital_visit_id = v.hospital_visit_id
),
long AS (
SELECT 
     wide.hospital_visit_id
    ,wide.location_visit_id
    ,wide.location_string
    ,wide.ward_lag1
    ,wide.ward
    ,event
    ,CASE
         WHEN event = 'bed_in' THEN 1                       --admission
         WHEN event = 'bed_dc' AND ts IS NULL THEN 0       --not yet discharged
         WHEN event = 'bed_dc' AND ts IS NOT NULL THEN -1  --discharge
         END census
    ,ts
FROM wide
JOIN LATERAL (
    VALUES('bed_in',wide.bed_in),
        ('bed_dc',wide.bed_dc))
    s(event, ts)
    ON TRUE
),
occ_now AS (
SELECT 
     wide.ward
    -- this is a hack to get rid of ghosts by only counting a bed once
    ,COUNT(DISTINCT wide.location_string) n
FROM wide
WHERE 
    wide.bed_in IS NOT NULL AND wide.bed_dc IS NULL
AND wide.hosp_in IS NOT NULL AND wide.hosp_dc IS NULL
GROUP BY wide.ward
)
SELECT 
    long.*
    -- census going forwards
    , sum(census) OVER (PARTITION BY long.ward ORDER BY ts DESC) AS occupancy_raw
    -- this line now works backwards from now to deliver the change in census to this point
    , occ_now.n - sum(census) OVER (PARTITION BY long.ward ORDER BY ts DESC) AS occupancy
FROM long
JOIN occ_now ON long.ward = occ_now.ward
--LIMIT 5
;

