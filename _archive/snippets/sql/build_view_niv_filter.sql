-- Steve Harris
-- Create a simple view of patients who have received NIV
-- returns a table of identifiers for other views to join against

-- LOG
-- 2021-01-22
-- V simple view that produces the foreign keys need to define patients who have received NIV

-- 2021-01-22
-- there is another version of this in the covid repo as an R script; that writes to icu_audit
-- saved here too just for good measure
-- would be good to wrap all this up in a single place

SET search_path to star_a, public;

DROP VIEW IF EXISTS flow.niv_filter;
CREATE VIEW flow.niv_filter AS

WITH obs AS (
SELECT 
	 DISTINCT ON (obs.hospital_visit_id) hospital_visit_id
--	,obs.value_as_text
--	,ot.name
FROM star_a.visit_observation obs
	LEFT JOIN icu_audit.emapr_visit_observation_type ot
	ON obs.visit_observation_type_id = ot.visit_observation_type
WHERE
 ot.name IN (
	 'R UCLH NIV MODE SETTING' 
	,'R UCLH NIV DEVICE'
	,'R UCLH EPAP/PEEP FOR CPAP' 
 )
 OR
 (ot.name = 'R OXYGEN DELIVERY METHOD' AND obs.value_as_text = 'CPAP/Bi-PAP mask')
)
SELECT 

    DISTINCT
	 p.core_demographic_id
    ,mrn.mrn_id
    ,mrn_to_live.mrn_id AS mrn_id_alt
	,mrn.mrn
	,mrn.nhs_number
	-- now bring in the hospital_visit_id captured from the visit_observation table above
	,obs.hospital_visit_id 
	,vo.encounter

FROM obs 
LEFT JOIN star_a.hospital_visit vo ON obs.hospital_visit_id = vo.hospital_visit_id
LEFT JOIN star_a.core_demographic p ON vo.mrn_id = p.mrn_id
-- get current MRN
LEFT JOIN star_a.mrn_to_live ON p.mrn_id = mrn_to_live.mrn_id
LEFT JOIN star_a.mrn ON mrn_to_live.live_mrn_id = mrn.mrn_id

;

EXPLAIN ANALYZE SELECT * FROM flow.niv_filter;
