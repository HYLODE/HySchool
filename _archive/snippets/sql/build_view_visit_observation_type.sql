-- 2021-01-21
-- depends on copying the table from caboodle to icu audit first
CREATE VIEW icu_audit.emapr_visit_observation_type
AS
SELECT 
	 vot.visit_observation_type
	,vot.id_in_application
	,vot.source_application
	,fs.name
	,fs.displayname
	,fs.abbreviation
	,fs.valuetype
	,fs.rowtype
	,fs.unit
	,fs.description
	,fs.iscalculated
	,fs._lastupdatedinstant
FROM star_a.visit_observation_type vot
	LEFT JOIN icu_audit.emapr_caboodle_flowsheetrowdim fs
		ON vot.id_in_application = fs.flowsheetrowepicid
;
