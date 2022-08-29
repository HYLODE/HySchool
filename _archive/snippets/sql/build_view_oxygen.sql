-- Steve Harris
-- Created 2021-01-26
-- produce a realtime view of oxygen demand across the tower
-- returns a week's worth of data (much more and slows down too much)

-- TODO
-- todo: finesse the calculation to include respiratory rate and machine type

SET search_path to star_a, public;
-- this moves all operations into memory
SET work_mem='256MB';

create or replace function flow.locf_s(a float, b float)
returns float
language sql
as '
  SELECT COALESCE(b, a)
';

drop aggregate if exists flow.locf(float);
create aggregate flow.locf(float) (
  sfunc = flow.locf_s,
  stype = float
);

DROP VIEW IF EXISTS flow.oxygen;
CREATE VIEW flow.oxygen AS
WITH wide AS (SELECT 
* 
FROM 
	crosstab(
	$$SELECT 
		  hospital_visit_id
		, observation_datetime
		, CASE 
			WHEN visit_observation_type_id = 2281790312 THEN 'o2_lmin'
			WHEN visit_observation_type_id = 2281789816 THEN 'o2_fi'
		 	WHEN visit_observation_type_id = 2281790343 THEN 'o2_device'
			END AS o2_obs
		, CASE 
			WHEN visit_observation_type_id = 2281790312 THEN value_as_real::TEXT
			WHEN visit_observation_type_id = 2281789816 THEN value_as_real::TEXT
			WHEN visit_observation_type_id = 2281790343 THEN value_as_text
			END AS o2_val
		FROM star_a.visit_observation
		WHERE visit_observation_type_id IN (
			  2281790312
			, 2281789816
			, 2281790343
			) -- flow rate / fio2 / device
			AND
			observation_datetime > NOW() - '7 DAYS'::INTERVAL			
		ORDER BY 2,1
	$$
	, $$VALUES (
			'o2_lmin')
		, ('o2_fi')
		, ('o2_device')
		$$
	)
	AS ct(
		  "hospital_visit_id" BIGINT 
		, "observation_datetime" TIMESTAMP
		, "o2_lmin" REAL
		, "o2_fi" REAL
		, "o2_device" TEXT
	)
ORDER BY hospital_visit_id, observation_datetime DESC
),
o2i AS (
	SELECT 
	 	  wide.hospital_visit_id
	 	, DATE_TRUNC('HOUR', wide.observation_datetime) observation_datetime
	 	, wide.o2_lmin
	 	, wide.o2_fi
	 	, wide.o2_device
	 	, CASE
	 	 		WHEN o2_lmin IS NOT NULL THEN o2_lmin 
				WHEN o2_device = 'High-flow nasal cannula (HFNC)' THEN 60
				WHEN o2_device = 'CPAP/Bi-PAP mask' THEN 15
				WHEN o2_device = 'Endotracheal tube' THEN 20 * 0.6 -- fudge factor based on comparison of VIE data and final calc
				WHEN o2_device = 'Tracheostomy' THEN 20 * 0.6 -- fudge factor based on comparison of VIE data and final calc
				WHEN o2_device = 'Non-rebreather mask' THEN 15
				WHEN o2_device = 'Nasal cannula' THEN 2
				WHEN o2_fi > 60 THEN 11
				WHEN o2_fi > 40 THEN 8
				WHEN o2_fi > 21 THEN 5
			ELSE 0
			END AS o2_demand
		, vd.location_string 
	FROM wide
	INNER JOIN LATERAL (
			SELECT 
				  vd.location_id
				, vd.discharge_time
				, loc.location_string
			FROM
				star_a.location_visit vd
			INNER JOIN 
			 	(SELECT 
			 		  location_id
			 		, location_string
				 FROM star_a.location) loc			  
				 ON vd.location_id = loc.location_id
			WHERE 
			 	wide.hospital_visit_id = vd.hospital_visit_id
			 	AND wide.observation_datetime >= vd.admission_time
			 	ORDER BY vd.admission_time DESC
			 	LIMIT 1
			)  vd ON TRUE
	-- for debugging; work with a single patient
	--WHERE hospital_visit_id = 2332134153
	WHERE SUBSTRING(SPLIT_PART(location_string, '^', 1), '^(\D+)\d*') IN ('T', 'P', 'HS')
), 
o2 AS (
    SELECT
          hospital_visit_id
        , observation_datetime
        , location_string
        , AVG(o2_demand) o2_demand
    FROM o2i
    GROUP BY hospital_visit_id, location_string, observation_datetime
),
grid AS (
	SELECT 
 		DATE_TRUNC('hour', obs_dt) obs_dt
	FROM GENERATE_SERIES(
		  NOW() - '7 DAYS'::INTERVAL
		, NOW()
		, '1 HOUR'::INTERVAL) obs_dt
),
loc AS (
	SELECT DISTINCT location_string FROM o2
),
xgrid AS (
	SELECT 
	 location_string
	, obs_dt 
	FROM grid CROSS JOIN loc
),
o2_sparse AS (
SELECT 
	  xgrid.location_string
	, xgrid.obs_dt
	, o2.hospital_visit_id
	, o2.o2_demand
FROM xgrid
LEFT JOIN o2 ON 
	xgrid.location_string = o2.location_string
	AND
	xgrid.obs_dt = o2.observation_datetime
),
locf AS (
SELECT
	  os.location_string
	, os.obs_dt
	, os.o2_demand
	, flow.locf(o2_demand) over (PARTITION BY location_string ORDER BY obs_dt) AS o2_locf 
	
	, SPLIT_PART(location_string, '^', 1) ward
	, SUBSTRING(SPLIT_PART(location_string, '^', 1), '^\D+(\d+)\D*')::INTEGER floor_index
	, SUBSTRING(location_string, '.*?(\d+)\D?$')::integer bed_index
FROM o2_sparse os
)
SELECT
*
FROM locf
WHERE o2_locf IS NOT NULL
;
RESET work_mem;
;
SELECT * FROM flow.oxygen LIMIT 3;
