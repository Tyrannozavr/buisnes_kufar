--
-- PostgreSQL database dump
--

\restrict CIK6YTj3UJBYwqqUXU3gPQvXK7ZGrvzfYFQE1wChKDnMkNHggEZFwoWmaMdZAYv

-- Dumped from database version 17.6
-- Dumped by pg_dump version 17.6

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

--
-- Name: businesstype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.businesstype AS ENUM (
    'GOODS',
    'SERVICES',
    'BOTH'
);


ALTER TYPE public.businesstype OWNER TO postgres;

--
-- Name: companyrelationtype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.companyrelationtype AS ENUM (
    'SUPPLIER',
    'BUYER',
    'PARTNER'
);


ALTER TYPE public.companyrelationtype OWNER TO postgres;

--
-- Name: employeerole; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.employeerole AS ENUM (
    'OWNER',
    'ADMIN',
    'USER'
);


ALTER TYPE public.employeerole OWNER TO postgres;

--
-- Name: employeestatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.employeestatus AS ENUM (
    'PENDING',
    'ACTIVE',
    'INACTIVE',
    'DELETED'
);


ALTER TYPE public.employeestatus OWNER TO postgres;

--
-- Name: orderstatus; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.orderstatus AS ENUM (
    'ACTIVE',
    'COMPLETED'
);


ALTER TYPE public.orderstatus OWNER TO postgres;

--
-- Name: ordertype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.ordertype AS ENUM (
    'GOODS',
    'SERVICES'
);


ALTER TYPE public.ordertype OWNER TO postgres;

--
-- Name: producttype; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.producttype AS ENUM (
    'GOOD',
    'SERVICE'
);


ALTER TYPE public.producttype OWNER TO postgres;

--
-- Name: tradeactivity; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.tradeactivity AS ENUM (
    'BUYER',
    'SELLER',
    'BOTH'
);


ALTER TYPE public.tradeactivity OWNER TO postgres;

--
-- Name: userrole; Type: TYPE; Schema: public; Owner: postgres
--

CREATE TYPE public.userrole AS ENUM (
    'OWNER',
    'ADMIN',
    'USER'
);


ALTER TYPE public.userrole OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: alembic_version; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);


ALTER TABLE public.alembic_version OWNER TO postgres;

--
-- Name: announcements; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.announcements (
    id integer NOT NULL,
    title character varying(255) NOT NULL,
    content text NOT NULL,
    category character varying(100) NOT NULL,
    images json,
    published boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    company_id integer NOT NULL
);


ALTER TABLE public.announcements OWNER TO postgres;

--
-- Name: announcements_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.announcements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.announcements_id_seq OWNER TO postgres;

--
-- Name: announcements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.announcements_id_seq OWNED BY public.announcements.id;


--
-- Name: chat_participants; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chat_participants (
    id integer NOT NULL,
    chat_id integer NOT NULL,
    company_id integer NOT NULL,
    user_id integer NOT NULL,
    is_admin boolean NOT NULL,
    joined_at timestamp without time zone NOT NULL,
    left_at timestamp without time zone
);


ALTER TABLE public.chat_participants OWNER TO postgres;

--
-- Name: chat_participants_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chat_participants_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chat_participants_id_seq OWNER TO postgres;

--
-- Name: chat_participants_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chat_participants_id_seq OWNED BY public.chat_participants.id;


--
-- Name: chats; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.chats (
    id integer NOT NULL,
    title character varying(255),
    is_group boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.chats OWNER TO postgres;

--
-- Name: chats_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.chats_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.chats_id_seq OWNER TO postgres;

--
-- Name: chats_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.chats_id_seq OWNED BY public.chats.id;


--
-- Name: cities; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.cities (
    id integer NOT NULL,
    country_id integer NOT NULL,
    region_id integer NOT NULL,
    federal_district_id integer,
    name character varying(100) NOT NULL,
    population integer,
    is_million_city boolean NOT NULL,
    is_regional_center boolean NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.cities OWNER TO postgres;

--
-- Name: cities_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.cities_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.cities_id_seq OWNER TO postgres;

--
-- Name: cities_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.cities_id_seq OWNED BY public.cities.id;


--
-- Name: companies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.companies (
    name character varying(255) NOT NULL,
    slug character varying(255) NOT NULL,
    logo character varying(255),
    type character varying(50) NOT NULL,
    trade_activity public.tradeactivity NOT NULL,
    business_type public.businesstype NOT NULL,
    activity_type character varying(100) NOT NULL,
    description text,
    country character varying(100) NOT NULL,
    federal_district character varying(100) NOT NULL,
    region character varying(100) NOT NULL,
    city character varying(100) NOT NULL,
    country_id integer,
    federal_district_id integer,
    region_id integer,
    city_id integer,
    full_name character varying(255) NOT NULL,
    inn character varying(12),
    ogrn character varying(15),
    kpp character varying(9) NOT NULL,
    registration_date timestamp without time zone NOT NULL,
    legal_address character varying(255) NOT NULL,
    production_address character varying(255),
    phone character varying(20) NOT NULL,
    email character varying(255) NOT NULL,
    website character varying(255),
    total_views integer NOT NULL,
    monthly_views integer NOT NULL,
    total_purchases integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    is_active boolean NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.companies OWNER TO postgres;

--
-- Name: companies_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.companies_id_seq OWNER TO postgres;

--
-- Name: companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.companies_id_seq OWNED BY public.companies.id;


--
-- Name: company_officials; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_officials (
    "position" character varying(100) NOT NULL,
    full_name character varying(255) NOT NULL,
    company_id integer NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.company_officials OWNER TO postgres;

--
-- Name: company_officials_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_officials_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_officials_id_seq OWNER TO postgres;

--
-- Name: company_officials_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_officials_id_seq OWNED BY public.company_officials.id;


--
-- Name: company_relations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.company_relations (
    id integer NOT NULL,
    company_id integer NOT NULL,
    related_company_id integer NOT NULL,
    relation_type public.companyrelationtype NOT NULL,
    created_at timestamp without time zone NOT NULL
);


ALTER TABLE public.company_relations OWNER TO postgres;

--
-- Name: company_relations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.company_relations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.company_relations_id_seq OWNER TO postgres;

--
-- Name: company_relations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.company_relations_id_seq OWNED BY public.company_relations.id;


--
-- Name: countries; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.countries (
    id integer NOT NULL,
    code character varying(3) NOT NULL,
    name character varying(100) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.countries OWNER TO postgres;

--
-- Name: countries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.countries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.countries_id_seq OWNER TO postgres;

--
-- Name: countries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.countries_id_seq OWNED BY public.countries.id;


--
-- Name: email_change_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.email_change_tokens (
    id integer NOT NULL,
    token character varying NOT NULL,
    user_id integer NOT NULL,
    new_email character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone NOT NULL,
    is_used boolean
);


ALTER TABLE public.email_change_tokens OWNER TO postgres;

--
-- Name: email_change_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.email_change_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.email_change_tokens_id_seq OWNER TO postgres;

--
-- Name: email_change_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.email_change_tokens_id_seq OWNED BY public.email_change_tokens.id;


--
-- Name: employee_permissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employee_permissions (
    id integer NOT NULL,
    employee_id integer NOT NULL,
    permission_key character varying NOT NULL,
    granted boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.employee_permissions OWNER TO postgres;

--
-- Name: employee_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employee_permissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employee_permissions_id_seq OWNER TO postgres;

--
-- Name: employee_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employee_permissions_id_seq OWNED BY public.employee_permissions.id;


--
-- Name: employees; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.employees (
    id integer NOT NULL,
    user_id integer,
    company_id integer NOT NULL,
    email character varying NOT NULL,
    first_name character varying,
    last_name character varying,
    patronymic character varying,
    phone character varying,
    "position" character varying,
    role public.employeerole NOT NULL,
    status public.employeestatus NOT NULL,
    permissions text,
    deletion_requested_at timestamp with time zone,
    deletion_requested_by integer,
    deletion_rejected_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    created_by integer
);


ALTER TABLE public.employees OWNER TO postgres;

--
-- Name: employees_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.employees_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.employees_id_seq OWNER TO postgres;

--
-- Name: employees_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.employees_id_seq OWNED BY public.employees.id;


--
-- Name: federal_districts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.federal_districts (
    id integer NOT NULL,
    country_id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(10) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.federal_districts OWNER TO postgres;

--
-- Name: federal_districts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.federal_districts_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.federal_districts_id_seq OWNER TO postgres;

--
-- Name: federal_districts_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.federal_districts_id_seq OWNED BY public.federal_districts.id;


--
-- Name: messages; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.messages (
    id integer NOT NULL,
    chat_id integer NOT NULL,
    sender_company_id integer NOT NULL,
    sender_user_id integer NOT NULL,
    content text NOT NULL,
    file_path character varying(500),
    file_name character varying(255),
    file_size integer,
    file_type character varying(100),
    is_read boolean NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL
);


ALTER TABLE public.messages OWNER TO postgres;

--
-- Name: messages_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.messages_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.messages_id_seq OWNER TO postgres;

--
-- Name: messages_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.messages_id_seq OWNED BY public.messages.id;


--
-- Name: order_documents; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_documents (
    order_id integer NOT NULL,
    document_type character varying(50) NOT NULL,
    document_number character varying(50) NOT NULL,
    document_date timestamp without time zone NOT NULL,
    document_content json,
    document_file_path character varying(500),
    is_sent boolean NOT NULL,
    sent_at timestamp without time zone,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.order_documents OWNER TO postgres;

--
-- Name: order_documents_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_documents_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_documents_id_seq OWNER TO postgres;

--
-- Name: order_documents_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_documents_id_seq OWNED BY public.order_documents.id;


--
-- Name: order_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_history (
    order_id integer NOT NULL,
    changed_by_company_id integer NOT NULL,
    change_type character varying(50) NOT NULL,
    change_description text NOT NULL,
    old_data json,
    new_data json,
    created_at timestamp without time zone NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.order_history OWNER TO postgres;

--
-- Name: order_history_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_history_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_history_id_seq OWNER TO postgres;

--
-- Name: order_history_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_history_id_seq OWNED BY public.order_history.id;


--
-- Name: order_items; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.order_items (
    order_id integer NOT NULL,
    product_id integer,
    product_name character varying(255) NOT NULL,
    product_slug character varying(255),
    product_description text,
    product_article character varying(100),
    product_type character varying(50),
    logo_url character varying(255),
    quantity double precision NOT NULL,
    unit_of_measurement character varying(50) NOT NULL,
    price double precision NOT NULL,
    amount double precision NOT NULL,
    "position" integer NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.order_items OWNER TO postgres;

--
-- Name: order_items_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.order_items_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.order_items_id_seq OWNER TO postgres;

--
-- Name: order_items_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.order_items_id_seq OWNED BY public.order_items.id;


--
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    buyer_order_number character varying(20) NOT NULL,
    seller_order_number character varying(20) NOT NULL,
    deal_type public.ordertype NOT NULL,
    status public.orderstatus NOT NULL,
    buyer_company_id integer NOT NULL,
    seller_company_id integer NOT NULL,
    invoice_number character varying(20),
    contract_number character varying(20),
    invoice_date timestamp without time zone,
    contract_date timestamp without time zone,
    comments text,
    total_amount double precision NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.orders OWNER TO postgres;

--
-- Name: orders_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.orders_id_seq OWNER TO postgres;

--
-- Name: orders_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_id_seq OWNED BY public.orders.id;


--
-- Name: password_recovery_codes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.password_recovery_codes (
    id integer NOT NULL,
    email character varying NOT NULL,
    code character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone NOT NULL,
    is_used boolean
);


ALTER TABLE public.password_recovery_codes OWNER TO postgres;

--
-- Name: password_recovery_codes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.password_recovery_codes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.password_recovery_codes_id_seq OWNER TO postgres;

--
-- Name: password_recovery_codes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.password_recovery_codes_id_seq OWNED BY public.password_recovery_codes.id;


--
-- Name: password_reset_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.password_reset_tokens (
    id integer NOT NULL,
    token character varying NOT NULL,
    email character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone NOT NULL,
    is_used boolean
);


ALTER TABLE public.password_reset_tokens OWNER TO postgres;

--
-- Name: password_reset_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.password_reset_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.password_reset_tokens_id_seq OWNER TO postgres;

--
-- Name: password_reset_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.password_reset_tokens_id_seq OWNED BY public.password_reset_tokens.id;


--
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    name character varying(255) NOT NULL,
    slug character varying(255) NOT NULL,
    description text,
    article character varying(100) NOT NULL,
    type public.producttype NOT NULL,
    price double precision NOT NULL,
    images json NOT NULL,
    characteristics json NOT NULL,
    is_hidden boolean NOT NULL,
    is_deleted boolean NOT NULL,
    unit_of_measurement character varying(100) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    company_id integer NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.products OWNER TO postgres;

--
-- Name: products_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.products_id_seq OWNER TO postgres;

--
-- Name: products_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_id_seq OWNED BY public.products.id;


--
-- Name: regions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.regions (
    id integer NOT NULL,
    country_id integer NOT NULL,
    federal_district_id integer,
    name character varying(100) NOT NULL,
    code character varying(20) NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.regions OWNER TO postgres;

--
-- Name: regions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.regions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.regions_id_seq OWNER TO postgres;

--
-- Name: regions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.regions_id_seq OWNED BY public.regions.id;


--
-- Name: registration_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.registration_tokens (
    id integer NOT NULL,
    token character varying NOT NULL,
    email character varying NOT NULL,
    user_id integer,
    created_at timestamp with time zone DEFAULT now(),
    expires_at timestamp with time zone NOT NULL,
    is_used boolean
);


ALTER TABLE public.registration_tokens OWNER TO postgres;

--
-- Name: registration_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.registration_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.registration_tokens_id_seq OWNER TO postgres;

--
-- Name: registration_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.registration_tokens_id_seq OWNED BY public.registration_tokens.id;


--
-- Name: units_of_measurement; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.units_of_measurement (
    name character varying(100) NOT NULL,
    symbol character varying(20) NOT NULL,
    code character varying(10) NOT NULL,
    created_at timestamp without time zone NOT NULL,
    updated_at timestamp without time zone NOT NULL,
    id integer NOT NULL
);


ALTER TABLE public.units_of_measurement OWNER TO postgres;

--
-- Name: units_of_measurement_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.units_of_measurement_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.units_of_measurement_id_seq OWNER TO postgres;

--
-- Name: units_of_measurement_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.units_of_measurement_id_seq OWNED BY public.units_of_measurement.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    email character varying NOT NULL,
    first_name character varying,
    last_name character varying,
    patronymic character varying,
    phone character varying NOT NULL,
    "position" character varying,
    hashed_password character varying,
    is_active boolean,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone,
    company_id integer,
    role public.userrole DEFAULT 'USER'::public.userrole NOT NULL,
    permissions text
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: announcements id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcements ALTER COLUMN id SET DEFAULT nextval('public.announcements_id_seq'::regclass);


--
-- Name: chat_participants id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_participants ALTER COLUMN id SET DEFAULT nextval('public.chat_participants_id_seq'::regclass);


--
-- Name: chats id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats ALTER COLUMN id SET DEFAULT nextval('public.chats_id_seq'::regclass);


--
-- Name: cities id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities ALTER COLUMN id SET DEFAULT nextval('public.cities_id_seq'::regclass);


--
-- Name: companies id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies ALTER COLUMN id SET DEFAULT nextval('public.companies_id_seq'::regclass);


--
-- Name: company_officials id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_officials ALTER COLUMN id SET DEFAULT nextval('public.company_officials_id_seq'::regclass);


--
-- Name: company_relations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_relations ALTER COLUMN id SET DEFAULT nextval('public.company_relations_id_seq'::regclass);


--
-- Name: countries id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.countries ALTER COLUMN id SET DEFAULT nextval('public.countries_id_seq'::regclass);


--
-- Name: email_change_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_change_tokens ALTER COLUMN id SET DEFAULT nextval('public.email_change_tokens_id_seq'::regclass);


--
-- Name: employee_permissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_permissions ALTER COLUMN id SET DEFAULT nextval('public.employee_permissions_id_seq'::regclass);


--
-- Name: employees id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees ALTER COLUMN id SET DEFAULT nextval('public.employees_id_seq'::regclass);


--
-- Name: federal_districts id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.federal_districts ALTER COLUMN id SET DEFAULT nextval('public.federal_districts_id_seq'::regclass);


--
-- Name: messages id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages ALTER COLUMN id SET DEFAULT nextval('public.messages_id_seq'::regclass);


--
-- Name: order_documents id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_documents ALTER COLUMN id SET DEFAULT nextval('public.order_documents_id_seq'::regclass);


--
-- Name: order_history id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_history ALTER COLUMN id SET DEFAULT nextval('public.order_history_id_seq'::regclass);


--
-- Name: order_items id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items ALTER COLUMN id SET DEFAULT nextval('public.order_items_id_seq'::regclass);


--
-- Name: orders id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders ALTER COLUMN id SET DEFAULT nextval('public.orders_id_seq'::regclass);


--
-- Name: password_recovery_codes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_recovery_codes ALTER COLUMN id SET DEFAULT nextval('public.password_recovery_codes_id_seq'::regclass);


--
-- Name: password_reset_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_tokens ALTER COLUMN id SET DEFAULT nextval('public.password_reset_tokens_id_seq'::regclass);


--
-- Name: products id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN id SET DEFAULT nextval('public.products_id_seq'::regclass);


--
-- Name: regions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regions ALTER COLUMN id SET DEFAULT nextval('public.regions_id_seq'::regclass);


--
-- Name: registration_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration_tokens ALTER COLUMN id SET DEFAULT nextval('public.registration_tokens_id_seq'::regclass);


--
-- Name: units_of_measurement id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.units_of_measurement ALTER COLUMN id SET DEFAULT nextval('public.units_of_measurement_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: alembic_version; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.alembic_version (version_num) FROM stdin;
dbbcb4d5aac3
\.


--
-- Data for Name: announcements; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.announcements (id, title, content, category, images, published, created_at, updated_at, company_id) FROM stdin;
\.


--
-- Data for Name: chat_participants; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chat_participants (id, chat_id, company_id, user_id, is_admin, joined_at, left_at) FROM stdin;
\.


--
-- Data for Name: chats; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.chats (id, title, is_group, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: cities; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.cities (id, country_id, region_id, federal_district_id, name, population, is_million_city, is_regional_center, is_active, created_at, updated_at) FROM stdin;
1	1	1	1	Москва	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
2	1	1	1	Абрамцево	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
3	1	1	1	Алабино	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
4	1	1	1	Апрелевка	18467	f	f	t	2025-10-26 06:31:31.599872+00	\N
5	1	1	1	Архангельское	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
6	1	1	1	Ашитково	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
7	1	1	1	Байконур	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
8	1	1	1	Бакшеево	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
9	1	1	1	Балашиха	215353	f	f	t	2025-10-26 06:31:31.599872+00	\N
10	1	1	1	Барыбино	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
11	1	1	1	Белозёрский	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
12	1	1	1	Белоомут	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
13	1	1	1	Белые Столбы	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
14	1	1	1	Бородино (Московская обл.	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
15	1	1	1	Бронницы	21102	f	f	t	2025-10-26 06:31:31.599872+00	\N
16	1	1	1	Быково (Московская обл.	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
17	1	1	1	Валуево	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
18	1	1	1	Вербилки	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
19	1	1	1	Верея	5368	f	f	t	2025-10-26 06:31:31.599872+00	\N
20	1	1	1	Видное	56798	f	t	t	2025-10-26 06:31:31.599872+00	\N
21	1	1	1	Внуково	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
22	1	1	1	Вождь Пролетариата	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
23	1	1	1	Волоколамск	23386	f	t	t	2025-10-26 06:31:31.599872+00	\N
24	1	1	1	Вороново	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
25	1	1	1	Воскресенск	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
26	1	1	1	Восточный	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
27	1	1	1	Востряково	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
28	1	1	1	Высоковск	10642	f	f	t	2025-10-26 06:31:31.599872+00	\N
29	1	1	1	Голицыно (Московская обл.	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
30	1	1	1	Деденево	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
31	1	1	1	Дедовск	29280	f	f	t	2025-10-26 06:31:31.599872+00	\N
32	1	1	1	Дзержинский	47125	f	f	t	2025-10-26 06:31:31.599872+00	\N
33	1	1	1	Дмитров	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
34	1	1	1	Долгопрудный	90976	f	f	t	2025-10-26 06:31:31.599872+00	\N
35	1	1	1	Домодедово	96123	f	f	t	2025-10-26 06:31:31.599872+00	\N
36	1	1	1	Дорохово	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
37	1	1	1	Дрезна	11815	f	f	t	2025-10-26 06:31:31.599872+00	\N
38	1	1	1	Дубки	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
39	1	1	1	Дубна	70569	f	f	t	2025-10-26 06:31:31.599872+00	\N
40	1	1	1	Егорьевск	70133	f	f	t	2025-10-26 06:31:31.599872+00	\N
41	1	1	1	Железнодорожный (Московск.	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
42	1	1	1	Жилево	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
43	1	10	1	Жуковка	18269	f	t	t	2025-10-26 06:31:31.599872+00	\N
44	1	1	1	Жуковский	102729	f	f	t	2025-10-26 06:31:31.599872+00	\N
45	1	1	1	Загорск	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
46	1	1	1	Загорянский	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
47	1	1	1	Запрудная	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
48	1	1	1	Зарайск	24648	f	t	t	2025-10-26 06:31:31.599872+00	\N
49	1	1	1	Звенигород	16395	f	f	t	2025-10-26 06:31:31.599872+00	\N
50	1	1	1	Зеленоград	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
51	1	1	1	Ивантеевка (Московская обл.	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
52	1	1	1	Икша	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
53	1	1	1	Ильинский (Московская обл.	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
54	1	1	1	Истра	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
55	1	1	1	Калининец	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
56	1	1	1	Кашира	41880	f	f	t	2025-10-26 06:31:31.599872+00	\N
57	1	1	1	Керва	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
58	1	1	1	Климовск	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
59	1	1	1	Клин	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
60	1	1	1	Клязьма	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
61	1	1	1	Кожино	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
62	1	1	1	Кокошкино	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
63	1	1	1	Коломна	144642	f	f	t	2025-10-26 06:31:31.599872+00	\N
64	1	1	1	Колюбакино	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
65	1	1	1	Королев	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
66	1	1	1	Косино	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
67	1	1	1	Котельники	32347	f	f	t	2025-10-26 06:31:31.599872+00	\N
68	1	1	1	Красково	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
69	1	1	1	Красноармейск (Московская обл.	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
70	1	1	1	Красногорск	116738	f	t	t	2025-10-26 06:31:31.599872+00	\N
71	1	1	1	Краснозаводск	13432	f	f	t	2025-10-26 06:31:31.599872+00	\N
72	1	1	1	Краснознаменск (Московская обл.	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
73	1	1	1	Красный Ткач	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
74	1	1	1	Крюково	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
75	1	1	1	Кубинка	22918	f	f	t	2025-10-26 06:31:31.599872+00	\N
76	1	1	1	Купавна	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
77	1	1	1	Куровское	21821	f	f	t	2025-10-26 06:31:31.599872+00	\N
78	1	1	1	Лесной Городок	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
79	1	1	1	Ликино-Дулево	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
80	1	1	1	Лобня	74350	f	f	t	2025-10-26 06:31:31.599872+00	\N
81	1	1	1	Лопатинский	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
82	1	1	1	Лосино-Петровский	22550	f	f	t	2025-10-26 06:31:31.599872+00	\N
83	1	1	1	Лотошино	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
84	1	1	1	Лукино	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
85	1	1	1	Луховицы	29849	f	t	t	2025-10-26 06:31:31.599872+00	\N
86	1	1	1	Лыткарино	55147	f	f	t	2025-10-26 06:31:31.599872+00	\N
87	1	1	1	Львовский	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
88	1	1	1	Люберцы	171978	f	t	t	2025-10-26 06:31:31.599872+00	\N
89	1	1	1	Малаховка	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
90	1	1	1	Михайловское	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
91	1	1	1	Михнево	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
92	1	1	1	Можайск	31388	f	t	t	2025-10-26 06:31:31.599872+00	\N
93	1	1	1	Монино	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
94	1	1	1	Московский	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
95	1	1	1	Муханово	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
96	1	1	1	Мытищи	173341	f	f	t	2025-10-26 06:31:31.599872+00	\N
97	1	1	1	Нарофоминск	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
98	1	1	1	Нахабино	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
99	1	1	1	Некрасовка	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
100	1	1	1	Немчиновка	0	f	f	t	2025-10-26 06:31:31.599872+00	\N
101	1	1	1	Новобратцевский	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
102	1	1	1	Новоподрезково	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
103	1	1	1	Ногинск	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
104	1	1	1	Обухово	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
105	1	1	1	Одинцово	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
106	1	1	1	Ожерелье	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
107	1	1	1	Озеры	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
108	1	1	1	Октябрьский (Московская обл.	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
109	1	1	1	Опалиха	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
110	1	1	1	Орехово-Зуево	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
111	1	1	1	Павловский Посад	63771	f	t	t	2025-10-26 06:31:31.626334+00	\N
112	1	1	1	Первомайский (Московская обл.	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
113	1	1	1	Пески (Московская обл.	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
114	1	1	1	Пироговский	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
115	1	1	1	Подольск	187956	f	f	t	2025-10-26 06:31:31.626334+00	\N
116	1	1	1	Полушкино	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
117	1	1	1	Правдинский	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
118	1	1	1	Привокзальный	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
119	1	1	1	Пролетарский	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
120	1	1	1	Протвино (Московская обл.	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
121	1	1	1	Пушкино	102840	f	t	t	2025-10-26 06:31:31.626334+00	\N
122	1	1	1	Пущино	20263	f	f	t	2025-10-26 06:31:31.626334+00	\N
123	1	1	1	Раменское	96355	f	t	t	2025-10-26 06:31:31.626334+00	\N
124	1	1	1	Реутов	87195	f	f	t	2025-10-26 06:31:31.626334+00	\N
125	1	1	1	Решетниково	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
126	1	1	1	Родники (Московская обл.	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
127	1	1	1	Рошаль	21265	f	f	t	2025-10-26 06:31:31.626334+00	\N
128	1	1	1	Рублево	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
129	1	1	1	Руза	13495	f	t	t	2025-10-26 06:31:31.626334+00	\N
130	1	1	1	Салтыковка	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
131	1	1	1	Северный	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
132	1	1	1	Сергиев Посад	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
133	1	1	1	Серебряные Пруды	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
134	1	1	1	Серпухов	126496	f	f	t	2025-10-26 06:31:31.626334+00	\N
135	1	1	1	Солнечногорск	52996	f	t	t	2025-10-26 06:31:31.626334+00	\N
136	1	1	1	Солнцево	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
137	1	1	1	Софрино	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
138	1	1	1	Старая Купавна	21859	f	f	t	2025-10-26 06:31:31.626334+00	\N
139	1	1	1	Старбеево	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
140	1	1	1	Ступино	66942	f	t	t	2025-10-26 06:31:31.626334+00	\N
141	1	1	1	Сходня	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
142	1	1	1	Талдом	13819	f	t	t	2025-10-26 06:31:31.626334+00	\N
143	1	1	1	Текстильщик	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
144	1	1	1	Темпы	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
145	1	1	1	Томилино	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
146	1	71	6	Троицк	78637	f	f	t	2025-10-26 06:31:31.626334+00	\N
147	1	1	1	Туголесский Бор	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
148	1	1	1	Тучково	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
149	1	1	1	Уваровка	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
150	1	1	1	Удельная	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
151	1	1	1	Успенское	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
152	1	1	1	Фирсановка	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
153	1	1	1	Фрязино	55449	f	f	t	2025-10-26 06:31:31.626334+00	\N
154	1	1	1	Фряново	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
155	1	1	1	Химки	207125	f	f	t	2025-10-26 06:31:31.626334+00	\N
156	1	1	1	Хотьково	21612	f	f	t	2025-10-26 06:31:31.626334+00	\N
157	1	1	1	Черкизово	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
158	1	1	1	Черноголовка	20986	f	f	t	2025-10-26 06:31:31.626334+00	\N
159	1	1	1	Черусти	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
160	1	1	1	Чехов	60677	f	t	t	2025-10-26 06:31:31.626334+00	\N
161	1	1	1	Шарапово	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
162	1	1	1	Шатура	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
163	1	1	1	Шатурторф	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
164	1	1	1	Шаховская	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
165	1	1	1	Шереметьевский	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
166	1	1	1	Щелково	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
167	1	1	1	Щербинка	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
168	1	1	1	Электрогорск	22120	f	f	t	2025-10-26 06:31:31.626334+00	\N
169	1	1	1	Электросталь	155324	f	f	t	2025-10-26 06:31:31.626334+00	\N
170	1	1	1	Электроугли	20120	f	f	t	2025-10-26 06:31:31.626334+00	\N
171	1	1	1	Юбилейный (Московская обл.	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
172	1	1	1	Яхрома	13248	f	f	t	2025-10-26 06:31:31.626334+00	\N
173	1	2	2	Санкт-Петербург	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
174	1	2	2	Александровская	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
175	1	2	2	Бокситогорск	16593	f	t	t	2025-10-26 06:31:31.626334+00	\N
176	1	2	2	Большая Ижора	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
177	1	2	2	Будогощь	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
178	1	2	2	Вознесенье	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
179	1	2	2	Волосово	12162	f	t	t	2025-10-26 06:31:31.626334+00	\N
180	1	2	2	Волхов	47344	f	t	t	2025-10-26 06:31:31.626334+00	\N
181	1	2	2	Всеволожск	59689	f	t	t	2025-10-26 06:31:31.626334+00	\N
182	1	2	2	Выборг	80013	f	t	t	2025-10-26 06:31:31.626334+00	\N
183	1	2	2	Вырица	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
184	1	2	2	Высоцк	1244	f	f	t	2025-10-26 06:31:31.626334+00	\N
185	1	2	2	Гатчина	92566	f	t	t	2025-10-26 06:31:31.626334+00	\N
186	1	2	2	Дружная Горка	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
187	1	2	2	Дубровка	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
188	1	2	2	Ефимовский	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
189	1	2	2	Зеленогорск (Ленинградская обл.	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
190	1	2	2	Ивангород	9797	f	f	t	2025-10-26 06:31:31.626334+00	\N
191	1	2	2	Каменногорск	6761	f	f	t	2025-10-26 06:31:31.626334+00	\N
192	1	2	2	Кикерино	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
193	1	2	2	Кингисепп	48667	f	t	t	2025-10-26 06:31:31.626334+00	\N
194	1	2	2	Кириши	52826	f	t	t	2025-10-26 06:31:31.626334+00	\N
195	1	38	2	Кировск	28659	f	f	t	2025-10-26 06:31:31.626334+00	\N
196	1	2	2	Кобринское	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
197	1	2	2	Колпино	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
198	1	2	2	Коммунар	20265	f	f	t	2025-10-26 06:31:31.626334+00	\N
199	1	2	2	Кронштадт	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
200	1	2	2	Лисий Нос	0	f	f	t	2025-10-26 06:31:31.626334+00	\N
201	1	2	2	Лодейное Поле	21053	f	t	t	2025-10-26 06:31:31.656166+00	\N
202	1	2	2	Ломоносов	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
203	1	2	2	Луга	36409	f	t	t	2025-10-26 06:31:31.656166+00	\N
204	1	2	2	Павловск (Ленинградская обл.	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
205	1	2	2	Парголово	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
206	1	2	2	Петродворец	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
207	1	2	2	Пикалёво	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
208	1	2	2	Подпорожье	18729	f	t	t	2025-10-26 06:31:31.656166+00	\N
209	1	2	2	Приозерск	18929	f	t	t	2025-10-26 06:31:31.656166+00	\N
210	1	2	2	Пушкин	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
211	1	2	2	Светогорск	15973	f	f	t	2025-10-26 06:31:31.656166+00	\N
212	1	2	2	Сертолово	47854	f	f	t	2025-10-26 06:31:31.656166+00	\N
213	1	2	2	Сестрорецк	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
214	1	2	2	Сланцы	33587	f	t	t	2025-10-26 06:31:31.656166+00	\N
215	1	2	2	Сосновый Бор	65901	f	f	t	2025-10-26 06:31:31.656166+00	\N
216	1	2	2	Тихвин	58843	f	t	t	2025-10-26 06:31:31.656166+00	\N
217	1	2	2	Тосно	39127	f	t	t	2025-10-26 06:31:31.656166+00	\N
218	1	2	2	Шлиссельбург	13305	f	f	t	2025-10-26 06:31:31.656166+00	\N
219	1	3	3	Адыгейск	12689	f	f	t	2025-10-26 06:31:31.656166+00	\N
220	1	3	3	Майкоп (Адыгея	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
221	1	4	5	Акташ	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
222	1	4	5	Акутиха	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
223	1	4	5	Алейск	28528	f	f	t	2025-10-26 06:31:31.656166+00	\N
224	1	4	5	Алтайский	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
225	1	4	5	Баево	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
226	1	4	5	Барнаул	635585	f	f	t	2025-10-26 06:31:31.656166+00	\N
227	1	4	5	Белово (Алтайский край	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
228	1	4	5	Белокуриха	15072	f	f	t	2025-10-26 06:31:31.656166+00	\N
229	1	4	5	Белоярск	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
230	1	4	5	Бийск	203826	f	f	t	2025-10-26 06:31:31.656166+00	\N
231	1	4	5	Благовещенск	34246	f	t	t	2025-10-26 06:31:31.656166+00	\N
232	1	4	5	Боровлянка	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
233	1	4	5	Бурла	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
234	1	4	5	Бурсоль	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
235	1	4	5	Быстрый Исток	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
236	1	4	5	Волчиха	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
237	1	4	5	Горно-Алтайск	62861	f	f	t	2025-10-26 06:31:31.656166+00	\N
238	1	50	1	Горняк	13040	f	t	t	2025-10-26 06:31:31.656166+00	\N
239	1	4	5	Ельцовка	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
240	1	4	5	Залесово	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
241	1	4	5	Заринск	47035	f	f	t	2025-10-26 06:31:31.656166+00	\N
242	1	4	5	Заток	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
243	1	4	5	Змеиногорск	10569	f	t	t	2025-10-26 06:31:31.656166+00	\N
244	1	4	5	Камень-на-Оби	41787	f	t	t	2025-10-26 06:31:31.656166+00	\N
245	1	4	5	Ключи (Алтайский край	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
246	1	4	5	Кош-Агач	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
247	1	4	5	Красногорское (Алтайский край	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
248	1	4	5	Краснощеково	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
249	1	4	5	Кулунда	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
250	1	4	5	Кытманово	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
251	1	4	5	Мамонтово	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
252	1	4	5	Новичиха	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
253	1	4	5	Новоалтайск	73134	f	f	t	2025-10-26 06:31:31.656166+00	\N
254	1	4	5	Онгудай	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
255	1	4	5	Павловск (Алтайский край	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
256	1	4	5	Петропавловское	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
257	1	4	5	Поспелиха	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
258	1	4	5	Ребриха	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
259	1	4	5	Родино	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
260	1	4	5	Рубцовск	146386	f	f	t	2025-10-26 06:31:31.656166+00	\N
261	1	4	5	Славгород	30370	f	f	t	2025-10-26 06:31:31.656166+00	\N
262	1	4	5	Смоленское	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
263	1	4	5	Солонешное	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
264	1	4	5	Солтон	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
265	1	4	5	Староаллейское	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
266	1	4	5	Табуны	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
267	1	4	5	Тальменка	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
268	1	4	5	Тогул	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
269	1	4	5	Топчиха	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
270	1	4	5	Троицкое (Алтайский край	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
271	1	4	5	Турочак	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
272	1	4	5	Тюменцево	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
273	1	4	5	Угловское	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
274	1	4	5	Усть-Калманка	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
275	1	4	5	Усть-Кан	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
276	1	4	5	Усть-Кокса	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
277	1	4	5	Усть-Улаган	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
278	1	4	5	Усть-Чарышская Пристань	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
279	1	4	5	Хабары	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
280	1	32	6	Целинное	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
281	1	4	5	Чарышское	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
282	1	4	5	Шебалино	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
283	1	4	5	Шелаболиха	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
284	1	4	5	Шипуново	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
285	1	5	4	Айгунь	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
286	1	5	4	Архара	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
287	1	26	5	Белогорск	16354	f	f	t	2025-10-26 06:31:31.656166+00	\N
288	1	5	4	Благовещенск (Амурская обл.	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
289	1	5	4	Бурея	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
290	1	5	4	Возжаевка	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
291	1	5	4	Екатеринославка	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
292	1	5	4	Ерофей Павлович	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
293	1	5	4	Завитинск	11481	f	t	t	2025-10-26 06:31:31.656166+00	\N
294	1	5	4	Зея	25042	f	f	t	2025-10-26 06:31:31.656166+00	\N
295	1	5	4	Златоустовск	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
296	1	5	4	Ивановка	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
297	1	5	4	Коболдо	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
298	1	5	4	Магдагачи	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
299	1	5	4	Новобурейский	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
300	1	5	4	Поярково	0	f	f	t	2025-10-26 06:31:31.656166+00	\N
301	1	5	4	Райчихинск	20499	f	f	t	2025-10-26 06:31:31.683128+00	\N
302	1	5	4	Ромны	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
303	1	5	4	Свободный	58594	f	f	t	2025-10-26 06:31:31.683128+00	\N
304	1	5	4	Серышево	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
305	1	5	4	Сковородино	9561	f	t	t	2025-10-26 06:31:31.683128+00	\N
306	1	5	4	Стойба	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
307	1	5	4	Тамбовка	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
308	1	5	4	Тында	35574	f	f	t	2025-10-26 06:31:31.683128+00	\N
309	1	5	4	Февральск	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
310	1	5	4	Шимановск	19815	f	f	t	2025-10-26 06:31:31.683128+00	\N
311	1	5	4	Экимчан	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
312	1	5	4	Ядрино	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
313	1	6	2	Амдерма	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
314	1	6	2	Архангельск	348716	f	f	t	2025-10-26 06:31:31.683128+00	\N
315	1	6	2	Березник	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
316	1	6	2	Вельск	23885	f	t	t	2025-10-26 06:31:31.683128+00	\N
317	1	6	2	Верхняя Тойма	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
318	1	6	2	Волошка	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
319	1	6	2	Вычегодский	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
320	1	6	2	Емца	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
321	1	6	2	Илеза	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
322	1	6	2	Ильинско-Подомское	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
323	1	6	2	Каргополь (Архангельская обл.	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
324	1	6	2	Карпогоры	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
325	1	6	2	Кодино	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
326	1	6	2	Коноша	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
327	1	6	2	Коряжма	39629	f	f	t	2025-10-26 06:31:31.683128+00	\N
328	1	6	2	Котлас	60562	f	t	t	2025-10-26 06:31:31.683128+00	\N
329	1	6	2	Красноборск	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
330	1	6	2	Лешуконское	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
331	1	6	2	Мезень	3599	f	t	t	2025-10-26 06:31:31.683128+00	\N
332	1	6	2	Мирный (Архангельская обл.	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
333	1	6	2	Нарьян-Мар	21296	f	f	t	2025-10-26 06:31:31.683128+00	\N
334	1	6	2	Новодвинск	40612	f	f	t	2025-10-26 06:31:31.683128+00	\N
335	1	6	2	Няндома	22354	f	t	t	2025-10-26 06:31:31.683128+00	\N
336	1	6	2	Онега	21359	f	t	t	2025-10-26 06:31:31.683128+00	\N
337	1	6	2	Пинега	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
338	1	6	2	Плесецк	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
339	1	6	2	Савинск	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
340	1	6	2	Северодвинск	192265	f	f	t	2025-10-26 06:31:31.683128+00	\N
341	1	6	2	Сольвычегодск	2460	f	f	t	2025-10-26 06:31:31.683128+00	\N
342	1	6	2	Холмогоры	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
343	1	6	2	Шенкурск	5702	f	t	t	2025-10-26 06:31:31.683128+00	\N
344	1	6	2	Яренск	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
345	1	7	3	Астрахань	520662	f	f	t	2025-10-26 06:31:31.683128+00	\N
346	1	7	3	Ахтубинск	41898	f	t	t	2025-10-26 06:31:31.683128+00	\N
347	1	7	3	Верхний Баскунчак	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
348	1	7	3	Володарский	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
349	1	7	3	Енотаевка	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
350	1	7	3	Икряное	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
351	1	7	3	Камызяк	16291	f	t	t	2025-10-26 06:31:31.683128+00	\N
352	1	7	3	Капустин Яр	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
353	1	7	3	Красный Яр (Астраханская обл.	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
354	1	7	3	Лиман	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
355	1	7	3	Началово	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
356	1	7	3	Харабали	18209	f	t	t	2025-10-26 06:31:31.683128+00	\N
357	1	7	3	Черный Яр	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
358	1	8	7	Агидель	16365	f	f	t	2025-10-26 06:31:31.683128+00	\N
359	1	8	7	Аксаково	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
360	1	8	7	Амзя	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
361	1	8	7	Архангелькое	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
362	1	8	7	Аскарово	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
363	1	8	7	Аскино	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
364	1	8	7	Баймак	17710	f	t	t	2025-10-26 06:31:31.683128+00	\N
365	1	8	7	Бакалы	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
366	1	8	7	Белебей	60183	f	t	t	2025-10-26 06:31:31.683128+00	\N
367	1	8	7	Белорецк	68804	f	t	t	2025-10-26 06:31:31.683128+00	\N
368	1	8	7	Бижбуляк	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
369	1	8	7	Бирск	41637	f	t	t	2025-10-26 06:31:31.683128+00	\N
370	1	8	7	Благовещенск (Башкирия	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
371	1	8	7	Большеустьикинское	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
372	1	8	7	Бураево	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
373	1	8	7	Верхнеяркеево	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
374	1	8	7	Верхние Киги	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
375	1	8	7	Верхние Татышлы	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
376	1	8	7	Верхний Авзян	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
377	1	8	7	Давлеканово	24040	f	t	t	2025-10-26 06:31:31.683128+00	\N
378	1	8	7	Дуван	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
379	1	8	7	Дюртюли	31272	f	t	t	2025-10-26 06:31:31.683128+00	\N
380	1	8	7	Ермекеево	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
381	1	8	7	Ермолаево	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
382	1	8	7	Зилаир	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
383	1	8	7	Зирган	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
384	1	8	7	Иглино	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
385	1	8	7	Инзер	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
386	1	8	7	Исянгулово	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
387	1	8	7	Ишимбай	66259	f	t	t	2025-10-26 06:31:31.683128+00	\N
388	1	8	7	Калтасы	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
389	1	8	7	Кананикольское	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
390	1	8	7	Кандры	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
391	1	8	7	Караидель	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
392	1	8	7	Караидельский	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
393	1	8	7	Киргиз-Мияки	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
394	1	8	7	Красноусольский	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
395	1	8	7	Кумертау	62854	f	f	t	2025-10-26 06:31:31.683128+00	\N
396	1	8	7	Кушнаренково	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
397	1	8	7	Малояз	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
398	1	8	7	Межгорье	17353	f	f	t	2025-10-26 06:31:31.683128+00	\N
399	1	8	7	Мелеуз	61408	f	t	t	2025-10-26 06:31:31.683128+00	\N
400	1	8	7	Месягутово	0	f	f	t	2025-10-26 06:31:31.683128+00	\N
401	1	8	7	Мраково	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
402	1	8	7	Нефтекамск	121757	f	f	t	2025-10-26 06:31:31.709417+00	\N
403	1	8	7	Октябрьский (Башкирия	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
404	1	8	7	Приютово	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
405	1	8	7	Раевский	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
406	1	8	7	Салават	156085	f	f	t	2025-10-26 06:31:31.709417+00	\N
407	1	8	7	Сибай	62732	f	f	t	2025-10-26 06:31:31.709417+00	\N
408	1	8	7	Старобалтачево	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
409	1	8	7	Старосубхангулово	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
410	1	8	7	Стерлибашево	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
411	1	8	7	Стерлитамак	273432	f	t	t	2025-10-26 06:31:31.709417+00	\N
412	1	8	7	Туймазы	66849	f	t	t	2025-10-26 06:31:31.709417+00	\N
413	1	8	7	Уфа	1062300	t	f	t	2025-10-26 06:31:31.709417+00	\N
414	1	8	7	Учалы	37771	f	t	t	2025-10-26 06:31:31.709417+00	\N
415	1	8	7	Федоровка (Башкирия	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
416	1	8	7	Чекмагуш	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
417	1	8	7	Чишмы	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
418	1	8	7	Шаран	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
419	1	8	7	Янаул	26988	f	t	t	2025-10-26 06:31:31.709417+00	\N
420	1	9	1	Алексеевка (Белгородская обл.	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
421	1	9	1	Белгород	356426	f	f	t	2025-10-26 06:31:31.709417+00	\N
422	1	9	1	Борисовка	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
423	1	9	1	Валуйки	35322	f	t	t	2025-10-26 06:31:31.709417+00	\N
424	1	9	1	Вейделевка	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
425	1	9	1	Волоконовка	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
426	1	9	1	Грайворон	6234	f	t	t	2025-10-26 06:31:31.709417+00	\N
427	1	9	1	Губкин	88562	f	t	t	2025-10-26 06:31:31.709417+00	\N
428	1	9	1	Ивня	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
429	1	9	1	Короча	5877	f	t	t	2025-10-26 06:31:31.709417+00	\N
430	1	9	1	Красногвардейское (Белгород.	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
431	1	9	1	Новый Оскол	19530	f	t	t	2025-10-26 06:31:31.709417+00	\N
432	1	9	1	Ракитное	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
433	1	9	1	Ровеньки	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
434	1	9	1	Старый Оскол	221163	f	t	t	2025-10-26 06:31:31.709417+00	\N
435	1	9	1	Строитель	23933	f	t	t	2025-10-26 06:31:31.709417+00	\N
436	1	9	1	Чернянка	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
437	1	9	1	Шебекино	44277	f	t	t	2025-10-26 06:31:31.709417+00	\N
438	1	10	1	Алтухово	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
439	1	10	1	Белая Березка	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
440	1	10	1	Белые Берега	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
441	1	10	1	Большое Полпино	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
442	1	10	1	Брянск	415640	f	f	t	2025-10-26 06:31:31.709417+00	\N
443	1	10	1	Бытошь	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
444	1	10	1	Выгоничи	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
445	1	10	1	Вышков	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
446	1	10	1	Гордеевка	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
447	1	10	1	Дубровка (Брянская обл.	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
448	1	10	1	Дятьково	29438	f	t	t	2025-10-26 06:31:31.709417+00	\N
449	1	10	1	Жирятино	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
450	1	10	1	Злынка	5507	f	t	t	2025-10-26 06:31:31.709417+00	\N
451	1	10	1	Ивот	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
452	1	10	1	Карачев	19715	f	t	t	2025-10-26 06:31:31.709417+00	\N
453	1	10	1	Клетня	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
454	1	10	1	Климово	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
455	1	10	1	Клинцы	62510	f	f	t	2025-10-26 06:31:31.709417+00	\N
456	1	10	1	Кокаревка	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
457	1	10	1	Комаричи	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
458	1	10	1	Красная Гора	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
459	1	10	1	Локоть (Брянская обл.	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
460	1	10	1	Мглин	7916	f	t	t	2025-10-26 06:31:31.709417+00	\N
461	1	10	1	Навля	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
462	1	10	1	Новозыбков	40552	f	f	t	2025-10-26 06:31:31.709417+00	\N
463	1	10	1	Погар	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
464	1	10	1	Почеп	17933	f	t	t	2025-10-26 06:31:31.709417+00	\N
465	1	10	1	Ржаница	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
466	1	10	1	Рогнедино	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
467	1	10	1	Севск	7282	f	t	t	2025-10-26 06:31:31.709417+00	\N
468	1	10	1	Стародуб	19010	f	t	t	2025-10-26 06:31:31.709417+00	\N
469	1	10	1	Суземка	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
470	1	10	1	Сураж	11640	f	t	t	2025-10-26 06:31:31.709417+00	\N
471	1	10	1	Трубчевск	15014	f	t	t	2025-10-26 06:31:31.709417+00	\N
472	1	10	1	Унеча	26196	f	t	t	2025-10-26 06:31:31.709417+00	\N
473	1	11	5	Бабушкин	4542	f	f	t	2025-10-26 06:31:31.709417+00	\N
474	1	11	5	Багдарин	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
475	1	11	5	Баргузин	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
476	1	11	5	Баянгол	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
477	1	11	5	Бичура	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
478	1	11	5	Выдрино	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
479	1	11	5	Гусиное Озеро	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
480	1	11	5	Гусиноозерск	23280	f	t	t	2025-10-26 06:31:31.709417+00	\N
481	1	11	5	Заиграево	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
482	1	11	5	Закаменск	11249	f	t	t	2025-10-26 06:31:31.709417+00	\N
483	1	11	5	Иволгинск	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
484	1	11	5	Илька	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
485	1	11	5	Кабанск	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
486	1	11	5	Каменск	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
487	1	11	5	Кижинга	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
488	1	11	5	Курумкан	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
489	1	11	5	Кырен	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
490	1	11	5	Кяхта	20013	f	t	t	2025-10-26 06:31:31.709417+00	\N
491	1	11	5	Монды	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
492	1	11	5	Мухоршибирь	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
493	1	11	5	Нижнеангарск	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
494	1	11	5	Орлик	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
495	1	11	5	Петропавловка (Бурятия	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
496	1	11	5	Романовка (Бурятия	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
497	1	11	5	Северобайкальск (Бурятия	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
498	1	11	5	Селенгинск	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
499	1	11	5	Сосново-Озерское	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
500	1	11	5	Таксимо (Бурятия	0	f	f	t	2025-10-26 06:31:31.709417+00	\N
501	1	11	5	Турунтаево	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
502	1	11	5	Улан-Удэ	431922	f	f	t	2025-10-26 06:31:31.734968+00	\N
503	1	11	5	Хоринск	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
504	1	12	1	Александров	61544	f	t	t	2025-10-26 06:31:31.734968+00	\N
505	1	12	1	Андреево	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
506	1	12	1	Анопино	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
507	1	12	1	Бавлены	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
508	1	12	1	Балакирево	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
509	1	12	1	Боголюбово	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
510	1	12	1	Великодворский	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
511	1	12	1	Вербовский	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
512	1	12	1	Владимир	348256	f	f	t	2025-10-26 06:31:31.734968+00	\N
513	1	12	1	Вязники	41252	f	t	t	2025-10-26 06:31:31.734968+00	\N
514	1	12	1	Городищи (Владимирская обл.	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
515	1	12	1	Гороховец	14015	f	t	t	2025-10-26 06:31:31.734968+00	\N
516	1	12	1	Гусевский	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
517	1	12	1	Гусь Хрустальный	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
518	1	12	1	Гусь-Хрустальный	60773	f	f	t	2025-10-26 06:31:31.734968+00	\N
519	1	12	1	Золотково	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
520	1	12	1	Иванищи	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
521	1	12	1	Камешково	13113	f	t	t	2025-10-26 06:31:31.734968+00	\N
522	1	12	1	Карабаново	14868	f	f	t	2025-10-26 06:31:31.734968+00	\N
523	1	12	1	Киржач	30044	f	t	t	2025-10-26 06:31:31.734968+00	\N
524	1	12	1	Ковров	145492	f	f	t	2025-10-26 06:31:31.734968+00	\N
525	1	12	1	Кольчугино	45804	f	t	t	2025-10-26 06:31:31.734968+00	\N
526	1	12	1	Красная Горбатка	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
527	1	12	1	Лакинск	15707	f	f	t	2025-10-26 06:31:31.734968+00	\N
528	1	12	1	Меленки	15208	f	t	t	2025-10-26 06:31:31.734968+00	\N
529	1	12	1	Муром	116078	f	f	t	2025-10-26 06:31:31.734968+00	\N
530	1	12	1	Петушки	15167	f	t	t	2025-10-26 06:31:31.734968+00	\N
531	1	12	1	Покров	17762	f	f	t	2025-10-26 06:31:31.734968+00	\N
532	1	12	1	Радужный (Владимирская обл.	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
533	1	12	1	Собинка	19482	f	t	t	2025-10-26 06:31:31.734968+00	\N
534	1	12	1	Судогда	11848	f	t	t	2025-10-26 06:31:31.734968+00	\N
535	1	12	1	Суздаль	10535	f	t	t	2025-10-26 06:31:31.734968+00	\N
536	1	12	1	Юрьев-Польский	19588	f	t	t	2025-10-26 06:31:31.734968+00	\N
537	1	13	3	Алексеевская	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
538	1	13	3	Алущевск	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
539	1	13	3	Быково (Волгоградская обл.	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
540	1	13	3	Волгоград	1021244	t	f	t	2025-10-26 06:31:31.734968+00	\N
541	1	13	3	Волжский (Волгоградская обл.	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
542	1	13	3	Городище (Волгоградская обл.	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
543	1	13	3	Дубовка (Волгоградская обл.	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
544	1	13	3	Елань	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
545	1	13	3	Жирновск	16890	f	t	t	2025-10-26 06:31:31.734968+00	\N
546	1	13	3	Иловля	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
547	1	13	3	Калач-на-Дону	26892	f	t	t	2025-10-26 06:31:31.734968+00	\N
548	1	13	3	Камышин	119924	f	f	t	2025-10-26 06:31:31.734968+00	\N
549	1	14	2	Кириллов	7735	f	t	t	2025-10-26 06:31:31.734968+00	\N
550	1	13	3	Клетский	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
551	1	13	3	Котельниково	20441	f	t	t	2025-10-26 06:31:31.734968+00	\N
552	1	13	3	Котово	24104	f	t	t	2025-10-26 06:31:31.734968+00	\N
553	1	13	3	Кумылженская	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
554	1	13	3	Ленинск	15527	f	t	t	2025-10-26 06:31:31.734968+00	\N
555	1	13	3	Михайловка	59153	f	f	t	2025-10-26 06:31:31.734968+00	\N
556	1	13	3	Нехаевский	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
557	1	13	3	Николаевск	15081	f	t	t	2025-10-26 06:31:31.734968+00	\N
558	1	13	3	Новоаннинский	17911	f	t	t	2025-10-26 06:31:31.734968+00	\N
559	1	13	3	Новониколаевский	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
560	1	13	3	Ольховка	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
561	1	13	3	Палласовка (Волгоградская обл.	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
562	1	13	3	Рудня (Волгоградская обл.	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
563	1	13	3	Светлый Яр	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
564	1	13	3	Серафимович	9368	f	t	t	2025-10-26 06:31:31.734968+00	\N
565	1	13	3	Средняя Ахтуба	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
566	1	13	3	Сталинград	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
567	1	13	3	Старая Полтавка	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
568	1	13	3	Суровикино	20527	f	t	t	2025-10-26 06:31:31.734968+00	\N
569	1	13	3	Урюпинск	41594	f	f	t	2025-10-26 06:31:31.734968+00	\N
570	1	13	3	Фролово	39489	f	f	t	2025-10-26 06:31:31.734968+00	\N
571	1	13	3	Чернышковский	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
572	1	14	2	Бабаево	12074	f	t	t	2025-10-26 06:31:31.734968+00	\N
573	1	14	2	Белозерск	9614	f	t	t	2025-10-26 06:31:31.734968+00	\N
574	1	14	2	Великий Устюг	31664	f	t	t	2025-10-26 06:31:31.734968+00	\N
575	1	14	2	Верховажье	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
576	1	14	2	Вожега	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
577	1	14	2	Вологда	301642	f	f	t	2025-10-26 06:31:31.734968+00	\N
578	1	14	2	Вохтога	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
579	1	14	2	Вытегра	10490	f	t	t	2025-10-26 06:31:31.734968+00	\N
580	1	14	2	Грязовец	15528	f	t	t	2025-10-26 06:31:31.734968+00	\N
581	1	14	2	Кадников	4797	f	f	t	2025-10-26 06:31:31.734968+00	\N
582	1	14	2	Кадуй	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
583	1	14	2	Кичменгский Городок	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
584	1	14	2	Липин Бор	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
585	1	14	2	Никольск	22471	f	t	t	2025-10-26 06:31:31.734968+00	\N
586	1	14	2	Нюксеница	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
587	1	14	2	Сокол	38454	f	t	t	2025-10-26 06:31:31.734968+00	\N
588	1	14	2	Сямжа	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
589	1	14	2	Тарногский Городок	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
590	1	14	2	Тотьма	9784	f	t	t	2025-10-26 06:31:31.734968+00	\N
591	1	14	2	Устюжна	9478	f	t	t	2025-10-26 06:31:31.734968+00	\N
592	1	14	2	Харовск	10078	f	t	t	2025-10-26 06:31:31.734968+00	\N
593	1	14	2	Чагода	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
594	1	14	2	Череповец	312311	f	f	t	2025-10-26 06:31:31.734968+00	\N
595	1	14	2	Шексна	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
596	1	14	2	Шуйское	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
597	1	15	1	Анна	0	f	f	t	2025-10-26 06:31:31.734968+00	\N
598	1	15	1	Бобров	19738	f	t	t	2025-10-26 06:31:31.734968+00	\N
599	1	15	1	Богучар	11811	f	t	t	2025-10-26 06:31:31.734968+00	\N
600	1	15	1	Борисоглебск	65585	f	t	t	2025-10-26 06:31:31.734968+00	\N
601	1	15	1	Бутурлиновка	27208	f	t	t	2025-10-26 06:31:31.760771+00	\N
602	1	15	1	Верхний Мамон	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
603	1	15	1	Верхняя Хава	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
604	1	15	1	Воробьевка	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
605	1	15	1	Воронеж	889680	f	f	t	2025-10-26 06:31:31.760771+00	\N
606	1	15	1	Грибановский	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
607	1	15	1	Давыдовка	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
608	1	15	1	Елань-Коленовский	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
609	1	15	1	Калач	20046	f	t	t	2025-10-26 06:31:31.760771+00	\N
610	1	15	1	Кантемировка	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
611	1	15	1	Лиски (Воронежская обл.	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
612	1	15	1	Нижнедевицк	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
613	1	15	1	Новая Усмань	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
614	1	15	1	Нововоронеж	32635	f	f	t	2025-10-26 06:31:31.760771+00	\N
615	1	15	1	Новохоперск	6849	f	t	t	2025-10-26 06:31:31.760771+00	\N
616	1	15	1	Ольховатка	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
617	1	15	1	Острогожск	33842	f	t	t	2025-10-26 06:31:31.760771+00	\N
618	1	15	1	Павловск (Воронежская обл.	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
619	1	15	1	Панино	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
620	1	15	1	Петропавловка	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
621	1	15	1	Поворино	17692	f	t	t	2025-10-26 06:31:31.760771+00	\N
622	1	15	1	Подгоренский	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
623	1	15	1	Рамонь	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
624	1	15	1	Репьевка	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
625	1	15	1	Россошь	62865	f	t	t	2025-10-26 06:31:31.760771+00	\N
626	1	15	1	Семилуки	26025	f	t	t	2025-10-26 06:31:31.760771+00	\N
627	1	15	1	Таловая	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
628	1	15	1	Терновка	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
629	1	15	1	Хохольский	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
630	1	15	1	Эртиль	11387	f	t	t	2025-10-26 06:31:31.760771+00	\N
631	1	16	8	Агвали	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
632	1	16	8	Акуша	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
633	1	16	8	Ахты	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
634	1	16	8	Ачису	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
635	1	16	8	Бабаюрт	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
636	1	16	8	Бежта	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
637	1	16	8	Ботлих	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
638	1	16	8	Буйнакск	65735	f	f	t	2025-10-26 06:31:31.760771+00	\N
639	1	16	8	Вачи	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
640	1	16	8	Гергебиль	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
641	1	16	8	Гуниб	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
642	1	16	8	Дагестанские Огни	30671	f	f	t	2025-10-26 06:31:31.760771+00	\N
643	1	16	8	Дербент	119961	f	f	t	2025-10-26 06:31:31.760771+00	\N
644	1	16	8	Дылым	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
645	1	16	8	Ершовка	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
646	1	16	8	Избербаш	56301	f	f	t	2025-10-26 06:31:31.760771+00	\N
647	1	16	8	Карабудахкент	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
648	1	16	8	Карата	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
649	1	16	8	Каспийск	103914	f	f	t	2025-10-26 06:31:31.760771+00	\N
650	1	16	8	Касумкент	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
651	1	16	8	Кизилюрт	36187	f	f	t	2025-10-26 06:31:31.760771+00	\N
652	1	16	8	Кизляр	49169	f	f	t	2025-10-26 06:31:31.760771+00	\N
653	1	16	8	Кочубей	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
654	1	16	8	Кумух	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
655	1	16	8	Курах	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
656	1	16	8	Магарамкент	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
657	1	16	8	Маджалис	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
658	1	16	8	Махачкала	577990	f	f	t	2025-10-26 06:31:31.760771+00	\N
659	1	16	8	Мехельта	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
660	1	16	8	Новолакское	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
661	1	16	8	Рутул	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
662	1	16	8	Советское (Дагестан	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
663	1	16	8	Тарумовка	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
664	1	16	8	Терекли-Мектеб	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
665	1	16	8	Тлярата	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
666	1	16	8	Тпиг	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
667	1	16	8	Унцукуль	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
668	1	16	8	Уркарах	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
669	1	16	8	Хасавюрт	133929	f	f	t	2025-10-26 06:31:31.760771+00	\N
670	1	16	8	Хив	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
671	1	16	8	Хунзах	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
672	1	16	8	Цуриб	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
673	1	16	8	Южно-Сухокумск	10048	f	f	t	2025-10-26 06:31:31.760771+00	\N
674	1	17	4	Биробиджан	75419	f	f	t	2025-10-26 06:31:31.760771+00	\N
675	1	18	1	Архиповка	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
676	1	18	1	Верхний Ландех	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
677	1	18	1	Вичуга	37609	f	t	t	2025-10-26 06:31:31.760771+00	\N
678	1	18	1	Гаврилов Посад	6434	f	t	t	2025-10-26 06:31:31.760771+00	\N
679	1	18	1	Долматовский	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
680	1	18	1	Дуляпино	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
681	1	18	1	Заволжск	12045	f	t	t	2025-10-26 06:31:31.760771+00	\N
682	1	18	1	Заречный (Ивановская обл.	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
683	1	18	1	Иваново	409277	f	f	t	2025-10-26 06:31:31.760771+00	\N
684	1	18	1	Иваньковский	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
685	1	18	1	Ильинское-Хованское	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
686	1	18	1	Каминский	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
687	1	18	1	Кинешма	88113	f	f	t	2025-10-26 06:31:31.760771+00	\N
688	1	18	1	Комсомольск	8693	f	t	t	2025-10-26 06:31:31.760771+00	\N
689	1	18	1	Кохма	29408	f	t	t	2025-10-26 06:31:31.760771+00	\N
690	1	18	1	Лух	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
691	1	18	1	Палех	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
692	1	18	1	Пестяки	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
693	1	18	1	Приволжск	16749	f	t	t	2025-10-26 06:31:31.760771+00	\N
694	1	18	1	Пучеж	8583	f	t	t	2025-10-26 06:31:31.760771+00	\N
695	1	18	1	Родники (Ивановская обл.	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
696	1	18	1	Савино	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
697	1	18	1	Сокольское	0	f	f	t	2025-10-26 06:31:31.760771+00	\N
698	1	18	1	Тейково	34993	f	t	t	2025-10-26 06:31:31.760771+00	\N
699	1	18	1	Фурманов	36149	f	t	t	2025-10-26 06:31:31.760771+00	\N
700	1	18	1	Шуя	58528	f	t	t	2025-10-26 06:31:31.760771+00	\N
701	1	18	1	Южа	14170	f	t	t	2025-10-26 06:31:31.790252+00	\N
702	1	18	1	Юрьевец	10205	f	t	t	2025-10-26 06:31:31.790252+00	\N
703	1	19	5	Алексеевск	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
704	1	19	5	Алзамай	6751	f	f	t	2025-10-26 06:31:31.790252+00	\N
705	1	19	5	Алыгжер	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
706	1	19	5	Ангарск	233765	f	f	t	2025-10-26 06:31:31.790252+00	\N
707	1	19	5	Артемовский (Иркутская обл.	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
708	1	19	5	Байкал	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
709	1	19	5	Байкальск	13589	f	f	t	2025-10-26 06:31:31.790252+00	\N
710	1	19	5	Балаганск	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
711	1	19	5	Баяндай	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
712	1	19	5	Бирюсинск	8981	f	f	t	2025-10-26 06:31:31.790252+00	\N
713	1	19	5	Бодайбо	15331	f	f	t	2025-10-26 06:31:31.790252+00	\N
714	1	19	5	Большая Речка	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
715	1	19	5	Большой Луг	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
716	1	19	5	Бохан	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
717	1	19	5	Братск	246348	f	f	t	2025-10-26 06:31:31.790252+00	\N
718	1	19	5	Видим	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
719	1	19	5	Витимский	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
720	1	19	5	Вихоревка	22528	f	f	t	2025-10-26 06:31:31.790252+00	\N
721	1	19	5	Еланцы	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
722	1	19	5	Ербогачен	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
723	1	19	5	Железногорск-Илимский	26134	f	t	t	2025-10-26 06:31:31.790252+00	\N
724	1	19	5	Жигалово	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
725	1	19	5	Забитуй	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
726	1	19	5	Залари	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
727	1	19	5	Звездный	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
728	1	19	5	Зима	32522	f	f	t	2025-10-26 06:31:31.790252+00	\N
729	1	19	5	Иркутск	587225	f	f	t	2025-10-26 06:31:31.790252+00	\N
730	1	19	5	Казачинское (Иркутская обл.	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
731	1	19	5	Качуг	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
732	1	19	5	Квиток	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
733	1	19	5	Киренск	12652	f	t	t	2025-10-26 06:31:31.790252+00	\N
734	1	19	5	Куйтун	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
735	1	19	5	Култук	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
736	1	19	5	Кутулик	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
737	1	19	5	Мама	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
738	1	19	5	Нижнеудинск	37056	f	f	t	2025-10-26 06:31:31.790252+00	\N
739	1	46	7	Оса	22420	f	t	t	2025-10-26 06:31:31.790252+00	\N
740	1	19	5	Саянск	40786	f	f	t	2025-10-26 06:31:31.790252+00	\N
741	1	19	5	Слюдянка	18542	f	t	t	2025-10-26 06:31:31.790252+00	\N
742	1	19	5	Тайшет	35481	f	f	t	2025-10-26 06:31:31.790252+00	\N
743	1	19	5	Тулун	44603	f	f	t	2025-10-26 06:31:31.790252+00	\N
744	1	19	5	Усолье-Сибирское (Иркутская обл.	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
745	1	19	5	Усть-Илимск	86591	f	f	t	2025-10-26 06:31:31.790252+00	\N
746	1	19	5	Усть-Кут	45061	f	f	t	2025-10-26 06:31:31.790252+00	\N
747	1	19	5	Усть-Ордынский	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
748	1	19	5	Усть-Уда	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
749	1	19	5	Черемхово	52650	f	f	t	2025-10-26 06:31:31.790252+00	\N
750	1	19	5	Чунский	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
751	1	19	5	Шелехов	47960	f	f	t	2025-10-26 06:31:31.790252+00	\N
752	1	20	1	Баксан	36857	f	t	t	2025-10-26 06:31:31.790252+00	\N
753	1	20	1	Майский	26755	f	t	t	2025-10-26 06:31:31.790252+00	\N
754	1	20	1	Нальчик	240095	f	f	t	2025-10-26 06:31:31.790252+00	\N
755	1	20	1	Нарткала	31679	f	t	t	2025-10-26 06:31:31.790252+00	\N
756	1	20	1	Прохладный	59595	f	f	t	2025-10-26 06:31:31.790252+00	\N
757	1	20	1	Советское (Кабардино-Балкария	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
758	1	20	1	Терек	19170	f	t	t	2025-10-26 06:31:31.790252+00	\N
759	1	20	1	Тырныауз	21000	f	t	t	2025-10-26 06:31:31.790252+00	\N
760	1	20	1	Чегем-Первый	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
761	1	21	2	Багратионовск	6399	f	t	t	2025-10-26 06:31:31.790252+00	\N
762	1	21	2	Балтийск	32670	f	t	t	2025-10-26 06:31:31.790252+00	\N
763	1	21	2	Гвардейск	13888	f	t	t	2025-10-26 06:31:31.790252+00	\N
764	1	21	2	Гурьевск (Калининградская обл.	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
765	1	21	2	Гусев	28260	f	t	t	2025-10-26 06:31:31.790252+00	\N
766	1	21	2	Железнодорожный (Калининград.	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
767	1	21	2	Зеленоградск	13015	f	t	t	2025-10-26 06:31:31.790252+00	\N
768	1	21	2	Знаменск	29357	f	f	t	2025-10-26 06:31:31.790252+00	\N
769	1	21	2	Калининград (Кенигсберг	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
770	1	21	2	Краснознаменск (Калининград.	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
771	1	21	2	Ладушкин	3788	f	f	t	2025-10-26 06:31:31.790252+00	\N
772	1	21	2	Мамоново	7757	f	f	t	2025-10-26 06:31:31.790252+00	\N
773	1	21	2	Неман	11794	f	t	t	2025-10-26 06:31:31.790252+00	\N
774	1	21	2	Нестеров	4584	f	t	t	2025-10-26 06:31:31.790252+00	\N
775	1	21	2	Озерск(Калининградская обл.	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
776	1	21	2	Пионерск	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
777	1	21	2	Полесск	7580	f	t	t	2025-10-26 06:31:31.790252+00	\N
778	1	21	2	Правдинск	4323	f	t	t	2025-10-26 06:31:31.790252+00	\N
779	1	21	2	Светлогорск	10775	f	t	t	2025-10-26 06:31:31.790252+00	\N
780	1	21	2	Светлый (Калининградская обл.	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
781	1	21	2	Славск	4614	f	t	t	2025-10-26 06:31:31.790252+00	\N
782	1	21	2	Советск (Калининградская обл.	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
783	1	21	2	Черняховск	40464	f	t	t	2025-10-26 06:31:31.790252+00	\N
784	1	22	3	Аршань	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
785	1	22	3	Городовиковск	9565	f	t	t	2025-10-26 06:31:31.790252+00	\N
786	1	22	3	Каспийский	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
787	1	22	3	Комсомольский (Калмыкия	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
788	1	22	3	Малые Дербеты	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
789	1	22	3	Приютное	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
790	1	22	3	Советское (Калмыкия	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
791	1	22	3	Троицкое (Калмыкия	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
792	1	22	3	Утта	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
793	1	22	3	Цаган-Аман	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
794	1	22	3	Элиста	103728	f	f	t	2025-10-26 06:31:31.790252+00	\N
795	1	22	3	Юста	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
796	1	22	3	Яшалта	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
797	1	22	3	Яшкуль	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
798	1	23	1	Бабынино	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
799	1	23	1	Балабаново	26337	f	f	t	2025-10-26 06:31:31.790252+00	\N
800	1	23	1	Барятино	0	f	f	t	2025-10-26 06:31:31.790252+00	\N
801	1	23	1	Белоусово	8432	f	f	t	2025-10-26 06:31:31.815805+00	\N
802	1	23	1	Бетлица	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
803	1	23	1	Боровск	12283	f	t	t	2025-10-26 06:31:31.815805+00	\N
804	1	23	1	Дудоровский	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
805	1	23	1	Думиничи	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
806	1	23	1	Еленский	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
807	1	23	1	Жиздра	5585	f	t	t	2025-10-26 06:31:31.815805+00	\N
808	1	23	1	Жуков	12150	f	t	t	2025-10-26 06:31:31.815805+00	\N
809	1	23	1	Износки	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
810	1	23	1	Калуга	325185	f	f	t	2025-10-26 06:31:31.815805+00	\N
811	1	23	1	Киров (Калужская обл.	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
812	1	23	1	Козельск	18203	f	t	t	2025-10-26 06:31:31.815805+00	\N
813	1	23	1	Кондрово	16672	f	t	t	2025-10-26 06:31:31.815805+00	\N
814	1	23	1	Кремёнки	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
815	1	23	1	Людиново	40550	f	t	t	2025-10-26 06:31:31.815805+00	\N
816	1	23	1	Малоярославец	30401	f	t	t	2025-10-26 06:31:31.815805+00	\N
817	1	23	1	Медынь	8298	f	t	t	2025-10-26 06:31:31.815805+00	\N
818	1	23	1	Мещовск	4101	f	t	t	2025-10-26 06:31:31.815805+00	\N
819	1	23	1	Мосальск	4285	f	t	t	2025-10-26 06:31:31.815805+00	\N
820	1	23	1	Обнинск	104798	f	f	t	2025-10-26 06:31:31.815805+00	\N
821	1	23	1	Перемышль	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
822	1	23	1	Спас-Деменск	4904	f	t	t	2025-10-26 06:31:31.815805+00	\N
823	1	23	1	Сухиничи	16295	f	t	t	2025-10-26 06:31:31.815805+00	\N
824	1	23	1	Таруса	9656	f	f	t	2025-10-26 06:31:31.815805+00	\N
825	1	23	1	Ульяново	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
826	1	23	1	Ферзиково	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
827	1	23	1	Хвастовичи	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
828	1	23	1	Юхнов	7056	f	t	t	2025-10-26 06:31:31.815805+00	\N
829	1	24	1	Атласово	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
830	1	24	1	Аянка	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
831	1	24	1	Большерецк	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
832	1	24	1	Вилючинск	22905	f	f	t	2025-10-26 06:31:31.815805+00	\N
833	1	24	1	Елизово (Камчатская обл.	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
834	1	24	1	Ильпырский	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
835	1	24	1	Каменское	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
836	1	47	4	Кировский	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
837	1	24	1	Ключи (Камчатская обл.	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
838	1	24	1	Крапивная	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
839	1	24	1	Мильково	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
840	1	24	1	Никольское	19345	f	f	t	2025-10-26 06:31:31.815805+00	\N
841	1	24	1	Озерновский	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
842	1	24	1	Оссора	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
843	1	24	1	Палана	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
844	1	24	1	Парень	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
845	1	24	1	Пахачи	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
846	1	24	1	Петропавловск-Камчатский	179526	f	f	t	2025-10-26 06:31:31.815805+00	\N
847	1	24	1	Тигиль	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
848	1	24	1	Тиличики	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
849	1	24	1	Усть-Большерецк	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
850	1	24	1	Усть-Камчатск	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
851	1	25	2	Амбарный	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
852	1	25	2	Беломорск	11217	f	t	t	2025-10-26 06:31:31.815805+00	\N
853	1	25	2	Валаам	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
854	1	25	2	Вирандозеро	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
855	1	25	2	Гирвас	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
856	1	25	2	Деревянка	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
857	1	25	2	Идель	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
858	1	25	2	Ильинский (Карелия	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
859	1	25	2	Калевала	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
860	1	25	2	Кемь	13061	f	f	t	2025-10-26 06:31:31.815805+00	\N
861	1	25	2	Кестеньга	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
862	1	25	2	Кондопога	32978	f	t	t	2025-10-26 06:31:31.815805+00	\N
863	1	25	2	Костомукша	28433	f	f	t	2025-10-26 06:31:31.815805+00	\N
864	1	25	2	Лахденпохья	7818	f	t	t	2025-10-26 06:31:31.815805+00	\N
865	1	25	2	Лоухи	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
866	1	25	2	Медвежьегорск	15536	f	t	t	2025-10-26 06:31:31.815805+00	\N
867	1	25	2	Муезерский	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
868	1	25	2	Олонец	9060	f	t	t	2025-10-26 06:31:31.815805+00	\N
869	1	25	2	Петрозаводск	263540	f	f	t	2025-10-26 06:31:31.815805+00	\N
870	1	25	2	Питкяранта	11484	f	t	t	2025-10-26 06:31:31.815805+00	\N
871	1	25	2	Повенец	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
872	1	25	2	Пряжа	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
873	1	25	2	Пудож	9698	f	t	t	2025-10-26 06:31:31.815805+00	\N
874	1	25	2	Сегежа	29660	f	t	t	2025-10-26 06:31:31.815805+00	\N
875	1	25	2	Сортавала	19215	f	f	t	2025-10-26 06:31:31.815805+00	\N
876	1	25	2	Суоярви	9763	f	t	t	2025-10-26 06:31:31.815805+00	\N
877	1	25	2	Хийденсельга	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
878	1	26	5	Анжеро-Судженск	76669	f	f	t	2025-10-26 06:31:31.815805+00	\N
879	1	26	5	Барзас	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
880	1	26	5	Белово	76752	f	f	t	2025-10-26 06:31:31.815805+00	\N
881	1	26	5	Березовский (Кемеровская обл.	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
882	1	26	5	Грамотеино	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
883	1	26	5	Гурьевск	24816	f	t	t	2025-10-26 06:31:31.815805+00	\N
884	1	26	5	Ижморский	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
885	1	26	5	Итатский	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
886	1	26	5	Калтан	21893	f	f	t	2025-10-26 06:31:31.815805+00	\N
887	1	26	5	Кедровка	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
888	1	26	5	Кемерово	532884	f	f	t	2025-10-26 06:31:31.815805+00	\N
889	1	26	5	Киселевск	98382	f	f	t	2025-10-26 06:31:31.815805+00	\N
890	1	26	5	Крапивинский	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
891	1	26	5	Ленинск-Кузнецкий	101666	f	f	t	2025-10-26 06:31:31.815805+00	\N
892	1	26	5	Мариинск	40522	f	t	t	2025-10-26 06:31:31.815805+00	\N
893	1	26	5	Междуреченск	101995	f	f	t	2025-10-26 06:31:31.815805+00	\N
894	1	26	5	Мыски	43029	f	f	t	2025-10-26 06:31:31.815805+00	\N
895	1	26	5	Новокузнецк	547885	f	f	t	2025-10-26 06:31:31.815805+00	\N
896	1	26	5	Осинники	45997	f	f	t	2025-10-26 06:31:31.815805+00	\N
897	1	26	5	Полысаево	27624	f	f	t	2025-10-26 06:31:31.815805+00	\N
898	1	26	5	Прокопьевск	210150	f	f	t	2025-10-26 06:31:31.815805+00	\N
899	1	26	5	Промышленная	0	f	f	t	2025-10-26 06:31:31.815805+00	\N
900	1	26	5	Тайга	25330	f	f	t	2025-10-26 06:31:31.815805+00	\N
901	1	26	5	Таштагол	23114	f	t	t	2025-10-26 06:31:31.841214+00	\N
902	1	26	5	Тисуль	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
903	1	26	5	Топки	28642	f	t	t	2025-10-26 06:31:31.841214+00	\N
904	1	26	5	Тяжинский	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
905	1	26	5	Юрга	81536	f	f	t	2025-10-26 06:31:31.841214+00	\N
906	1	26	5	Яшкино	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
907	1	26	5	Яя	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
908	1	27	7	Арбаж	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
909	1	27	7	Аркуль	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
910	1	27	7	Белая Холуница	11232	f	t	t	2025-10-26 06:31:31.841214+00	\N
911	1	27	7	Богородское (Кировская обл.	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
912	1	27	7	Боровой	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
913	1	27	7	Верхошижемье	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
914	1	27	7	Вятские Поляны (Кировская обл.	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
915	1	27	7	Зуевка	11198	f	t	t	2025-10-26 06:31:31.841214+00	\N
916	1	27	7	Каринторф	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
917	1	27	7	Кикнур	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
918	1	27	7	Кильмезь	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
919	1	27	7	Киров (Кировская обл.	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
920	1	27	7	Кирово-Чепецк	80920	f	t	t	2025-10-26 06:31:31.841214+00	\N
921	1	27	7	Кирс	10420	f	t	t	2025-10-26 06:31:31.841214+00	\N
922	1	27	7	Кобра	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
923	1	27	7	Котельнич	24979	f	t	t	2025-10-26 06:31:31.841214+00	\N
924	1	27	7	Кумены	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
925	1	69	4	Ленинское	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
926	1	27	7	Луза	11262	f	t	t	2025-10-26 06:31:31.841214+00	\N
927	1	27	7	Малмыж	8265	f	t	t	2025-10-26 06:31:31.841214+00	\N
928	1	27	7	Мураши	6752	f	t	t	2025-10-26 06:31:31.841214+00	\N
929	1	27	7	Нагорск	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
930	1	27	7	Нема	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
931	1	27	7	Нововятск	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
932	1	27	7	Нолинск	9556	f	t	t	2025-10-26 06:31:31.841214+00	\N
933	1	27	7	Омутнинск	23618	f	t	t	2025-10-26 06:31:31.841214+00	\N
934	1	27	7	Опарино	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
935	1	27	7	Оричи	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
936	1	27	7	Пижанка	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
937	1	27	7	Подосиновец	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
938	1	27	7	Санчурск	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
939	1	27	7	Свеча	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
940	1	27	7	Слободской	33983	f	t	t	2025-10-26 06:31:31.841214+00	\N
941	1	27	7	Советск (Кировская обл.	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
942	1	27	7	Суна	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
943	1	27	7	Тужа	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
944	1	27	7	Уни	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
945	1	27	7	Уржум	10213	f	t	t	2025-10-26 06:31:31.841214+00	\N
946	1	27	7	Фаленки	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
947	1	27	7	Халтурин	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
948	1	27	7	Юрья	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
949	1	27	7	Яранск	17252	f	t	t	2025-10-26 06:31:31.841214+00	\N
950	1	28	2	Абезь	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
951	1	28	2	Адзьвавом	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
952	1	28	2	Айкино	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
953	1	28	2	Верхняя Инта	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
954	1	28	2	Визинга	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
955	1	28	2	Водный	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
956	1	28	2	Воркута	70551	f	f	t	2025-10-26 06:31:31.841214+00	\N
957	1	28	2	Вуктыл	12357	f	f	t	2025-10-26 06:31:31.841214+00	\N
958	1	28	2	Елецкий	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
959	1	28	2	Емва	14574	f	t	t	2025-10-26 06:31:31.841214+00	\N
960	1	28	2	Жешарт	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
961	1	38	2	Заполярный	15835	f	f	t	2025-10-26 06:31:31.841214+00	\N
962	1	28	2	Ижма	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
963	1	28	2	Инта	32021	f	f	t	2025-10-26 06:31:31.841214+00	\N
964	1	28	2	Ираель	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
965	1	28	2	Каджером	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
966	1	28	2	Кажым	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
967	1	28	2	Кожым	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
968	1	28	2	Койгородок	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
969	1	28	2	Корткерос	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
970	1	28	2	Кослан	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
971	1	28	2	Микунь	10732	f	f	t	2025-10-26 06:31:31.841214+00	\N
972	1	28	2	Нижний Одес	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
973	1	28	2	Объячево	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
974	1	28	2	Печора	43458	f	f	t	2025-10-26 06:31:31.841214+00	\N
975	1	28	2	Сосногорск	27809	f	f	t	2025-10-26 06:31:31.841214+00	\N
976	1	28	2	Сыктывкар	235006	f	f	t	2025-10-26 06:31:31.841214+00	\N
977	1	28	2	Троицко-Печерск	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
978	1	28	2	Усинск	41100	f	f	t	2025-10-26 06:31:31.841214+00	\N
979	1	28	2	Усогорск	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
980	1	28	2	Усть-Кулом	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
981	1	28	2	Усть-Цильма	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
982	1	28	2	Ухта	99642	f	f	t	2025-10-26 06:31:31.841214+00	\N
983	1	29	1	Антропово	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
984	1	29	1	Боговарово	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
985	1	29	1	Буй	25763	f	t	t	2025-10-26 06:31:31.841214+00	\N
986	1	29	1	Волгореченск	17108	f	f	t	2025-10-26 06:31:31.841214+00	\N
987	1	29	1	Галич	17346	f	t	t	2025-10-26 06:31:31.841214+00	\N
988	1	29	1	Горчуха	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
989	1	29	1	Зебляки	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
990	1	29	1	Кадый	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
991	1	29	1	Кологрив	3314	f	t	t	2025-10-26 06:31:31.841214+00	\N
992	1	29	1	Кострома	268617	f	f	t	2025-10-26 06:31:31.841214+00	\N
993	1	29	1	Красное-на-Волге	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
994	1	29	1	Макарьев	7114	f	t	t	2025-10-26 06:31:31.841214+00	\N
995	1	33	1	Мантурово	17479	f	t	t	2025-10-26 06:31:31.841214+00	\N
996	1	29	1	Нерехта	22817	f	t	t	2025-10-26 06:31:31.841214+00	\N
997	1	29	1	Нея	9827	f	t	t	2025-10-26 06:31:31.841214+00	\N
998	1	29	1	Островское	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
999	1	29	1	Павино	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
1000	1	29	1	Парфентьево	0	f	f	t	2025-10-26 06:31:31.841214+00	\N
1001	1	29	1	Поназырево	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1002	1	29	1	Солигалич	6438	f	t	t	2025-10-26 06:31:31.87048+00	\N
1003	1	29	1	Судиславль	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1004	1	29	1	Сусанино	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1005	1	29	1	Чухлома	5209	f	t	t	2025-10-26 06:31:31.87048+00	\N
1006	1	29	1	Шарья	23668	f	t	t	2025-10-26 06:31:31.87048+00	\N
1007	1	29	1	Шемятино	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1008	1	30	3	Абинск	34926	f	t	t	2025-10-26 06:31:31.87048+00	\N
1009	1	30	3	Абрау-Дюрсо	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1010	1	30	3	Адлер	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1011	1	30	3	Анапа	58983	f	t	t	2025-10-26 06:31:31.87048+00	\N
1012	1	30	3	Апшеронск	40229	f	t	t	2025-10-26 06:31:31.87048+00	\N
1013	1	30	3	Армавир	188897	f	f	t	2025-10-26 06:31:31.87048+00	\N
1014	1	30	3	Архипо-Осиповка	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1015	1	30	3	Афипский	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1016	1	30	3	Ахтырский	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1017	1	30	3	Ачуево	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1018	1	30	3	Белая Глина	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1019	1	30	3	Белореченск	53891	f	t	t	2025-10-26 06:31:31.87048+00	\N
1020	1	30	3	Верхнебаканский	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1021	1	30	3	Выселки	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1022	1	30	3	Геленджик	54813	f	f	t	2025-10-26 06:31:31.87048+00	\N
1023	1	30	3	Гиагинская	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1024	1	30	3	Горячий Ключ	30093	f	f	t	2025-10-26 06:31:31.87048+00	\N
1025	1	30	3	Гулькевичи	35225	f	t	t	2025-10-26 06:31:31.87048+00	\N
1026	1	30	3	Джубга	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1027	1	30	3	Динская	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1028	1	30	3	Ейск	87771	f	t	t	2025-10-26 06:31:31.87048+00	\N
1029	1	30	3	Ильский	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1030	1	30	3	Кабардинка	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1031	1	30	3	Калинино	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1032	1	30	3	Калининская	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1033	1	30	3	Каменномостский	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1034	1	30	3	Каневская	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1035	1	30	3	Кореновск	41179	f	t	t	2025-10-26 06:31:31.87048+00	\N
1036	1	30	3	Красноармейская	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1037	1	30	3	Краснодар	744933	f	f	t	2025-10-26 06:31:31.87048+00	\N
1038	1	30	3	Кропоткин	80743	f	f	t	2025-10-26 06:31:31.87048+00	\N
1039	1	30	3	Крыловская	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1040	1	30	3	Крымск	57370	f	t	t	2025-10-26 06:31:31.87048+00	\N
1041	1	30	3	Курганинск	47974	f	t	t	2025-10-26 06:31:31.87048+00	\N
1042	1	30	3	Кущевская	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1043	1	30	3	Лабинск	62822	f	t	t	2025-10-26 06:31:31.87048+00	\N
1044	1	30	3	Лазаревское	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1045	1	30	3	Ленинградская	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1046	1	30	3	Майкоп (Краснодарский край	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1047	1	30	3	Мостовской	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1048	1	30	3	Новокубанск	34847	f	t	t	2025-10-26 06:31:31.87048+00	\N
1049	1	30	3	Новороссийск	241788	f	f	t	2025-10-26 06:31:31.87048+00	\N
1050	1	30	3	Отрадная	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1051	1	30	3	Павловская	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1052	1	30	3	Приморско-Ахтарск	32253	f	t	t	2025-10-26 06:31:31.87048+00	\N
1053	1	30	3	Северская	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1054	1	30	3	Славянск-на-Кубани	63768	f	t	t	2025-10-26 06:31:31.87048+00	\N
1055	1	30	3	Сочи	343285	f	f	t	2025-10-26 06:31:31.87048+00	\N
1056	1	30	3	Староминская	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1057	1	30	3	Старощербиновская	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1058	1	30	3	Тбилисская	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1059	1	30	3	Темрюк	38014	f	t	t	2025-10-26 06:31:31.87048+00	\N
1060	1	30	3	Тимашевск	53921	f	t	t	2025-10-26 06:31:31.87048+00	\N
1061	1	30	3	Тихорецк	61825	f	t	t	2025-10-26 06:31:31.87048+00	\N
1062	1	30	3	Туапсе	63233	f	t	t	2025-10-26 06:31:31.87048+00	\N
1063	1	30	3	Тульский	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1064	1	30	3	Усть-Лабинск	43268	f	t	t	2025-10-26 06:31:31.87048+00	\N
1065	1	30	3	Хадыженск	21580	f	f	t	2025-10-26 06:31:31.87048+00	\N
1066	1	30	3	Хоста	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1067	1	30	3	Шовгеновский	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1068	1	31	5	Абаза	17111	f	f	t	2025-10-26 06:31:31.87048+00	\N
1069	1	70	5	Абакан	165183	f	f	t	2025-10-26 06:31:31.87048+00	\N
1070	1	73	1	Агинское	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1071	1	31	5	Артемовск	2180	f	f	t	2025-10-26 06:31:31.87048+00	\N
1072	1	31	5	Аскиз	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1073	1	31	5	Ачинск	109156	f	f	t	2025-10-26 06:31:31.87048+00	\N
1074	1	31	5	Байкит	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1075	1	31	5	Балахта	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1076	1	31	5	Балыкса	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1077	1	62	5	Белый Яр	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1078	1	31	5	Бея	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1079	1	31	5	Бискамжа	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1080	1	31	5	Боготол	21029	f	f	t	2025-10-26 06:31:31.87048+00	\N
1081	1	31	5	Боград	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1082	1	31	5	Богучаны	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1083	1	31	5	Большая Мурта	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1084	1	31	5	Большой Улуй	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1085	1	31	5	Бородино (Красноярский край	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1086	1	31	5	Ванавара	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1087	1	31	5	Верхнеимбатск	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1088	1	31	5	Горячегорск	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1089	1	31	5	Дзержинское	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1090	1	31	5	Дивногорск	28271	f	f	t	2025-10-26 06:31:31.87048+00	\N
1091	1	31	5	Диксон	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1092	1	31	5	Дудинка	22207	f	t	t	2025-10-26 06:31:31.87048+00	\N
1093	1	31	5	Емельяново	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1094	1	31	5	Енисейск	18769	f	f	t	2025-10-26 06:31:31.87048+00	\N
1095	1	31	5	Ермаковское	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1096	1	33	1	Железногорск	95057	f	t	t	2025-10-26 06:31:31.87048+00	\N
1097	1	31	5	Заозерный	10683	f	f	t	2025-10-26 06:31:31.87048+00	\N
1098	1	31	5	Зеленогорск (Красноярский край	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1099	1	31	5	Игарка	6183	f	f	t	2025-10-26 06:31:31.87048+00	\N
1100	1	31	5	Идринское	0	f	f	t	2025-10-26 06:31:31.87048+00	\N
1101	1	31	5	Иланский	16108	f	t	t	2025-10-26 06:31:31.899884+00	\N
1102	1	31	5	Ирбейское	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1103	1	31	5	Казачинское  (Красноярский край	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1104	1	31	5	Канск	94230	f	f	t	2025-10-26 06:31:31.899884+00	\N
1105	1	31	5	Каратузское	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1106	1	31	5	Караул	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1107	1	31	5	Кодинск	14835	f	t	t	2025-10-26 06:31:31.899884+00	\N
1108	1	31	5	Козулька	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1109	1	31	5	Копьево	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1110	1	31	5	Краснотуранск	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1111	1	31	5	Красноярск	973826	f	f	t	2025-10-26 06:31:31.899884+00	\N
1112	1	31	5	Курагино	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1113	1	31	5	Лесосибирск	61146	f	f	t	2025-10-26 06:31:31.899884+00	\N
1114	1	31	5	Минусинск	71171	f	f	t	2025-10-26 06:31:31.899884+00	\N
1115	1	31	5	Мотыгино	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1116	1	31	5	Назарово	52829	f	f	t	2025-10-26 06:31:31.899884+00	\N
1117	1	31	5	Нижний Ингаш	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1118	1	31	5	Новоселово	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1119	1	41	5	Норильск	175301	f	f	t	2025-10-26 06:31:31.899884+00	\N
1120	1	31	5	Партизанское	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1121	1	31	5	Пировское	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1122	1	31	5	Северо-Енисейский	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1123	1	31	5	Сосновоборск (Красноярский край	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1124	1	31	5	Тасеево	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1125	1	31	5	Таштып	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1126	1	31	5	Тура	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1127	1	31	5	Туруханск	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1128	1	31	5	Тюхтет	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1129	1	31	5	Ужур	16079	f	t	t	2025-10-26 06:31:31.899884+00	\N
1130	1	31	5	Уяр	12666	f	t	t	2025-10-26 06:31:31.899884+00	\N
1131	1	31	5	Хатанга	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1132	1	31	5	Черемушки	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1133	1	70	5	Черногорск	72117	f	f	t	2025-10-26 06:31:31.899884+00	\N
1134	1	31	5	Шалинское	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1135	1	31	5	Шарыпово  (Красноярский край	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1136	1	31	5	Шира	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1137	1	31	5	Шушенское	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1138	1	32	6	Варгаши	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1139	1	32	6	Глядянское	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1140	1	32	6	Далматово	13913	f	t	t	2025-10-26 06:31:31.899884+00	\N
1141	1	32	6	Каргаполье	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1142	1	32	6	Катайск	14017	f	t	t	2025-10-26 06:31:31.899884+00	\N
1143	1	32	6	Кетово	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1144	1	32	6	Курган	333640	f	f	t	2025-10-26 06:31:31.899884+00	\N
1145	1	32	6	Куртамыш	17098	f	t	t	2025-10-26 06:31:31.899884+00	\N
1146	1	32	6	Лебяжье	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1147	1	32	6	Макушино	8337	f	t	t	2025-10-26 06:31:31.899884+00	\N
1148	1	32	6	Мишкино	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1149	1	32	6	Мокроусово	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1150	1	32	6	Петухово	11291	f	t	t	2025-10-26 06:31:31.899884+00	\N
1151	1	32	6	Половинное	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1152	1	32	6	Сафакулево	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1153	1	32	6	Шадринск	77744	f	f	t	2025-10-26 06:31:31.899884+00	\N
1154	1	32	6	Шатрово	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1155	1	32	6	Шумиха	17821	f	t	t	2025-10-26 06:31:31.899884+00	\N
1156	1	32	6	Щучье	10971	f	t	t	2025-10-26 06:31:31.899884+00	\N
1157	1	32	6	Юргамыш	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1158	1	33	1	Альменево	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1159	1	33	1	Белая	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1160	1	33	1	Большое Солдатское	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1161	1	33	1	Глушково	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1162	1	33	1	Горшечное	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1163	1	33	1	Дмитриев-Льговский	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1164	1	33	1	Золотухино	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1165	1	33	1	Касторное	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1166	1	33	1	Конышевка	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1167	1	33	1	Коренево	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1168	1	33	1	Курск	414595	f	f	t	2025-10-26 06:31:31.899884+00	\N
1169	1	33	1	Курчатов	42691	f	t	t	2025-10-26 06:31:31.899884+00	\N
1170	1	33	1	Кшенский	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1171	1	33	1	Льгов	21452	f	t	t	2025-10-26 06:31:31.899884+00	\N
1172	1	33	1	Медвенка	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1173	1	33	1	Обоянь	13562	f	t	t	2025-10-26 06:31:31.899884+00	\N
1174	1	33	1	Поныри	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1175	1	33	1	Пристень	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1176	1	33	1	Прямицыно	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1177	1	33	1	Рыльск	15667	f	t	t	2025-10-26 06:31:31.899884+00	\N
1178	1	33	1	Суджа	6036	f	t	t	2025-10-26 06:31:31.899884+00	\N
1179	1	33	1	Тим	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1180	1	33	1	Фатеж	5404	f	t	t	2025-10-26 06:31:31.899884+00	\N
1181	1	33	1	Хомутовка	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1182	1	33	1	Черемисиново	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1183	1	33	1	Щигры	17043	f	t	t	2025-10-26 06:31:31.899884+00	\N
1184	1	34	1	Грязи	46798	f	t	t	2025-10-26 06:31:31.899884+00	\N
1185	1	34	1	Данков	21056	f	t	t	2025-10-26 06:31:31.899884+00	\N
1186	1	34	1	Доброе	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1187	1	34	1	Долгоруково	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1188	1	34	1	Елец	108404	f	f	t	2025-10-26 06:31:31.899884+00	\N
1189	1	34	1	Задонск	9695	f	t	t	2025-10-26 06:31:31.899884+00	\N
1190	1	34	1	Измалково	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1191	1	34	1	Казинка	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1192	1	34	1	Лебедянь	20991	f	t	t	2025-10-26 06:31:31.899884+00	\N
1193	1	34	1	Лев Толстой	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1194	1	34	1	Липецк	508124	f	f	t	2025-10-26 06:31:31.899884+00	\N
1195	1	34	1	Тербуны	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1196	1	34	1	Усмань	18752	f	t	t	2025-10-26 06:31:31.899884+00	\N
1197	1	34	1	Хлевное	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1198	1	34	1	Чаплыгин	12656	f	t	t	2025-10-26 06:31:31.899884+00	\N
1199	1	35	4	Анадырь (Магаданская обл.	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1200	1	35	4	Атка	0	f	f	t	2025-10-26 06:31:31.899884+00	\N
1201	1	35	4	Беринговский	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1202	1	75	4	Билибино	5504	f	t	t	2025-10-26 06:31:31.931302+00	\N
1203	1	35	4	Большевик	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1204	1	35	4	Ванкарем	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1205	1	35	4	Кадыкчан	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1206	1	35	4	Лаврентия	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1207	1	35	4	Магадан	95925	f	f	t	2025-10-26 06:31:31.931302+00	\N
1208	1	35	4	Мыс Шмидта	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1209	1	35	4	Ола	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1210	1	35	4	Омсукчан	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1211	1	35	4	Палатка	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1212	1	75	4	ПЕВЕК	4161	f	t	t	2025-10-26 06:31:31.931302+00	\N
1213	1	35	4	Провидения	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1214	1	35	4	Сеймчан	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1215	1	35	4	Синегорье	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1216	1	35	4	Сусуман	5865	f	t	t	2025-10-26 06:31:31.931302+00	\N
1217	1	35	4	Усть-Омчуг	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1218	1	35	4	Эвенск	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1219	1	35	4	Эгвекинот	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1220	1	35	4	Ягодное	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1221	1	36	7	Волжск	55671	f	f	t	2025-10-26 06:31:31.931302+00	\N
1222	1	36	7	Дубовский	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1223	1	36	7	Звенигово	11945	f	t	t	2025-10-26 06:31:31.931302+00	\N
1224	1	36	7	Йошкар-Ола	248688	f	f	t	2025-10-26 06:31:31.931302+00	\N
1225	1	36	7	Килемары	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1226	1	36	7	Козьмодемьянск	21262	f	f	t	2025-10-26 06:31:31.931302+00	\N
1227	1	36	7	Куженер	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1228	1	36	7	Мари-Турек	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1229	1	36	7	Медведево	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1230	1	36	7	Морки	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1231	1	36	7	Новый Торьял	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1232	1	36	7	Оршанка	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1233	1	36	7	Параньга	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1234	1	36	7	Сернур	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1235	1	36	7	Советский (Марий Эл	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1236	1	36	7	Юрино	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1237	1	39	7	Ардатов	9400	f	t	t	2025-10-26 06:31:31.931302+00	\N
1238	1	37	7	Атюрьево	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1239	1	37	7	Атяшево	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1240	1	37	7	Большие Березники	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1241	1	37	7	Большое Игнатово	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1242	1	37	7	Выша	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1243	1	37	7	Ельники	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1244	1	37	7	Зубова Поляна	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1245	1	37	7	Инсар	8687	f	t	t	2025-10-26 06:31:31.931302+00	\N
1246	1	37	7	Кадошкино	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1247	1	37	7	Кемля	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1248	1	37	7	Ковылкино	21307	f	t	t	2025-10-26 06:31:31.931302+00	\N
1249	1	37	7	Комсомольский (Мордовия	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1250	1	37	7	Кочкурово	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1251	1	37	7	Краснослободск	10151	f	t	t	2025-10-26 06:31:31.931302+00	\N
1252	1	37	7	Лямбирь	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1253	1	37	7	Ромоданово	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1254	1	37	7	Рузаевка	47529	f	t	t	2025-10-26 06:31:31.931302+00	\N
1255	1	37	7	Саранск	318841	f	f	t	2025-10-26 06:31:31.931302+00	\N
1256	1	37	7	Старое Шайгово	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1257	1	37	7	Темников	7247	f	t	t	2025-10-26 06:31:31.931302+00	\N
1258	1	37	7	Теньгушево	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1259	1	37	7	Торбеево	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1260	1	37	7	Чамзинка	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1261	1	38	2	Апатиты	59690	f	f	t	2025-10-26 06:31:31.931302+00	\N
1262	1	38	2	Африканда	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1263	1	38	2	Верхнетуломский	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1264	1	38	2	Видяево	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1265	1	38	2	Гаджиево	11089	f	f	t	2025-10-26 06:31:31.931302+00	\N
1266	1	38	2	Заозерск	11206	f	f	t	2025-10-26 06:31:31.931302+00	\N
1267	1	38	2	Зареченск	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1268	1	38	2	Зашеек	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1269	1	38	2	Зеленоборский	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1270	1	38	2	Кандалакша	35659	f	t	t	2025-10-26 06:31:31.931302+00	\N
1271	1	38	2	Кильдинстрой	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1272	1	38	2	Ковдор	18836	f	t	t	2025-10-26 06:31:31.931302+00	\N
1273	1	38	2	Кола	10447	f	t	t	2025-10-26 06:31:31.931302+00	\N
1274	1	38	2	Конда	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1275	1	38	2	Ловозеро	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1276	1	38	2	Мончегорск	45381	f	f	t	2025-10-26 06:31:31.931302+00	\N
1277	1	38	2	Мурманск	307664	f	f	t	2025-10-26 06:31:31.931302+00	\N
1278	1	38	2	Мурмаши	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1279	1	38	2	Никель	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1280	1	38	2	Оленегорск	23079	f	f	t	2025-10-26 06:31:31.931302+00	\N
1281	1	38	2	Полярные Зори	15106	f	f	t	2025-10-26 06:31:31.931302+00	\N
1282	1	38	2	Полярный	17304	f	f	t	2025-10-26 06:31:31.931302+00	\N
1283	1	38	2	Ревда (Мурманская обл.	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1284	1	38	2	Североморск	50076	f	f	t	2025-10-26 06:31:31.931302+00	\N
1285	1	38	2	Снежногорск	12698	f	f	t	2025-10-26 06:31:31.931302+00	\N
1286	1	38	2	Умба	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1287	1	39	7	Арзамас	106367	f	f	t	2025-10-26 06:31:31.931302+00	\N
1288	1	39	7	Арья	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1289	1	39	7	Балахна	51526	f	t	t	2025-10-26 06:31:31.931302+00	\N
1290	1	39	7	Богородск	25497	f	t	t	2025-10-26 06:31:31.931302+00	\N
1291	1	39	7	Большереченск	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1292	1	39	7	Большое Болдино	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1293	1	39	7	Большое Козино	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1294	1	39	7	Большое Мурашкино	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1295	1	39	7	Большое Пикино	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1296	1	39	7	Бор	78079	f	f	t	2025-10-26 06:31:31.931302+00	\N
1297	1	39	7	Бутурлино	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1298	1	39	7	Вад	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1299	1	39	7	Варнавино	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1300	1	39	7	Васильсурск	0	f	f	t	2025-10-26 06:31:31.931302+00	\N
1301	1	39	7	Вахтан	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1302	1	39	7	Вача	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1303	1	39	7	Ветлуга	8956	f	t	t	2025-10-26 06:31:31.956553+00	\N
1304	1	39	7	Виля	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1305	1	39	7	Вознесенское	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1306	1	39	7	Володарск	9924	f	t	t	2025-10-26 06:31:31.956553+00	\N
1307	1	39	7	Воротынец	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1308	1	39	7	Ворсма	11622	f	f	t	2025-10-26 06:31:31.956553+00	\N
1309	1	39	7	Воскресенское	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1310	1	39	7	Выездное	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1311	1	39	7	Выкса	56196	f	t	t	2025-10-26 06:31:31.956553+00	\N
1312	1	39	7	Гагино	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1313	1	39	7	Гидроторф	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1314	1	39	7	Горбатов	2278	f	f	t	2025-10-26 06:31:31.956553+00	\N
1315	1	39	7	Горбатовка	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1316	1	39	7	Городец	30699	f	t	t	2025-10-26 06:31:31.956553+00	\N
1317	1	39	7	Дальнее Константиново	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1318	1	39	7	Дзержинск	240762	f	f	t	2025-10-26 06:31:31.956553+00	\N
1319	1	39	7	Дивеево	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1320	1	39	7	Досчатое	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1321	1	39	7	Заволжье	40265	f	f	t	2025-10-26 06:31:31.956553+00	\N
1322	1	39	7	Керженец	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1323	1	39	7	Княгинино	6708	f	t	t	2025-10-26 06:31:31.956553+00	\N
1324	1	39	7	Ковернино	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1325	1	39	7	Красные Баки	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1326	1	39	7	Кстово	66641	f	t	t	2025-10-26 06:31:31.956553+00	\N
1327	1	39	7	Кулебаки	35762	f	t	t	2025-10-26 06:31:31.956553+00	\N
1328	1	39	7	Лукоянов	14949	f	t	t	2025-10-26 06:31:31.956553+00	\N
1329	1	39	7	Лысково	21882	f	t	t	2025-10-26 06:31:31.956553+00	\N
1330	1	39	7	Навашино	16413	f	t	t	2025-10-26 06:31:31.956553+00	\N
1331	1	39	7	Нижний Новгород	1250615	t	f	t	2025-10-26 06:31:31.956553+00	\N
1332	1	39	7	Новосмолинский	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1333	1	39	7	Павлово	60699	f	t	t	2025-10-26 06:31:31.956553+00	\N
1334	1	39	7	Первомайск	14567	f	f	t	2025-10-26 06:31:31.956553+00	\N
1335	1	39	7	Перевоз	9201	f	t	t	2025-10-26 06:31:31.956553+00	\N
1336	1	39	7	Пильна	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1337	1	39	7	Починки	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1338	1	39	7	Саров (Нижегородская обл.	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1339	1	39	7	Семенов	24472	f	f	t	2025-10-26 06:31:31.956553+00	\N
1340	1	39	7	Сергач	21387	f	t	t	2025-10-26 06:31:31.956553+00	\N
1341	1	39	7	Сеченово	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1342	1	39	7	Сосновское	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1343	1	39	7	Спасское	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1344	1	39	7	Тонкино	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1345	1	39	7	Тоншаево	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1346	1	39	7	Уразовка	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1347	1	39	7	Урень	12311	f	t	t	2025-10-26 06:31:31.956553+00	\N
1348	1	39	7	Чкаловск	12371	f	t	t	2025-10-26 06:31:31.956553+00	\N
1349	1	39	7	Шаранга	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1350	1	39	7	Шатки	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1351	1	39	7	Шахунья	21337	f	f	t	2025-10-26 06:31:31.956553+00	\N
1352	1	40	2	Анциферово	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1353	1	40	2	Батецкий	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1354	1	40	2	Большая Вишера	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1355	1	40	2	Боровичи	54731	f	t	t	2025-10-26 06:31:31.956553+00	\N
1356	1	40	2	Валдай	16099	f	t	t	2025-10-26 06:31:31.956553+00	\N
1357	1	40	2	Великий Новгород (Новгород	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1358	1	40	2	Волот	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1359	1	40	2	Деманск	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1360	1	47	4	Зарубино	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1361	1	40	2	Крестцы	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1362	1	40	2	Любытино	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1363	1	40	2	Малая Вишера	12461	f	t	t	2025-10-26 06:31:31.956553+00	\N
1364	1	40	2	Марево	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1365	1	40	2	Мошенское	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1366	1	40	2	Окуловка	12464	f	t	t	2025-10-26 06:31:31.956553+00	\N
1367	1	40	2	Парфино	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1368	1	40	2	Пестово	15911	f	t	t	2025-10-26 06:31:31.956553+00	\N
1369	1	40	2	Поддорье	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1370	1	40	2	Сольцы	10317	f	t	t	2025-10-26 06:31:31.956553+00	\N
1371	1	40	2	Старая Русса	32235	f	t	t	2025-10-26 06:31:31.956553+00	\N
1372	1	40	2	Хвойная	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1373	1	40	2	Холм	3829	f	t	t	2025-10-26 06:31:31.956553+00	\N
1374	1	40	2	Чудово	16148	f	t	t	2025-10-26 06:31:31.956553+00	\N
1375	1	40	2	Шимск	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1376	1	41	5	Баган	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1377	1	41	5	Барабинск	30250	f	f	t	2025-10-26 06:31:31.956553+00	\N
1378	1	41	5	Бердск	98809	f	f	t	2025-10-26 06:31:31.956553+00	\N
1379	1	41	5	Биаза	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1380	1	41	5	Болотное	16969	f	t	t	2025-10-26 06:31:31.956553+00	\N
1381	1	41	5	Венгерово	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1382	1	41	5	Довольное	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1383	1	66	1	Завьялово	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1384	1	41	5	Искитим	60072	f	f	t	2025-10-26 06:31:31.956553+00	\N
1385	1	41	5	Карасук	28929	f	t	t	2025-10-26 06:31:31.956553+00	\N
1386	1	41	5	Каргат	10620	f	t	t	2025-10-26 06:31:31.956553+00	\N
1387	1	41	5	Колывань	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1388	1	41	5	Краснозерское	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1389	1	41	5	Крутиха	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1390	1	41	5	Куйбышев (Новосибирская обл.	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1391	1	41	5	Купино	15448	f	t	t	2025-10-26 06:31:31.956553+00	\N
1392	1	41	5	Кыштовка	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1393	1	41	5	Маслянино	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1394	1	41	5	Мошково	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1395	1	41	5	Новосибирск	1498921	t	f	t	2025-10-26 06:31:31.956553+00	\N
1396	1	41	5	Обь	26137	f	f	t	2025-10-26 06:31:31.956553+00	\N
1397	1	41	5	Ордынское	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1398	1	43	7	Северное	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1399	1	41	5	Сузун	0	f	f	t	2025-10-26 06:31:31.956553+00	\N
1400	1	41	5	Татарск	26114	f	f	t	2025-10-26 06:31:31.956553+00	\N
1401	1	41	5	Тогучин	21531	f	t	t	2025-10-26 06:31:31.982944+00	\N
1402	1	41	5	Убинское	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1403	1	41	5	Усть-Тарка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1404	1	41	5	Чаны	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1405	1	41	5	Черепаново	19346	f	t	t	2025-10-26 06:31:31.982944+00	\N
1406	1	41	5	Чистоозерное	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1407	1	41	5	Чулым	11964	f	t	t	2025-10-26 06:31:31.982944+00	\N
1408	1	42	5	Береговой	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1409	1	42	5	Большеречье	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1410	1	42	5	Большие Уки	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1411	1	42	5	Горьковское	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1412	1	42	5	Знаменское (Омская обл.	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1413	1	42	5	Исилькуль	25905	f	t	t	2025-10-26 06:31:31.982944+00	\N
1414	1	42	5	Калачинск	24000	f	t	t	2025-10-26 06:31:31.982944+00	\N
1415	1	42	5	Колосовка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1416	1	42	5	Кормиловка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1417	1	42	5	Крутинка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1418	1	42	5	Любинский	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1419	1	42	5	Марьяновка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1420	1	42	5	Муромцево	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1421	1	42	5	Называевск	12119	f	t	t	2025-10-26 06:31:31.982944+00	\N
1422	1	42	5	Нижняя Омка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1423	1	42	5	Нововаршавка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1424	1	42	5	Одесское	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1425	1	42	5	Оконешниково	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1426	1	42	5	Омск	1154000	t	f	t	2025-10-26 06:31:31.982944+00	\N
1427	1	42	5	Павлоградка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1428	1	42	5	Полтавка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1429	1	42	5	Русская Поляна	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1430	1	42	5	Саргатское	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1431	1	42	5	Седельниково	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1432	1	42	5	Таврическое	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1433	1	42	5	Тара	26664	f	t	t	2025-10-26 06:31:31.982944+00	\N
1434	1	42	5	Тевриз	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1435	1	42	5	Тюкалинск	12050	f	t	t	2025-10-26 06:31:31.982944+00	\N
1436	1	42	5	Усть-Ишим	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1437	1	42	5	Черлак	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1438	1	42	5	Шербакуль	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1439	1	43	7	Абдулино	20663	f	t	t	2025-10-26 06:31:31.982944+00	\N
1440	1	43	7	Адамовка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1441	1	43	7	Айдырлинский	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1442	1	43	7	Акбулак	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1443	1	43	7	Аккермановка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1444	1	43	7	Асекеево	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1445	1	43	7	Беляевка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1446	1	43	7	Бугуруслан	52249	f	f	t	2025-10-26 06:31:31.982944+00	\N
1447	1	43	7	Бузулук	82816	f	f	t	2025-10-26 06:31:31.982944+00	\N
1448	1	43	7	Гай	38302	f	f	t	2025-10-26 06:31:31.982944+00	\N
1449	1	43	7	Грачевка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1450	1	43	7	Домбаровский	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1451	1	43	7	Дубенский	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1452	1	43	7	Илек	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1453	1	43	7	Ириклинский	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1454	1	43	7	Кувандык	26176	f	f	t	2025-10-26 06:31:31.982944+00	\N
1455	1	43	7	Курманаевка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1456	1	43	7	Матвеевка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1457	1	43	7	Медногорск	27253	f	f	t	2025-10-26 06:31:31.982944+00	\N
1458	1	43	7	Новоорск	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1459	1	43	7	Новосергиевка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1460	1	43	7	Новотроицк	97914	f	f	t	2025-10-26 06:31:31.982944+00	\N
1461	1	43	7	Октябрьское (Оренбург.	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1462	1	43	7	Оренбург	570329	f	f	t	2025-10-26 06:31:31.982944+00	\N
1463	1	43	7	Орск	238006	f	f	t	2025-10-26 06:31:31.982944+00	\N
1464	1	43	7	Первомайский (Оренбург.	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1465	1	43	7	Переволоцкий	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1466	1	43	7	Пономаревка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1467	1	43	7	Саракташ	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1468	1	43	7	Светлый (Оренбургская обл.	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1469	1	43	7	Соль-Илецк	26308	f	t	t	2025-10-26 06:31:31.982944+00	\N
1470	1	43	7	Сорочинск	30136	f	f	t	2025-10-26 06:31:31.982944+00	\N
1471	1	43	7	Ташла	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1472	1	43	7	Тоцкое	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1473	1	43	7	Тюльган	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1474	1	43	7	Шарлык	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1475	1	43	7	Энергетик	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1476	1	43	7	Ясный	16082	f	t	t	2025-10-26 06:31:31.982944+00	\N
1477	1	44	1	Болхов	11421	f	t	t	2025-10-26 06:31:31.982944+00	\N
1478	1	44	1	Верховье	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1479	1	44	1	Глазуновка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1480	1	44	1	Дмитровск-Орловский	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1481	1	44	1	Долгое	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1482	1	44	1	Залегощь	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1483	1	44	1	Змиевка	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1484	1	44	1	Знаменское (Орловская обл.	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1485	1	44	1	Колпны	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1486	1	44	1	Красная Заря	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1487	1	44	1	Кромы	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1488	1	44	1	Ливны	50430	f	f	t	2025-10-26 06:31:31.982944+00	\N
1489	1	44	1	Малоархангельск	3872	f	t	t	2025-10-26 06:31:31.982944+00	\N
1490	1	44	1	Мценск	43216	f	f	t	2025-10-26 06:31:31.982944+00	\N
1491	1	44	1	Нарышкино	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1492	1	44	1	Новосиль	3799	f	t	t	2025-10-26 06:31:31.982944+00	\N
1493	1	44	1	Орел	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1494	1	49	3	Покровское	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1495	1	44	1	Сосково	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1496	1	44	1	Тросна	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1497	1	44	1	Хомутово	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1498	1	44	1	Хотынец	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1499	1	44	1	Шаблыкино	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1500	1	45	7	Башмаково	0	f	f	t	2025-10-26 06:31:31.982944+00	\N
1501	1	45	7	Беднодемьяновск	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1502	1	45	7	Беково	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1503	1	45	7	Белинский	8567	f	t	t	2025-10-26 06:31:32.01098+00	\N
1504	1	45	7	Бессоновка	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1505	1	45	7	Вадинск	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1506	1	45	7	Верхозим	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1507	1	45	7	Городище (Пензенская обл.	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1508	1	45	7	Евлашево	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1509	1	45	7	Заречный (Пензенская обл.	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1510	1	45	7	Земетчино	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1511	1	45	7	Золотаревка	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1512	1	45	7	Исса	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1513	1	45	7	Каменка	39579	f	t	t	2025-10-26 06:31:32.01098+00	\N
1514	1	45	7	Колышлей	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1515	1	45	7	Кондоль	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1516	1	45	7	Кузнецк	88886	f	t	t	2025-10-26 06:31:32.01098+00	\N
1517	1	45	7	Лопатино	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1518	1	45	7	Малая Сердоба	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1519	1	45	7	Мокшан	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1520	1	45	7	Наровчат	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1521	1	45	7	Неверкино	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1522	1	45	7	Нижний Ломов	22678	f	t	t	2025-10-26 06:31:32.01098+00	\N
1523	1	45	7	Никольск (Пензенская обл.	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1524	1	45	7	Пачелма	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1525	1	45	7	Пенза	519592	f	f	t	2025-10-26 06:31:32.01098+00	\N
1526	1	45	7	Русский Камешкир	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1527	1	45	7	Сердобск	35393	f	t	t	2025-10-26 06:31:32.01098+00	\N
1528	1	45	7	Сосновоборск	33090	f	f	t	2025-10-26 06:31:32.01098+00	\N
1529	1	45	7	Сура	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1530	1	45	7	Тамала	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1531	1	45	7	Шемышейка	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1532	1	46	7	Александровск	15022	f	f	t	2025-10-26 06:31:32.01098+00	\N
1533	1	46	7	Барда	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1534	1	46	7	Березники	156350	f	f	t	2025-10-26 06:31:32.01098+00	\N
1535	1	46	7	Большая Соснова	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1536	1	46	7	Верещагино	22760	f	t	t	2025-10-26 06:31:32.01098+00	\N
1537	1	46	7	Гайны	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1538	1	46	7	Горнозаводск (Пермский край	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1539	1	46	7	Гремячинск	11005	f	f	t	2025-10-26 06:31:32.01098+00	\N
1540	1	46	7	Губаха	27544	f	f	t	2025-10-26 06:31:32.01098+00	\N
1541	1	46	7	Добрянка	35720	f	f	t	2025-10-26 06:31:32.01098+00	\N
1542	1	46	7	Елово	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1543	1	46	7	Зюкайка	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1544	1	46	7	Ильинский (Пермская обл.	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1545	1	46	7	Карагай	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1546	1	46	7	Керчевский	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1547	1	46	7	Кизел	20277	f	f	t	2025-10-26 06:31:32.01098+00	\N
1548	1	46	7	Коса	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1549	1	46	7	Кочево	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1550	1	46	7	Красновишерск	17129	f	t	t	2025-10-26 06:31:32.01098+00	\N
1551	1	46	7	Краснокамск	52632	f	f	t	2025-10-26 06:31:32.01098+00	\N
1552	1	46	7	Кудымкар	30711	f	f	t	2025-10-26 06:31:32.01098+00	\N
1553	1	46	7	Куеда	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1554	1	46	7	Кунгур	67857	f	f	t	2025-10-26 06:31:32.01098+00	\N
1555	1	46	7	Лысьва	67712	f	f	t	2025-10-26 06:31:32.01098+00	\N
1556	1	46	7	Ныроб	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1557	1	46	7	Нытва	19041	f	t	t	2025-10-26 06:31:32.01098+00	\N
1558	1	46	7	Октябрьский	109379	f	f	t	2025-10-26 06:31:32.01098+00	\N
1559	1	46	7	Орда	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1560	1	46	7	Оханск	7597	f	t	t	2025-10-26 06:31:32.01098+00	\N
1561	1	46	7	Очер	15003	f	t	t	2025-10-26 06:31:32.01098+00	\N
1562	1	46	7	Пермь	1000679	t	f	t	2025-10-26 06:31:32.01098+00	\N
1563	1	46	7	Соликамск	97239	f	f	t	2025-10-26 06:31:32.01098+00	\N
1564	1	46	7	Суксун	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1565	1	46	7	Уинское	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1566	1	46	7	Усолье	5694	f	t	t	2025-10-26 06:31:32.01098+00	\N
1567	1	46	7	Усть-Кишерть	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1568	1	46	7	Чайковский	82933	f	f	t	2025-10-26 06:31:32.01098+00	\N
1569	1	46	7	Частые	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1570	1	46	7	Чердынь	4920	f	t	t	2025-10-26 06:31:32.01098+00	\N
1571	1	46	7	Чернореченский	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1572	1	46	7	Чернушка	33275	f	t	t	2025-10-26 06:31:32.01098+00	\N
1573	1	46	7	Чусовой	46740	f	f	t	2025-10-26 06:31:32.01098+00	\N
1574	1	46	7	Юрла	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1575	1	46	7	Юсьва	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1576	1	47	4	Анучино	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1577	1	47	4	Арсеньев	56742	f	f	t	2025-10-26 06:31:32.01098+00	\N
1578	1	47	4	Артем	102636	f	f	t	2025-10-26 06:31:32.01098+00	\N
1579	1	47	4	Артемовский (Приморский край	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1580	1	47	4	Большой Камень	39257	f	f	t	2025-10-26 06:31:32.01098+00	\N
1581	1	47	4	Валентин	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1582	1	47	4	Владивосток	592069	f	f	t	2025-10-26 06:31:32.01098+00	\N
1583	1	47	4	Высокогорск	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1584	1	47	4	Горные Ключи	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1585	1	69	4	Горный	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1586	1	47	4	Дальнегорск	37503	f	f	t	2025-10-26 06:31:32.01098+00	\N
1587	1	47	4	Дальнереченск	27601	f	f	t	2025-10-26 06:31:32.01098+00	\N
1588	1	47	4	Кавалерово	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1589	1	47	4	Каменка (Приморский край	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1590	1	47	4	Камень-Рыболов	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1591	1	47	4	Лазо	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1592	1	47	4	Лесозаводск	36975	f	f	t	2025-10-26 06:31:32.01098+00	\N
1593	1	47	4	Лучегорск	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1594	1	47	4	Михайловка (Приморский край	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1595	1	47	4	Находка (Приморский край	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1596	1	47	4	Новопокровка	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1597	1	47	4	Ольга	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1598	1	47	4	Партизанск	38648	f	f	t	2025-10-26 06:31:32.01098+00	\N
1599	1	47	4	Пластун	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1600	1	47	4	Пограничный	0	f	f	t	2025-10-26 06:31:32.01098+00	\N
1601	1	47	4	Покровка	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1602	1	47	4	Посьет	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1603	1	47	4	Русский	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1604	1	47	4	Славянка	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1605	1	47	4	Спасск-Дальний	44166	f	f	t	2025-10-26 06:31:32.037664+00	\N
1606	1	47	4	Терней	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1607	1	47	4	Уссурийск	157946	f	f	t	2025-10-26 06:31:32.037664+00	\N
1608	1	47	4	Фокино	23683	f	f	t	2025-10-26 06:31:32.037664+00	\N
1609	1	47	4	Хасан	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1610	1	47	4	Хороль	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1611	1	47	4	Черниговка	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1612	1	47	4	Чугуевка	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1613	1	47	4	Яковлевка	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1614	1	47	4	Ярославский	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1615	1	48	2	Бежаницы	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1616	1	48	2	Великие Луки	98778	f	f	t	2025-10-26 06:31:32.037664+00	\N
1617	1	48	2	Гдов	4379	f	t	t	2025-10-26 06:31:32.037664+00	\N
1618	1	48	2	Дедовичи	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1619	1	48	2	Дно	9061	f	t	t	2025-10-26 06:31:32.037664+00	\N
1620	1	48	2	Заплюсье	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1621	1	48	2	Идрица	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1622	1	48	2	Красногородское	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1623	1	48	2	Кунья	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1624	1	48	2	Локня	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1625	1	48	2	Невель	16324	f	t	t	2025-10-26 06:31:32.037664+00	\N
1626	1	48	2	Новоржев	3695	f	t	t	2025-10-26 06:31:32.037664+00	\N
1627	1	48	2	Новосокольники	8119	f	t	t	2025-10-26 06:31:32.037664+00	\N
1628	1	48	2	Опочка	11601	f	t	t	2025-10-26 06:31:32.037664+00	\N
1629	1	48	2	Остров	21670	f	t	t	2025-10-26 06:31:32.037664+00	\N
1630	1	48	2	Палкино	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1631	1	48	2	Печоры	12308	f	t	t	2025-10-26 06:31:32.037664+00	\N
1632	1	48	2	Плюсса	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1633	1	48	2	Порхов	10608	f	t	t	2025-10-26 06:31:32.037664+00	\N
1634	1	48	2	Псков	203974	f	f	t	2025-10-26 06:31:32.037664+00	\N
1635	1	48	2	Пустошка	4619	f	t	t	2025-10-26 06:31:32.037664+00	\N
1636	1	48	2	Пушкинские Горы	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1637	1	48	2	Пыталово	5826	f	t	t	2025-10-26 06:31:32.037664+00	\N
1638	1	48	2	Себеж	6375	f	t	t	2025-10-26 06:31:32.037664+00	\N
1639	1	48	2	Струги-Красные	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1640	1	48	2	Усвяты	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1641	1	49	3	Азов	82882	f	f	t	2025-10-26 06:31:32.037664+00	\N
1642	1	49	3	Аксай (Ростовская обл.	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1643	1	49	3	Алмазный	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1644	1	49	3	Аютинск	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1645	1	49	3	Багаевский	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1646	1	49	3	Батайск	112400	f	f	t	2025-10-26 06:31:32.037664+00	\N
1647	1	49	3	Белая Калитва	43688	f	t	t	2025-10-26 06:31:32.037664+00	\N
1648	1	49	3	Боковская	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1649	1	49	3	Большая Мартыновка	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1650	1	49	3	Вешенская	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1651	1	49	3	Волгодонск	170621	f	f	t	2025-10-26 06:31:32.037664+00	\N
1652	1	49	3	Восход	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1653	1	49	3	Гигант	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1654	1	49	3	Горняцкий	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1655	1	49	3	Гуково	67268	f	f	t	2025-10-26 06:31:32.037664+00	\N
1656	1	49	3	Донецк	50085	f	f	t	2025-10-26 06:31:32.037664+00	\N
1657	1	49	3	Донской (Ростовская обл.	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1658	1	49	3	Дубовское	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1659	1	49	3	Егорлыкская	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1660	1	49	3	Жирнов	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1661	1	49	3	Заветное	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1662	1	49	3	Заводской	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1663	1	49	3	Зверево	22416	f	f	t	2025-10-26 06:31:32.037664+00	\N
1664	1	49	3	Зерноград	26850	f	t	t	2025-10-26 06:31:32.037664+00	\N
1665	1	49	3	Зимовники	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1666	1	49	3	Кагальницкая	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1667	1	49	3	Казанская	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1668	1	49	3	Каменоломни	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1669	1	49	3	Каменск-Шахтинский	95306	f	f	t	2025-10-26 06:31:32.037664+00	\N
1670	1	49	3	Кашары	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1671	1	49	3	Коксовый	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1672	1	49	3	Константиновск	17926	f	t	t	2025-10-26 06:31:32.037664+00	\N
1673	1	49	3	Красный Сулин	40866	f	t	t	2025-10-26 06:31:32.037664+00	\N
1674	1	49	3	Куйбышево	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1675	1	49	3	Матвеев Курган	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1676	1	49	3	Мигулинская	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1677	1	49	3	Миллерово	36493	f	t	t	2025-10-26 06:31:32.037664+00	\N
1678	1	49	3	Милютинская	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1679	1	49	3	Морозовск	27644	f	t	t	2025-10-26 06:31:32.037664+00	\N
1680	1	49	3	Новочеркасск	169039	f	f	t	2025-10-26 06:31:32.037664+00	\N
1681	1	49	3	Новошахтинск	111087	f	f	t	2025-10-26 06:31:32.037664+00	\N
1682	1	49	3	Обливская	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1683	1	49	3	Орловский	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1684	1	49	3	Песчанокопское	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1685	1	49	3	Пролетарск	20267	f	t	t	2025-10-26 06:31:32.037664+00	\N
1686	1	49	3	Ремонтное	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1687	1	49	3	Родионово-Несветайская	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1688	1	49	3	Ростов-на-Дону	1091544	t	f	t	2025-10-26 06:31:32.037664+00	\N
1689	1	49	3	Сальск	61312	f	t	t	2025-10-26 06:31:32.037664+00	\N
1690	1	49	3	Семикаракорск	23884	f	t	t	2025-10-26 06:31:32.037664+00	\N
1691	1	49	3	Таганрог	257692	f	f	t	2025-10-26 06:31:32.037664+00	\N
1692	1	49	3	Тарасовский	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1693	1	49	3	Тацинский	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1694	1	49	3	Усть-Донецкий	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1695	1	49	3	Целина	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1696	1	49	3	Цимлянск	15029	f	t	t	2025-10-26 06:31:32.037664+00	\N
1697	1	49	3	Чалтырь	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1698	1	49	3	Чертково	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1699	1	49	3	Шахты	240152	f	f	t	2025-10-26 06:31:32.037664+00	\N
1700	1	49	3	Шолоховский	0	f	f	t	2025-10-26 06:31:32.037664+00	\N
1701	1	50	1	Александро-Невский	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1702	1	50	1	Гусь Железный	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1703	1	50	1	Елатьма	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1704	1	50	1	Ермишь	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1705	1	50	1	Заречный (Рязанская обл.	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1706	1	50	1	Захарово	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1707	1	50	1	Кадом	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1708	1	50	1	Касимов	33494	f	t	t	2025-10-26 06:31:32.06386+00	\N
1709	1	50	1	Кораблино	12657	f	t	t	2025-10-26 06:31:32.06386+00	\N
1710	1	50	1	Милославское	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1711	1	50	1	Михайлов	11783	f	t	t	2025-10-26 06:31:32.06386+00	\N
1712	1	50	1	Новомичуринск	19309	f	f	t	2025-10-26 06:31:32.06386+00	\N
1713	1	50	1	Пителино	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1714	1	50	1	Пронск	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1715	1	50	1	Путятино	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1716	1	50	1	Рыбное	18378	f	t	t	2025-10-26 06:31:32.06386+00	\N
1717	1	50	1	Ряжск	21676	f	t	t	2025-10-26 06:31:32.06386+00	\N
1718	1	50	1	Рязань	525062	f	f	t	2025-10-26 06:31:32.06386+00	\N
1719	1	50	1	Сапожок	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1720	1	50	1	Сараи	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1721	1	50	1	Сасово	28117	f	f	t	2025-10-26 06:31:32.06386+00	\N
1722	1	50	1	Скопин	30374	f	t	t	2025-10-26 06:31:32.06386+00	\N
1723	1	50	1	Спас-Клепики	5917	f	t	t	2025-10-26 06:31:32.06386+00	\N
1724	1	50	1	Спасск-Рязанский	7745	f	t	t	2025-10-26 06:31:32.06386+00	\N
1725	1	50	1	Старожилово	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1726	1	50	1	Ухолово	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1727	1	50	1	Чучково	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1728	1	50	1	Шацк	6562	f	t	t	2025-10-26 06:31:32.06386+00	\N
1729	1	50	1	Шилово	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1730	1	51	7	Алексеевка (Самарская обл.	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1731	1	51	7	Безенчук	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1732	1	51	7	Богатое	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1733	1	51	7	Богатырь	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1734	1	51	7	Большая Глушица	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1735	1	51	7	Большая Глущица (Самарск.	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1736	1	51	7	Большая Черниговка	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1737	1	51	7	Борское	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1738	1	51	7	Волжский (Самарская обл.	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1739	1	51	7	Жигулевск	57565	f	f	t	2025-10-26 06:31:32.06386+00	\N
1740	1	51	7	Зольное	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1741	1	51	7	Исаклы	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1742	1	51	7	Камышла	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1743	1	51	7	Кинель	34472	f	f	t	2025-10-26 06:31:32.06386+00	\N
1744	1	51	7	Кинель-Черкасы	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1745	1	51	7	Клявлино	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1746	1	51	7	Кошки	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1747	1	51	7	Красноармейское (Самарск.	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1748	1	51	7	Красный Яр (Самарская обл.	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1749	1	51	7	Куйбышев	47278	f	f	t	2025-10-26 06:31:32.06386+00	\N
1750	1	51	7	Нефтегорск	18732	f	t	t	2025-10-26 06:31:32.06386+00	\N
1751	1	51	7	Новокуйбышевск	108449	f	f	t	2025-10-26 06:31:32.06386+00	\N
1752	1	51	7	Октябрьск	27244	f	f	t	2025-10-26 06:31:32.06386+00	\N
1753	1	51	7	Отрадный	47709	f	f	t	2025-10-26 06:31:32.06386+00	\N
1754	1	51	7	Пестравка	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1755	1	51	7	Похвистнево	28181	f	f	t	2025-10-26 06:31:32.06386+00	\N
1756	1	51	7	Приволжье	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1757	1	51	7	Самара	1164900	t	f	t	2025-10-26 06:31:32.06386+00	\N
1758	1	51	7	Сергиевск	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1759	1	51	7	Сургут (Самарская обл.	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1760	1	51	7	Сызрань	178773	f	f	t	2025-10-26 06:31:32.06386+00	\N
1761	1	51	7	Тольятти	719484	f	f	t	2025-10-26 06:31:32.06386+00	\N
1762	1	51	7	Хворостянка	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1763	1	51	7	Чапаевск	72689	f	f	t	2025-10-26 06:31:32.06386+00	\N
1764	1	51	7	Челно-Вершины	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1765	1	51	7	Шентала	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1766	1	51	7	Шигоны	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1767	1	52	7	Александров Гай	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1768	1	52	7	Аркадак	12846	f	t	t	2025-10-26 06:31:32.06386+00	\N
1769	1	52	7	Аткарск	25620	f	f	t	2025-10-26 06:31:32.06386+00	\N
1770	1	52	7	Базарный Карабулак	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1771	1	52	7	Балаково	199576	f	f	t	2025-10-26 06:31:32.06386+00	\N
1772	1	52	7	Балашов	82222	f	f	t	2025-10-26 06:31:32.06386+00	\N
1773	1	52	7	Балтай	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1774	1	52	7	Возрождение	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1775	1	52	7	Вольск	66520	f	f	t	2025-10-26 06:31:32.06386+00	\N
1776	1	52	7	Воскресенское (Саратовск.	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1777	1	52	7	Дергачи	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1778	1	52	7	Духовницкое	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1779	1	52	7	Екатериновка	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1780	1	52	7	Ершов	21447	f	t	t	2025-10-26 06:31:32.06386+00	\N
1781	1	52	7	Ивантеевка (Саратовская обл.	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1782	1	52	7	Калининск	16442	f	t	t	2025-10-26 06:31:32.06386+00	\N
1783	1	52	7	Каменский	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1784	1	52	7	Красноармейск (Саратовск.	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1785	1	52	7	Красный Кут	14420	f	t	t	2025-10-26 06:31:32.06386+00	\N
1786	1	52	7	Лысые Горы	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1787	1	52	7	Маркс	31535	f	f	t	2025-10-26 06:31:32.06386+00	\N
1788	1	52	7	Мокроус	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1789	1	52	7	Новоузенск	17015	f	t	t	2025-10-26 06:31:32.06386+00	\N
1790	1	52	7	Новые Бурасы	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1791	1	52	7	Озинки	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1792	1	52	7	Перелюб	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1793	1	52	7	Петровск	31158	f	t	t	2025-10-26 06:31:32.06386+00	\N
1794	1	52	7	Питерка	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1795	1	52	7	Пугачев	41705	f	t	t	2025-10-26 06:31:32.06386+00	\N
1796	1	52	7	Ровное	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1797	1	52	7	Романовка	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1798	1	52	7	Ртищево	41295	f	f	t	2025-10-26 06:31:32.06386+00	\N
1799	1	52	7	Самойловка	0	f	f	t	2025-10-26 06:31:32.06386+00	\N
1800	1	52	7	Саратов	836900	f	f	t	2025-10-26 06:31:32.06386+00	\N
1801	1	52	7	Степное (Саратовская обл.	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1802	1	52	7	Татищево	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1803	1	52	7	Турки	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1804	1	52	7	Хвалынск	13199	f	f	t	2025-10-26 06:31:32.093871+00	\N
1805	1	52	7	Энгельс	202838	f	f	t	2025-10-26 06:31:32.093871+00	\N
1806	1	53	4	Абый	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1807	1	53	4	Айхал	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1808	1	53	4	Алдан	21277	f	t	t	2025-10-26 06:31:32.093871+00	\N
1809	1	53	4	Амга	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1810	1	53	4	Батагай	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1811	1	53	4	Бердигестях	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1812	1	53	4	Беркакит	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1813	1	53	4	Бестях	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1814	1	53	4	Борогонцы	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1815	1	53	4	Верхневилюйск	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1816	1	53	4	Верхоянск	1311	f	f	t	2025-10-26 06:31:32.093871+00	\N
1817	1	53	4	Вилюйск	10233	f	t	t	2025-10-26 06:31:32.093871+00	\N
1818	1	53	4	Витим	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1819	1	53	4	Власово	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1820	1	53	4	Депутатский	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1821	1	53	4	Жиганск	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1822	1	53	4	Зырянка	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1823	1	53	4	Кангалассы	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1824	1	53	4	Ленск	24955	f	t	t	2025-10-26 06:31:32.093871+00	\N
1825	1	53	4	Майя	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1826	1	53	4	Мирный (Саха	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1827	1	53	4	Нерюнгри	61746	f	f	t	2025-10-26 06:31:32.093871+00	\N
1828	1	53	4	Нижний Куранах	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1829	1	53	4	Нюрба	10156	f	t	t	2025-10-26 06:31:32.093871+00	\N
1830	1	53	4	Олекминск	9487	f	t	t	2025-10-26 06:31:32.093871+00	\N
1831	1	53	4	Покровск	9495	f	t	t	2025-10-26 06:31:32.093871+00	\N
1832	1	53	4	Сангар	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1833	1	53	4	Саскылах	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1834	1	53	4	Солнечный	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1835	1	53	4	Среднеколымск	3525	f	t	t	2025-10-26 06:31:32.093871+00	\N
1836	1	53	4	Сунтар	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1837	1	53	4	Тикси	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1838	1	53	4	Удачный	12611	f	f	t	2025-10-26 06:31:32.093871+00	\N
1839	1	53	4	Усть-Мая	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1840	1	53	4	Усть-Нера	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1841	1	53	4	Хандыга	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1842	1	53	4	Хонуу	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1843	1	53	4	Чернышевский	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1844	1	53	4	Черский	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1845	1	53	4	Чокурдах	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1846	1	53	4	Чульман	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1847	1	53	4	Чурапча	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1848	1	53	4	Якутск	269486	f	f	t	2025-10-26 06:31:32.093871+00	\N
1849	1	54	4	Александровск-Сахалинский	10613	f	t	t	2025-10-26 06:31:32.093871+00	\N
1850	1	54	4	Анбэцу	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1851	1	54	4	Анива	8449	f	t	t	2025-10-26 06:31:32.093871+00	\N
1852	1	54	4	Бошняково	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1853	1	54	4	Быков	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1854	1	54	4	Вахрушев	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1855	1	54	4	Взморье	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1856	1	54	4	Гастелло	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1857	1	54	4	Горнозаводск (Сахалин	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1858	1	54	4	Долинск	12200	f	t	t	2025-10-26 06:31:32.093871+00	\N
1859	1	54	4	Ильинский (Сахалин	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1860	1	54	4	Катангли	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1861	1	54	4	Корсаков	33526	f	t	t	2025-10-26 06:31:32.093871+00	\N
1862	1	54	4	Курильск	2070	f	t	t	2025-10-26 06:31:32.093871+00	\N
1863	1	54	4	Макаров	6788	f	t	t	2025-10-26 06:31:32.093871+00	\N
1864	1	54	4	Невельск	11682	f	t	t	2025-10-26 06:31:32.093871+00	\N
1865	1	54	4	Ноглики	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1866	1	54	4	Оха	23007	f	t	t	2025-10-26 06:31:32.093871+00	\N
1867	1	54	4	Поронайск	16461	f	t	t	2025-10-26 06:31:32.093871+00	\N
1868	1	54	4	Северо-Курильск	2381	f	t	t	2025-10-26 06:31:32.093871+00	\N
1869	1	54	4	Смирных	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1870	1	54	4	Томари	4537	f	t	t	2025-10-26 06:31:32.093871+00	\N
1871	1	54	4	Тымовское	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1872	1	54	4	Углегорск	11880	f	t	t	2025-10-26 06:31:32.093871+00	\N
1873	1	54	4	Холмск	30936	f	t	t	2025-10-26 06:31:32.093871+00	\N
1874	1	54	4	Шахтерск	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1875	1	54	4	Южно-Курильск	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1876	1	54	4	Южно-Сахалинск	181727	f	f	t	2025-10-26 06:31:32.093871+00	\N
1877	1	55	6	Алапаевск	38198	f	f	t	2025-10-26 06:31:32.093871+00	\N
1878	1	55	6	Алтынай	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1879	1	55	6	Арамиль	14227	f	f	t	2025-10-26 06:31:32.093871+00	\N
1880	1	55	6	Артемовский (Свердловская обл.	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1881	1	55	6	Арти	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1882	1	55	6	Асбест	70067	f	f	t	2025-10-26 06:31:32.093871+00	\N
1883	1	55	6	Ачит	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1884	1	55	6	Байкалово	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1885	1	55	6	Басьяновский	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1886	1	55	6	Белоярский (Свердловская обл.	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1887	1	55	6	Березовский (Свердловская обл.	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1888	1	55	6	Бисерть	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1889	1	55	6	Богданович	31752	f	f	t	2025-10-26 06:31:32.093871+00	\N
1890	1	55	6	Буланаш	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1891	1	55	6	Верхний Тагил	11843	f	f	t	2025-10-26 06:31:32.093871+00	\N
1892	1	55	6	Верхняя Пышма	58707	f	f	t	2025-10-26 06:31:32.093871+00	\N
1893	1	55	6	Верхняя Салда	46240	f	f	t	2025-10-26 06:31:32.093871+00	\N
1894	1	55	6	Верхняя Синячиха	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1895	1	55	6	Верхняя Сысерть	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1896	1	55	6	Верхняя Тура	9468	f	f	t	2025-10-26 06:31:32.093871+00	\N
1897	1	55	6	Верхотурье	8815	f	t	t	2025-10-26 06:31:32.093871+00	\N
1898	1	55	6	Висим	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1899	1	55	6	Волчанск	10008	f	f	t	2025-10-26 06:31:32.093871+00	\N
1900	1	55	6	Гари	0	f	f	t	2025-10-26 06:31:32.093871+00	\N
1901	1	55	6	Дегтярск	15521	f	f	t	2025-10-26 06:31:32.119597+00	\N
1902	1	55	6	Екатеринбург	1377738	t	f	t	2025-10-26 06:31:32.119597+00	\N
1903	1	55	6	Ертарский	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1904	1	55	6	Заводоуспенское	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1905	1	55	6	Заречный	26803	f	f	t	2025-10-26 06:31:32.119597+00	\N
1906	1	55	6	Ивдель	17764	f	f	t	2025-10-26 06:31:32.119597+00	\N
1907	1	55	6	Изумруд	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1908	1	55	6	Ирбит	38352	f	f	t	2025-10-26 06:31:32.119597+00	\N
1909	1	55	6	Ис	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1910	1	55	6	Каменск-Уральский	174710	f	f	t	2025-10-26 06:31:32.119597+00	\N
1911	1	55	6	Камышлов	26875	f	f	t	2025-10-26 06:31:32.119597+00	\N
1912	1	55	6	Карпинск	29118	f	f	t	2025-10-26 06:31:32.119597+00	\N
1913	1	55	6	Качканар	42563	f	f	t	2025-10-26 06:31:32.119597+00	\N
1914	1	55	6	Кировград	21959	f	f	t	2025-10-26 06:31:32.119597+00	\N
1915	1	55	6	Краснотурьинск	59701	f	f	t	2025-10-26 06:31:32.119597+00	\N
1916	1	55	6	Красноуральск	24973	f	f	t	2025-10-26 06:31:32.119597+00	\N
1917	1	55	6	Красноуфимск	39765	f	f	t	2025-10-26 06:31:32.119597+00	\N
1918	1	55	6	Кушва	33027	f	f	t	2025-10-26 06:31:32.119597+00	\N
1919	1	55	6	Лесной	52464	f	f	t	2025-10-26 06:31:32.119597+00	\N
1920	1	58	8	Михайловск	71018	f	t	t	2025-10-26 06:31:32.119597+00	\N
1921	1	55	6	Невьянск	25147	f	t	t	2025-10-26 06:31:32.119597+00	\N
1922	1	55	6	Нижние Серги	11217	f	t	t	2025-10-26 06:31:32.119597+00	\N
1923	1	55	6	Нижний Тагил	361883	f	f	t	2025-10-26 06:31:32.119597+00	\N
1924	1	55	6	Нижняя Салда	17969	f	f	t	2025-10-26 06:31:32.119597+00	\N
1925	1	55	6	Нижняя Тура	21596	f	f	t	2025-10-26 06:31:32.119597+00	\N
1926	1	55	6	Новая Ляля	12400	f	t	t	2025-10-26 06:31:32.119597+00	\N
1927	1	55	6	Новоуральск	91813	f	f	t	2025-10-26 06:31:32.119597+00	\N
1928	1	55	6	Новоуральск (Свердловская обл.	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1929	1	55	6	Оус	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1930	1	55	6	Первоуральск	149800	f	f	t	2025-10-26 06:31:32.119597+00	\N
1931	1	55	6	Полевской	64316	f	f	t	2025-10-26 06:31:32.119597+00	\N
1932	1	55	6	Пышма	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1933	1	55	6	Ревда (Свердловская обл.	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1934	1	55	6	Реж	38709	f	t	t	2025-10-26 06:31:32.119597+00	\N
1935	1	55	6	Рефтинск	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1936	1	55	6	Свердловск	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1937	1	55	6	Североуральск	29279	f	f	t	2025-10-26 06:31:32.119597+00	\N
1938	1	55	6	Серов	99381	f	f	t	2025-10-26 06:31:32.119597+00	\N
1939	1	55	6	Сосьва	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1940	1	55	6	Среднеуральск	20357	f	f	t	2025-10-26 06:31:32.119597+00	\N
1941	1	55	6	Сухой Лог	34836	f	f	t	2025-10-26 06:31:32.119597+00	\N
1942	1	55	6	Сысерть	20594	f	t	t	2025-10-26 06:31:32.119597+00	\N
1943	1	55	6	Таборы	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1944	1	55	6	Тавда	35421	f	f	t	2025-10-26 06:31:32.119597+00	\N
1945	1	55	6	Талица	18339	f	t	t	2025-10-26 06:31:32.119597+00	\N
1946	1	55	6	Тугулым	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1947	1	55	6	Туринск	17990	f	t	t	2025-10-26 06:31:32.119597+00	\N
1948	1	55	6	Туринская Слобода	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1949	1	56	8	Алагир	20949	f	t	t	2025-10-26 06:31:32.119597+00	\N
1950	1	56	8	Ардон	18774	f	t	t	2025-10-26 06:31:32.119597+00	\N
1951	1	56	8	Беслан	36724	f	t	t	2025-10-26 06:31:32.119597+00	\N
1952	1	56	8	Бурон	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1953	1	56	8	Владикавказ	311635	f	f	t	2025-10-26 06:31:32.119597+00	\N
1954	1	56	8	Дигора	10856	f	t	t	2025-10-26 06:31:32.119597+00	\N
1955	1	56	8	Моздок	38748	f	t	t	2025-10-26 06:31:32.119597+00	\N
1956	1	56	8	Орджоникидзе	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1957	1	56	8	Чикола	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1958	1	57	1	Велиж	7620	f	t	t	2025-10-26 06:31:32.119597+00	\N
1959	1	57	1	Верхнеднепровский	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1960	1	57	1	Ворга	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1961	1	57	1	Вязьма	57103	f	t	t	2025-10-26 06:31:32.119597+00	\N
1962	1	57	1	Гагарин	31721	f	t	t	2025-10-26 06:31:32.119597+00	\N
1963	1	57	1	Глинка	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1964	1	57	1	Голынки	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1965	1	57	1	Демидов	7333	f	t	t	2025-10-26 06:31:32.119597+00	\N
1966	1	57	1	Десногорск	29677	f	f	t	2025-10-26 06:31:32.119597+00	\N
1967	1	57	1	Дорогобуж	10720	f	t	t	2025-10-26 06:31:32.119597+00	\N
1968	1	57	1	Духовщина	4370	f	t	t	2025-10-26 06:31:32.119597+00	\N
1969	1	57	1	Ельня	10095	f	t	t	2025-10-26 06:31:32.119597+00	\N
1970	1	57	1	Ершичи	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1971	1	57	1	Издешково	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1972	1	57	1	Кардымово	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1973	1	57	1	Красный	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1974	1	57	1	Монастырщина	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1975	1	57	1	Новодугино	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1976	1	57	1	Починок	8776	f	t	t	2025-10-26 06:31:32.119597+00	\N
1977	1	57	1	Рославль	54898	f	t	t	2025-10-26 06:31:32.119597+00	\N
1978	1	57	1	Рудня	10029	f	t	t	2025-10-26 06:31:32.119597+00	\N
1979	1	57	1	Сафоново	46116	f	t	t	2025-10-26 06:31:32.119597+00	\N
1980	1	57	1	Смоленск	326863	f	f	t	2025-10-26 06:31:32.119597+00	\N
1981	1	57	1	Сычевка	8111	f	t	t	2025-10-26 06:31:32.119597+00	\N
1982	1	57	1	Угра	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1983	1	57	1	Хиславичи	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1984	1	57	1	Холм-Жирковский	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1985	1	57	1	Шумячи	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1986	1	57	1	Ярцево	47853	f	t	t	2025-10-26 06:31:32.119597+00	\N
1987	1	58	8	Александровское (Ставрополь.	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1988	1	58	8	Арзгир	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1989	1	58	8	Благодарный	32736	f	t	t	2025-10-26 06:31:32.119597+00	\N
1990	1	58	8	Буденновск	64628	f	t	t	2025-10-26 06:31:32.119597+00	\N
1991	1	58	8	Георгиевск	72126	f	f	t	2025-10-26 06:31:32.119597+00	\N
1992	1	58	8	Дивное (Ставропольский край	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1993	1	58	8	Домбай	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1994	1	58	8	Донское	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1995	1	58	8	Ессентуки	100969	f	f	t	2025-10-26 06:31:32.119597+00	\N
1996	1	58	8	Железноводск(Ставропольский	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
1997	1	58	8	Зеленокумск	35790	f	t	t	2025-10-26 06:31:32.119597+00	\N
1998	1	58	8	Изобильный	40546	f	t	t	2025-10-26 06:31:32.119597+00	\N
1999	1	58	8	Иноземцево	0	f	f	t	2025-10-26 06:31:32.119597+00	\N
2000	1	58	8	Ипатово	26055	f	t	t	2025-10-26 06:31:32.119597+00	\N
2001	1	58	8	Карачаевск	23848	f	t	t	2025-10-26 06:31:32.14866+00	\N
2002	1	58	8	Кисловодск	128502	f	f	t	2025-10-26 06:31:32.14866+00	\N
2003	1	58	8	Кочубеевское	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2004	1	58	8	Красногвардейское (Ставрополь.	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2005	1	58	8	Курсавка	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2006	1	58	8	Левокумское	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2007	1	58	8	Лермонтов	22540	f	f	t	2025-10-26 06:31:32.14866+00	\N
2008	1	58	8	Минеральные Воды	76715	f	t	t	2025-10-26 06:31:32.14866+00	\N
2009	1	58	8	Невинномысск	118351	f	f	t	2025-10-26 06:31:32.14866+00	\N
2010	1	58	8	Нефтекумск	27700	f	t	t	2025-10-26 06:31:32.14866+00	\N
2011	1	58	8	Новоалександровск	26759	f	t	t	2025-10-26 06:31:32.14866+00	\N
2012	1	58	8	Новоалександровская	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2013	1	58	8	Новопавловск	26556	f	t	t	2025-10-26 06:31:32.14866+00	\N
2014	1	58	8	Новоселицкое	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2015	1	58	8	Преградная	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2016	1	58	8	Пятигорск	142397	f	f	t	2025-10-26 06:31:32.14866+00	\N
2017	1	58	8	Светлоград	38520	f	t	t	2025-10-26 06:31:32.14866+00	\N
2018	1	58	8	Солнечнодольск	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2019	1	58	8	Ставрополь	398266	f	f	t	2025-10-26 06:31:32.14866+00	\N
2020	1	58	8	Степное (Ставропольский край	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2021	1	58	8	Теберда	9097	f	f	t	2025-10-26 06:31:32.14866+00	\N
2022	1	58	8	Усть-Джегута	30602	f	t	t	2025-10-26 06:31:32.14866+00	\N
2023	1	58	8	Хабез	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2024	1	78	8	Черкесск	121439	f	f	t	2025-10-26 06:31:32.14866+00	\N
2025	1	59	1	Бондари	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2026	1	59	1	Гавриловка Вторая	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2027	1	59	1	Жердевка	15211	f	t	t	2025-10-26 06:31:32.14866+00	\N
2028	1	59	1	Знаменка	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2029	1	59	1	Инжавино	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2030	1	59	1	Кирсанов	17240	f	f	t	2025-10-26 06:31:32.14866+00	\N
2031	1	59	1	Котовск	31851	f	f	t	2025-10-26 06:31:32.14866+00	\N
2032	1	59	1	Мичуринск	98758	f	t	t	2025-10-26 06:31:32.14866+00	\N
2033	1	59	1	Мордово	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2034	1	59	1	Моршанск	41550	f	f	t	2025-10-26 06:31:32.14866+00	\N
2035	1	59	1	Мучкапский	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2036	1	59	1	Первомайский (Тамбовская обл.	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2037	1	59	1	Петровское	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2038	1	59	1	Пичаево	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2039	1	59	1	Рассказово	45484	f	f	t	2025-10-26 06:31:32.14866+00	\N
2040	1	59	1	Ржакса	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2041	1	59	1	Сосновка	11960	f	f	t	2025-10-26 06:31:32.14866+00	\N
2042	1	59	1	Староюрьево	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2043	1	59	1	Тамбов	280457	f	f	t	2025-10-26 06:31:32.14866+00	\N
2044	1	59	1	Токаревка	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2045	1	59	1	Уварово	26829	f	f	t	2025-10-26 06:31:32.14866+00	\N
2046	1	59	1	Умет	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2047	1	60	7	Агрыз	19299	f	t	t	2025-10-26 06:31:32.14866+00	\N
2048	1	60	7	Азнакаево	34859	f	t	t	2025-10-26 06:31:32.14866+00	\N
2049	1	60	7	Аксубаево	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2050	1	60	7	Актаныш	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2051	1	60	7	Актюбинский	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2052	1	60	7	Алексеевское	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2053	1	60	7	Альметьевск	146309	f	t	t	2025-10-26 06:31:32.14866+00	\N
2054	1	60	7	Апастово	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2055	1	60	7	Арск	18114	f	t	t	2025-10-26 06:31:32.14866+00	\N
2056	1	60	7	Бавлы	22109	f	t	t	2025-10-26 06:31:32.14866+00	\N
2057	1	60	7	Базарные Матаки	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2058	1	60	7	Балтаси	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2059	1	60	7	Богатые Сабы	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2060	1	60	7	Брежнев	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2061	1	60	7	Бугульма	89144	f	t	t	2025-10-26 06:31:32.14866+00	\N
2062	1	74	1	Буинск	20342	f	t	t	2025-10-26 06:31:32.14866+00	\N
2063	1	60	7	Васильево	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2064	1	60	7	Верхний Услон	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2065	1	60	7	Высокая Гора	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2066	1	60	7	Дербешкинский	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2067	1	60	7	Елабуга	70750	f	t	t	2025-10-26 06:31:32.14866+00	\N
2068	1	60	7	Заинск	41798	f	t	t	2025-10-26 06:31:32.14866+00	\N
2069	1	60	7	Зеленодольск	97651	f	t	t	2025-10-26 06:31:32.14866+00	\N
2070	1	60	7	Казань	1216965	t	f	t	2025-10-26 06:31:32.14866+00	\N
2071	1	60	7	Камское Устье	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2072	1	60	7	Карабаш (Татарстан	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2073	1	60	7	Куйбышев (Татарстан	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2074	1	60	7	Кукмод	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2075	1	60	7	Кукмор	17700	f	t	t	2025-10-26 06:31:32.14866+00	\N
2076	1	60	7	Лаишево	7735	f	t	t	2025-10-26 06:31:32.14866+00	\N
2077	1	60	7	Лениногорск	64145	f	t	t	2025-10-26 06:31:32.14866+00	\N
2078	1	60	7	Мамадыш	14432	f	t	t	2025-10-26 06:31:32.14866+00	\N
2079	1	60	7	Менделеевск	22075	f	t	t	2025-10-26 06:31:32.14866+00	\N
2080	1	60	7	Мензелинск	16474	f	t	t	2025-10-26 06:31:32.14866+00	\N
2081	1	60	7	Муслюмово	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2082	1	60	7	Набережные Челны	513242	f	f	t	2025-10-26 06:31:32.14866+00	\N
2083	1	60	7	Нижнекамск	234108	f	t	t	2025-10-26 06:31:32.14866+00	\N
2084	1	60	7	Новошешминск	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2085	1	60	7	Нурлат	32600	f	t	t	2025-10-26 06:31:32.14866+00	\N
2086	1	60	7	Пестрецы	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2087	1	60	7	Рыбная Слобода	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2088	1	60	7	Сарманово	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2089	1	60	7	Старое Дрожжаное	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2090	1	60	7	Тетюши	11596	f	t	t	2025-10-26 06:31:32.14866+00	\N
2091	1	60	7	Черемшан	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2092	1	60	7	Чистополь	60703	f	t	t	2025-10-26 06:31:32.14866+00	\N
2093	1	61	1	Андреаполь	8265	f	t	t	2025-10-26 06:31:32.14866+00	\N
2094	1	61	1	Бежецк	24517	f	t	t	2025-10-26 06:31:32.14866+00	\N
2095	1	61	1	Белый	3771	f	t	t	2025-10-26 06:31:32.14866+00	\N
2096	1	61	1	Белый Городок	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2097	1	61	1	Березайка	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2098	1	61	1	Бологое	23499	f	t	t	2025-10-26 06:31:32.14866+00	\N
2099	1	61	1	Васильевский Мох	0	f	f	t	2025-10-26 06:31:32.14866+00	\N
2100	1	61	1	Весьегонск	7330	f	t	t	2025-10-26 06:31:32.14866+00	\N
2101	1	61	1	Выползово	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2102	1	61	1	Вышний Волочек	52326	f	f	t	2025-10-26 06:31:32.18109+00	\N
2103	1	61	1	Жарковский	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2104	1	61	1	Западная Двина	9376	f	t	t	2025-10-26 06:31:32.18109+00	\N
2105	1	61	1	Зубцов	6937	f	t	t	2025-10-26 06:31:32.18109+00	\N
2106	1	61	1	Изоплит	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2107	1	61	1	Калашниково	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2108	1	61	1	Калинин	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2109	1	61	1	Калязин	13870	f	t	t	2025-10-26 06:31:32.18109+00	\N
2110	1	61	1	Кашин	16174	f	t	t	2025-10-26 06:31:32.18109+00	\N
2111	1	61	1	Кесова Гора	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2112	1	61	1	Кимры	49623	f	f	t	2025-10-26 06:31:32.18109+00	\N
2113	1	61	1	Конаково	41303	f	t	t	2025-10-26 06:31:32.18109+00	\N
2114	1	61	1	Красный Холм	5608	f	t	t	2025-10-26 06:31:32.18109+00	\N
2115	1	61	1	Кувшиново	10008	f	t	t	2025-10-26 06:31:32.18109+00	\N
2116	1	61	1	Лесное	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2117	1	61	1	Лихославль	12259	f	t	t	2025-10-26 06:31:32.18109+00	\N
2118	1	61	1	Максатиха	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2119	1	61	1	Молоково	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2120	1	61	1	Нелидово	22886	f	t	t	2025-10-26 06:31:32.18109+00	\N
2121	1	61	1	Оленино	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2122	1	61	1	Осташков	18073	f	t	t	2025-10-26 06:31:32.18109+00	\N
2123	1	61	1	Пено	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2124	1	61	1	Рамешки	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2125	1	61	1	Ржев	62026	f	f	t	2025-10-26 06:31:32.18109+00	\N
2126	1	61	1	Сандово	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2127	1	61	1	Селижарово	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2128	1	61	1	Сонково	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2129	1	61	1	Спирово	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2130	1	61	1	Старица	8610	f	t	t	2025-10-26 06:31:32.18109+00	\N
2131	1	61	1	Тверь	403726	f	f	t	2025-10-26 06:31:32.18109+00	\N
2132	1	61	1	Торжок	47702	f	f	t	2025-10-26 06:31:32.18109+00	\N
2133	1	61	1	Торопец	13018	f	t	t	2025-10-26 06:31:32.18109+00	\N
2134	1	61	1	Удомля	31048	f	t	t	2025-10-26 06:31:32.18109+00	\N
2135	1	61	1	Фирово	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2136	1	62	5	Александровское (Томская обл.	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2137	1	62	5	Асино	25614	f	t	t	2025-10-26 06:31:32.18109+00	\N
2138	1	62	5	Бакчар	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2139	1	62	5	Батурино	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2140	1	62	5	Зырянское	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2141	1	62	5	Итатка	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2142	1	62	5	Каргасок	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2143	1	62	5	Катайга	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2144	1	62	5	Кожевниково	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2145	1	62	5	Колпашево	24126	f	t	t	2025-10-26 06:31:32.18109+00	\N
2146	1	62	5	Кривошеино	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2147	1	62	5	Мельниково	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2148	1	62	5	Молчаново	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2149	1	62	5	Парабель	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2150	1	62	5	Первомайское	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2151	1	62	5	Подгорное	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2152	1	62	5	Северск	108466	f	f	t	2025-10-26 06:31:32.18109+00	\N
2153	1	62	5	Стрежевой	42216	f	f	t	2025-10-26 06:31:32.18109+00	\N
2154	1	62	5	Томск	522940	f	f	t	2025-10-26 06:31:32.18109+00	\N
2155	1	62	5	Тымск	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2156	1	63	1	Ак-Довурак	13469	f	f	t	2025-10-26 06:31:32.18109+00	\N
2157	1	63	1	Бай Хаак	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2158	1	63	1	Кызыл	109906	f	f	t	2025-10-26 06:31:32.18109+00	\N
2159	1	63	1	Самагалтай	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2160	1	63	1	Сарыг-Сеп	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2161	1	63	1	Суть-Холь	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2162	1	63	1	Тоора-Хем	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2163	1	63	1	Туран	4988	f	t	t	2025-10-26 06:31:32.18109+00	\N
2164	1	63	1	Тээли	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2165	1	63	1	Хову-Аксы	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2166	1	63	1	Чадан	9037	f	t	t	2025-10-26 06:31:32.18109+00	\N
2167	1	63	1	Шагонар	10958	f	t	t	2025-10-26 06:31:32.18109+00	\N
2168	1	63	1	Эрзин	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2169	1	64	1	Агеево	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2170	1	64	1	Алексин	61738	f	t	t	2025-10-26 06:31:32.18109+00	\N
2171	1	64	1	Арсеньево	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2172	1	64	1	Барсуки	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2173	1	64	1	Белев	13918	f	t	t	2025-10-26 06:31:32.18109+00	\N
2174	1	64	1	Богородицк	31897	f	t	t	2025-10-26 06:31:32.18109+00	\N
2175	1	64	1	Болохово	9619	f	f	t	2025-10-26 06:31:32.18109+00	\N
2176	1	64	1	Велегож	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2177	1	64	1	Венев	15220	f	t	t	2025-10-26 06:31:32.18109+00	\N
2178	1	64	1	Волово	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2179	1	64	1	Горелки	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2180	1	64	1	Донской	64561	f	f	t	2025-10-26 06:31:32.18109+00	\N
2181	1	64	1	Дубна (Тульская обл.	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2182	1	64	1	Епифань	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2183	1	64	1	Ефремов	42350	f	t	t	2025-10-26 06:31:32.18109+00	\N
2184	1	64	1	Заокский	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2185	1	64	1	Казановка	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2186	1	64	1	Кимовск	28493	f	t	t	2025-10-26 06:31:32.18109+00	\N
2187	1	64	1	Киреевск	25585	f	t	t	2025-10-26 06:31:32.18109+00	\N
2188	1	64	1	Куркино	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2189	1	64	1	Ленинский	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2190	1	64	1	Лянтор	38922	f	f	t	2025-10-26 06:31:32.18109+00	\N
2191	1	64	1	Новомосковск	131227	f	t	t	2025-10-26 06:31:32.18109+00	\N
2192	1	64	1	Одоев	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2193	1	64	1	Плавск	16248	f	t	t	2025-10-26 06:31:32.18109+00	\N
2194	1	64	1	Советск (Тульская обл.	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2195	1	64	1	Суворов	18975	f	t	t	2025-10-26 06:31:32.18109+00	\N
2196	1	64	1	Тула	501129	f	f	t	2025-10-26 06:31:32.18109+00	\N
2197	1	64	1	Узловая	55282	f	t	t	2025-10-26 06:31:32.18109+00	\N
2198	1	64	1	Щекино	58154	f	t	t	2025-10-26 06:31:32.18109+00	\N
2199	1	64	1	Ясногорск	16804	f	t	t	2025-10-26 06:31:32.18109+00	\N
2200	1	65	6	Абатский	0	f	f	t	2025-10-26 06:31:32.18109+00	\N
2201	1	65	6	Аган	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2202	1	65	6	Аксарка	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2203	1	65	6	Армизонское	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2204	1	65	6	Аромашево	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2205	1	65	6	Белоярский (Тюменская обл.	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2206	1	65	6	Бердюжье	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2207	1	65	6	Березово	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2208	1	65	6	Большое Сорокино	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2209	1	65	6	Вагай	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2210	1	65	6	Викулово	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2211	1	65	6	Винзили	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2212	1	65	6	Голышманово	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2213	1	65	6	Губкинский (Тюменская обл.	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2214	1	65	6	Заводопетровский	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2215	1	65	6	Заводоуковск	25657	f	t	t	2025-10-26 06:31:32.217995+00	\N
2216	1	65	6	Игрим	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2217	1	65	6	Излучинск	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2218	1	65	6	Исетское	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2219	1	65	6	Ишим	69567	f	t	t	2025-10-26 06:31:32.217995+00	\N
2220	1	65	6	Казанское	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2221	1	65	6	Казым-Мыс	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2222	1	65	6	Когалым (Тюменская обл.	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2223	1	65	6	Кондинское	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2224	1	65	6	Красноселькуп	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2225	1	65	6	Лабытнанги	26948	f	f	t	2025-10-26 06:31:32.217995+00	\N
2226	1	65	6	Лангепас	41675	f	f	t	2025-10-26 06:31:32.217995+00	\N
2227	1	65	6	Ларьяк	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2228	1	65	6	Лянторский	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2229	1	65	6	Мегион	49471	f	f	t	2025-10-26 06:31:32.217995+00	\N
2230	1	65	6	Междуреченский	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2231	1	65	6	Мужи	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2232	1	65	6	Муравленко (Тюменская обл.	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2233	1	65	6	Надым (Тюменская обл.	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2234	1	65	6	Находка (Тюменская обл.	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2235	1	65	6	Нефтеюганск	123276	f	f	t	2025-10-26 06:31:32.217995+00	\N
2236	1	65	6	Нижневартовск	251860	f	f	t	2025-10-26 06:31:32.217995+00	\N
2237	1	65	6	Нижняя Тавда	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2238	1	65	6	Новоаганск	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2239	1	65	6	Новый Уренгой (Тюменская обл.	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2240	1	65	6	Ноябрьск (Тюменская обл.	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2241	1	65	6	Нягань	54903	f	f	t	2025-10-26 06:31:32.217995+00	\N
2242	1	65	6	Октябрьское (Тюменская обл.	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2243	1	65	6	Омутинский	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2244	1	65	6	Покачи (Тюменская обл.	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2245	1	65	6	Приобье	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2246	1	65	6	Пыть-Ях	41453	f	f	t	2025-10-26 06:31:32.217995+00	\N
2247	1	65	6	Радужный (Ханты-Мансийский АО	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2248	1	76	2	Салехард	42494	f	f	t	2025-10-26 06:31:32.217995+00	\N
2249	1	65	6	Сладково	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2250	1	65	6	Советский (Тюменская обл.	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2251	1	65	6	Сургут	306703	f	f	t	2025-10-26 06:31:32.217995+00	\N
2252	1	76	2	Тазовский	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2253	1	65	6	Тобольск	99698	f	f	t	2025-10-26 06:31:32.217995+00	\N
2254	1	65	6	Тюмень	581758	f	f	t	2025-10-26 06:31:32.217995+00	\N
2255	1	65	6	Уват	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2256	1	65	6	Унъюган	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2257	1	65	6	Упорово	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2258	1	65	6	Урай	39435	f	f	t	2025-10-26 06:31:32.217995+00	\N
2259	1	65	6	Ханты-Мансийск	79410	f	f	t	2025-10-26 06:31:32.217995+00	\N
2260	1	65	6	Югорск	34066	f	f	t	2025-10-26 06:31:32.217995+00	\N
2261	1	65	6	Юрибей	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2262	1	65	6	Ялуторовск	36494	f	t	t	2025-10-26 06:31:32.217995+00	\N
2263	1	65	6	Яр-Сале	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2264	1	65	6	Ярково	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2265	1	66	1	Алнаши	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2266	1	66	1	Балезино	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2267	1	66	1	Вавож	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2268	1	66	1	Воткинск	100034	f	f	t	2025-10-26 06:31:32.217995+00	\N
2269	1	66	1	Глазов	95835	f	f	t	2025-10-26 06:31:32.217995+00	\N
2270	1	66	1	Грахово	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2271	1	66	1	Дебесы	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2272	1	66	1	Игра	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2273	1	66	1	Ижевск	628117	f	f	t	2025-10-26 06:31:32.217995+00	\N
2274	1	66	1	Кама	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2275	1	66	1	Камбарка	11028	f	t	t	2025-10-26 06:31:32.217995+00	\N
2276	1	66	1	Каракулино	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2277	1	66	1	Кез	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2278	1	66	1	Кизнер	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2279	1	66	1	Киясово	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2280	1	66	1	Красногорское (Удмуртия	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2281	1	66	1	Можга	47959	f	f	t	2025-10-26 06:31:32.217995+00	\N
2282	1	66	1	Сарапул	101390	f	f	t	2025-10-26 06:31:32.217995+00	\N
2283	1	66	1	Селты	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2284	1	66	1	Сюмси	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2285	1	66	1	Ува	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2286	1	66	1	Устинов	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2287	1	66	1	Шаркан	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2288	1	66	1	Юкаменское	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2289	1	66	1	Якшур-Бодья	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2290	1	66	1	Яр	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2291	1	67	7	Базарный Сызган	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2292	1	67	7	Барыш	17149	f	f	t	2025-10-26 06:31:32.217995+00	\N
2293	1	67	7	Большое Нагаткино	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2294	1	67	7	Вешкайма	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2295	1	67	7	Глотовка	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2296	1	67	7	Димитровград	122549	f	f	t	2025-10-26 06:31:32.217995+00	\N
2297	1	67	7	Игнатовка	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2298	1	67	7	Измайлово	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2299	1	67	7	Инза	18547	f	t	t	2025-10-26 06:31:32.217995+00	\N
2300	1	67	7	Ишеевка	0	f	f	t	2025-10-26 06:31:32.217995+00	\N
2301	1	67	7	Канадей	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2302	1	67	7	Карсун	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2303	1	67	7	Кузоватово	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2304	1	67	7	Майна	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2305	1	67	7	Новая Малыкла	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2306	1	67	7	Новоспасское	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2307	1	67	7	Новоульяновск	16032	f	f	t	2025-10-26 06:31:32.243429+00	\N
2308	1	67	7	Павловка	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2309	1	67	7	Радищево	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2310	1	67	7	Сенгилей	6959	f	t	t	2025-10-26 06:31:32.243429+00	\N
2311	1	67	7	Старая Кулатка	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2312	1	67	7	Старая Майна	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2313	1	67	7	Сурское	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2314	1	67	7	Тереньга	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2315	1	67	7	Ульяновск	613793	f	f	t	2025-10-26 06:31:32.243429+00	\N
2316	1	67	7	Чердаклы	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2317	1	68	1	Аксай (Уральская обл.	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2318	1	68	1	Дарьинское	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2319	1	68	1	Деркул	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2320	1	68	1	Джамбейты	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2321	1	68	1	Переметное	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2322	1	68	1	Уральск	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2323	1	68	1	Федоровка (Уральская обл.	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2324	1	68	1	Фурманово	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2325	1	68	1	Чапаев	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2326	1	69	4	Амурск	42977	f	f	t	2025-10-26 06:31:32.243429+00	\N
2327	1	69	4	Аян	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2328	1	69	4	Березовый	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2329	1	69	4	Бикин	17156	f	f	t	2025-10-26 06:31:32.243429+00	\N
2330	1	69	4	Бира	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2331	1	69	4	Биракан	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2332	1	69	4	Богородское (Хабаровский край	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2333	1	69	4	Ванино	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2334	1	69	4	Волочаевка Вторая	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2335	1	69	4	Высокогорный	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2336	1	69	4	Вяземский	14556	f	t	t	2025-10-26 06:31:32.243429+00	\N
2337	1	69	4	Гурское	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2338	1	69	4	Дормидонтовка	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2339	1	69	4	Заветы Ильича	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2340	1	69	4	Известковый	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2341	1	69	4	Иннокентьевка	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2342	1	69	4	Комсомольск-на-Амуре	263906	f	f	t	2025-10-26 06:31:32.243429+00	\N
2343	1	69	4	Нелькан	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2344	1	69	4	Николаевск-на-Амуре	22773	f	f	t	2025-10-26 06:31:32.243429+00	\N
2345	1	69	4	Облучье	9379	f	t	t	2025-10-26 06:31:32.243429+00	\N
2346	1	69	4	Охотск	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2347	1	69	4	Переяславка	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2348	1	69	4	Смидович	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2349	1	69	4	Советская Гавань	27712	f	f	t	2025-10-26 06:31:32.243429+00	\N
2350	1	69	4	Софийск	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2351	1	69	4	Троицкое	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2352	1	69	4	Тугур	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2353	1	69	4	Хабаровск	577668	f	f	t	2025-10-26 06:31:32.243429+00	\N
2354	1	69	4	Чегдомын	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2355	1	69	4	Чумикан	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2356	1	70	5	Саяногорск	49889	f	f	t	2025-10-26 06:31:32.243429+00	\N
2357	1	71	6	Агаповка	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2358	1	71	6	Аргаяш	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2359	1	71	6	Аша	31916	f	t	t	2025-10-26 06:31:32.243429+00	\N
2360	1	71	6	Бакал	20953	f	f	t	2025-10-26 06:31:32.243429+00	\N
2361	1	71	6	Бреды	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2362	1	71	6	Варна	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2363	1	71	6	Верхнеуральск	9459	f	t	t	2025-10-26 06:31:32.243429+00	\N
2364	1	71	6	Верхний Уфалей	30504	f	f	t	2025-10-26 06:31:32.243429+00	\N
2365	1	71	6	Еманжелинск	30218	f	t	t	2025-10-26 06:31:32.243429+00	\N
2366	1	71	6	Златоуст	174985	f	f	t	2025-10-26 06:31:32.243429+00	\N
2367	1	71	6	Карабаш	13151	f	f	t	2025-10-26 06:31:32.243429+00	\N
2368	1	71	6	Карталы	29136	f	t	t	2025-10-26 06:31:32.243429+00	\N
2369	1	71	6	Касли	16998	f	t	t	2025-10-26 06:31:32.243429+00	\N
2370	1	71	6	Катав-Ивановск	17640	f	t	t	2025-10-26 06:31:32.243429+00	\N
2371	1	71	6	Копейск	137604	f	f	t	2025-10-26 06:31:32.243429+00	\N
2372	1	71	6	Коркино	38950	f	t	t	2025-10-26 06:31:32.243429+00	\N
2373	1	71	6	Красногорский	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2374	1	71	6	Кунашак	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2375	1	71	6	Куса	18792	f	t	t	2025-10-26 06:31:32.243429+00	\N
2376	1	71	6	Кыштым	38950	f	f	t	2025-10-26 06:31:32.243429+00	\N
2377	1	71	6	Магнитогорск	408401	f	f	t	2025-10-26 06:31:32.243429+00	\N
2378	1	71	6	Миасс	151812	f	f	t	2025-10-26 06:31:32.243429+00	\N
2379	1	71	6	Миньяр	10195	f	f	t	2025-10-26 06:31:32.243429+00	\N
2380	1	71	6	Озерск(Челябинская обл.	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2381	1	71	6	Октябрьское (Челябинская обл.	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2382	1	71	6	Пласт	17344	f	t	t	2025-10-26 06:31:32.243429+00	\N
2383	1	71	6	Сатка	45465	f	t	t	2025-10-26 06:31:32.243429+00	\N
2384	1	71	6	Сим	14465	f	f	t	2025-10-26 06:31:32.243429+00	\N
2385	1	71	6	Снежинск (Челябинская обл.	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2386	1	71	6	Трехгорный	33678	f	f	t	2025-10-26 06:31:32.243429+00	\N
2387	1	71	6	Увельский	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2388	1	71	6	Уйское	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2389	1	71	6	Усть-Катав	23586	f	f	t	2025-10-26 06:31:32.243429+00	\N
2390	1	71	6	Фершампенуаз	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2391	1	71	6	Чебаркуль	43405	f	f	t	2025-10-26 06:31:32.243429+00	\N
2392	1	71	6	Челябинск	1130273	t	f	t	2025-10-26 06:31:32.243429+00	\N
2393	1	71	6	Чесма	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2394	1	71	6	Южно-Уральск	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2395	1	71	6	Юрюзань	12568	f	f	t	2025-10-26 06:31:32.243429+00	\N
2396	1	72	8	Аргун	29528	f	f	t	2025-10-26 06:31:32.243429+00	\N
2397	1	72	8	Грозный	271596	f	f	t	2025-10-26 06:31:32.243429+00	\N
2398	1	72	8	Гудермес	45643	f	t	t	2025-10-26 06:31:32.243429+00	\N
2399	1	72	8	Знаменское	0	f	f	t	2025-10-26 06:31:32.243429+00	\N
2400	1	72	8	Малгобек	31076	f	f	t	2025-10-26 06:31:32.243429+00	\N
2401	1	72	8	Назрань	93357	f	t	t	2025-10-26 06:31:32.271245+00	\N
2402	1	72	8	Наурская	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2403	1	72	8	Ножай-Юрт	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2404	1	72	8	Орджоникидзевская	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2405	1	72	8	Советское (Чечено-Ингушетия	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2406	1	72	8	Урус-Мартан	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2407	1	72	8	Шали	47715	f	t	t	2025-10-26 06:31:32.271245+00	\N
2408	1	73	1	Аксеново-Зиловское	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2409	1	73	1	Акша	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2410	1	73	1	Арбагар	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2411	1	73	1	Атамановка	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2412	1	73	1	Балей	12536	f	t	t	2025-10-26 06:31:32.271245+00	\N
2413	1	73	1	Борзя	31376	f	t	t	2025-10-26 06:31:32.271245+00	\N
2414	1	73	1	Букачача	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2415	1	73	1	Газимурский Завод	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2416	1	73	1	Давенда	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2417	1	73	1	Дарасун	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2418	1	73	1	Домна	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2419	1	73	1	Дровяная	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2420	1	73	1	Дульдурга	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2421	1	73	1	Забайкальск	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2422	1	73	1	Карымское	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2423	1	73	1	Ключевский	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2424	1	73	1	Кокуй	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2425	1	73	1	Краснокаменск	55668	f	t	t	2025-10-26 06:31:32.271245+00	\N
2426	1	73	1	Красный Чикой	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2427	1	73	1	Кыра	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2428	1	73	1	Моготуй	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2429	1	73	1	Могоча	13228	f	t	t	2025-10-26 06:31:32.271245+00	\N
2430	1	73	1	Нерчинск	14976	f	t	t	2025-10-26 06:31:32.271245+00	\N
2431	1	73	1	Нерчинский Завод	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2432	1	73	1	Нижний Цасучей	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2433	1	73	1	Оловянная	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2434	1	73	1	Первомайский (Читинская обл.	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2435	1	73	1	Петровск-Забайкальский	18555	f	t	t	2025-10-26 06:31:32.271245+00	\N
2436	1	73	1	Приаргунск	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2437	1	73	1	Сретенск	6850	f	t	t	2025-10-26 06:31:32.271245+00	\N
2438	1	73	1	Тупик	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2439	1	73	1	Улеты	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2440	1	73	1	Хилок	11530	f	t	t	2025-10-26 06:31:32.271245+00	\N
2441	1	73	1	Чара	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2442	1	73	1	Чернышевск	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2443	1	73	1	Чита	323964	f	f	t	2025-10-26 06:31:32.271245+00	\N
2444	1	73	1	Шелопугино	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2445	1	73	1	Шилка	13947	f	t	t	2025-10-26 06:31:32.271245+00	\N
2446	1	74	1	Алатырь	38202	f	f	t	2025-10-26 06:31:32.271245+00	\N
2447	1	74	1	Аликово	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2448	1	74	1	Батырева	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2449	1	74	1	Вурнары	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2450	1	74	1	Ибреси	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2451	1	74	1	Канаш	45608	f	f	t	2025-10-26 06:31:32.271245+00	\N
2452	1	74	1	Киря	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2453	1	74	1	Комсомольское	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2454	1	74	1	Красноармейское (Чувашия	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2455	1	74	1	Красные Четаи	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2456	1	74	1	Кугеси	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2457	1	74	1	Мариинский Посад	10186	f	t	t	2025-10-26 06:31:32.271245+00	\N
2458	1	74	1	Моргауши	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2459	1	74	1	Новочебоксарск	124094	f	f	t	2025-10-26 06:31:32.271245+00	\N
2460	1	74	1	Порецкое	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2461	1	74	1	Урмары	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2462	1	74	1	Цивильск	13478	f	t	t	2025-10-26 06:31:32.271245+00	\N
2463	1	74	1	Чебоксары	447929	f	f	t	2025-10-26 06:31:32.271245+00	\N
2464	1	74	1	Шемурша	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2465	1	74	1	Шумерля	33412	f	f	t	2025-10-26 06:31:32.271245+00	\N
2466	1	74	1	Ядрин	9614	f	t	t	2025-10-26 06:31:32.271245+00	\N
2467	1	74	1	Яльчики	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2468	1	74	1	Янтиково	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2469	1	75	4	Анадырь (Чукотский АО	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2470	1	76	2	Губкинский (Ямало-Ненецкий АО	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2471	1	76	2	Заполярный (Ямало-Ненецкий АО	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2472	1	76	2	Муравленко	33401	f	f	t	2025-10-26 06:31:32.271245+00	\N
2473	1	76	2	Надым	46550	f	f	t	2025-10-26 06:31:32.271245+00	\N
2474	1	76	2	Новый Уренгой	104144	f	f	t	2025-10-26 06:31:32.271245+00	\N
2475	1	76	2	Ноябрьск	110572	f	f	t	2025-10-26 06:31:32.271245+00	\N
2476	1	76	2	Пангоды	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2477	1	76	2	Пуровск	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2478	1	76	2	Тарко-Сале	20372	f	t	t	2025-10-26 06:31:32.271245+00	\N
2479	1	77	1	Андропов	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2480	1	77	1	Берендеево	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2481	1	77	1	Большое Село	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2482	1	77	1	Борисоглебский	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2483	1	77	1	Брейтово	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2484	1	77	1	Бурмакино	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2485	1	77	1	Варегово	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2486	1	77	1	Волга	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2487	1	77	1	Гаврилов Ям	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2488	1	77	1	Данилов	15861	f	t	t	2025-10-26 06:31:32.271245+00	\N
2489	1	77	1	Любим	5553	f	t	t	2025-10-26 06:31:32.271245+00	\N
2490	1	77	1	Мышкин	5932	f	t	t	2025-10-26 06:31:32.271245+00	\N
2491	1	77	1	Некрасовское	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2492	1	77	1	Новый Некоуз	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2493	1	77	1	Переславль-Залесский	41923	f	f	t	2025-10-26 06:31:32.271245+00	\N
2494	1	77	1	Пошехонье-Володарск	0	f	f	t	2025-10-26 06:31:32.271245+00	\N
2495	1	77	1	Ростов	31791	f	t	t	2025-10-26 06:31:32.271245+00	\N
2496	1	77	1	Рыбинск	200771	f	t	t	2025-10-26 06:31:32.271245+00	\N
2497	1	77	1	Тутаев	41001	f	t	t	2025-10-26 06:31:32.271245+00	\N
2498	1	77	1	Углич	34505	f	t	t	2025-10-26 06:31:32.271245+00	\N
2499	1	77	1	Ярославль	591486	f	f	t	2025-10-26 06:31:32.271245+00	\N
2500	1	3	3	Майкоп	144055	f	f	t	2025-10-26 06:31:32.271245+00	\N
2501	1	4	5	Яровое	18085	f	f	t	2025-10-26 06:31:32.302027+00	\N
2502	1	5	4	Циолковский	6208	f	f	t	2025-10-26 06:31:32.302027+00	\N
2503	1	6	2	Каргополь	10148	f	t	t	2025-10-26 06:31:32.302027+00	\N
2504	1	6	2	Мирный	37179	f	t	t	2025-10-26 06:31:32.302027+00	\N
2505	1	7	3	Нариманов	11386	f	t	t	2025-10-26 06:31:32.302027+00	\N
2506	1	9	1	Алексеевка	39026	f	t	t	2025-10-26 06:31:32.302027+00	\N
2507	1	9	1	Бирюч	7842	f	t	t	2025-10-26 06:31:32.302027+00	\N
2508	1	10	1	Сельцо	17933	f	f	t	2025-10-26 06:31:32.302027+00	\N
2509	1	11	5	Северобайкальск	23673	f	f	t	2025-10-26 06:31:32.302027+00	\N
2510	1	12	1	Костерево	9136	f	f	t	2025-10-26 06:31:32.302027+00	\N
2511	1	12	1	Курлово	6791	f	f	t	2025-10-26 06:31:32.302027+00	\N
2512	1	12	1	Радужный	43394	f	f	t	2025-10-26 06:31:32.302027+00	\N
2513	1	12	1	Струнино	14372	f	f	t	2025-10-26 06:31:32.302027+00	\N
2514	1	13	3	Волжский	314436	f	f	t	2025-10-26 06:31:32.302027+00	\N
2515	1	13	3	Дубовка	14345	f	t	t	2025-10-26 06:31:32.302027+00	\N
2516	1	13	3	Палласовка	15984	f	t	t	2025-10-26 06:31:32.302027+00	\N
2517	1	13	3	Петров Вал	13264	f	f	t	2025-10-26 06:31:32.302027+00	\N
2518	1	14	2	Красавино	7003	f	f	t	2025-10-26 06:31:32.302027+00	\N
2519	1	15	1	Лиски	55864	f	t	t	2025-10-26 06:31:32.302027+00	\N
2520	1	15	1	Павловск	25126	f	t	t	2025-10-26 06:31:32.302027+00	\N
2521	1	18	1	Наволоки	10207	f	f	t	2025-10-26 06:31:32.302027+00	\N
2522	1	18	1	Плес	2341	f	f	t	2025-10-26 06:31:32.302027+00	\N
2523	1	18	1	Родники	26318	f	t	t	2025-10-26 06:31:32.302027+00	\N
2524	1	72	8	Карабулак	31081	f	f	t	2025-10-26 06:31:32.302027+00	\N
2525	1	72	8	Магас	2505	f	f	t	2025-10-26 06:31:32.302027+00	\N
2526	1	72	8	Сунжа	64493	f	t	t	2025-10-26 06:31:32.302027+00	\N
2527	1	19	5	Свирск	13649	f	f	t	2025-10-26 06:31:32.302027+00	\N
2528	1	19	5	Усолье-Сибирское	83364	f	f	t	2025-10-26 06:31:32.302027+00	\N
2529	1	1	1	Чегем	17988	f	t	t	2025-10-26 06:31:32.302027+00	\N
2530	1	21	2	Калининград	431491	f	f	t	2025-10-26 06:31:32.302027+00	\N
2531	1	21	2	Краснознаменск	36057	f	f	t	2025-10-26 06:31:32.302027+00	\N
2532	1	21	2	Озерск	82268	f	f	t	2025-10-26 06:31:32.302027+00	\N
2533	1	21	2	Пионерский	11017	f	f	t	2025-10-26 06:31:32.302027+00	\N
2534	1	21	2	Приморск	6122	f	f	t	2025-10-26 06:31:32.302027+00	\N
2535	1	21	2	Светлый	21380	f	f	t	2025-10-26 06:31:32.302027+00	\N
2536	1	21	2	Советск	7537	f	f	t	2025-10-26 06:31:32.302027+00	\N
2537	1	22	3	Лагань	14323	f	t	t	2025-10-26 06:31:32.302027+00	\N
2538	1	23	1	Ермолино	10409	f	f	t	2025-10-26 06:31:32.302027+00	\N
2539	1	23	1	Киров	473668	f	f	t	2025-10-26 06:31:32.302027+00	\N
2540	1	23	1	Кременки	11617	f	f	t	2025-10-26 06:31:32.302027+00	\N
2541	1	23	1	Сосенский	12394	f	f	t	2025-10-26 06:31:32.302027+00	\N
2542	1	1	1	Елизово	39548	f	t	t	2025-10-26 06:31:32.302027+00	\N
2543	1	1	1	Березовский	51583	f	f	t	2025-10-26 06:31:32.302027+00	\N
2544	1	1	1	Салаир	8263	f	f	t	2025-10-26 06:31:32.302027+00	\N
2545	1	27	7	Вятские Поляны	35159	f	t	t	2025-10-26 06:31:32.302027+00	\N
2546	1	27	7	Орлов	6959	f	t	t	2025-10-26 06:31:32.302027+00	\N
2547	1	31	5	Бородино	17423	f	f	t	2025-10-26 06:31:32.302027+00	\N
2548	1	31	5	Зеленогорск	66018	f	f	t	2025-10-26 06:31:32.302027+00	\N
2549	1	31	5	Шарыпово	38570	f	f	t	2025-10-26 06:31:32.302027+00	\N
2550	1	1	1	Ялта	76746	f	f	t	2025-10-26 06:31:32.302027+00	\N
2551	1	1	1	Алушта	29078	f	f	t	2025-10-26 06:31:32.302027+00	\N
2552	1	1	1	Армянск	21987	f	f	t	2025-10-26 06:31:32.302027+00	\N
2553	1	1	1	Бахчисарай	27448	f	f	t	2025-10-26 06:31:32.302027+00	\N
2554	1	1	1	Джанкой	38622	f	f	t	2025-10-26 06:31:32.302027+00	\N
2555	1	1	1	Евпатория	105719	f	f	t	2025-10-26 06:31:32.302027+00	\N
2556	1	1	1	Керчь	147033	f	f	t	2025-10-26 06:31:32.302027+00	\N
2557	1	1	1	Красноперекопск	26268	f	f	t	2025-10-26 06:31:32.302027+00	\N
2558	1	1	1	Саки	25146	f	f	t	2025-10-26 06:31:32.302027+00	\N
2559	1	1	1	Симферополь	332317	f	f	t	2025-10-26 06:31:32.302027+00	\N
2560	1	1	1	Старый Крым	9277	f	f	t	2025-10-26 06:31:32.302027+00	\N
2561	1	1	1	Судак	16492	f	f	t	2025-10-26 06:31:32.302027+00	\N
2562	1	1	1	Феодосия	69038	f	f	t	2025-10-26 06:31:32.302027+00	\N
2563	1	1	1	Щелкино	10620	f	f	t	2025-10-26 06:31:32.302027+00	\N
2564	1	33	1	Дмитриев	7721	f	f	t	2025-10-26 06:31:32.302027+00	\N
2565	1	1	1	Кудрово	13501	f	f	t	2025-10-26 06:31:32.302027+00	\N
2566	1	1	1	Любань	4188	f	f	t	2025-10-26 06:31:32.302027+00	\N
2567	1	1	1	Мурино	19775	f	f	t	2025-10-26 06:31:32.302027+00	\N
2568	1	1	1	Новая Ладога	8890	f	f	t	2025-10-26 06:31:32.302027+00	\N
2569	1	1	1	Отрадное	23874	f	f	t	2025-10-26 06:31:32.302027+00	\N
2570	1	1	1	Пикалево	21567	f	f	t	2025-10-26 06:31:32.302027+00	\N
2571	1	1	1	Сясьстрой	13747	f	f	t	2025-10-26 06:31:32.302027+00	\N
2572	1	1	1	Белоозёрский	17842	f	f	t	2025-10-26 06:31:32.302027+00	\N
2573	1	1	1	Голицыно	17447	f	f	t	2025-10-26 06:31:32.302027+00	\N
2574	1	1	1	Ивантеевка	58594	f	f	t	2025-10-26 06:31:32.302027+00	\N
2575	1	1	1	Королёв	183452	f	f	t	2025-10-26 06:31:32.302027+00	\N
2576	1	1	1	Красноармейск	24362	f	f	t	2025-10-26 06:31:32.302027+00	\N
2577	1	1	1	Ликино-Дулёво	31331	f	f	t	2025-10-26 06:31:32.302027+00	\N
2578	1	1	1	Озёры	25788	f	f	t	2025-10-26 06:31:32.302027+00	\N
2579	1	1	1	Пересвет	14142	f	f	t	2025-10-26 06:31:32.302027+00	\N
2580	1	1	1	Протвино	37308	f	f	t	2025-10-26 06:31:32.302027+00	\N
2581	1	1	1	Щёлково	110380	f	t	t	2025-10-26 06:31:32.302027+00	\N
2582	1	38	2	Островной	2177	f	f	t	2025-10-26 06:31:32.302027+00	\N
2583	1	39	7	Саров	92073	f	f	t	2025-10-26 06:31:32.302027+00	\N
2584	1	40	2	Великий Новгород	218724	f	f	t	2025-10-26 06:31:32.302027+00	\N
2585	1	44	1	Дмитровск	5956	f	t	t	2025-10-26 06:31:32.302027+00	\N
2586	1	44	1	Орёл	317854	f	f	t	2025-10-26 06:31:32.302027+00	\N
2587	1	45	7	Городище	8102	f	t	t	2025-10-26 06:31:32.302027+00	\N
2588	1	45	7	Спасск	7442	f	t	t	2025-10-26 06:31:32.302027+00	\N
2589	1	45	7	Сурск	7032	f	f	t	2025-10-26 06:31:32.302027+00	\N
2590	1	46	7	Горнозаводск	12334	f	t	t	2025-10-26 06:31:32.302027+00	\N
2591	1	46	7	Чермоз	4017	f	f	t	2025-10-26 06:31:32.302027+00	\N
2592	1	47	4	Находка	159695	f	f	t	2025-10-26 06:31:32.302027+00	\N
2593	1	49	3	Аксай	41984	f	t	t	2025-10-26 06:31:32.302027+00	\N
2594	1	52	7	Шиханы	6067	f	f	t	2025-10-26 06:31:32.302027+00	\N
2595	1	55	6	Артемовский	32878	f	t	t	2025-10-26 06:31:32.302027+00	\N
2596	1	55	6	Ревда	61713	f	f	t	2025-10-26 06:31:32.302027+00	\N
2597	1	58	8	Железноводск	24496	f	f	t	2025-10-26 06:31:32.302027+00	\N
2598	1	60	7	Болгар	8650	f	t	t	2025-10-26 06:31:32.302027+00	\N
2599	1	60	7	Иннополис	96	f	f	t	2025-10-26 06:31:32.302027+00	\N
2600	1	62	5	Кедровый	2451	f	f	t	2025-10-26 06:31:32.302027+00	\N
2601	1	64	1	Липки	8741	f	f	t	2025-10-26 06:31:32.354014+00	\N
2602	1	64	1	Чекалин	994	f	f	t	2025-10-26 06:31:32.354014+00	\N
2603	1	70	5	Сорск	12140	f	f	t	2025-10-26 06:31:32.354014+00	\N
2604	1	1	1	Белоярский	20283	f	f	t	2025-10-26 06:31:32.354014+00	\N
2605	1	1	1	Когалым	58192	f	f	t	2025-10-26 06:31:32.354014+00	\N
2606	1	1	1	Покачи	17053	f	f	t	2025-10-26 06:31:32.354014+00	\N
2607	1	1	1	Советский	26434	f	t	t	2025-10-26 06:31:32.354014+00	\N
2608	1	71	6	Нязепетровск	12452	f	t	t	2025-10-26 06:31:32.354014+00	\N
2609	1	71	6	Снежинск	48896	f	f	t	2025-10-26 06:31:32.354014+00	\N
2610	1	71	6	Южноуральск	37890	f	f	t	2025-10-26 06:31:32.354014+00	\N
2611	1	1	1	Курчалой	25672	f	t	t	2025-10-26 06:31:32.354014+00	\N
2612	1	1	1	Козловка	10355	f	t	t	2025-10-26 06:31:32.354014+00	\N
2613	1	75	4	Анадырь	13053	f	f	t	2025-10-26 06:31:32.354014+00	\N
2614	1	1	1	Томмот	8054	f	f	t	2025-10-26 06:31:32.354014+00	\N
2615	1	76	2	Губкинский	23340	f	f	t	2025-10-26 06:31:32.354014+00	\N
2616	1	77	1	Гаврилов-Ям	17792	f	t	t	2025-10-26 06:31:32.354014+00	\N
2617	1	77	1	Пошехонье	6085	f	t	t	2025-10-26 06:31:32.354014+00	\N
\.


--
-- Data for Name: companies; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.companies (name, slug, logo, type, trade_activity, business_type, activity_type, description, country, federal_district, region, city, country_id, federal_district_id, region_id, city_id, full_name, inn, ogrn, kpp, registration_date, legal_address, production_address, phone, email, website, total_views, monthly_views, total_purchases, created_at, updated_at, is_active, id) FROM stdin;
СтройДом 4	стройдом-4	\N	ООО	BUYER	GOODS	Строительство	Компания СтройДом 4 в городе Жирновск	Россия			Жирновск	1	3	13	545	СтройДом 4 - полное наименование	3918768410	9852148974188	197157668	2025-10-26 09:40:16.412888	г. Жирновск, ул. Строительная, д. 56	г. Жирновск, ул. Промышленная, д. 38	+79604679883	стройдом-4@mail.ru	https://стройдом-4.ru	0	0	0	2025-10-26 06:40:16.413188	2025-10-26 06:40:16.41319	t	33
Новая компания	novaia-kompaniia	\N	ООО	BOTH	BOTH	Деятельность не указана	\N	Россия	Центральный федеральный округ	Москва	Москва	\N	\N	\N	\N	Полное наименование не указано	1212121212	\N	000000000	2025-10-25 22:42:34.354874	Адрес не указан	\N	895548552544	dmitriy40647274@gmail.com	\N	0	0	0	2025-10-25 19:42:34.355792	2025-10-25 19:42:34.355795	f	29
СтройКонсалт 1	стройконсалт-1	\N	ООО	BOTH	SERVICES	Строительство	Компания СтройКонсалт 1 в городе Городище (Волгоградская обл.	Россия			Городище (Волгоградская обл.	1	3	13	542	СтройКонсалт 1 - полное наименование	6566737958	9396310263194	250726439	2025-10-26 09:40:16.391537	г. Городище (Волгоградская обл., ул. Строительная, д. 21	г. Городище (Волгоградская обл., ул. Промышленная, д. 28	+79349292665	стройконсалт-1@mail.ru	https://стройконсалт-1.ru	0	0	0	2025-10-26 06:40:16.393345	2025-10-26 06:40:16.393347	t	30
СтройТех 2	стройтех-2	\N	ООО	BUYER	GOODS	Строительство	Компания СтройТех 2 в городе Дубовка (Волгоградская обл.	Россия			Дубовка (Волгоградская обл.	1	3	13	543	СтройТех 2 - полное наименование	8432041854	7759953199301	730942016	2025-10-26 09:40:16.40388	г. Дубовка (Волгоградская обл., ул. Строительная, д. 30	г. Дубовка (Волгоградская обл., ул. Промышленная, д. 21	+79635924794	стройтех-2@mail.ru	https://стройтех-2.ru	0	0	0	2025-10-26 06:40:16.404301	2025-10-26 06:40:16.404303	t	31
СтройСервис 3	стройсервис-3	\N	ООО	BOTH	SERVICES	Строительство	Компания СтройСервис 3 в городе Елань	Россия			Елань	1	3	13	544	СтройСервис 3 - полное наименование	9807953603	2186760669123	504810229	2025-10-26 09:40:16.410879	г. Елань, ул. Строительная, д. 43	г. Елань, ул. Промышленная, д. 34	+79644498401	стройсервис-3@mail.ru	https://стройсервис-3.ru	0	0	0	2025-10-26 06:40:16.411268	2025-10-26 06:40:16.41127	t	32
СтройФорум 5	стройфорум-5	\N	ООО	SELLER	GOODS	Строительство	Компания СтройФорум 5 в городе Иловля	Россия			Иловля	1	3	13	546	СтройФорум 5 - полное наименование	6866074839	5847036138583	541925720	2025-10-26 09:40:16.414291	г. Иловля, ул. Строительная, д. 29	г. Иловля, ул. Промышленная, д. 82	+79380997049	стройфорум-5@mail.ru	https://стройфорум-5.ru	0	0	0	2025-10-26 06:40:16.414577	2025-10-26 06:40:16.414579	t	34
СтройСнаб 6	стройснаб-6	\N	ООО	BUYER	SERVICES	Строительство	Компания СтройСнаб 6 в городе Калач-на-Дону	Россия			Калач-на-Дону	1	3	13	547	СтройСнаб 6 - полное наименование	6300876550	9453342696255	719311592	2025-10-26 09:40:16.416981	г. Калач-на-Дону, ул. Строительная, д. 88	г. Калач-на-Дону, ул. Промышленная, д. 89	+79798024754	стройснаб-6@mail.ru	https://стройснаб-6.ru	0	0	0	2025-10-26 06:40:16.417502	2025-10-26 06:40:16.417504	t	35
СтройЭксперт 7	стройэксперт-7	\N	ООО	BUYER	SERVICES	Строительство	Компания СтройЭксперт 7 в городе Камышин	Россия			Камышин	1	3	13	548	СтройЭксперт 7 - полное наименование	6120823135	9055189062565	998221290	2025-10-26 09:40:16.418154	г. Камышин, ул. Строительная, д. 32	г. Камышин, ул. Промышленная, д. 61	+79255207837	стройэксперт-7@mail.ru	https://стройэксперт-7.ru	0	0	0	2025-10-26 06:40:16.418452	2025-10-26 06:40:16.418453	t	36
СтройФорум 8	стройфорум-8	\N	ООО	SELLER	BOTH	Строительство	Компания СтройФорум 8 в городе Кириллов	Россия			Кириллов	1	2	14	549	СтройФорум 8 - полное наименование	3724174191	9475831613337	191031267	2025-10-26 09:40:16.419536	г. Кириллов, ул. Строительная, д. 70	г. Кириллов, ул. Промышленная, д. 82	+79692079818	стройфорум-8@mail.ru	https://стройфорум-8.ru	0	0	0	2025-10-26 06:40:16.419845	2025-10-26 06:40:16.419846	t	37
СтройЦентр 9	стройцентр-9	\N	ООО	BOTH	BOTH	Строительство	Компания СтройЦентр 9 в городе Клетский	Россия			Клетский	1	3	13	550	СтройЦентр 9 - полное наименование	5233041685	7203670046025	575962635	2025-10-26 09:40:16.420876	г. Клетский, ул. Строительная, д. 51	г. Клетский, ул. Промышленная, д. 54	+79434861117	стройцентр-9@mail.ru	https://стройцентр-9.ru	0	0	0	2025-10-26 06:40:16.421157	2025-10-26 06:40:16.421158	t	38
СтройКонсалт 10	стройконсалт-10	\N	ООО	SELLER	BOTH	Строительство	Компания СтройКонсалт 10 в городе Котельниково	Россия			Котельниково	1	3	13	551	СтройКонсалт 10 - полное наименование	6015300268	7310930277013	683571837	2025-10-26 09:40:16.422025	г. Котельниково, ул. Строительная, д. 4	г. Котельниково, ул. Промышленная, д. 34	+79491824170	стройконсалт-10@mail.ru	https://стройконсалт-10.ru	0	0	0	2025-10-26 06:40:16.422292	2025-10-26 06:40:16.422294	t	39
Новая компания	novaia-kompaniia-2362	\N	ООО	BOTH	BOTH	Деятельность не указана	\N	Россия	Центральный федеральный округ	Москва	Москва	\N	\N	\N	\N	345634	0000000000		000000000	2025-10-26 13:44:41.866706	Адрес не указан	\N	+1234567890	dmitriy40647274@gmail.com	\N	0	0	0	2025-10-26 10:44:41.875422	2025-10-26 10:44:41.875424	f	40
Новая компания	novaia-kompaniia-2215	\N	ООО	BOTH	BOTH	Деятельность не указана	\N	BY			тест	\N	\N	\N	\N	Полное наименование не указано	1234567890	1234567890123	000000000	2025-10-26 11:02:55.721954	Адрес не указан	г. Минск, ул. Промышленная, д. 100	+79991112233	testcustom@example.com	\N	0	0	0	2025-10-26 11:02:55.723151	2025-10-26 11:33:53.266556	f	41
Новая компания	novaia-kompaniia-8276	\N	ООО	BOTH	BOTH	Деятельность не указана	\N	RU	FD4	АМУРСКАЯОБЛ	Архара	\N	\N	\N	\N	Полное наименование не указано	1231231231	1231231231231	000000000	2025-10-30 00:00:00	Адрес не указан	fdfgd	895548552544	owner@gmail.com	\N	0	0	0	2025-10-26 11:35:19.497387	2025-10-26 11:35:52.834214	f	42
\.


--
-- Data for Name: company_officials; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.company_officials ("position", full_name, company_id, id) FROM stdin;
Руководитель	Дмитрий Счислёнок Сергеевич	29	5
owner	Пользователь Тестовый	41	6
owner	Дмитрий Счислёнок Сергеевич	42	7
\.


--
-- Data for Name: company_relations; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.company_relations (id, company_id, related_company_id, relation_type, created_at) FROM stdin;
\.


--
-- Data for Name: countries; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.countries (id, code, name, is_active, created_at, updated_at) FROM stdin;
1	RU	Россия	t	2025-10-26 06:31:31.565817+00	\N
2	UA	Украина	t	2025-10-26 06:31:31.565817+00	\N
3	BY	Беларусь	t	2025-10-26 06:31:31.565817+00	\N
4	KZ	Казахстан	t	2025-10-26 06:31:31.565817+00	\N
5			t	2025-10-26 11:07:42.735891+00	\N
\.


--
-- Data for Name: email_change_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.email_change_tokens (id, token, user_id, new_email, created_at, expires_at, is_used) FROM stdin;
\.


--
-- Data for Name: employee_permissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employee_permissions (id, employee_id, permission_key, granted, created_at) FROM stdin;
\.


--
-- Data for Name: employees; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.employees (id, user_id, company_id, email, first_name, last_name, patronymic, phone, "position", role, status, permissions, deletion_requested_at, deletion_requested_by, deletion_rejected_at, created_at, updated_at, created_by) FROM stdin;
\.


--
-- Data for Name: federal_districts; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.federal_districts (id, country_id, name, code, is_active, created_at, updated_at) FROM stdin;
1	1	Центральный федеральный округ	FD1	t	2025-10-26 06:31:31.568373+00	\N
2	1	Северо-Западный федеральный округ	FD2	t	2025-10-26 06:31:31.568373+00	\N
3	1	Южный федеральный округ	FD3	t	2025-10-26 06:31:31.568373+00	\N
4	1	Дальневосточный федеральный округ	FD4	t	2025-10-26 06:31:31.568373+00	\N
5	1	Сибирский федеральный округ	FD5	t	2025-10-26 06:31:31.568373+00	\N
6	1	Уральский федеральный округ	FD6	t	2025-10-26 06:31:31.568373+00	\N
7	1	Приволжский федеральный округ	FD7	t	2025-10-26 06:31:31.568373+00	\N
8	1	Северо-Кавказский федеральный округ	FD8	t	2025-10-26 06:31:31.568373+00	\N
9	1	Тестовый федеральный округ	FD646	t	2025-10-26 10:40:21.957715+00	\N
\.


--
-- Data for Name: messages; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.messages (id, chat_id, sender_company_id, sender_user_id, content, file_path, file_name, file_size, file_type, is_read, created_at, updated_at) FROM stdin;
\.


--
-- Data for Name: order_documents; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_documents (order_id, document_type, document_number, document_date, document_content, document_file_path, is_sent, sent_at, created_at, updated_at, id) FROM stdin;
\.


--
-- Data for Name: order_history; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_history (order_id, changed_by_company_id, change_type, change_description, old_data, new_data, created_at, id) FROM stdin;
\.


--
-- Data for Name: order_items; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.order_items (order_id, product_id, product_name, product_slug, product_description, product_article, product_type, logo_url, quantity, unit_of_measurement, price, amount, "position", created_at, updated_at, id) FROM stdin;
\.


--
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.orders (buyer_order_number, seller_order_number, deal_type, status, buyer_company_id, seller_company_id, invoice_number, contract_number, invoice_date, contract_date, comments, total_amount, created_at, updated_at, id) FROM stdin;
\.


--
-- Data for Name: password_recovery_codes; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.password_recovery_codes (id, email, code, created_at, expires_at, is_used) FROM stdin;
1	dmitriy40647274@gmail.com	771556	2025-10-26 03:25:45.656478+00	2025-10-26 06:40:45.611931+00	t
2	dmitriy40647274@gmail.com	254270	2025-10-26 03:26:59.779985+00	2025-10-26 06:41:59.778087+00	t
3	dmitriy40647274@gmail.com	136949	2025-10-26 03:28:23.986757+00	2025-10-26 06:43:23.984581+00	t
\.


--
-- Data for Name: password_reset_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.password_reset_tokens (id, token, email, created_at, expires_at, is_used) FROM stdin;
\.


--
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.products (name, slug, description, article, type, price, images, characteristics, is_hidden, is_deleted, unit_of_measurement, created_at, updated_at, company_id, id) FROM stdin;
Лейка - Москва	лейка-novaia-kompaniia	Качественный лейка от компании Новая компания. Доставка в Москва.	ART-495288	GOOD	599.0060055033317	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0411\\u0435\\u0442\\u043e\\u043d"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "312x29"}, {"name": "\\u0412\\u0435\\u0441", "value": "64 \\u043a\\u0433"}]	f	f	день	2025-10-26 06:39:48.991995	2025-10-26 06:39:48.991998	29	26
ДСП - Москва	дсп-novaia-kompaniia	Качественный дсп от компании Новая компания. Доставка в Москва.	ART-930827	GOOD	31045.20936405166	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0414\\u0435\\u0440\\u0435\\u0432\\u043e"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "794x992"}, {"name": "\\u0412\\u0435\\u0441", "value": "78 \\u043a\\u0433"}]	f	f	час	2025-10-26 06:39:48.991999	2025-10-26 06:39:48.992	29	27
Рубероид - Москва	рубероид-novaia-kompaniia	Качественный рубероид от компании Новая компания. Доставка в Москва.	ART-749531	GOOD	20595.28759493795	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0411\\u0435\\u0442\\u043e\\u043d"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "261x920"}, {"name": "\\u0412\\u0435\\u0441", "value": "64 \\u043a\\u0433"}]	f	f	м²	2025-10-26 06:39:48.992001	2025-10-26 06:39:48.992001	29	28
Щебень - Москва	щебень-novaia-kompaniia	Качественный щебень от компании Новая компания. Доставка в Москва.	ART-834763	GOOD	33210.485965299784	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0414\\u0435\\u0440\\u0435\\u0432\\u043e"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "500x129"}, {"name": "\\u0412\\u0435\\u0441", "value": "60 \\u043a\\u0433"}]	f	f	м²	2025-10-26 06:39:48.992002	2025-10-26 06:39:48.992002	29	29
Оклейка обоями - Москва	оклейка-обоями-novaia-kompaniia	Качественный оклейка обоями от компании Новая компания. Доставка в Москва.	ART-305479	SERVICE	9061.030785531695	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0411\\u0435\\u0442\\u043e\\u043d"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "572x926"}, {"name": "\\u0412\\u0435\\u0441", "value": "68 \\u043a\\u0433"}]	f	f	час	2025-10-26 06:39:48.992003	2025-10-26 06:39:48.992004	29	30
Керамзит - Москва	керамзит-novaia-kompaniia	Качественный керамзит от компании Новая компания. Доставка в Москва.	ART-127973	GOOD	45905.44868455223	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0411\\u0435\\u0442\\u043e\\u043d"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "929x487"}, {"name": "\\u0412\\u0435\\u0441", "value": "96 \\u043a\\u0433"}]	f	f	шт	2025-10-26 06:39:48.999255	2025-10-26 06:39:48.999262	29	31
Утепление - Москва	утепление-novaia-kompaniia	Качественный утепление от компании Новая компания. Доставка в Москва.	ART-752943	SERVICE	27074.372966595718	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041f\\u043b\\u0430\\u0441\\u0442\\u0438\\u043a"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "259x318"}, {"name": "\\u0412\\u0435\\u0441", "value": "7 \\u043a\\u0433"}]	f	f	час	2025-10-26 06:39:48.999264	2025-10-26 06:39:48.999266	29	32
Плитка - Москва	плитка-novaia-kompaniia	Качественный плитка от компании Новая компания. Доставка в Москва.	ART-450496	GOOD	15557.706845313567	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0421\\u0442\\u0430\\u043b\\u044c"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "860x394"}, {"name": "\\u0412\\u0435\\u0441", "value": "6 \\u043a\\u0433"}]	f	f	шт	2025-10-26 06:39:48.999267	2025-10-26 06:39:48.999268	29	33
Лейка - Москва	лейка-novaia-kompaniia-1	Качественный лейка от компании Новая компания. Доставка в Москва.	ART-373005	GOOD	28843.211164774708	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0421\\u0442\\u0430\\u043b\\u044c"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "285x294"}, {"name": "\\u0412\\u0435\\u0441", "value": "81 \\u043a\\u0433"}]	f	f	час	2025-10-26 06:39:48.99927	2025-10-26 06:39:48.999271	29	34
Рубероид - Москва	рубероид-novaia-kompaniia-1	Качественный рубероид от компании Новая компания. Доставка в Москва.	ART-748243	GOOD	41622.87366367885	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041f\\u043b\\u0430\\u0441\\u0442\\u0438\\u043a"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "94x98"}, {"name": "\\u0412\\u0435\\u0441", "value": "82 \\u043a\\u0433"}]	f	f	кг	2025-10-26 06:39:48.999272	2025-10-26 06:39:48.999273	29	35
Фитинг - Москва	фитинг-novaia-kompaniia	Качественный фитинг от компании Новая компания. Доставка в Москва.	ART-288883	GOOD	4523.555348009512	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0414\\u0435\\u0440\\u0435\\u0432\\u043e"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "782x491"}, {"name": "\\u0412\\u0435\\u0441", "value": "23 \\u043a\\u0433"}]	f	f	м³	2025-10-26 06:39:49.002225	2025-10-26 06:39:49.002228	29	36
Погрузка - Москва	погрузка-novaia-kompaniia	Качественный погрузка от компании Новая компания. Доставка в Москва.	ART-406302	SERVICE	20685.508724269603	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041f\\u043b\\u0430\\u0441\\u0442\\u0438\\u043a"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "69x889"}, {"name": "\\u0412\\u0435\\u0441", "value": "38 \\u043a\\u0433"}]	f	f	час	2025-10-26 06:39:49.00223	2025-10-26 06:39:49.002231	29	37
Песок - Москва	песок-novaia-kompaniia	Качественный песок от компании Новая компания. Доставка в Москва.	ART-877984	GOOD	35125.20880117535	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0414\\u0435\\u0440\\u0435\\u0432\\u043e"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "295x152"}, {"name": "\\u0412\\u0435\\u0441", "value": "11 \\u043a\\u0433"}]	f	f	кг	2025-10-26 06:39:49.002233	2025-10-26 06:39:49.002234	29	38
Монтаж - Москва	монтаж-novaia-kompaniia	Качественный монтаж от компании Новая компания. Доставка в Москва.	ART-914033	SERVICE	46292.134864982516	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041f\\u043b\\u0430\\u0441\\u0442\\u0438\\u043a"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "698x837"}, {"name": "\\u0412\\u0435\\u0441", "value": "98 \\u043a\\u0433"}]	f	f	час	2025-10-26 06:39:49.002235	2025-10-26 06:39:49.002237	29	39
Керамзит - Москва	керамзит-novaia-kompaniia-1	Качественный керамзит от компании Новая компания. Доставка в Москва.	ART-377161	GOOD	31767.53279303227	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0421\\u0442\\u0430\\u043b\\u044c"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "951x341"}, {"name": "\\u0412\\u0435\\u0441", "value": "26 \\u043a\\u0433"}]	f	f	час	2025-10-26 06:39:49.002238	2025-10-26 06:39:49.002239	29	40
Металлочерепица - Москва	металлочерепица-novaia-kompaniia	Качественный металлочерепица от компании Новая компания. Доставка в Москва.	ART-134393	GOOD	25416.683699877824	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0421\\u0442\\u0430\\u043b\\u044c"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "878x859"}, {"name": "\\u0412\\u0435\\u0441", "value": "30 \\u043a\\u0433"}]	f	f	час	2025-10-26 06:39:49.004539	2025-10-26 06:39:49.004541	29	41
Погрузка - Москва	погрузка-novaia-kompaniia-1	Качественный погрузка от компании Новая компания. Доставка в Москва.	ART-429761	SERVICE	43150.37433534256	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041f\\u043b\\u0430\\u0441\\u0442\\u0438\\u043a"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "398x721"}, {"name": "\\u0412\\u0435\\u0441", "value": "99 \\u043a\\u0433"}]	f	f	час	2025-10-26 06:39:49.004543	2025-10-26 06:39:49.004544	29	42
Монтаж - Москва	монтаж-novaia-kompaniia-1	Качественный монтаж от компании Новая компания. Доставка в Москва.	ART-833317	SERVICE	23274.044272255494	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0421\\u0442\\u0430\\u043b\\u044c"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "415x12"}, {"name": "\\u0412\\u0435\\u0441", "value": "95 \\u043a\\u0433"}]	f	f	час	2025-10-26 06:39:49.004545	2025-10-26 06:39:49.004547	29	43
Профнастил - Москва	профнастил-novaia-kompaniia	Качественный профнастил от компании Новая компания. Доставка в Москва.	ART-166075	GOOD	27360.033561090073	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0411\\u0435\\u0442\\u043e\\u043d"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "475x264"}, {"name": "\\u0412\\u0435\\u0441", "value": "65 \\u043a\\u0433"}]	f	f	час	2025-10-26 06:39:49.004548	2025-10-26 06:39:49.004549	29	44
Ведро - Москва	ведро-novaia-kompaniia	Качественный ведро от компании Новая компания. Доставка в Москва.	ART-673299	GOOD	35387.649650736734	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u0414\\u0435\\u0440\\u0435\\u0432\\u043e"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "653x264"}, {"name": "\\u0412\\u0435\\u0441", "value": "58 \\u043a\\u0433"}]	f	f	день	2025-10-26 06:39:49.00455	2025-10-26 06:39:49.004552	29	45
Профнастил Городище (Волгоградская обл.	профнастил-городище-волгоградская-обл	Качественный профнастил в городе Городище (Волгоградская обл.	ART-421025	GOOD	29032.00007065426	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	м²	2025-10-26 06:40:16.40581	2025-10-26 06:40:16.405811	30	46
Сантехника Городище (Волгоградская обл.	сантехника-городище-волгоградская-обл	Качественный сантехника в городе Городище (Волгоградская обл.	ART-443976	SERVICE	23019.30211617523	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	час	2025-10-26 06:40:16.405812	2025-10-26 06:40:16.405813	30	47
Гипсокартон Городище (Волгоградская обл.	гипсокартон-городище-волгоградская-обл	Качественный гипсокартон в городе Городище (Волгоградская обл.	ART-300721	GOOD	47024.63576226869	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	п.м	2025-10-26 06:40:16.405814	2025-10-26 06:40:16.405814	30	48
Монтаж стен Дубовка (Волгоградская обл.	монтаж-стен-дубовка-волгоградская-обл	Качественный монтаж стен в городе Дубовка (Волгоградская обл.	ART-761923	SERVICE	32689.900830778803	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	час	2025-10-26 06:40:16.411996	2025-10-26 06:40:16.411998	31	49
Укладка плитки Дубовка (Волгоградская обл.	укладка-плитки-дубовка-волгоградская-обл	Качественный укладка плитки в городе Дубовка (Волгоградская обл.	ART-202572	SERVICE	44733.24129070338	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	час	2025-10-26 06:40:16.411999	2025-10-26 06:40:16.412	31	50
Фанера Дубовка (Волгоградская обл.	фанера-дубовка-волгоградская-обл	Качественный фанера в городе Дубовка (Волгоградская обл.	ART-298225	GOOD	32629.15294451079	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	т	2025-10-26 06:40:16.412	2025-10-26 06:40:16.412001	31	51
Вагонка Елань	вагонка-елань	Качественный вагонка в городе Елань	ART-707797	GOOD	28742.107917833182	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	т	2025-10-26 06:40:16.413675	2025-10-26 06:40:16.413676	32	52
Монтаж стен Елань	монтаж-стен-елань	Качественный монтаж стен в городе Елань	ART-605553	SERVICE	7826.083004701217	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	час	2025-10-26 06:40:16.413677	2025-10-26 06:40:16.413678	32	53
Бетон Елань	бетон-елань	Качественный бетон в городе Елань	ART-246271	GOOD	35123.52623644164	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	м²	2025-10-26 06:40:16.413679	2025-10-26 06:40:16.413679	32	54
Фанера Жирновск	фанера-жирновск	Качественный фанера в городе Жирновск	ART-972257	GOOD	34418.000293121666	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	м	2025-10-26 06:40:16.415061	2025-10-26 06:40:16.415063	33	55
Профнастил Жирновск	профнастил-жирновск	Качественный профнастил в городе Жирновск	ART-510792	GOOD	36730.3539346021	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	м	2025-10-26 06:40:16.415063	2025-10-26 06:40:16.415064	33	56
Укладка плитки Жирновск	укладка-плитки-жирновск	Качественный укладка плитки в городе Жирновск	ART-403365	SERVICE	46104.02090019493	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	час	2025-10-26 06:40:16.415065	2025-10-26 06:40:16.415065	33	57
Металлочерепица Иловля	металлочерепица-иловля	Качественный металлочерепица в городе Иловля	ART-439765	GOOD	10149.768353794274	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	шт	2025-10-26 06:40:16.415813	2025-10-26 06:40:16.415814	34	58
Плитка Иловля	плитка-иловля	Качественный плитка в городе Иловля	ART-940695	GOOD	34656.462962957674	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	м²	2025-10-26 06:40:16.415815	2025-10-26 06:40:16.415816	34	59
ДСП Калач-на-Дону	дсп-калач-на-дону	Качественный дсп в городе Калач-на-Дону	ART-654546	GOOD	13765.346384688643	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	м³	2025-10-26 06:40:16.418864	2025-10-26 06:40:16.418867	35	60
Сантехника Калач-на-Дону	сантехника-калач-на-дону	Качественный сантехника в городе Калач-на-Дону	ART-786054	SERVICE	25647.63668055316	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	час	2025-10-26 06:40:16.418869	2025-10-26 06:40:16.41887	35	61
Кирпич Калач-на-Дону	кирпич-калач-на-дону	Качественный кирпич в городе Калач-на-Дону	ART-612539	GOOD	33570.40177575026	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	т	2025-10-26 06:40:16.418871	2025-10-26 06:40:16.418872	35	62
Вагонка Камышин	вагонка-камышин	Качественный вагонка в городе Камышин	ART-884569	GOOD	47646.17746561573	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	п.м	2025-10-26 06:40:16.420321	2025-10-26 06:40:16.420323	36	63
Плитка Камышин	плитка-камышин	Качественный плитка в городе Камышин	ART-709879	GOOD	10402.23703295507	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	п.м	2025-10-26 06:40:16.420324	2025-10-26 06:40:16.420324	36	64
Монтаж потолка Кириллов	монтаж-потолка-кириллов	Качественный монтаж потолка в городе Кириллов	ART-816999	SERVICE	23162.08010445502	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	час	2025-10-26 06:40:16.421503	2025-10-26 06:40:16.421504	37	65
Покраска Кириллов	покраска-кириллов	Качественный покраска в городе Кириллов	ART-246516	SERVICE	19499.01743382672	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	час	2025-10-26 06:40:16.421505	2025-10-26 06:40:16.421506	37	66
Цемент Клетский	цемент-клетский	Качественный цемент в городе Клетский	ART-273881	GOOD	27279.503854243747	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	м³	2025-10-26 06:40:16.422643	2025-10-26 06:40:16.422644	38	67
ДСП Клетский	дсп-клетский	Качественный дсп в городе Клетский	ART-540064	GOOD	31665.323555898998	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	шт	2025-10-26 06:40:16.422645	2025-10-26 06:40:16.422646	38	68
Вагонка Котельниково	вагонка-котельниково	Качественный вагонка в городе Котельниково	ART-683028	GOOD	23785.051472620195	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	кг	2025-10-26 06:40:16.423333	2025-10-26 06:40:16.423335	39	69
Вагонка Котельниково	вагонка-котельниково-1	Качественный вагонка в городе Котельниково	ART-184308	GOOD	6172.541050614942	[]	[{"name": "\\u041c\\u0430\\u0442\\u0435\\u0440\\u0438\\u0430\\u043b", "value": "\\u041a\\u0430\\u0447\\u0435\\u0441\\u0442\\u0432\\u0435\\u043d\\u043d\\u044b\\u0439"}, {"name": "\\u0420\\u0430\\u0437\\u043c\\u0435\\u0440", "value": "\\u0421\\u0442\\u0430\\u043d\\u0434\\u0430\\u0440\\u0442\\u043d\\u044b\\u0439"}]	f	f	м³	2025-10-26 06:40:16.423336	2025-10-26 06:40:16.423336	39	70
\.


--
-- Data for Name: regions; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.regions (id, country_id, federal_district_id, name, code, is_active, created_at, updated_at) FROM stdin;
1	1	1	Москва и Московская обл.	МОСКВАИМОСКОВСКАЯ	t	2025-10-26 06:31:31.57218+00	\N
2	1	2	Санкт-Петербург и область	САНКТ-ПЕТЕРБУРГИОБ	t	2025-10-26 06:31:31.57218+00	\N
3	1	3	Адыгея	АДЫГЕЯ	t	2025-10-26 06:31:31.57218+00	\N
4	1	5	Алтайский край	АЛТАЙСКИЙКРАЙ	t	2025-10-26 06:31:31.57218+00	\N
5	1	4	Амурская обл.	АМУРСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
6	1	2	Архангельская обл.	АРХАНГЕЛЬСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
7	1	3	Астраханская обл.	АСТРАХАНСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
8	1	7	Башкортостан(Башкирия	БАШКОРТОСТАН(БАШКИРИ	t	2025-10-26 06:31:31.57218+00	\N
9	1	1	Белгородская обл.	БЕЛГОРОДСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
10	1	1	Брянская обл.	БРЯНСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
11	1	5	Бурятия	БУРЯТИЯ	t	2025-10-26 06:31:31.57218+00	\N
12	1	1	Владимирская обл.	ВЛАДИМИРСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
13	1	3	Волгоградская обл.	ВОЛГОГРАДСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
14	1	2	Вологодская обл.	ВОЛОГОДСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
15	1	1	Воронежская обл.	ВОРОНЕЖСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
16	1	8	Дагестан	ДАГЕСТАН	t	2025-10-26 06:31:31.57218+00	\N
17	1	4	Еврейская обл.	ЕВРЕЙСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
18	1	1	Ивановская обл.	ИВАНОВСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
19	1	5	Иркутская обл.	ИРКУТСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
20	1	1	Кабардино-Балкария	КАБАРДИНО-БАЛКАРИЯ	t	2025-10-26 06:31:31.57218+00	\N
21	1	2	Калининградская обл.	КАЛИНИНГРАДСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
22	1	3	Калмыкия	КАЛМЫКИЯ	t	2025-10-26 06:31:31.57218+00	\N
23	1	1	Калужская обл.	КАЛУЖСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
24	1	1	Камчатская обл.	КАМЧАТСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
25	1	2	Карелия	КАРЕЛИЯ	t	2025-10-26 06:31:31.57218+00	\N
26	1	5	Кемеровская обл.	КЕМЕРОВСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
27	1	7	Кировская обл.	КИРОВСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
28	1	2	Коми	КОМИ	t	2025-10-26 06:31:31.57218+00	\N
29	1	1	Костромская обл.	КОСТРОМСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
30	1	3	Краснодарский край	КРАСНОДАРСКИЙКРАЙ	t	2025-10-26 06:31:31.57218+00	\N
31	1	5	Красноярский край	КРАСНОЯРСКИЙКРАЙ	t	2025-10-26 06:31:31.57218+00	\N
32	1	6	Курганская обл.	КУРГАНСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
33	1	1	Курская обл.	КУРСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
34	1	1	Липецкая обл.	ЛИПЕЦКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
35	1	4	Магаданская обл.	МАГАДАНСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
36	1	7	Марий Эл	МАРИЙЭЛ	t	2025-10-26 06:31:31.57218+00	\N
37	1	7	Мордовия	МОРДОВИЯ	t	2025-10-26 06:31:31.57218+00	\N
38	1	2	Мурманская обл.	МУРМАНСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
39	1	7	Нижегородская (Горьковская	НИЖЕГОРОДСКАЯ(ГОРЬК	t	2025-10-26 06:31:31.57218+00	\N
40	1	2	Новгородская обл.	НОВГОРОДСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
41	1	5	Новосибирская обл.	НОВОСИБИРСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
42	1	5	Омская обл.	ОМСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
43	1	7	Оренбургская обл.	ОРЕНБУРГСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
44	1	1	Орловская обл.	ОРЛОВСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
45	1	7	Пензенская обл.	ПЕНЗЕНСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
46	1	7	Пермский край	ПЕРМСКИЙКРАЙ	t	2025-10-26 06:31:31.57218+00	\N
47	1	4	Приморский край	ПРИМОРСКИЙКРАЙ	t	2025-10-26 06:31:31.57218+00	\N
48	1	2	Псковская обл.	ПСКОВСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
49	1	3	Ростовская обл.	РОСТОВСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
50	1	1	Рязанская обл.	РЯЗАНСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
51	1	7	Самарская обл.	САМАРСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
52	1	7	Саратовская обл.	САРАТОВСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
53	1	4	Саха (Якутия	САХА(ЯКУТИЯ	t	2025-10-26 06:31:31.57218+00	\N
54	1	4	Сахалин	САХАЛИН	t	2025-10-26 06:31:31.57218+00	\N
55	1	6	Свердловская обл.	СВЕРДЛОВСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
56	1	8	Северная Осетия	СЕВЕРНАЯОСЕТИЯ	t	2025-10-26 06:31:31.57218+00	\N
57	1	1	Смоленская обл.	СМОЛЕНСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
58	1	8	Ставропольский край	СТАВРОПОЛЬСКИЙКРАЙ	t	2025-10-26 06:31:31.57218+00	\N
59	1	1	Тамбовская обл.	ТАМБОВСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
60	1	7	Татарстан	ТАТАРСТАН	t	2025-10-26 06:31:31.57218+00	\N
61	1	1	Тверская обл.	ТВЕРСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
62	1	5	Томская обл.	ТОМСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
63	1	1	Тува (Тувинская Респ.	ТУВА(ТУВИНСКАЯРЕСП	t	2025-10-26 06:31:31.57218+00	\N
64	1	1	Тульская обл.	ТУЛЬСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
65	1	6	Тюменская обл. и Ханты-Мансийский АО	ТЮМЕНСКАЯОБЛИХАН	t	2025-10-26 06:31:31.57218+00	\N
66	1	1	Удмуртия	УДМУРТИЯ	t	2025-10-26 06:31:31.57218+00	\N
67	1	7	Ульяновская обл.	УЛЬЯНОВСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
68	1	1	Уральская обл.	УРАЛЬСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
69	1	4	Хабаровский край	ХАБАРОВСКИЙКРАЙ	t	2025-10-26 06:31:31.57218+00	\N
70	1	5	Хакасия	ХАКАСИЯ	t	2025-10-26 06:31:31.57218+00	\N
71	1	6	Челябинская обл.	ЧЕЛЯБИНСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
72	1	8	Чечено-Ингушетия	ЧЕЧЕНО-ИНГУШЕТИЯ	t	2025-10-26 06:31:31.57218+00	\N
73	1	1	Читинская обл.	ЧИТИНСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
74	1	1	Чувашия	ЧУВАШИЯ	t	2025-10-26 06:31:31.57218+00	\N
75	1	4	Чукотский АО	ЧУКОТСКИЙАО	t	2025-10-26 06:31:31.57218+00	\N
76	1	2	Ямало-Ненецкий АО	ЯМАЛО-НЕНЕЦКИЙАО	t	2025-10-26 06:31:31.57218+00	\N
77	1	1	Ярославская обл.	ЯРОСЛАВСКАЯОБЛ	t	2025-10-26 06:31:31.57218+00	\N
78	1	8	Карачаево-Черкесская Республика	КАРАЧАЕВО-ЧЕРКЕССКАЯ	t	2025-10-26 06:31:31.57218+00	\N
\.


--
-- Data for Name: registration_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.registration_tokens (id, token, email, user_id, created_at, expires_at, is_used) FROM stdin;
1	sTGsuM6u2Pddn-BvAtNS3yoqy0rEDvG5mKab2i6zy7k	dmitriy40647274@gmail.com	\N	2025-10-25 09:53:18.405687+00	2025-10-26 09:53:18.405676+00	f
2	lLs5U0e2tCJsU4D1DWUB8QaGV2tK3B7FJz5BpIIEZZo	dmitriy40647274@gmail.com	\N	2025-10-25 09:55:14.455376+00	2025-10-26 09:55:14.455358+00	t
3	AuEzOPTTYoXEL0b_KL-DAwciwtIR8l_3ZsRiijEq1dI	test3@example.com	\N	2025-10-25 10:36:55.500406+00	2025-10-26 10:36:55.500394+00	f
4	WQ7bQr4R0oENwFEJuk-wQhfmNWEFv-CAW3U0zH8q8hE	test4@example.com	\N	2025-10-25 10:37:22.263234+00	2025-10-26 10:37:22.263219+00	t
5	3bc4CE9vBiQOcd-W7LbAHBMRafgQJEFj9TRL1OtDZ5o	test5@example.com	\N	2025-10-25 10:44:35.469849+00	2025-10-26 10:44:35.469837+00	t
6	OldbT1QRkNZKdGOgyBDgd5MUUJxYZAZu0pqjb26d-fw	test@example.com	\N	2025-10-25 16:09:37.498695+00	2025-10-26 19:09:37.498682+00	t
7	GEIT9QpdvTmhnFy69EB1xDXcHvFgzmTh_Sy7KHEH47Y	test@example.com	\N	2025-10-25 16:14:28.540477+00	2025-10-26 19:14:28.540463+00	t
8	bEQWaoBFxs-LQxDP24NqSzPe_n-3oYgeOHdTpPGWxOk	dmitriy40647274@gmail.com	\N	2025-10-25 16:42:15.130978+00	2025-10-26 19:42:15.130967+00	t
9	ccmRa6zCZ5ZKIFGy-ycKbuf2mLhoJgbaWhvGfEcSyxQ	testcompany@example.com	\N	2025-10-26 08:00:43.417556+00	2025-10-27 11:00:43.417544+00	f
10	ARwy2qt7YPO0_hAh9bue8bdJGXAVx2P_FWJBXDN6UFw	testcustom@example.com	\N	2025-10-26 11:02:30.880306+00	2025-10-27 11:02:30.880286+00	t
11	gO79gKvsnaGaApcqOUo0d1fjTUj6DzUnY_Ht_KkEZ7c	owner@gmail.com	\N	2025-10-26 08:35:00.462948+00	2025-10-27 11:35:00.462937+00	t
\.


--
-- Data for Name: units_of_measurement; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.units_of_measurement (name, symbol, code, created_at, updated_at, id) FROM stdin;
Штука	шт	796	2025-10-23 20:56:56.324429	2025-10-23 20:56:56.324429	1
Бобина	боб	616	2025-10-23 20:56:56.326024	2025-10-23 20:56:56.326024	2
Лист	л.	625	2025-10-23 20:56:56.326393	2025-10-23 20:56:56.326393	3
Набор	набор	704	2025-10-23 20:56:56.326752	2025-10-23 20:56:56.326752	4
Пара	пар	715	2025-10-23 20:56:56.327158	2025-10-23 20:56:56.327158	5
Рулон	рул	736	2025-10-23 20:56:56.327506	2025-10-23 20:56:56.327506	6
Миллиметр	мм	003	2025-10-23 20:56:56.327834	2025-10-23 20:56:56.327834	7
Сантиметр	см	004	2025-10-23 20:56:56.328064	2025-10-23 20:56:56.328064	8
Метр	м	006	2025-10-23 20:56:56.328406	2025-10-23 20:56:56.328406	9
Километр	км	008	2025-10-23 20:56:56.328746	2025-10-23 20:56:56.328746	10
Погонный метр	пог. м	018	2025-10-23 20:56:56.329059	2025-10-23 20:56:56.329059	11
Квадратный миллиметр	мм²	050	2025-10-23 20:56:56.329365	2025-10-23 20:56:56.329365	12
Квадратный сантиметр	см²	051	2025-10-23 20:56:56.3297	2025-10-23 20:56:56.3297	13
Квадратный метр	м²	055	2025-10-23 20:56:56.330027	2025-10-23 20:56:56.330027	14
Квадратный километр	км²	061	2025-10-23 20:56:56.330319	2025-10-23 20:56:56.330319	15
Гектар	га	059	2025-10-23 20:56:56.330653	2025-10-23 20:56:56.330653	16
Миллилитр	мл	111	2025-10-23 20:56:56.330927	2025-10-23 20:56:56.330927	17
Литр	л	112	2025-10-23 20:56:56.331162	2025-10-23 20:56:56.331162	18
Кубический миллиметр	мм³	110	2025-10-23 20:56:56.331382	2025-10-23 20:56:56.331382	19
Кубический сантиметр	см³	111	2025-10-23 20:56:56.331611	2025-10-23 20:56:56.331611	20
Кубический метр	м³	113	2025-10-23 20:56:56.331865	2025-10-23 20:56:56.331865	21
Миллиграмм	мг	161	2025-10-23 20:56:56.332088	2025-10-23 20:56:56.332088	22
Грамм	г	163	2025-10-23 20:56:56.332303	2025-10-23 20:56:56.332303	23
Килограмм	кг	166	2025-10-23 20:56:56.332608	2025-10-23 20:56:56.332608	24
Тонна	т	168	2025-10-23 20:56:56.332947	2025-10-23 20:56:56.332947	25
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.users (id, email, first_name, last_name, patronymic, phone, "position", hashed_password, is_active, created_at, updated_at, company_id, role, permissions) FROM stdin;
15	dmitriy40647274@gmail.com	Дмитрий	Счислёнок	Сергеевич	895548552544	\N	$argon2id$v=19$m=65536,t=3,p=4$AEDovbf2/l8rBSDEOOfcuw$w4ns+NRhMPDbiuTTf/FYYDY0h7SmxJAjGodzpHpyrpA	t	2025-10-25 16:42:15.102771+00	2025-10-26 10:44:41.878451+00	40	USER	\N
16	testcompany@example.com	Тест	Компании		+79991234567	\N	\N	f	2025-10-26 08:00:43.366617+00	2025-10-26 08:00:43.36662+00	\N	USER	\N
17	testcustom@example.com	Пользователь	Тестовый		+79991112233	owner	$argon2id$v=19$m=65536,t=3,p=4$LoVwLoVQKqX0fs/ZG8NYCw$9OOeP6pU8J2RBjQLke53mydg3BmZzgoa7aGXz5hdCKw	t	2025-10-26 11:02:30.809554+00	2025-10-26 11:02:55.725635+00	41	OWNER	["view_statistics", "contracts", "documents", "product_management", "user_management", "announcement_management", "sales", "purchases", "messages", "company_management", "chat_access", "authorization"]
18	owner@gmail.com	Дмитрий	Счислёнок	Сергеевич	895548552544	owner	$argon2id$v=19$m=65536,t=3,p=4$CaGUsrb2fu9daw1BKMU4Zw$x5Yvhn0xWnQgN8qEC9rAYe9fcKKvtWjAKm9sxiBWDf4	t	2025-10-26 08:35:00.437347+00	2025-10-26 11:35:19.499761+00	42	OWNER	["company_management", "sales", "messages", "documents", "purchases", "contracts", "view_statistics", "chat_access", "user_management", "authorization", "announcement_management", "product_management"]
\.


--
-- Name: announcements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.announcements_id_seq', 1, false);


--
-- Name: chat_participants_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chat_participants_id_seq', 1, false);


--
-- Name: chats_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.chats_id_seq', 1, false);


--
-- Name: cities_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.cities_id_seq', 69, true);


--
-- Name: companies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.companies_id_seq', 42, true);


--
-- Name: company_officials_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.company_officials_id_seq', 7, true);


--
-- Name: company_relations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.company_relations_id_seq', 1, false);


--
-- Name: countries_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.countries_id_seq', 12, true);


--
-- Name: email_change_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.email_change_tokens_id_seq', 1, false);


--
-- Name: employee_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employee_permissions_id_seq', 1, false);


--
-- Name: employees_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.employees_id_seq', 4, true);


--
-- Name: federal_districts_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.federal_districts_id_seq', 9, true);


--
-- Name: messages_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.messages_id_seq', 1, false);


--
-- Name: order_documents_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_documents_id_seq', 4, true);


--
-- Name: order_history_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_history_id_seq', 16, true);


--
-- Name: order_items_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.order_items_id_seq', 22, true);


--
-- Name: orders_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orders_id_seq', 21, true);


--
-- Name: password_recovery_codes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.password_recovery_codes_id_seq', 3, true);


--
-- Name: password_reset_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.password_reset_tokens_id_seq', 1, false);


--
-- Name: products_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_id_seq', 70, true);


--
-- Name: regions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.regions_id_seq', 53, true);


--
-- Name: registration_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.registration_tokens_id_seq', 11, true);


--
-- Name: units_of_measurement_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.units_of_measurement_id_seq', 25, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 18, true);


--
-- Name: alembic_version alembic_version_pkc; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);


--
-- Name: announcements announcements_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcements
    ADD CONSTRAINT announcements_pkey PRIMARY KEY (id);


--
-- Name: chat_participants chat_participants_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_participants
    ADD CONSTRAINT chat_participants_pkey PRIMARY KEY (id);


--
-- Name: chats chats_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chats
    ADD CONSTRAINT chats_pkey PRIMARY KEY (id);


--
-- Name: cities cities_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_pkey PRIMARY KEY (id);


--
-- Name: companies companies_inn_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_inn_key UNIQUE (inn);


--
-- Name: companies companies_ogrn_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_ogrn_key UNIQUE (ogrn);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: company_officials company_officials_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_officials
    ADD CONSTRAINT company_officials_pkey PRIMARY KEY (id);


--
-- Name: company_relations company_relations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_relations
    ADD CONSTRAINT company_relations_pkey PRIMARY KEY (id);


--
-- Name: countries countries_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.countries
    ADD CONSTRAINT countries_code_key UNIQUE (code);


--
-- Name: countries countries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.countries
    ADD CONSTRAINT countries_pkey PRIMARY KEY (id);


--
-- Name: email_change_tokens email_change_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_change_tokens
    ADD CONSTRAINT email_change_tokens_pkey PRIMARY KEY (id);


--
-- Name: employee_permissions employee_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_permissions
    ADD CONSTRAINT employee_permissions_pkey PRIMARY KEY (id);


--
-- Name: employees employees_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_pkey PRIMARY KEY (id);


--
-- Name: federal_districts federal_districts_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.federal_districts
    ADD CONSTRAINT federal_districts_pkey PRIMARY KEY (id);


--
-- Name: messages messages_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_pkey PRIMARY KEY (id);


--
-- Name: order_documents order_documents_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_documents
    ADD CONSTRAINT order_documents_pkey PRIMARY KEY (id);


--
-- Name: order_history order_history_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_history
    ADD CONSTRAINT order_history_pkey PRIMARY KEY (id);


--
-- Name: order_items order_items_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_pkey PRIMARY KEY (id);


--
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (id);


--
-- Name: password_recovery_codes password_recovery_codes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_recovery_codes
    ADD CONSTRAINT password_recovery_codes_pkey PRIMARY KEY (id);


--
-- Name: password_reset_tokens password_reset_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.password_reset_tokens
    ADD CONSTRAINT password_reset_tokens_pkey PRIMARY KEY (id);


--
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (id);


--
-- Name: regions regions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_pkey PRIMARY KEY (id);


--
-- Name: registration_tokens registration_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration_tokens
    ADD CONSTRAINT registration_tokens_pkey PRIMARY KEY (id);


--
-- Name: units_of_measurement units_of_measurement_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.units_of_measurement
    ADD CONSTRAINT units_of_measurement_pkey PRIMARY KEY (id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: idx_cities_country_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cities_country_id ON public.cities USING btree (country_id);


--
-- Name: idx_cities_federal_district_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cities_federal_district_id ON public.cities USING btree (federal_district_id);


--
-- Name: idx_cities_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cities_is_active ON public.cities USING btree (is_active);


--
-- Name: idx_cities_region_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_cities_region_id ON public.cities USING btree (region_id);


--
-- Name: idx_companies_city_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_companies_city_id ON public.companies USING btree (city_id);


--
-- Name: idx_companies_is_active; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_companies_is_active ON public.companies USING btree (is_active);


--
-- Name: idx_products_active_lookup; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_products_active_lookup ON public.products USING btree (type, is_deleted, is_hidden);


--
-- Name: idx_products_company_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_products_company_id ON public.products USING btree (company_id);


--
-- Name: idx_products_is_deleted; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_products_is_deleted ON public.products USING btree (is_deleted);


--
-- Name: idx_products_is_hidden; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_products_is_hidden ON public.products USING btree (is_hidden);


--
-- Name: idx_products_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX idx_products_type ON public.products USING btree (type);


--
-- Name: ix_announcements_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_announcements_id ON public.announcements USING btree (id);


--
-- Name: ix_chat_participants_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chat_participants_id ON public.chat_participants USING btree (id);


--
-- Name: ix_chats_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_chats_id ON public.chats USING btree (id);


--
-- Name: ix_cities_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_cities_id ON public.cities USING btree (id);


--
-- Name: ix_companies_slug; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_companies_slug ON public.companies USING btree (slug);


--
-- Name: ix_countries_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_countries_id ON public.countries USING btree (id);


--
-- Name: ix_email_change_tokens_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_email_change_tokens_id ON public.email_change_tokens USING btree (id);


--
-- Name: ix_email_change_tokens_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_email_change_tokens_token ON public.email_change_tokens USING btree (token);


--
-- Name: ix_employee_permissions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employee_permissions_id ON public.employee_permissions USING btree (id);


--
-- Name: ix_employees_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employees_email ON public.employees USING btree (email);


--
-- Name: ix_employees_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_employees_id ON public.employees USING btree (id);


--
-- Name: ix_federal_districts_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_federal_districts_id ON public.federal_districts USING btree (id);


--
-- Name: ix_messages_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_messages_id ON public.messages USING btree (id);


--
-- Name: ix_password_recovery_codes_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_password_recovery_codes_email ON public.password_recovery_codes USING btree (email);


--
-- Name: ix_password_recovery_codes_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_password_recovery_codes_id ON public.password_recovery_codes USING btree (id);


--
-- Name: ix_password_reset_tokens_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_password_reset_tokens_id ON public.password_reset_tokens USING btree (id);


--
-- Name: ix_password_reset_tokens_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_password_reset_tokens_token ON public.password_reset_tokens USING btree (token);


--
-- Name: ix_products_slug; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_products_slug ON public.products USING btree (slug);


--
-- Name: ix_regions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_regions_id ON public.regions USING btree (id);


--
-- Name: ix_registration_tokens_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_registration_tokens_id ON public.registration_tokens USING btree (id);


--
-- Name: ix_registration_tokens_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_registration_tokens_token ON public.registration_tokens USING btree (token);


--
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- Name: announcements announcements_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.announcements
    ADD CONSTRAINT announcements_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: chat_participants chat_participants_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_participants
    ADD CONSTRAINT chat_participants_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.chats(id);


--
-- Name: chat_participants chat_participants_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_participants
    ADD CONSTRAINT chat_participants_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: chat_participants chat_participants_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.chat_participants
    ADD CONSTRAINT chat_participants_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: cities cities_country_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id);


--
-- Name: cities cities_federal_district_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_federal_district_id_fkey FOREIGN KEY (federal_district_id) REFERENCES public.federal_districts(id);


--
-- Name: cities cities_region_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.cities
    ADD CONSTRAINT cities_region_id_fkey FOREIGN KEY (region_id) REFERENCES public.regions(id);


--
-- Name: companies companies_city_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_city_id_fkey FOREIGN KEY (city_id) REFERENCES public.cities(id);


--
-- Name: companies companies_country_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id);


--
-- Name: companies companies_federal_district_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_federal_district_id_fkey FOREIGN KEY (federal_district_id) REFERENCES public.federal_districts(id);


--
-- Name: companies companies_region_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_region_id_fkey FOREIGN KEY (region_id) REFERENCES public.regions(id);


--
-- Name: company_officials company_officials_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_officials
    ADD CONSTRAINT company_officials_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: company_relations company_relations_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_relations
    ADD CONSTRAINT company_relations_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: company_relations company_relations_related_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.company_relations
    ADD CONSTRAINT company_relations_related_company_id_fkey FOREIGN KEY (related_company_id) REFERENCES public.companies(id);


--
-- Name: email_change_tokens email_change_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.email_change_tokens
    ADD CONSTRAINT email_change_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- Name: employee_permissions employee_permissions_employee_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employee_permissions
    ADD CONSTRAINT employee_permissions_employee_id_fkey FOREIGN KEY (employee_id) REFERENCES public.employees(id);


--
-- Name: employees employees_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: employees employees_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- Name: employees employees_deletion_requested_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_deletion_requested_by_fkey FOREIGN KEY (deletion_requested_by) REFERENCES public.users(id);


--
-- Name: employees employees_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.employees
    ADD CONSTRAINT employees_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: federal_districts federal_districts_country_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.federal_districts
    ADD CONSTRAINT federal_districts_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id);


--
-- Name: companies fk_companies_city_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT fk_companies_city_id FOREIGN KEY (city_id) REFERENCES public.cities(id);


--
-- Name: companies fk_companies_country_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT fk_companies_country_id FOREIGN KEY (country_id) REFERENCES public.countries(id);


--
-- Name: companies fk_companies_federal_district_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT fk_companies_federal_district_id FOREIGN KEY (federal_district_id) REFERENCES public.federal_districts(id);


--
-- Name: companies fk_companies_region_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT fk_companies_region_id FOREIGN KEY (region_id) REFERENCES public.regions(id);


--
-- Name: users fk_users_company_id; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_company_id FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: messages messages_chat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_chat_id_fkey FOREIGN KEY (chat_id) REFERENCES public.chats(id);


--
-- Name: messages messages_sender_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_sender_company_id_fkey FOREIGN KEY (sender_company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: messages messages_sender_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.messages
    ADD CONSTRAINT messages_sender_user_id_fkey FOREIGN KEY (sender_user_id) REFERENCES public.users(id);


--
-- Name: order_documents order_documents_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_documents
    ADD CONSTRAINT order_documents_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: order_history order_history_changed_by_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_history
    ADD CONSTRAINT order_history_changed_by_company_id_fkey FOREIGN KEY (changed_by_company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: order_history order_history_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_history
    ADD CONSTRAINT order_history_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id);


--
-- Name: order_items order_items_order_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_order_id_fkey FOREIGN KEY (order_id) REFERENCES public.orders(id) ON DELETE CASCADE;


--
-- Name: order_items order_items_product_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.order_items
    ADD CONSTRAINT order_items_product_id_fkey FOREIGN KEY (product_id) REFERENCES public.products(id);


--
-- Name: orders orders_buyer_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_buyer_company_id_fkey FOREIGN KEY (buyer_company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: orders orders_seller_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_seller_company_id_fkey FOREIGN KEY (seller_company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: products products_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id) ON DELETE CASCADE;


--
-- Name: regions regions_country_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id);


--
-- Name: regions regions_federal_district_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.regions
    ADD CONSTRAINT regions_federal_district_id_fkey FOREIGN KEY (federal_district_id) REFERENCES public.federal_districts(id);


--
-- Name: registration_tokens registration_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.registration_tokens
    ADD CONSTRAINT registration_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- PostgreSQL database dump complete
--

\unrestrict CIK6YTj3UJBYwqqUXU3gPQvXK7ZGrvzfYFQE1wChKDnMkNHggEZFwoWmaMdZAYv

