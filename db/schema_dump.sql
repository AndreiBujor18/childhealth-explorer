--
-- PostgreSQL database dump
--

\restrict XI2QmJ26ud6AkzRckKMCBvxXjjt0iNzlzTYiIbpN1vqm9f2iFcUviurEEFdjD14

-- Dumped from database version 18.6
-- Dumped by pg_dump version 18.6

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: country; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.country (
    iso3 character varying(3) NOT NULL,
    iso2 character varying(2),
    name character varying(100) NOT NULL,
    region character varying(100),
    income_group character varying(50)
);


--
-- Name: import_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.import_log (
    import_id integer NOT NULL,
    source_name character varying(100) NOT NULL,
    indicator_code character varying(80) NOT NULL,
    url text NOT NULL,
    rows_loaded integer NOT NULL,
    imported_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: import_log_import_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.import_log_import_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: import_log_import_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.import_log_import_id_seq OWNED BY public.import_log.import_id;


--
-- Name: indicator; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.indicator (
    indicator_id integer NOT NULL,
    code character varying(80) NOT NULL,
    concept_code character varying(80) NOT NULL,
    name character varying(255) NOT NULL,
    unit character varying(100),
    age_group character varying(80),
    source_id integer NOT NULL
);


--
-- Name: indicator_indicator_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.indicator_indicator_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: indicator_indicator_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.indicator_indicator_id_seq OWNED BY public.indicator.indicator_id;


--
-- Name: observation; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.observation (
    observation_id bigint NOT NULL,
    country_iso3 character varying(3) NOT NULL,
    indicator_id integer NOT NULL,
    year smallint NOT NULL,
    sex character varying(10) DEFAULT 'BTSX'::character varying NOT NULL,
    value numeric(18,4),
    imported_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT ck_observation_nonnegative CHECK (((value IS NULL) OR (value >= (0)::numeric))),
    CONSTRAINT ck_observation_sex CHECK (((sex)::text = ANY ((ARRAY['BTSX'::character varying, 'MLE'::character varying, 'FMLE'::character varying])::text[]))),
    CONSTRAINT ck_observation_year CHECK (((year >= 1900) AND (year <= 2100)))
);


--
-- Name: observation_observation_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.observation_observation_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: observation_observation_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.observation_observation_id_seq OWNED BY public.observation.observation_id;


--
-- Name: source; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.source (
    source_id integer NOT NULL,
    name character varying(100) NOT NULL,
    url text
);


--
-- Name: source_source_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.source_source_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: source_source_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.source_source_id_seq OWNED BY public.source.source_id;


--
-- Name: import_log import_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.import_log ALTER COLUMN import_id SET DEFAULT nextval('public.import_log_import_id_seq'::regclass);


--
-- Name: indicator indicator_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicator ALTER COLUMN indicator_id SET DEFAULT nextval('public.indicator_indicator_id_seq'::regclass);


--
-- Name: observation observation_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation ALTER COLUMN observation_id SET DEFAULT nextval('public.observation_observation_id_seq'::regclass);


--
-- Name: source source_id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source ALTER COLUMN source_id SET DEFAULT nextval('public.source_source_id_seq'::regclass);


--
-- Name: country country_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.country
    ADD CONSTRAINT country_pkey PRIMARY KEY (iso3);


--
-- Name: import_log import_log_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.import_log
    ADD CONSTRAINT import_log_pkey PRIMARY KEY (import_id);


--
-- Name: indicator indicator_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicator
    ADD CONSTRAINT indicator_pkey PRIMARY KEY (indicator_id);


--
-- Name: observation observation_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation
    ADD CONSTRAINT observation_pkey PRIMARY KEY (observation_id);


--
-- Name: source source_name_key; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source
    ADD CONSTRAINT source_name_key UNIQUE (name);


--
-- Name: source source_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.source
    ADD CONSTRAINT source_pkey PRIMARY KEY (source_id);


--
-- Name: indicator uq_indicator_source_code; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicator
    ADD CONSTRAINT uq_indicator_source_code UNIQUE (source_id, code);


--
-- Name: observation uq_observation; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation
    ADD CONSTRAINT uq_observation UNIQUE (country_iso3, indicator_id, year, sex);


--
-- Name: ix_observation_indicator_year; Type: INDEX; Schema: public; Owner: -
--

CREATE INDEX ix_observation_indicator_year ON public.observation USING btree (indicator_id, year);


--
-- Name: indicator indicator_source_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.indicator
    ADD CONSTRAINT indicator_source_id_fkey FOREIGN KEY (source_id) REFERENCES public.source(source_id);


--
-- Name: observation observation_country_iso3_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation
    ADD CONSTRAINT observation_country_iso3_fkey FOREIGN KEY (country_iso3) REFERENCES public.country(iso3);


--
-- Name: observation observation_indicator_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.observation
    ADD CONSTRAINT observation_indicator_id_fkey FOREIGN KEY (indicator_id) REFERENCES public.indicator(indicator_id);


--
-- PostgreSQL database dump complete
--

\unrestrict XI2QmJ26ud6AkzRckKMCBvxXjjt0iNzlzTYiIbpN1vqm9f2iFcUviurEEFdjD14
