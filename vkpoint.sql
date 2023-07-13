--
-- PostgreSQL database dump
--

-- Dumped from database version 15.3
-- Dumped by pg_dump version 15.3

-- Started on 2023-07-13 21:42:04

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

SET default_table_access_method = heap;

--
-- TOC entry 219 (class 1259 OID 16439)
-- Name: checked_list; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.checked_list (
    id integer NOT NULL,
    vk_id integer,
    id_user integer
);


ALTER TABLE public.checked_list OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 16438)
-- Name: checked_list_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.checked_list_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.checked_list_id_seq OWNER TO postgres;

--
-- TOC entry 3347 (class 0 OID 0)
-- Dependencies: 218
-- Name: checked_list_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.checked_list_id_seq OWNED BY public.checked_list.id;


--
-- TOC entry 217 (class 1259 OID 16411)
-- Name: dating_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.dating_user (
    id integer NOT NULL,
    vk_id integer,
    id_user integer
);


ALTER TABLE public.dating_user OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 16410)
-- Name: dating_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.dating_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.dating_user_id_seq OWNER TO postgres;

--
-- TOC entry 3348 (class 0 OID 0)
-- Dependencies: 216
-- Name: dating_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.dating_user_id_seq OWNED BY public.dating_user.id;


--
-- TOC entry 215 (class 1259 OID 16400)
-- Name: user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."user" (
    id integer NOT NULL,
    vk_id integer,
    full_name character varying,
    age_from integer,
    age_to integer,
    target_gender integer,
    city character varying,
    "position" integer,
    "offset" integer
);


ALTER TABLE public."user" OWNER TO postgres;

--
-- TOC entry 214 (class 1259 OID 16399)
-- Name: user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.user_id_seq OWNER TO postgres;

--
-- TOC entry 3349 (class 0 OID 0)
-- Dependencies: 214
-- Name: user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_id_seq OWNED BY public."user".id;


--
-- TOC entry 3185 (class 2604 OID 16442)
-- Name: checked_list id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.checked_list ALTER COLUMN id SET DEFAULT nextval('public.checked_list_id_seq'::regclass);


--
-- TOC entry 3184 (class 2604 OID 16414)
-- Name: dating_user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dating_user ALTER COLUMN id SET DEFAULT nextval('public.dating_user_id_seq'::regclass);


--
-- TOC entry 3183 (class 2604 OID 16403)
-- Name: user id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user" ALTER COLUMN id SET DEFAULT nextval('public.user_id_seq'::regclass);


--
-- TOC entry 3195 (class 2606 OID 16444)
-- Name: checked_list checked_list_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.checked_list
    ADD CONSTRAINT checked_list_pkey PRIMARY KEY (id);


--
-- TOC entry 3197 (class 2606 OID 16446)
-- Name: checked_list checked_list_vk_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.checked_list
    ADD CONSTRAINT checked_list_vk_id_key UNIQUE (vk_id);


--
-- TOC entry 3191 (class 2606 OID 16416)
-- Name: dating_user dating_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dating_user
    ADD CONSTRAINT dating_user_pkey PRIMARY KEY (id);


--
-- TOC entry 3193 (class 2606 OID 16418)
-- Name: dating_user dating_user_vk_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dating_user
    ADD CONSTRAINT dating_user_vk_id_key UNIQUE (vk_id);


--
-- TOC entry 3187 (class 2606 OID 16407)
-- Name: user user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_pkey PRIMARY KEY (id);


--
-- TOC entry 3189 (class 2606 OID 16409)
-- Name: user user_vk_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."user"
    ADD CONSTRAINT user_vk_id_key UNIQUE (vk_id);


--
-- TOC entry 3199 (class 2606 OID 16447)
-- Name: checked_list checked_list_id_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.checked_list
    ADD CONSTRAINT checked_list_id_user_fkey FOREIGN KEY (id_user) REFERENCES public."user"(id) ON DELETE CASCADE;


--
-- TOC entry 3198 (class 2606 OID 16419)
-- Name: dating_user dating_user_id_user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.dating_user
    ADD CONSTRAINT dating_user_id_user_fkey FOREIGN KEY (id_user) REFERENCES public."user"(id) ON DELETE CASCADE;


-- Completed on 2023-07-13 21:42:05

--
-- PostgreSQL database dump complete
--

