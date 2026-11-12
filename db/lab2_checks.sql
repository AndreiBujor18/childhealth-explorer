-- Lab 2: overview and the seven quality checks, adapted to child mortality.
-- Run each SELECT in pgAdmin, connected to global_health.

-- name: overview
SELECT s.name AS source, i.code, i.name, COUNT(*) AS rows,
       MIN(o.year) AS first_year, MAX(o.year) AS last_year,
       COUNT(*) FILTER (WHERE o.is_outlier) AS outliers
FROM observation o JOIN indicator i USING (indicator_id) JOIN source s USING (source_id)
GROUP BY s.name, i.code, i.name ORDER BY s.name, i.code;

-- name: romania_trends
SELECT o.year,
       MAX(o.value) FILTER (WHERE s.name='worldbank' AND i.code='SH.DYN.MORT') AS under5_mortality,
       MAX(o.value) FILTER (WHERE s.name='unicef' AND i.code='IM_DTP3') AS dtp3_coverage,
       MAX(o.value) FILTER (WHERE s.name='worldbank' AND i.code='SH.XPD.CHEX.GD.ZS') AS health_spending_pct_gdp
FROM observation o JOIN indicator i USING (indicator_id) JOIN source s USING (source_id)
WHERE o.country_iso3='ROU' AND o.sex='BTSX'
GROUP BY o.year ORDER BY o.year;

-- name: import_history
SELECT * FROM import_log ORDER BY import_id DESC;

-- name: check1
SELECT COUNT(*) AS countries, COUNT(DISTINCT region) AS regions FROM country;

-- name: check2
SELECT country_iso3, indicator_id, year, sex, COUNT(*) AS copies
FROM observation GROUP BY country_iso3, indicator_id, year, sex HAVING COUNT(*)>1;

-- name: check3
SELECT s.name AS source, i.code, i.unit, MIN(o.value) AS minimum,
       MAX(o.value) AS maximum, ROUND(AVG(o.value),2) AS average
FROM observation o JOIN indicator i USING (indicator_id) JOIN source s USING (source_id)
GROUP BY s.name, i.code, i.unit ORDER BY s.name, i.code;

-- name: check4
SELECT sex, COUNT(*) AS rows FROM observation GROUP BY sex ORDER BY sex;

-- name: check5
SELECT COUNT(*) FILTER (WHERE value IS NULL) AS null_values,
       COUNT(*) FILTER (WHERE year NOT BETWEEN 2000 AND 2023) AS out_of_window
FROM observation;

-- name: check6
WITH latest AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY source_name,indicator_code ORDER BY imported_at DESC,import_id DESC
    ) AS rank FROM import_log
)
SELECT l.source_name AS source,l.indicator_code,l.rows_loaded,
       (SELECT COUNT(*) FROM observation o JOIN indicator i USING(indicator_id)
        JOIN source s USING(source_id)
        WHERE s.name=l.source_name AND i.code=l.indicator_code) AS rows_stored
FROM latest l WHERE rank=1 ORDER BY l.source_name,l.indicator_code;

-- name: check7
SELECT c.iso3,c.name FROM country c
WHERE NOT EXISTS (
    SELECT 1 FROM observation o JOIN indicator i USING(indicator_id) JOIN source s USING(source_id)
    WHERE o.country_iso3=c.iso3 AND s.name='worldbank' AND i.code='SH.DYN.MORT'
)
ORDER BY c.name;
