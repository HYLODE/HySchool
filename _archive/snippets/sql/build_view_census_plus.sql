-- Steve Harris
-- Created 24 Nov
-- Query for inspecting ward admissions and discharges

-- LOG
-- 2021-01-27 switched to star_a

-- TODO
-- todo: optimise using explain analyse
-- todo: debug issues with discharges
-- todo: remove the loc_all clause and switch to using location_attribute

SET search_path to star_a, public;
-- this moves all operations into memory
SET work_mem='256MB';

DROP VIEW IF EXISTS flow.census_plus;
CREATE OR REPLACE VIEW flow.census_plus AS

WITH
loc_all AS (
    /* SELECT * FROM flow.location_mv WHERE census = true */
    SELECT
         location_id
        ,location_string
        -- grab ward
        ,CASE
            WHEN SPLIT_PART(location_string,'^',1) != 'null' then SPLIT_PART(location_string,'^',1)
            WHEN SPLIT_PART(location_string,'^',1) = 'null' 
                 AND SPLIT_PART(location_string,'^',2) ~ '^(T07CV.*)' then 'T07CV'
            END AS ward
        ,SPLIT_PART(location_string,'^',3) bed
        ,SPLIT_PART(location_string,'^',1) ward_raw
        -- define if census move or otherwise
        ,CASE 
            -- BEWARE / CHECK that this doesn't drop deaths or similar
            -- DROP OPD etc where there is no bed
            WHEN SPLIT_PART(location_string,'^',3) ~ '(BY|CB|CH|SR|HR|BD|NU|PD).*$|.*(MAJ|RAT|SDEC|RESUS|TRIAGE).*' then true 
            WHEN SPLIT_PART(location_string,'^',3) IN ('null', 'POOL', 'WAIT', 'NONE', 'DISCHARGE', 'VIRTUAL') then false 
            END AS census
        -- define building / physical site
        ,CASE 
            -- THP3 includes podium theatres
            WHEN SPLIT_PART(location_string,'^',1) ~ '^(T0|T1|THP3|ED(?!H))'  THEN 'tower'
            WHEN SUBSTR(location_string,1,2) IN ('WM', 'WS')  THEN 'WMS'
            WHEN location_string LIKE '%MCC%' then 'MCC'
            WHEN location_string LIKE '%NICU%' then 'NICU'
            WHEN location_string LIKE '%NHNN%' then 'NHNN'
            WHEN location_string LIKE 'EDH%' then 'EDH'
            WHEN location_string LIKE '%OUTSC%' then 'EXTERNAL'
            END AS building
        -- define critical care
        ,CASE 
            WHEN SPLIT_PART(location_string,'^',1) ~ '^(T03|WSCC|SINQ|MINQ|P03CV|T07CV)' THEN true
            WHEN SPLIT_PART(location_string,'^',2) ~ '^(T07CV.*)' THEN true
            END AS critical_care
        -- define ED areas
        ,CASE 
            WHEN SPLIT_PART(location_string,'^',1) = 'ED' AND location_string LIKE '%RESUS%' THEN 'RESUS'
            WHEN SPLIT_PART(location_string,'^',1) = 'ED' AND location_string LIKE '%MAJ%' THEN 'MAJORS'
            WHEN SPLIT_PART(location_string,'^',1) = 'ED' AND location_string LIKE '%UTC%' THEN 'UTC'
            WHEN SPLIT_PART(location_string,'^',1) = 'ED' AND location_string LIKE '%RAT%' THEN 'RAT'
            WHEN SPLIT_PART(location_string,'^',1) = 'ED' AND location_string LIKE '%SDEC%' THEN 'SDEC'
            WHEN SPLIT_PART(location_string,'^',1) = 'ED' AND location_string LIKE '%SAA%' THEN 'SAA' -- specialty assessment area
            WHEN SPLIT_PART(location_string,'^',1) = 'ED' AND location_string LIKE '%TRIAGE%' THEN 'TRIAGE'
            WHEN SPLIT_PART(location_string,'^',1) = 'ED' AND location_string LIKE '%PAEDS%' THEN 'PAEDS'
            END AS ed_zone
        -- define bed type
        ,CASE
            WHEN SUBSTR(SPLIT_PART(location_string,'^',3),1,2) IN ('BY', 'CB') then 'bay' 
            WHEN SUBSTR(SPLIT_PART(location_string,'^',3),1,2) IN ('SR') then 'sideroom' 
            WHEN SUBSTR(SPLIT_PART(location_string,'^',3),1,2) IN ('CH') then 'chair' 
            WHEN location_string ~ '.*(SURGERY|THR|PROC|ENDO|TREAT|ANGI).*|.+(?<!CHA)IN?R\^.*' then 'procedure' 
            WHEN location_string ~ '.*XR.*|.*MRI.*|.+CT\^.*|.*SCANNER.*' then 'imaging' 
            END AS bed_type
    FROM star_a.location
),
loc AS (
    SELECT * FROM loc_all WHERE census = true
),
mvp AS (
    SELECT v.hospital_visit_id
        ,m.mrn
        ,p.lastname
        ,p.firstname
        ,p.datetime_of_death
        ,v.encounter
        ,v.patient_class
        ,v.admission_time hosp_in
        ,v.discharge_time hosp_dc
    FROM star_a.hospital_visit v 
        JOIN star_a.core_demographic p ON v.mrn_id = p.mrn_id
        JOIN star_a.mrn m ON p.mrn_id = m.mrn_id
    WHERE
        -- not Winpath since we're only looking at movement
        v.patient_class = 'INPATIENT'
        AND v.source_system = 'EPIC'
        AND v.admission_time IS NOT NULL
        AND (v.discharge_time IS NULL OR v.discharge_time > now() - INTERVAL '3 MONTHS')
),
WIDE AS (
    SELECT
         vd.location_visit_id
        ,vd.admission_time bed_in
        ,vd.discharge_time bed_dc
        ,mvp.*
        ,loc.building
        ,loc.ward
        ,loc.bed
        ,loc.bed_type
        ,loc.ed_zone
        ,LAG(loc.ward,1) OVER ( PARTITION BY vd.hospital_visit_id ORDER BY vd.admission_time ASC) ward_lag1
        ,LEAD(loc.ward,1) OVER ( PARTITION BY vd.hospital_visit_id ORDER BY vd.admission_time ASC) ward_lead1
        -- moves in/out of transient locations
        ,CASE WHEN LAG(loc.bed_type,1)
                OVER ( PARTITION BY vd.hospital_visit_id ORDER BY vd.admission_time ASC)
                IN ('procedure', 'imaging') then true END AS transient_lag1
        ,CASE WHEN LEAD(loc.bed_type,1)
                OVER ( PARTITION BY vd.hospital_visit_id ORDER BY vd.admission_time ASC)
                IN ('procedure', 'imaging') then true END AS transient_lead1
        -- roundtrips in and out of exactly the same location 
        ,CASE WHEN LAG(vd.location_id,2)
                OVER ( PARTITION BY vd.hospital_visit_id ORDER BY vd.admission_time ASC)
                = vd.location_id THEN true END AS roundtrip_lag2
        ,CASE WHEN LEAD(vd.location_id,2)
                OVER ( PARTITION BY vd.hospital_visit_id ORDER BY vd.admission_time ASC)
                = vd.location_id THEN true END AS roundtrip_lead2
    FROM star_a.location_visit vd
        JOIN mvp ON vd.hospital_visit_id = mvp.hospital_visit_id
        JOIN loc ON vd.location_id = loc.location_id
        
),
LONG AS (
SELECT 
     mrn
    ,encounter
    /* ,wide.patient_class */
    ,lastname
    ,firstname
    ,datetime_of_death 
    ,wide.hosp_in
    ,wide.hosp_dc
    ,ts
    ,event
    ,building
    ,location_visit_id 
    ,wide.ward
    ,wide.bed
    ,wide.bed_type
    ,wide.ed_zone
    ,wide.ward_lag1
    ,wide.ward_lead1
    -- identify if this is a census move (looks for round trips to a procedure or imaging area)
    ,CASE WHEN (transient_lag1 AND wide.roundtrip_lag2) THEN true ELSE false END AS noncensus_in
    ,CASE WHEN (transient_lead1 AND wide.roundtrip_lead2) THEN true ELSE false END AS noncensus_out
    ,CASE
        WHEN (hosp_dc IS NULL AND bed_dc IS NULL AND datetime_of_death IS NULL AND bed != 'WAIT') THEN true END census_now
    -- identify in which location a death occurred
    ,CASE WHEN 
        (ROW_NUMBER() OVER ( PARTITION BY mrn ORDER BY (datetime_of_death - bed_in) ASC) = 1)
            AND
        ( datetime_of_death > hosp_in AND (datetime_of_death <= hosp_dc OR hosp_dc IS NULL) )
    THEN true END AS bed_death
    -- now convert to long
    ,CASE
         WHEN event = 'bed_in' THEN 1                       --admission
         WHEN event = 'bed_dc' AND ts IS NULL THEN 0       --not yet discharged
         WHEN event = 'bed_dc' AND ts IS NOT NULL THEN -1  --discharge
         END census
FROM WIDE
JOIN LATERAL (
    VALUES('bed_in',wide.bed_in),
        ('bed_dc',wide.bed_dc))
    s(event, ts)
    ON TRUE
),
OCC_NOW AS (
SELECT 
     ward
    -- this is a hack to get rid of ghosts by only counting a bed once
    ,COUNT(DISTINCT bed) occupancy_now
FROM WIDE
WHERE 
    wide.bed_in IS NOT NULL AND wide.bed_dc IS NULL
AND wide.hosp_in IS NOT NULL AND wide.hosp_dc IS NULL
GROUP BY wide.ward
)
    SELECT 
        long.*
        ,occ_now.occupancy_now
        -- this line now works backwards from now to deliver the change in census to this point
        ,occ_now.occupancy_now - sum(census) OVER (PARTITION BY long.ward ORDER BY ts DESC) AS occupancy
        -- ward census counter
        ,CASE
            WHEN event = 'bed_in' AND (long.ward_lag1 != long.ward OR long.ward_lag1 IS NULL) AND noncensus_in = false THEN 1
            WHEN event = 'bed_dc' AND (long.ward_lead1 != long.ward OR long.ward_lead1 IS NULL) AND noncensus_out = false AND ts IS NOT NULL THEN -1
            END ward_census
        ,CASE WHEN
            (EXTRACT(HOUR FROM ts) >= 22 OR EXTRACT(HOUR FROM ts) < 7)
            THEN true ELSE FALSE END AS out_of_hours
    FROM LONG
    JOIN OCC_NOW ON long.ward = OCC_NOW.ward
;
/* SELECT COUNT(*) FROM RES */
/* SELECT * FROM RES LIMIT 12 */
RESET work_mem;
SELECT COUNT(*) FROM flow.census_plus;
/* SELECT * FROM flow.census_plus LIMIT 1; */

