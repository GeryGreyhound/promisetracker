--
-- PostgreSQL database dump
--

-- Dumped from database version 11.9 (Debian 11.9-0+deb10u1)
-- Dumped by pg_dump version 11.9 (Debian 11.9-0+deb10u1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: elections; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.elections (
    id character varying,
    dt timestamp without time zone,
    description character varying,
    next_following character varying
);


--
-- Name: invitations; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.invitations (
    email character varying,
    display_name character varying,
    politicians character varying
);


--
-- Name: kemocloud_system_status; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.kemocloud_system_status (
    dt timestamp without time zone,
    base character varying,
    machine character varying,
    ip character varying,
    notes character varying
);


--
-- Name: news_articles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.news_articles (
    article_date timestamp without time zone,
    url character varying,
    source_name character varying,
    article_title character varying,
    politician_id character varying,
    promise_id integer,
    promise_status character varying
);


--
-- Name: politician_meta; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.politician_meta (
    politician_id character varying,
    meta_parameter character varying,
    meta_value character varying
);


--
-- Name: politicians; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.politicians (
    id character varying,
    name character varying,
    location character varying,
    "position" character varying,
    last_elected character varying,
    program_name character varying,
    elected timestamp without time zone
);


--
-- Name: promise_categories; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.promise_categories (
    politician_id character varying,
    category_id integer,
    category_name character varying
);


--
-- Name: promises; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.promises (
    id integer,
    politician_id character varying,
    category_id integer,
    name character varying,
    custom_options character varying,
    sub_items text[]
);


--
-- Name: subitems; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.subitems (
    politician_id character varying,
    parent_id integer,
    sub_id character varying,
    title character varying
);


--
-- Name: submissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.submissions (
    article_date timestamp without time zone,
    submitter_ip character varying,
    url character varying,
    source_name character varying,
    article_title character varying,
    politician_id character varying,
    promise_id integer,
    submitted_at timestamp without time zone,
    submitted_by character varying,
    id integer NOT NULL,
    confirm_status character varying,
    confirmed_by integer,
    suggested_status character varying,
    not_valid_items text[]
);


--
-- Name: submissions_activity_log; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.submissions_activity_log (
    dt timestamp without time zone,
    mod_user character varying,
    submission_id integer,
    modified_field character varying,
    original_value character varying,
    modified_value character varying
);


--
-- Name: submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.submissions_id_seq OWNED BY public.submissions.id;


--
-- Name: user_permissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.user_permissions (
    user_id integer,
    politician_id character varying
);


--
-- Name: users; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying,
    password character varying,
    permissions character varying,
    display_name character varying
);


--
-- Name: v2_news_articles; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.v2_news_articles (
    id integer NOT NULL,
    date timestamp without time zone,
    url character varying,
    source_name character varying,
    title character varying,
    politician_id character varying,
    promise_id integer,
    promise_status character varying,
    og_image character varying,
    og_description character varying,
    submission_id integer
);


--
-- Name: v2_news_articles_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.v2_news_articles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: v2_news_articles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.v2_news_articles_id_seq OWNED BY public.v2_news_articles.id;


--
-- Name: v2_submissions; Type: TABLE; Schema: public; Owner: -
--

CREATE TABLE public.v2_submissions (
    id integer NOT NULL,
    article_date timestamp without time zone,
    submitter_ip character varying,
    article_url character varying,
    source_name character varying,
    article_title character varying,
    politician_id character varying,
    promise_id integer,
    submitted_at timestamp without time zone,
    submitted_by character varying,
    confirm_level character varying,
    confirm_status character varying,
    confirmed_by integer,
    suggested_status character varying
);


--
-- Name: v2_submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: -
--

CREATE SEQUENCE public.v2_submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


--
-- Name: v2_submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: -
--

ALTER SEQUENCE public.v2_submissions_id_seq OWNED BY public.v2_submissions.id;


--
-- Name: submissions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions ALTER COLUMN id SET DEFAULT nextval('public.submissions_id_seq'::regclass);


--
-- Name: v2_news_articles id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.v2_news_articles ALTER COLUMN id SET DEFAULT nextval('public.v2_news_articles_id_seq'::regclass);


--
-- Name: v2_submissions id; Type: DEFAULT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.v2_submissions ALTER COLUMN id SET DEFAULT nextval('public.v2_submissions_id_seq'::regclass);


--
-- Name: submissions submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.submissions
    ADD CONSTRAINT submissions_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: v2_news_articles v2_news_articles_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.v2_news_articles
    ADD CONSTRAINT v2_news_articles_pkey PRIMARY KEY (id);


--
-- Name: v2_submissions v2_submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: -
--

ALTER TABLE ONLY public.v2_submissions
    ADD CONSTRAINT v2_submissions_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

