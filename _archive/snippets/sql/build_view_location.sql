-- Steve Harris
-- Created 25 Nov 2020
-- Build materialized view for locations
-- this will not be useful if the list of locations ever updates without remembering to update the materialised view

-- LOG
-- 2021-01-27 switched to star_a

SET search_path to star_a, public;

DROP VIEW IF EXISTS flow.location;
CREATE VIEW flow.location AS

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
            WHEN SUBSTR(location_string,1,4) IN ('SINQ', 'MINQ')  THEN 'NHNN'
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
ORDER BY location_string ASC
;
EXPLAIN ANALYZE SELECT * FROM flow.location;

