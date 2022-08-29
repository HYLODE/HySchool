-- Steve Harris
-- created Dec 2020
-- convert targets to long

DROP VIEW IF EXISTS informus.alltargets_long;

CREATE OR REPLACE VIEW informus.alltargets_long AS
WITH long AS (
SELECT
   a.mrn
  ,a.csn
  ,a.side
  ,a.log_dt ts
  ,s.target_name
  ,s.target_value
  ,CASE WHEN s.target_value = true THEN 1 ELSE 0 END AS target01
  ,a.bay
  ,a.bed
  /* ,mod(right(a.bed, 2)::int,10) as loc_y */
  /* ,CASE */
  /*   WHEN a.bay LIKE 'BY%' THEN right(a.bay, 1)::int */ 
  /*   WHEN a.bay LIKE 'SR%' THEN 0 */
  /*   ELSE NULL END AS loc_x */
FROM informus.all_targets a,
    LATERAL (VALUES
     ('spo2', a.spo2)
    ,('map', a.map)
    ,('pa02', a.pao2)
    ,('ph', a.ph)
    ,('hb', a.hb)
    ,('fb', a.fb)
    ,('rass', a.rass)
    )
    s(target_name, target_value)
)
SELECT
    long.*
    ,g.loc_x
    ,g.loc_y
    ,g.bed bed_number
FROM long
LEFT JOIN informus.t03_bed_grid as g
    ON long.bed = g.key
    ;
SELECT * FROM informus.alltargets_long LIMIT 1;
