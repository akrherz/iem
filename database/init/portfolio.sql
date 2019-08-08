-- Boilerplate IEM schema_manager_version, the version gets incremented each
-- time we make an upgrade script
CREATE TABLE iem_schema_manager_version(
	version int,
	updated timestamptz);
INSERT into iem_schema_manager_version values (0, now());
GRANT ALL on iem_schema_manager_version to ldm,mesonet;

--
-- Name: abuse; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.abuse (
    userid character varying(30)
);


ALTER TABLE public.abuse OWNER to mesonet;

--
-- Name: admins; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.admins (
    portfolio character varying(50),
    admin text
);


ALTER TABLE public.admins OWNER to mesonet;

--
-- Name: afc_days; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.afc_days (
    portfolio character varying,
    day date,
    fxsiteid character varying(6),
    fxsitename character varying,
    period smallint
);


ALTER TABLE public.afc_days OWNER TO postgres;

--
-- Name: afc_forecasts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.afc_forecasts (
    username character varying,
    portfolio character varying,
    day date,
    high smallint,
    low smallint,
    qpf00 smallint,
    qpf12 smallint,
    pop00 smallint,
    entered timestamp with time zone DEFAULT ('now'::text)::timestamp(6) with time zone,
    pop12 smallint,
    wind14 smallint,
    ceil02 smallint,
    vis02 smallint,
    qsf00 smallint,
    qsf12 smallint
);


ALTER TABLE public.afc_forecasts OWNER TO postgres;

--
-- Name: appregistry; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.appregistry (
    portfolio character varying(50),
    use_calendar boolean DEFAULT true,
    use_dialog boolean DEFAULT true,
    use_forecast boolean DEFAULT true,
    use_quiz boolean DEFAULT true,
    use_chat boolean DEFAULT true
);


ALTER TABLE public.appregistry OWNER TO postgres;

--
-- Name: biosketch; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.biosketch (
    username character varying(50),
    body text,
    updated timestamp with time zone DEFAULT ('now'::text)::timestamp without time zone
);


ALTER TABLE public.biosketch OWNER TO postgres;

--
-- Name: calendar; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.calendar (
    portfolio character varying(50),
    valid timestamp with time zone DEFAULT ('now'::text)::timestamp without time zone,
    description text,
    url character varying(126)
);


ALTER TABLE public.calendar OWNER to mesonet;

--
-- Name: dialog; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.dialog (
    username character varying(50),
    name text,
    gid integer,
    date timestamp with time zone DEFAULT ('now'::text)::timestamp without time zone,
    subject text,
    body text,
    threadid integer,
    second integer,
    oidid oid,
    mimetype text,
    idnum numeric(40,0),
    portfolio character varying(50),
    type character varying(50),
    security character varying(50),
    expires timestamp with time zone,
    touser character varying(50),
    link character varying(300),
    smile integer DEFAULT 0,
    frown integer DEFAULT 0,
    cat_smile integer DEFAULT 0,
    cat_frown integer DEFAULT 0,
    learn_smile integer DEFAULT 0,
    learn_frown integer DEFAULT 0,
    topicid character varying(256)
);


ALTER TABLE public.dialog OWNER to mesonet;

--
-- Name: dialog_1996; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.dialog_1996 (
    subject character varying(100),
    email character varying(100),
    abstract character varying(100),
    title character varying(100),
    fname character varying(100),
    responseto character varying(100),
    affliation character varying(100),
    lname character varying(100),
    body text,
    block_id character varying(100),
    portfolio character varying(30),
    category character varying(30),
    thedate date
);


ALTER TABLE public.dialog_1996 OWNER to mesonet;

--
-- Name: dialog_1997; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.dialog_1997 (
    subject character varying(100),
    email character varying(100),
    abstract character varying(100),
    title character varying(100),
    fname character varying(100),
    responseto character varying(100),
    affliation character varying(100),
    lname character varying(100),
    body text,
    block_id character varying(100),
    portfolio character varying(30),
    category character varying(30),
    thedate date
);


ALTER TABLE public.dialog_1997 OWNER to mesonet;

--
-- Name: dialog_1998; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.dialog_1998 (
    name character(60),
    id character(4),
    category character(60),
    subject character(100),
    thedate character(60),
    block_id character(60),
    body text,
    msgid character(5),
    replythread character(400),
    gen1 character(60),
    gen2 character(60),
    portfolio character varying(20)
);


ALTER TABLE public.dialog_1998 OWNER to mesonet;

--
-- Name: dialog_1999; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.dialog_1999 (
    subject character varying(200),
    thedate date,
    id integer,
    body text,
    category character varying(30),
    block_id character varying(50),
    portfolio character varying(30)
);


ALTER TABLE public.dialog_1999 OWNER to mesonet;

--
-- Name: dialog_2000; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.dialog_2000 (
    subject character varying(2000),
    thedate date,
    id integer,
    body text,
    category character varying(30),
    block_id character varying(50),
    comments text,
    score integer,
    portfolio character varying(30)
);


ALTER TABLE public.dialog_2000 OWNER to mesonet;

--
-- Name: forecast_answers; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.forecast_answers (
    portfolio character varying(20),
    day date,
    local_high integer,
    local_low integer,
    local_prec integer,
    local_snow integer,
    float_high integer,
    float_low integer,
    float_prec integer,
    float_snow integer,
    local_prec_txt character varying(50),
    local_snow_txt character varying(50),
    float_prec_txt character varying(50),
    float_snow_txt character varying(50)
);


ALTER TABLE public.forecast_answers OWNER to mesonet;

--
-- Name: forecast_climo; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.forecast_climo (
    portfolio character varying(20),
    day date,
    local_high integer,
    local_low integer,
    local_prec integer,
    local_snow integer,
    float_high integer,
    float_low integer,
    float_prec integer,
    float_snow integer,
    local_prec_txt character varying(10),
    local_snow_txt character varying(10),
    float_prec_txt character varying(10),
    float_snow_txt character varying(10)
);


ALTER TABLE public.forecast_climo OWNER to mesonet;

--
-- Name: forecast_days; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.forecast_days (
    portfolio character varying(20),
    day date,
    floater_city character varying(40),
    floater_abv character varying(40),
    case_group integer DEFAULT 0
);


ALTER TABLE public.forecast_days OWNER to mesonet;

--
-- Name: forecast_grades; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.forecast_grades (
    userid character varying(50),
    portfolio character varying(20),
    day date,
    local_high integer,
    local_low integer,
    local_prec integer,
    local_snow integer,
    local_err integer,
    float_high integer,
    float_low integer,
    float_prec integer,
    float_snow integer,
    float_err integer,
    total_err integer,
    case_group integer
);


ALTER TABLE public.forecast_grades OWNER to mesonet;

--
-- Name: forecast_totals; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.forecast_totals (
    userid character varying(20),
    portfolio character varying(20),
    local_high integer,
    local_low integer,
    local_prec integer,
    local_snow integer,
    local_err integer,
    float_high integer,
    float_low integer,
    float_prec integer,
    float_snow integer,
    float_err integer,
    p0_total integer,
    p1_total integer DEFAULT 0,
    p2_total integer DEFAULT 0,
    p3_total integer DEFAULT 0
);


ALTER TABLE public.forecast_totals OWNER to mesonet;

--
-- Name: forecasts; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.forecasts (
    userid character varying(40),
    portfolio character varying(20),
    local_high integer,
    local_low integer,
    local_prec integer,
    local_snow integer,
    float_high integer,
    float_low integer,
    float_prec integer,
    float_snow integer,
    day date,
    type character(1) DEFAULT 'g'::bpchar,
    discussion text,
    confidence smallint,
    entered timestamp with time zone DEFAULT now()
);


ALTER TABLE public.forecasts OWNER to mesonet;

--
-- Name: iem_calibration; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.iem_calibration (
    id integer NOT NULL,
    station character varying(10),
    portfolio character varying(10),
    valid timestamp with time zone,
    parameter character varying(10),
    adjustment real,
    final real,
    comments text
);


ALTER TABLE public.iem_calibration OWNER TO postgres;

--
-- Name: iem_calibration_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.iem_calibration_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.iem_calibration_id_seq OWNER TO postgres;

--
-- Name: iem_calibration_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.iem_calibration_id_seq OWNED BY public.iem_calibration.id;


--
-- Name: iem_sensor; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.iem_sensor (
    id integer DEFAULT nextval(('"iem_sensor_id_seq"'::text)::regclass) NOT NULL,
    portfolio character varying(30),
    r_id integer,
    purchased timestamp with time zone,
    o_serial character varying(100)
);


ALTER TABLE public.iem_sensor OWNER TO postgres;

--
-- Name: iem_sensor_history; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.iem_sensor_history (
    portfolio character varying(30),
    o_id integer,
    installed timestamp with time zone,
    removed timestamp with time zone,
    s_id integer
);


ALTER TABLE public.iem_sensor_history OWNER TO postgres;

--
-- Name: iem_sensor_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.iem_sensor_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE public.iem_sensor_id_seq OWNER TO postgres;

--
-- Name: iem_sensors; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.iem_sensors (
    id integer DEFAULT nextval(('"iem_sensors_id_seq"'::text)::regclass) NOT NULL,
    portfolio character varying(30),
    r_name character varying(30),
    r_hid character varying(20),
    r_type character varying(100),
    r_model character varying(50),
    r_vendor character varying(50)
);


ALTER TABLE public.iem_sensors OWNER TO postgres;

--
-- Name: iem_sensors_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.iem_sensors_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE public.iem_sensors_id_seq OWNER TO postgres;

--
-- Name: iem_site_contacts; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.iem_site_contacts (
    id integer DEFAULT nextval(('"iem_site_contacts_id_seq"'::text)::regclass) NOT NULL,
    portfolio character varying(30),
    s_mid character varying(10),
    name character varying(256),
    phone character varying(20),
    email character varying(100)
);


ALTER TABLE public.iem_site_contacts OWNER TO postgres;

--
-- Name: iem_site_contacts_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.iem_site_contacts_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE public.iem_site_contacts_id_seq OWNER TO postgres;

--
-- Name: iem_sites; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.iem_sites (
    id integer DEFAULT nextval(('"iem_sites_id_seq"'::text)::regclass) NOT NULL,
    portfolio character varying(30),
    s_name character varying(100),
    s_hid character varying(20),
    s_nid character varying(5),
    s_mid character varying(10),
    s_lat real,
    s_lon real,
    s_st character varying(40),
    s_elev real,
    entered timestamp with time zone DEFAULT now(),
    s_mid_new character varying(7)
);


ALTER TABLE public.iem_sites OWNER TO postgres;

--
-- Name: iem_sites_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.iem_sites_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE public.iem_sites_id_seq OWNER TO postgres;

--
-- Name: motd; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.motd (
    portfolio character varying(50),
    issue timestamp with time zone DEFAULT ('now'::text)::timestamp without time zone,
    body text,
    id integer DEFAULT nextval(('motd_id_seq'::text)::regclass) NOT NULL
);


ALTER TABLE public.motd OWNER to mesonet;

--
-- Name: motd_id_seq; Type: SEQUENCE; Schema: public; Owner: ldm,mesonet
--

CREATE SEQUENCE public.motd_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE public.motd_id_seq OWNER to mesonet;

--
-- Name: notify; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notify (
    username character varying(50),
    portfolio character varying(50),
    program character varying(300),
    message text,
    idnum integer DEFAULT nextval(('"notify_idnum_seq"'::text)::regclass) NOT NULL,
    entered timestamp with time zone DEFAULT ('now'::text)::timestamp without time zone
);


ALTER TABLE public.notify OWNER TO postgres;

--
-- Name: notify2; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.notify2 (
    username character varying(50),
    portfolio character varying(50),
    program character varying(300),
    message text
);


ALTER TABLE public.notify2 OWNER TO postgres;

--
-- Name: notify_idnum_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.notify_idnum_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE public.notify_idnum_seq OWNER TO postgres;

--
-- Name: pga_forms; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.pga_forms (
    formname character varying(64),
    formsource text
);


ALTER TABLE public.pga_forms OWNER to mesonet;

--
-- Name: pga_layout; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.pga_layout (
    tablename character varying(64),
    nrcols smallint,
    colnames text,
    colwidth text
);


ALTER TABLE public.pga_layout OWNER to mesonet;

--
-- Name: pga_queries; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.pga_queries (
    queryname character varying(64),
    querytype character(1),
    querycommand text,
    querytables text,
    querylinks text,
    queryresults text,
    querycomments text
);


ALTER TABLE public.pga_queries OWNER to mesonet;

--
-- Name: pga_reports; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.pga_reports (
    reportname character varying(64),
    reportsource text,
    reportbody text,
    reportprocs text,
    reportoptions text
);


ALTER TABLE public.pga_reports OWNER to mesonet;

--
-- Name: pga_schema; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.pga_schema (
    schemaname character varying(64),
    schematables text,
    schemalinks text
);


ALTER TABLE public.pga_schema OWNER to mesonet;

--
-- Name: pga_scripts; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.pga_scripts (
    scriptname character varying(64),
    scriptsource text
);


ALTER TABLE public.pga_scripts OWNER to mesonet;

--
-- Name: portfolios; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.portfolios (
    portfolio character varying(50),
    name text,
    about text,
    instructor text,
    passwd character varying(50),
    homepage text,
    fxtime integer,
    porthome character varying(100) DEFAULT '/jportfolio/servlet/'::character varying,
    usesgcp boolean DEFAULT false,
    groupp character varying(50),
    active boolean DEFAULT true
);


ALTER TABLE public.portfolios OWNER to mesonet;

--
-- Name: questions; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.questions (
    qid integer DEFAULT nextval(('questions_qid_seq'::text)::regclass) NOT NULL,
    portfolio character varying(50),
    question text,
    qtype character(1) DEFAULT 'M'::bpchar,
    optiona text DEFAULT 'Z'::text,
    optionb text DEFAULT 'Z'::text,
    optionc text DEFAULT 'Z'::text,
    optiond text DEFAULT 'Z'::text,
    optione text DEFAULT 'Z'::text,
    optionf text DEFAULT 'Z'::text,
    optiong text DEFAULT 'Z'::text,
    optionh text DEFAULT 'Z'::text,
    answer character(1) DEFAULT 'Z'::bpchar
);


ALTER TABLE public.questions OWNER to mesonet;

--
-- Name: questions_qid_seq; Type: SEQUENCE; Schema: public; Owner: ldm,mesonet
--

CREATE SEQUENCE public.questions_qid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE public.questions_qid_seq OWNER to mesonet;

--
-- Name: quizattempts; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.quizattempts (
    userid character varying(50),
    portfolio character varying(50),
    qid integer,
    question1 character(1),
    question2 character(1),
    question3 character(1),
    question1id integer,
    question2id integer,
    question3id integer,
    attempt integer DEFAULT 1,
    entered timestamp with time zone DEFAULT ('now'::text)::timestamp without time zone
);


ALTER TABLE public.quizattempts OWNER to mesonet;

--
-- Name: quizes; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.quizes (
    qname character varying(256),
    quiznum integer DEFAULT nextval(('quizes_quiznum_seq'::text)::regclass) NOT NULL,
    portfolio character varying(50),
    question1 integer,
    question2 integer,
    question3 integer,
    startdate timestamp with time zone,
    stopdate timestamp with time zone,
    attempts integer,
    topicid character varying(256)
);


ALTER TABLE public.quizes OWNER to mesonet;

--
-- Name: quizes_quiznum_seq; Type: SEQUENCE; Schema: public; Owner: ldm,mesonet
--

CREATE SEQUENCE public.quizes_quiznum_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE public.quizes_quiznum_seq OWNER to mesonet;

--
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id smallint UNIQUE,
    name character varying(24),
    isadmin boolean DEFAULT false
);


ALTER TABLE public.roles OWNER TO postgres;

INSERT into roles values (-1, 'Site Admin', 't');
INSERT into roles values (1, 'Portfolio Admin', 't');
INSERT into roles values (2, 'User', 'f');
INSERT into roles values (3, 'Guest', 'f');
INSERT into roles values (4, 'Anonymous', 'f');
INSERT into roles values (5, 'GC Alumni', 'f');
INSERT into roles values (6, 'ICT Guest', 'f');


--
-- Name: scores; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.scores (
    portfolio character varying(50),
    userid character varying(50),
    assign character varying(256),
    app character varying(50),
    score integer,
    possible integer
);


ALTER TABLE public.scores OWNER to mesonet;

--
-- Name: sessions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.sessions (
    username character varying(50),
    login timestamp with time zone DEFAULT ('now'::text)::timestamp without time zone,
    logout timestamp with time zone
);


ALTER TABLE public.sessions OWNER TO postgres;

--
-- Name: students; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.students (
    username character varying(50),
    portfolio character varying(50),
    gid integer DEFAULT '-99'::integer,
    cred smallint,
    nofx boolean DEFAULT false,
    role smallint DEFAULT 2
);


ALTER TABLE public.students OWNER TO postgres;

--
-- Name: temp; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.temp (
    portfolio character varying(50),
    issue timestamp with time zone,
    body text
);


ALTER TABLE public.temp OWNER to mesonet;

--
-- Name: transfer; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.transfer (
    portfolio character varying(50),
    question text,
    qtype character(1),
    optiona text,
    optionb text,
    optionc text,
    optiond text,
    optione text,
    optionf text,
    optiong text,
    optionh text,
    answer text
);


ALTER TABLE public.transfer OWNER to mesonet;

--
-- Name: tt_base; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tt_base (
    id integer DEFAULT nextval(('"tt_base_id_seq"'::text)::regclass) NOT NULL,
    portfolio character varying(30),
    s_mid character varying(10),
    entered timestamp with time zone DEFAULT now(),
    last timestamp with time zone DEFAULT now(),
    closed timestamp with time zone,
    subject character varying(256),
    status character varying(30),
    author character varying(30),
    sensor character varying
);


ALTER TABLE public.tt_base OWNER TO postgres;

--
-- Name: tt_base_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tt_base_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE public.tt_base_id_seq OWNER TO postgres;

--
-- Name: tt_flags; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tt_flags (
    id integer NOT NULL,
    portfolio character varying,
    s_mid character varying,
    vname character varying,
    entered timestamp with time zone DEFAULT now()
);


ALTER TABLE public.tt_flags OWNER TO postgres;

--
-- Name: tt_flags_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tt_flags_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.tt_flags_id_seq OWNER TO postgres;

--
-- Name: tt_flags_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.tt_flags_id_seq OWNED BY public.tt_flags.id;


--
-- Name: tt_log; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.tt_log (
    id integer DEFAULT nextval(('"tt_log_id_seq"'::text)::regclass) NOT NULL,
    portfolio character varying(30),
    s_mid character varying(10),
    entered timestamp with time zone DEFAULT now(),
    author character varying(30),
    status_c character varying(30),
    comments text,
    tt_id integer
);


ALTER TABLE public.tt_log OWNER TO postgres;

--
-- Name: tt_log_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.tt_log_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE public.tt_log_id_seq OWNER TO postgres;

--
-- Name: units; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.units (
    idnum integer DEFAULT nextval(('"units_idnum_seq"'::text)::regclass) NOT NULL,
    blockid integer,
    unitid integer,
    title character varying(256),
    name character varying(256),
    url character varying(256),
    start date,
    portfolio character varying(256)
);


ALTER TABLE public.units OWNER to mesonet;

--
-- Name: units_idnum_seq; Type: SEQUENCE; Schema: public; Owner: ldm,mesonet
--

CREATE SEQUENCE public.units_idnum_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    MAXVALUE 2147483647
    CACHE 1;


ALTER TABLE public.units_idnum_seq OWNER to mesonet;

--
-- Name: users; Type: TABLE; Schema: public; Owner: ldm,mesonet
--

CREATE TABLE public.users (
    fname text,
    lname text,
    passwd character varying(100),
    username character varying(50),
    email text,
    color text,
    picture character varying(100)
);


ALTER TABLE public.users OWNER to mesonet;

--
-- Name: iem_calibration id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.iem_calibration ALTER COLUMN id SET DEFAULT nextval('public.iem_calibration_id_seq'::regclass);


--
-- Name: tt_flags id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.tt_flags ALTER COLUMN id SET DEFAULT nextval('public.tt_flags_id_seq'::regclass);

--
-- Name: afc_days_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX afc_days_idx ON public.afc_days USING btree (portfolio, day);


--
-- Name: afc_forecasts_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX afc_forecasts_idx ON public.afc_forecasts USING btree (username, portfolio, day);


--
-- Name: appregistry_portfolio_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX appregistry_portfolio_key ON public.appregistry USING btree (portfolio);


--
-- Name: calendar_portfolio_idx; Type: INDEX; Schema: public; Owner: ldm,mesonet
--

CREATE INDEX calendar_portfolio_idx ON public.calendar USING btree (portfolio);


--
-- Name: calendar_valid_idx; Type: INDEX; Schema: public; Owner: ldm,mesonet
--

CREATE INDEX calendar_valid_idx ON public.calendar USING btree (valid);


--
-- Name: dailog_idnum_idx; Type: INDEX; Schema: public; Owner: ldm,mesonet
--

CREATE INDEX dailog_idnum_idx ON public.dialog USING btree (idnum);


--
-- Name: dialog_portfolio_idx; Type: INDEX; Schema: public; Owner: ldm,mesonet
--

CREATE INDEX dialog_portfolio_idx ON public.dialog USING btree (portfolio);


--
-- Name: forecasts_portfolio_idx; Type: INDEX; Schema: public; Owner: ldm,mesonet
--

CREATE INDEX forecasts_portfolio_idx ON public.forecasts USING btree (portfolio);


--
-- Name: iem_calibration_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX iem_calibration_idx ON public.iem_calibration USING btree (station, portfolio, valid, parameter);


--
-- Name: iem_sensor_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX iem_sensor_id_key ON public.iem_sensor USING btree (id);


--
-- Name: iem_sensors_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX iem_sensors_id_key ON public.iem_sensors USING btree (id);


--
-- Name: iem_site_contacts_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX iem_site_contacts_id_key ON public.iem_site_contacts USING btree (id);


--
-- Name: iem_sites_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX iem_sites_id_key ON public.iem_sites USING btree (id);


--
-- Name: iem_sites_smid_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX iem_sites_smid_idx ON public.iem_sites USING btree (s_mid);


--
-- Name: motd_id_key; Type: INDEX; Schema: public; Owner: ldm,mesonet
--

CREATE UNIQUE INDEX motd_id_key ON public.motd USING btree (id);


--
-- Name: motd_portfolio_idx; Type: INDEX; Schema: public; Owner: ldm,mesonet
--

CREATE INDEX motd_portfolio_idx ON public.motd USING btree (portfolio);


--
-- Name: notify_idnum_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX notify_idnum_key ON public.notify USING btree (idnum);


--
-- Name: notify_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX notify_idx ON public.notify USING btree (username, portfolio);


--
-- Name: portfolios_portfolio_idx; Type: INDEX; Schema: public; Owner: ldm,mesonet
--

CREATE INDEX portfolios_portfolio_idx ON public.portfolios USING btree (portfolio);


--
-- Name: questions_qid_key; Type: INDEX; Schema: public; Owner: ldm,mesonet
--

CREATE UNIQUE INDEX questions_qid_key ON public.questions USING btree (qid);


--
-- Name: quizes_portfolio_idx; Type: INDEX; Schema: public; Owner: ldm,mesonet
--

CREATE INDEX quizes_portfolio_idx ON public.quizes USING btree (portfolio);


--
-- Name: quizes_quiznum_key; Type: INDEX; Schema: public; Owner: ldm,mesonet
--

CREATE UNIQUE INDEX quizes_quiznum_key ON public.quizes USING btree (quiznum);


--
-- Name: students_portfolio_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_portfolio_idx ON public.students USING btree (portfolio);


--
-- Name: students_username_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX students_username_idx ON public.students USING btree (username);


--
-- Name: tt_base_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX tt_base_id_key ON public.tt_base USING btree (id);


--
-- Name: tt_base_s_mid_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tt_base_s_mid_idx ON public.tt_base USING btree (s_mid);


--
-- Name: tt_log_id_key; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX tt_log_id_key ON public.tt_log USING btree (id);


--
-- Name: tt_log_tt_id_idx; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX tt_log_tt_id_idx ON public.tt_log USING btree (tt_id);


--
-- Name: units_idnum_key; Type: INDEX; Schema: public; Owner: ldm,mesonet
--

CREATE UNIQUE INDEX units_idnum_key ON public.units USING btree (idnum);


--
-- Name: units_idx; Type: INDEX; Schema: public; Owner: ldm,mesonet
--

CREATE UNIQUE INDEX units_idx ON public.units USING btree (blockid, unitid, portfolio);


--
-- Name: users_username_idx; Type: INDEX; Schema: public; Owner: ldm,mesonet
--

CREATE UNIQUE INDEX users_username_idx ON public.users USING btree (username);


--
-- Name: students $1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT "$1" FOREIGN KEY (role) REFERENCES public.roles(id);


--
-- Name: TABLE abuse; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.abuse TO nobody;


--
-- Name: TABLE admins; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.admins TO nobody;


--
-- Name: TABLE afc_days; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.afc_days TO nobody;


--
-- Name: TABLE afc_forecasts; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.afc_forecasts TO nobody;


--
-- Name: TABLE appregistry; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.appregistry TO nobody;


--
-- Name: TABLE biosketch; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.biosketch TO nobody;


--
-- Name: TABLE calendar; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.calendar TO nobody;


--
-- Name: TABLE dialog; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.dialog TO nobody;


--
-- Name: TABLE dialog_1996; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.dialog_1996 TO nobody;


--
-- Name: TABLE dialog_1997; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.dialog_1997 TO nobody;


--
-- Name: TABLE dialog_1998; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.dialog_1998 TO nobody;


--
-- Name: TABLE dialog_1999; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.dialog_1999 TO nobody;


--
-- Name: TABLE dialog_2000; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.dialog_2000 TO nobody;


--
-- Name: TABLE forecast_answers; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.forecast_answers TO nobody;


--
-- Name: TABLE forecast_climo; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.forecast_climo TO nobody;


--
-- Name: TABLE forecast_days; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.forecast_days TO nobody;


--
-- Name: TABLE forecast_grades; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.forecast_grades TO nobody;


--
-- Name: TABLE forecast_totals; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.forecast_totals TO nobody;


--
-- Name: TABLE forecasts; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.forecasts TO nobody;


--
-- Name: TABLE iem_calibration; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.iem_calibration TO nobody;


--
-- Name: SEQUENCE iem_calibration_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.iem_calibration_id_seq TO nobody;


--
-- Name: TABLE iem_sensor; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.iem_sensor TO nobody;


--
-- Name: TABLE iem_sensor_history; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.iem_sensor_history TO nobody;


--
-- Name: SEQUENCE iem_sensor_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.iem_sensor_id_seq TO nobody;


--
-- Name: TABLE iem_sensors; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.iem_sensors TO nobody;


--
-- Name: SEQUENCE iem_sensors_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.iem_sensors_id_seq TO nobody;


--
-- Name: TABLE iem_site_contacts; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.iem_site_contacts TO nobody;


--
-- Name: SEQUENCE iem_site_contacts_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.iem_site_contacts_id_seq TO nobody;


--
-- Name: TABLE iem_sites; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.iem_sites TO nobody;


--
-- Name: SEQUENCE iem_sites_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.iem_sites_id_seq TO nobody;


--
-- Name: TABLE motd; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.motd TO nobody;


--
-- Name: SEQUENCE motd_id_seq; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON SEQUENCE public.motd_id_seq TO nobody;


--
-- Name: TABLE notify; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.notify TO nobody;


--
-- Name: SEQUENCE notify_idnum_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.notify_idnum_seq TO nobody;


--
-- Name: TABLE pga_forms; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.pga_forms TO PUBLIC;


--
-- Name: TABLE pga_layout; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.pga_layout TO PUBLIC;


--
-- Name: TABLE pga_queries; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.pga_queries TO PUBLIC;


--
-- Name: TABLE pga_reports; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.pga_reports TO PUBLIC;


--
-- Name: TABLE pga_schema; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.pga_schema TO PUBLIC;


--
-- Name: TABLE pga_scripts; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.pga_scripts TO PUBLIC;


--
-- Name: TABLE portfolios; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.portfolios TO nobody;


--
-- Name: TABLE questions; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.questions TO nobody;


--
-- Name: SEQUENCE questions_qid_seq; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON SEQUENCE public.questions_qid_seq TO nobody;


--
-- Name: TABLE quizattempts; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.quizattempts TO nobody;


--
-- Name: TABLE quizes; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.quizes TO nobody;


--
-- Name: SEQUENCE quizes_quiznum_seq; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON SEQUENCE public.quizes_quiznum_seq TO nobody;


--
-- Name: TABLE roles; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.roles TO nobody;


--
-- Name: TABLE scores; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.scores TO nobody;


--
-- Name: TABLE sessions; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.sessions TO nobody;


--
-- Name: TABLE students; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.students TO nobody;


--
-- Name: TABLE tt_base; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.tt_base TO nobody;


--
-- Name: SEQUENCE tt_base_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.tt_base_id_seq TO nobody;


--
-- Name: TABLE tt_flags; Type: ACL; Schema: public; Owner: postgres
--

GRANT SELECT ON TABLE public.tt_flags TO nobody;


--
-- Name: TABLE tt_log; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.tt_log TO nobody;


--
-- Name: SEQUENCE tt_log_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.tt_log_id_seq TO nobody;


--
-- Name: TABLE units; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.units TO nobody;


--
-- Name: TABLE users; Type: ACL; Schema: public; Owner: ldm,mesonet
--

GRANT ALL ON TABLE public.users TO nobody;


--
-- PostgreSQL database dump complete
--


--
-- Name: getemail(text); Type: FUNCTION; Schema: public; Owner: ldm,mesonet
--

CREATE FUNCTION public.getemail(text) RETURNS text
    LANGUAGE sql
    AS $_$SELECT email from users 
WHERE username = $1;$_$;


ALTER FUNCTION public.getemail(text) OWNER to mesonet;

--
-- Name: getfxtime(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.getfxtime(text) RETURNS integer
    LANGUAGE sql
    AS $_$SELECT fxtime FROM portfolios
	WHERE portfolio = $1;$_$;


ALTER FUNCTION public.getfxtime(text) OWNER TO postgres;

--
-- Name: getgid4post(numeric); Type: FUNCTION; Schema: public; Owner: ldm,mesonet
--

CREATE FUNCTION public.getgid4post(numeric) RETURNS text
    LANGUAGE sql
    AS $_$SELECT gid::text from dialog
WHERE idnum = $1;$_$;


ALTER FUNCTION public.getgid4post(numeric) OWNER to mesonet;

--
-- Name: getquestiontext(integer); Type: FUNCTION; Schema: public; Owner: ldm,mesonet
--

CREATE FUNCTION public.getquestiontext(integer) RETURNS text
    LANGUAGE sql
    AS $_$SELECT question FROM questions
	WHERE qid = $1;$_$;


ALTER FUNCTION public.getquestiontext(integer) OWNER to mesonet;

--
-- Name: getquizname(integer); Type: FUNCTION; Schema: public; Owner: ldm,mesonet
--

CREATE FUNCTION public.getquizname(integer) RETURNS text
    LANGUAGE sql
    AS $_$SELECT qname::text FROM quizes
	WHERE quiznum = $1;$_$;


ALTER FUNCTION public.getquizname(integer) OWNER to mesonet;

--
-- Name: getroleid(character varying, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.getroleid(character varying, character varying) RETURNS smallint
    LANGUAGE sql
    AS $_$select r.id from roles r, students s  WHERE s.role = r.id and s.username = $1 and s.portfolio = $2$_$;


ALTER FUNCTION public.getroleid(character varying, character varying) OWNER TO postgres;

--
-- Name: getrolename(character varying, character varying); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.getrolename(character varying, character varying) RETURNS character varying
    LANGUAGE sql
    AS $_$select r.name from roles r, students s  WHERE s.role = r.id and s.username = $1 and s.portfolio = $2$_$;


ALTER FUNCTION public.getrolename(character varying, character varying) OWNER TO postgres;

--
-- Name: getsitename(text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.getsitename(text) RETURNS text
    LANGUAGE sql
    AS $_$SELECT s_name::text from iem_sites
        WHERE s_mid = $1;$_$;


ALTER FUNCTION public.getsitename(text) OWNER TO postgres;

--
-- Name: getusergid(text, text); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.getusergid(text, text) RETURNS text
    LANGUAGE sql
    AS $_$SELECT gid::text from students
        WHERE username = $2 and portfolio = $1;$_$;


ALTER FUNCTION public.getusergid(text, text) OWNER TO postgres;

--
-- Name: getusername(text); Type: FUNCTION; Schema: public; Owner: ldm,mesonet
--

CREATE FUNCTION public.getusername(text) RETURNS text
    LANGUAGE sql
    AS $_$SELECT fname||' '||lname as name from users 
	WHERE username = $1;$_$;


ALTER FUNCTION public.getusername(text) OWNER to mesonet;

--
-- Name: totalerrorbycase(text, text, real); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.totalerrorbycase(text, text, real) RETURNS numeric
    LANGUAGE sql
    AS $_$SELECT sum(total_err)::numeric  from forecast_grades WHERE userid = $1 and portfolio = $2 and case_group = $3 ;$_$;


ALTER FUNCTION public.totalerrorbycase(text, text, real) OWNER TO postgres;