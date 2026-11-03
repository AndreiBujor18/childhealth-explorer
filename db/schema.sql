-- Task 1.8: design reference; app/models.py must describe the same schema.
CREATE TABLE source (
    source_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    url TEXT
);
CREATE TABLE country (
    iso3 VARCHAR(3) PRIMARY KEY,
    iso2 VARCHAR(2),
    name VARCHAR(100) NOT NULL,
    region VARCHAR(100),
    income_group VARCHAR(50)
);
CREATE TABLE indicator (
    indicator_id SERIAL PRIMARY KEY,
    code VARCHAR(80) NOT NULL,
    concept_code VARCHAR(80) NOT NULL,
    name VARCHAR(255) NOT NULL,
    unit VARCHAR(100),
    age_group VARCHAR(80),
    source_id INTEGER NOT NULL REFERENCES source(source_id),
    CONSTRAINT uq_indicator_source_code UNIQUE (source_id, code)
);
CREATE TABLE observation (
    observation_id BIGSERIAL PRIMARY KEY,
    country_iso3 VARCHAR(3) NOT NULL REFERENCES country(iso3),
    indicator_id INTEGER NOT NULL REFERENCES indicator(indicator_id),
    year SMALLINT NOT NULL,
    sex VARCHAR(10) NOT NULL DEFAULT 'BTSX',
    value NUMERIC(18, 4),
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT uq_observation UNIQUE (country_iso3, indicator_id, year, sex),
    CONSTRAINT ck_observation_year CHECK (year BETWEEN 1900 AND 2100),
    CONSTRAINT ck_observation_sex CHECK (sex IN ('BTSX', 'MLE', 'FMLE')),
    CONSTRAINT ck_observation_nonnegative CHECK (value IS NULL OR value >= 0)
);
CREATE INDEX ix_observation_indicator_year ON observation (indicator_id, year);
CREATE TABLE import_log (
    import_id SERIAL PRIMARY KEY,
    source_name VARCHAR(100) NOT NULL,
    indicator_code VARCHAR(80) NOT NULL,
    url TEXT NOT NULL,
    rows_loaded INTEGER NOT NULL,
    imported_at TIMESTAMPTZ NOT NULL DEFAULT now()
);
