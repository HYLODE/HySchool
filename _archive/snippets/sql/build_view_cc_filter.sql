-- Created at 2021-01-09
-- V simple view that produces the foreign keys need to define patients who have ever been in critical care

-- LOG
-- 2021-01-27 switched to star_a

SET search_path to star_a, public;
-- this moves all operations into memory

DROP VIEW IF EXISTS flow.cc_filter;
CREATE VIEW flow.cc_filter AS
SELECT 
    DISTINCT
	 p.core_demographic_id
    ,mrn.mrn_id
    ,mrn_to_live.mrn_id AS mrn_id_alt
	,mrn.mrn
	,mrn.nhs_number
	,vd.hospital_visit_id 
	,vo.encounter
FROM star_a.location_visit vd 
LEFT JOIN flow.location loc ON vd.location_id = loc.location_id 
LEFT JOIN star_a.hospital_visit vo ON vd.hospital_visit_id = vo.hospital_visit_id
LEFT JOIN star_a.core_demographic p ON vo.mrn_id = p.mrn_id
-- get current MRN
LEFT JOIN star_a.mrn_to_live ON p.mrn_id = mrn_to_live.mrn_id
LEFT JOIN star_a.mrn ON mrn_to_live.live_mrn_id = mrn.mrn_id
-- where ever seen in a critical care bed
WHERE loc.critical_care = true ;
EXPLAIN ANALYZE SELECT * FROM flow.cc_filter;


