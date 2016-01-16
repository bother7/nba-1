--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: current_season_player_gamelogs; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE current_season_player_gamelogs (
    player_gamelogs_id integer NOT NULL,
    season_id integer NOT NULL,
    player_id integer NOT NULL,
    player_name character varying(50) DEFAULT NULL::character varying,
    team_abbreviation character varying(3) NOT NULL,
    team_name character varying(50) DEFAULT NULL::character varying,
    game_id integer NOT NULL,
    game_date timestamp(0) without time zone NOT NULL,
    matchup character varying(50) DEFAULT NULL::character varying,
    wl character varying(1) DEFAULT NULL::character varying,
    min smallint,
    fgm smallint,
    fga smallint,
    fg_pct numeric(4,3) DEFAULT NULL::numeric,
    fg3m smallint,
    fg3a smallint,
    fg3_pct numeric(4,3) DEFAULT NULL::numeric,
    ftm smallint,
    fta smallint,
    ft_pct numeric(4,3) DEFAULT NULL::numeric,
    oreb smallint,
    dreb smallint,
    reb smallint,
    ast smallint,
    stl smallint,
    blk smallint,
    tov smallint,
    pf smallint,
    pts smallint,
    plus_minus smallint,
    dk_points numeric(5,2) DEFAULT NULL::numeric,
    fd_points numeric(5,2) DEFAULT NULL::numeric
);


ALTER TABLE current_season_player_gamelogs OWNER TO postgres;

--
-- Name: current_season_player_gamelogs_player_gamelogs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE current_season_player_gamelogs_player_gamelogs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE current_season_player_gamelogs_player_gamelogs_id_seq OWNER TO postgres;

--
-- Name: current_season_player_gamelogs_player_gamelogs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE current_season_player_gamelogs_player_gamelogs_id_seq OWNED BY current_season_player_gamelogs.player_gamelogs_id;


--
-- Name: games; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE games (
    game_id integer NOT NULL,
    game_date_est timestamp(0) without time zone NOT NULL,
    gamecode character varying(30) NOT NULL,
    visitor_team_id integer NOT NULL,
    visitor_team_code character varying(3) NOT NULL,
    home_team_id integer NOT NULL,
    home_team_code character varying(3) NOT NULL,
    season smallint NOT NULL,
    CONSTRAINT games_home_team_id_check CHECK ((home_team_id > 0)),
    CONSTRAINT games_visitor_team_id_check CHECK ((visitor_team_id > 0))
);


ALTER TABLE games OWNER TO postgres;

--
-- Name: nbastuffer; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE nbastuffer (
    nbastuffer_id integer NOT NULL,
    dataset character varying(30) DEFAULT NULL::character varying,
    gamedate date,
    rest_days character varying(20) NOT NULL,
    days_last_game smallint NOT NULL,
    back_to_back smallint NOT NULL,
    back_to_back_to_back smallint NOT NULL,
    three_in_four smallint NOT NULL,
    four_in_five smallint NOT NULL,
    game_id integer,
    gamecode character varying(20) DEFAULT NULL::character varying,
    team_code character varying(3) NOT NULL,
    opponent_team_code character varying(3) NOT NULL,
    venue character varying(4) NOT NULL,
    away_team character varying(3) DEFAULT NULL::character varying,
    home_team character varying(3) DEFAULT NULL::character varying,
    q1 smallint,
    q2 smallint,
    q3 smallint,
    q4 smallint,
    ot1 character varying(3) DEFAULT NULL::character varying,
    ot2 character varying(3) DEFAULT NULL::character varying,
    ot3 character varying(3) DEFAULT NULL::character varying,
    ot4 character varying(3) DEFAULT NULL::character varying,
    min smallint,
    fgm smallint,
    fga smallint,
    ftm smallint,
    fta smallint,
    fg3m smallint,
    fg3a smallint,
    dreb smallint,
    oreb smallint,
    reb smallint,
    ast smallint,
    stl smallint,
    blk smallint,
    tov smallint,
    to_to smallint,
    pf smallint,
    poss numeric(5,2) DEFAULT NULL::numeric,
    pts smallint,
    opponent_points smallint,
    pace numeric(5,2) DEFAULT NULL::numeric,
    deff numeric(5,2) DEFAULT NULL::numeric,
    oeff numeric(5,2) DEFAULT NULL::numeric,
    moneyline character varying(30) DEFAULT NULL::character varying,
    movements character varying(30) DEFAULT NULL::character varying,
    opening_odds character varying(30) DEFAULT NULL::character varying,
    opening_spread character varying(30) DEFAULT NULL::character varying,
    opening_total character varying(30) DEFAULT NULL::character varying,
    closing character varying(30) DEFAULT NULL::character varying,
    closing_odds character varying(30) DEFAULT NULL::character varying,
    game_ou numeric(5,2) DEFAULT NULL::numeric,
    away_spread numeric(5,2) DEFAULT NULL::numeric,
    home_spread numeric(5,2) DEFAULT NULL::numeric,
    starter1 character varying(30) DEFAULT NULL::character varying,
    starter2 character varying(30) DEFAULT NULL::character varying,
    starter3 character varying(30) DEFAULT NULL::character varying,
    starter4 character varying(30) DEFAULT NULL::character varying,
    starter5 character varying(30) DEFAULT NULL::character varying,
    main_referee character varying(30) DEFAULT NULL::character varying,
    crew_referees character varying(60) DEFAULT NULL::character varying
);


ALTER TABLE nbastuffer OWNER TO postgres;

--
-- Name: nbastuffer_nbastuffer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE nbastuffer_nbastuffer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE nbastuffer_nbastuffer_id_seq OWNER TO postgres;

--
-- Name: nbastuffer_nbastuffer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE nbastuffer_nbastuffer_id_seq OWNED BY nbastuffer.nbastuffer_id;


--
-- Name: player_gamelogs; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE player_gamelogs (
    player_gamelogs_id integer NOT NULL,
    game_id integer NOT NULL,
    player_id integer NOT NULL,
    player_name character varying(50) DEFAULT NULL::character varying,
    team_id integer,
    team_abbreviation character varying(3) DEFAULT NULL::character varying,
    team_city character varying(30) DEFAULT NULL::character varying,
    start_position character varying(3) DEFAULT NULL::character varying,
    comment character varying(255) DEFAULT NULL::character varying,
    season smallint,
    season_id smallint NOT NULL,
    min smallint,
    fgm smallint,
    fga smallint,
    fg_pct numeric,
    fg3m smallint,
    fg3a smallint,
    fg3_pct numeric,
    ftm smallint,
    fta smallint,
    ft_pct numeric,
    oreb smallint,
    dreb smallint,
    reb smallint,
    ast smallint,
    tov smallint,
    stl smallint,
    blk smallint,
    pf smallint,
    pts smallint,
    plus_minus smallint,
    dk_points numeric,
    fd_points numeric,
    wl character(1) DEFAULT NULL::bpchar
);


ALTER TABLE player_gamelogs OWNER TO postgres;

--
-- Name: player_gamelogs_player_gamelogs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE player_gamelogs_player_gamelogs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE player_gamelogs_player_gamelogs_id_seq OWNER TO postgres;

--
-- Name: player_gamelogs_player_gamelogs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE player_gamelogs_player_gamelogs_id_seq OWNED BY player_gamelogs.player_gamelogs_id;


--
-- Name: players; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE players (
    players_id integer NOT NULL,
    person_id integer,
    first_name character varying(25) DEFAULT NULL::character varying,
    last_name character varying(25) DEFAULT NULL::character varying,
    display_first_last character varying(50) DEFAULT NULL::character varying,
    display_last_comma_first character varying(50) DEFAULT NULL::character varying,
    display_fi_last character varying(50) DEFAULT NULL::character varying,
    birthdate date,
    school character varying(50) DEFAULT NULL::character varying,
    country character varying(50) DEFAULT NULL::character varying,
    last_affiliation character varying(50) DEFAULT NULL::character varying,
    height smallint,
    weight smallint,
    season_exp smallint,
    jersey character varying(3) DEFAULT NULL::character varying,
    nbacom_position character varying(20) DEFAULT NULL::character varying,
    rosterstatus character varying(20) DEFAULT NULL::character varying,
    nbacom_team_id integer,
    team_name character varying(30) DEFAULT NULL::character varying,
    team_abbreviation character varying(3) DEFAULT NULL::character varying,
    team_code character varying(30) DEFAULT NULL::character varying,
    team_city character varying(30) DEFAULT NULL::character varying,
    playercode character varying(50) DEFAULT NULL::character varying,
    from_year smallint,
    to_year smallint,
    dleague_flag character varying(100) DEFAULT NULL::character varying,
    primary_position character varying(2) DEFAULT NULL::character varying,
    position_group character varying(5) DEFAULT NULL::character varying
);


ALTER TABLE players OWNER TO postgres;

--
-- Name: players_players_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE players_players_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE players_players_id_seq OWNER TO postgres;

--
-- Name: players_players_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE players_players_id_seq OWNED BY players.players_id;


--
-- Name: rg_stat_summarizer; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE rg_stat_summarizer (
    rg_stat_summarizer_id integer NOT NULL,
    gid integer NOT NULL,
    rg_name character varying(30) NOT NULL,
    espn_id integer,
    espn_name character varying(30) DEFAULT NULL::character varying,
    team character(3) NOT NULL,
    gp boolean,
    gs boolean,
    min smallint,
    fg smallint,
    fga smallint,
    tpm smallint,
    tpa smallint,
    ft smallint,
    fta smallint,
    orb smallint,
    drb smallint,
    rb smallint,
    ast smallint,
    stl smallint,
    blk smallint,
    tov smallint,
    pf smallint,
    dq smallint,
    pm smallint,
    dd boolean,
    td boolean,
    fanduel_pts numeric(5,2) DEFAULT NULL::numeric,
    draftkings_pts numeric(5,2) DEFAULT NULL::numeric,
    draftday_pts numeric(5,2) DEFAULT NULL::numeric,
    fanduel_position character(2) DEFAULT NULL::bpchar,
    fanduel_salary smallint,
    draftkings_position character(2) DEFAULT NULL::bpchar,
    draftkings_salary smallint,
    draftday_position character(2) DEFAULT NULL::bpchar,
    draftday_salary smallint,
    team_pts smallint,
    oppt_pts smallint,
    total_pts smallint
);


ALTER TABLE rg_stat_summarizer OWNER TO postgres;

--
-- Name: rg_stat_summarizer_rg_stat_summarizer_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE rg_stat_summarizer_rg_stat_summarizer_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE rg_stat_summarizer_rg_stat_summarizer_id_seq OWNER TO postgres;

--
-- Name: rg_stat_summarizer_rg_stat_summarizer_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE rg_stat_summarizer_rg_stat_summarizer_id_seq OWNED BY rg_stat_summarizer.rg_stat_summarizer_id;


--
-- Name: salaries; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE salaries (
    salaries_id integer NOT NULL,
    nbacom_player_id integer NOT NULL,
    site_player_name character varying(50) NOT NULL,
    game_date timestamp(0) without time zone NOT NULL,
    site character(2) NOT NULL,
    site_position character(2) DEFAULT NULL::bpchar,
    salary smallint NOT NULL
);


ALTER TABLE salaries OWNER TO postgres;

--
-- Name: salaries_salaries_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE salaries_salaries_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE salaries_salaries_id_seq OWNER TO postgres;

--
-- Name: salaries_salaries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE salaries_salaries_id_seq OWNED BY salaries.salaries_id;


--
-- Name: team_gamelogs; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE team_gamelogs (
    team_gamelogs_id integer NOT NULL,
    team_id integer NOT NULL,
    team_abbreviation character varying(3) NOT NULL,
    game_id integer NOT NULL,
    game_date timestamp(0) without time zone NOT NULL,
    season smallint NOT NULL,
    season_id integer NOT NULL,
    matchup character varying(30) NOT NULL,
    away_team_abbreviation character(3) NOT NULL,
    home_away character(1) DEFAULT NULL::bpchar,
    home_team_abbreviation character(3) NOT NULL,
    wl character(1),
    minutes smallint,
    fgm smallint,
    fga smallint,
    fg_pct numeric(4,3) DEFAULT NULL::numeric,
    fg3m smallint,
    fg3a smallint,
    fg3_pct numeric(4,3) DEFAULT NULL::numeric,
    ftm smallint,
    fta smallint,
    ft_pct numeric(4,3) DEFAULT NULL::numeric,
    oreb smallint,
    dreb smallint,
    reb smallint,
    ast smallint,
    tov smallint,
    stl smallint,
    blk smallint,
    pf smallint,
    pts smallint,
    plus_minus smallint,
    opponent_pts smallint
);


ALTER TABLE team_gamelogs OWNER TO postgres;

--
-- Name: team_gamelogs_team_gamelogs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE team_gamelogs_team_gamelogs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE team_gamelogs_team_gamelogs_id_seq OWNER TO postgres;

--
-- Name: team_gamelogs_team_gamelogs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE team_gamelogs_team_gamelogs_id_seq OWNED BY team_gamelogs.team_gamelogs_id;


--
-- Name: team_stats_game; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE team_stats_game (
    team_stats_game_id integer NOT NULL,
    statdate date NOT NULL,
    season smallint NOT NULL,
    team_id integer NOT NULL,
    gp smallint NOT NULL,
    w smallint NOT NULL,
    l smallint NOT NULL,
    min smallint NOT NULL,
    off_rating numeric(5,2) NOT NULL,
    def_rating numeric(5,2) NOT NULL,
    net_rating numeric(5,2) NOT NULL,
    ast_pct numeric(5,3) NOT NULL,
    ast_to numeric(5,3) NOT NULL,
    ast_ratio numeric(5,3) NOT NULL,
    oreb_pct numeric(5,3) NOT NULL,
    dreb_pct numeric(5,3) NOT NULL,
    reb_pct numeric(5,3) NOT NULL,
    tm_tov_pct numeric(5,3) NOT NULL,
    efg_pct numeric(5,3) NOT NULL,
    ts_pct numeric(5,3) NOT NULL,
    pace numeric(5,2) NOT NULL,
    pie numeric(5,3) NOT NULL
);


ALTER TABLE team_stats_game OWNER TO postgres;

--
-- Name: team_stats_game_team_stats_game_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE team_stats_game_team_stats_game_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE team_stats_game_team_stats_game_id_seq OWNER TO postgres;

--
-- Name: team_stats_game_team_stats_game_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE team_stats_game_team_stats_game_id_seq OWNED BY team_stats_game.team_stats_game_id;


--
-- Name: teamgames; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE teamgames (
    teamgames_id integer NOT NULL,
    game_id integer NOT NULL,
    gamecode character(16) NOT NULL,
    game_date_est timestamp(0) without time zone NOT NULL,
    season smallint NOT NULL,
    team_id integer NOT NULL,
    team_code character(3) NOT NULL,
    opponent_team_id integer NOT NULL,
    opponent_team_code character(3) NOT NULL,
    is_home boolean NOT NULL,
    gamenum smallint
);


ALTER TABLE teamgames OWNER TO postgres;

--
-- Name: teamgames_teamgames_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE teamgames_teamgames_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE teamgames_teamgames_id_seq OWNER TO postgres;

--
-- Name: teamgames_teamgames_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE teamgames_teamgames_id_seq OWNED BY teamgames.teamgames_id;


--
-- Name: teams; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE teams (
    teams_id integer NOT NULL,
    nbacom_team_id integer DEFAULT 0 NOT NULL,
    team_code character varying(3) NOT NULL
);


ALTER TABLE teams OWNER TO postgres;

--
-- Name: teams_teams_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE teams_teams_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE teams_teams_id_seq OWNER TO postgres;

--
-- Name: teams_teams_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE teams_teams_id_seq OWNED BY teams.teams_id;


--
-- Name: yearly_playerstats_advanced; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE yearly_playerstats_advanced (
    yearly_playerstats_advanced_id integer NOT NULL,
    player_id integer NOT NULL,
    player_name character varying(30) NOT NULL,
    team_id integer NOT NULL,
    team_abbreviation character varying(3) NOT NULL,
    season smallint NOT NULL,
    age smallint NOT NULL,
    gp smallint NOT NULL,
    w smallint NOT NULL,
    l smallint NOT NULL,
    w_pct numeric(5,2) NOT NULL,
    min smallint NOT NULL,
    off_rating numeric(5,2) NOT NULL,
    def_rating numeric(5,2) NOT NULL,
    net_rating numeric(5,2) NOT NULL,
    ast_pct numeric(5,2) NOT NULL,
    ast_to numeric(5,2) NOT NULL,
    ast_ratio numeric(5,2) NOT NULL,
    oreb_pct numeric(5,2) NOT NULL,
    dreb_pct numeric(5,2) NOT NULL,
    reb_pct numeric(5,2) NOT NULL,
    tm_tov_pct numeric(5,2) NOT NULL,
    efg_pct numeric(5,2) NOT NULL,
    ts_pct numeric(5,2) NOT NULL,
    usg_pct numeric(5,2) NOT NULL,
    pace numeric(5,2) NOT NULL,
    pie numeric(5,2) NOT NULL,
    cfid smallint NOT NULL,
    cfparams character varying(30) NOT NULL
);


ALTER TABLE yearly_playerstats_advanced OWNER TO postgres;

--
-- Name: yearly_playerstats_advanced_yearly_playerstats_advanced_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE yearly_playerstats_advanced_yearly_playerstats_advanced_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE yearly_playerstats_advanced_yearly_playerstats_advanced_id_seq OWNER TO postgres;

--
-- Name: yearly_playerstats_advanced_yearly_playerstats_advanced_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE yearly_playerstats_advanced_yearly_playerstats_advanced_id_seq OWNED BY yearly_playerstats_advanced.yearly_playerstats_advanced_id;


--
-- Name: yearly_playerstats_basic; Type: TABLE; Schema: public; Owner: postgres; Tablespace: 
--

CREATE TABLE yearly_playerstats_basic (
    yearly_playerstats_basic_id integer NOT NULL,
    player_id integer NOT NULL,
    player_name character varying(30) NOT NULL,
    team_id integer NOT NULL,
    team_abbreviation character varying(3) NOT NULL,
    season smallint NOT NULL,
    age smallint,
    gp smallint NOT NULL,
    w smallint NOT NULL,
    l smallint NOT NULL,
    w_pct numeric(5,2) NOT NULL,
    min smallint NOT NULL,
    fgm smallint NOT NULL,
    fga smallint NOT NULL,
    fg_pct numeric(5,2) NOT NULL,
    fg3m smallint NOT NULL,
    fg3a smallint NOT NULL,
    fg3_pct numeric(5,2) NOT NULL,
    ftm smallint NOT NULL,
    fta smallint NOT NULL,
    ft_pct numeric(5,2) NOT NULL,
    oreb smallint NOT NULL,
    dreb smallint NOT NULL,
    reb smallint NOT NULL,
    ast smallint NOT NULL,
    tov smallint NOT NULL,
    stl smallint NOT NULL,
    blk smallint NOT NULL,
    blka smallint NOT NULL,
    pf smallint NOT NULL,
    pfd smallint NOT NULL,
    pts smallint NOT NULL,
    plus_minus smallint NOT NULL,
    dd2 smallint NOT NULL,
    td3 smallint NOT NULL,
    cfid smallint,
    cfparams character varying(50) DEFAULT NULL::character varying
);


ALTER TABLE yearly_playerstats_basic OWNER TO postgres;

--
-- Name: yearly_playerstats_basic_yearly_playerstats_basic_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE yearly_playerstats_basic_yearly_playerstats_basic_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE yearly_playerstats_basic_yearly_playerstats_basic_id_seq OWNER TO postgres;

--
-- Name: yearly_playerstats_basic_yearly_playerstats_basic_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE yearly_playerstats_basic_yearly_playerstats_basic_id_seq OWNED BY yearly_playerstats_basic.yearly_playerstats_basic_id;


--
-- Name: player_gamelogs_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY current_season_player_gamelogs ALTER COLUMN player_gamelogs_id SET DEFAULT nextval('current_season_player_gamelogs_player_gamelogs_id_seq'::regclass);


--
-- Name: nbastuffer_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY nbastuffer ALTER COLUMN nbastuffer_id SET DEFAULT nextval('nbastuffer_nbastuffer_id_seq'::regclass);


--
-- Name: player_gamelogs_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY player_gamelogs ALTER COLUMN player_gamelogs_id SET DEFAULT nextval('player_gamelogs_player_gamelogs_id_seq'::regclass);


--
-- Name: players_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY players ALTER COLUMN players_id SET DEFAULT nextval('players_players_id_seq'::regclass);


--
-- Name: rg_stat_summarizer_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY rg_stat_summarizer ALTER COLUMN rg_stat_summarizer_id SET DEFAULT nextval('rg_stat_summarizer_rg_stat_summarizer_id_seq'::regclass);


--
-- Name: salaries_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY salaries ALTER COLUMN salaries_id SET DEFAULT nextval('salaries_salaries_id_seq'::regclass);


--
-- Name: team_gamelogs_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY team_gamelogs ALTER COLUMN team_gamelogs_id SET DEFAULT nextval('team_gamelogs_team_gamelogs_id_seq'::regclass);


--
-- Name: team_stats_game_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY team_stats_game ALTER COLUMN team_stats_game_id SET DEFAULT nextval('team_stats_game_team_stats_game_id_seq'::regclass);


--
-- Name: teamgames_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY teamgames ALTER COLUMN teamgames_id SET DEFAULT nextval('teamgames_teamgames_id_seq'::regclass);


--
-- Name: teams_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY teams ALTER COLUMN teams_id SET DEFAULT nextval('teams_teams_id_seq'::regclass);


--
-- Name: yearly_playerstats_advanced_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY yearly_playerstats_advanced ALTER COLUMN yearly_playerstats_advanced_id SET DEFAULT nextval('yearly_playerstats_advanced_yearly_playerstats_advanced_id_seq'::regclass);


--
-- Name: yearly_playerstats_basic_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY yearly_playerstats_basic ALTER COLUMN yearly_playerstats_basic_id SET DEFAULT nextval('yearly_playerstats_basic_yearly_playerstats_basic_id_seq'::regclass);


--
-- Name: current_season_player_gamelogs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY current_season_player_gamelogs
    ADD CONSTRAINT current_season_player_gamelogs_pkey PRIMARY KEY (player_gamelogs_id);


--
-- Name: games_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY games
    ADD CONSTRAINT games_pkey PRIMARY KEY (game_id);


--
-- Name: nbastuffer_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY nbastuffer
    ADD CONSTRAINT nbastuffer_pkey PRIMARY KEY (nbastuffer_id);


--
-- Name: person_id; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY players
    ADD CONSTRAINT person_id UNIQUE (person_id);


--
-- Name: player_gamelogs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY player_gamelogs
    ADD CONSTRAINT player_gamelogs_pkey PRIMARY KEY (player_gamelogs_id);


--
-- Name: players_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY players
    ADD CONSTRAINT players_pkey PRIMARY KEY (players_id);


--
-- Name: rg_stat_summarizer_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY rg_stat_summarizer
    ADD CONSTRAINT rg_stat_summarizer_pkey PRIMARY KEY (rg_stat_summarizer_id);


--
-- Name: salaries_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY salaries
    ADD CONSTRAINT salaries_pkey PRIMARY KEY (salaries_id);


--
-- Name: team_gamelogs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY team_gamelogs
    ADD CONSTRAINT team_gamelogs_pkey PRIMARY KEY (team_gamelogs_id);


--
-- Name: team_stats_game_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY team_stats_game
    ADD CONSTRAINT team_stats_game_pkey PRIMARY KEY (team_stats_game_id);


--
-- Name: teamgames_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY teamgames
    ADD CONSTRAINT teamgames_pkey PRIMARY KEY (teamgames_id);


--
-- Name: teams_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (teams_id);


--
-- Name: yearly_playerstats_advanced_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY yearly_playerstats_advanced
    ADD CONSTRAINT yearly_playerstats_advanced_pkey PRIMARY KEY (yearly_playerstats_advanced_id);


--
-- Name: yearly_playerstats_basic_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres; Tablespace: 
--

ALTER TABLE ONLY yearly_playerstats_basic
    ADD CONSTRAINT yearly_playerstats_basic_pkey PRIMARY KEY (yearly_playerstats_basic_id);


--
-- Name: current_season_player_gamelog_dk_points_player_name_player__idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX current_season_player_gamelog_dk_points_player_name_player__idx ON current_season_player_gamelogs USING btree (dk_points, player_name, player_id);


--
-- Name: current_season_player_gamelog_team_abbreviation_game_id_gam_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX current_season_player_gamelog_team_abbreviation_game_id_gam_idx ON current_season_player_gamelogs USING btree (team_abbreviation, game_id, game_date);


--
-- Name: current_season_player_gamelog_team_abbreviation_game_id_pla_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX current_season_player_gamelog_team_abbreviation_game_id_pla_idx ON current_season_player_gamelogs USING btree (team_abbreviation, game_id, player_id);


--
-- Name: current_season_player_gamelog_team_abbreviation_player_name_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX current_season_player_gamelog_team_abbreviation_player_name_idx ON current_season_player_gamelogs USING btree (team_abbreviation, player_name, dk_points);


--
-- Name: current_season_player_gamelogs_game_id_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX current_season_player_gamelogs_game_id_idx ON current_season_player_gamelogs USING btree (game_id);


--
-- Name: current_season_player_gamelogs_player_id_dk_points_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX current_season_player_gamelogs_player_id_dk_points_idx ON current_season_player_gamelogs USING btree (player_id, dk_points);


--
-- Name: current_season_player_gamelogs_team_abbreviation_game_date_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX current_season_player_gamelogs_team_abbreviation_game_date_idx ON current_season_player_gamelogs USING btree (team_abbreviation, game_date);


--
-- Name: dk_points; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX dk_points ON player_gamelogs USING btree (dk_points);


--
-- Name: game_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX game_id ON player_gamelogs USING btree (game_id);


--
-- Name: game_player_season; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX game_player_season ON player_gamelogs USING btree (game_id, player_id, season_id);


--
-- Name: idx_gamecode_gameid_gamedate; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX idx_gamecode_gameid_gamedate ON games USING btree (gamecode, game_id, game_date_est);


--
-- Name: idx_gameid_gamedate; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX idx_gameid_gamedate ON games USING btree (game_id, game_date_est);


--
-- Name: idx_home_gamedate; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX idx_home_gamedate ON games USING btree (game_date_est, home_team_code);


--
-- Name: idx_player_game_salary; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX idx_player_game_salary ON salaries USING btree (game_date, nbacom_player_id, salary);


--
-- Name: idx_player_person_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX idx_player_person_id ON players USING btree (person_id, display_first_last);


--
-- Name: idx_playername_game_salary; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX idx_playername_game_salary ON salaries USING btree (game_date, site_player_name, salary);


--
-- Name: idx_position_salary; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX idx_position_salary ON salaries USING btree (site_position, salary);


--
-- Name: idx_vis_gamedate; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX idx_vis_gamedate ON games USING btree (game_date_est, visitor_team_code);


--
-- Name: player_id; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX player_id ON player_gamelogs USING btree (game_id, player_id, dk_points);


--
-- Name: player_name; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX player_name ON player_gamelogs USING btree (player_name);


--
-- Name: player_season_game; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX player_season_game ON player_gamelogs USING btree (player_name, game_id, season_id);


--
-- Name: player_season_game_pts; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX player_season_game_pts ON player_gamelogs USING btree (player_id, season_id, game_id, dk_points);


--
-- Name: salaries_nbacom_player_id_site_game_date_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX salaries_nbacom_player_id_site_game_date_idx ON salaries USING btree (nbacom_player_id, site, game_date);


--
-- Name: salaries_site_game_date_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX salaries_site_game_date_idx ON salaries USING btree (site, game_date);


--
-- Name: season; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX season ON player_gamelogs USING btree (season);


--
-- Name: team_abbreviation; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX team_abbreviation ON player_gamelogs USING btree (team_abbreviation);


--
-- Name: team_code; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX team_code ON teams USING btree (team_code, nbacom_team_id);


--
-- Name: teamgames_game_date_est_gamecode_team_code_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX teamgames_game_date_est_gamecode_team_code_idx ON teamgames USING btree (game_date_est, gamecode, team_code);


--
-- Name: teamgames_game_date_est_opponent_team_code_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX teamgames_game_date_est_opponent_team_code_idx ON teamgames USING btree (game_date_est, opponent_team_code);


--
-- Name: teamgames_game_date_est_team_code_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX teamgames_game_date_est_team_code_idx ON teamgames USING btree (game_date_est, team_code);


--
-- Name: teamgames_team_code_is_home_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX teamgames_team_code_is_home_idx ON teamgames USING btree (team_code, is_home);


--
-- Name: teamgames_team_code_opponent_team_code_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX teamgames_team_code_opponent_team_code_idx ON teamgames USING btree (team_code, opponent_team_code);


--
-- Name: teamgames_team_code_opponent_team_code_is_home_idx; Type: INDEX; Schema: public; Owner: postgres; Tablespace: 
--

CREATE INDEX teamgames_team_code_opponent_team_code_is_home_idx ON teamgames USING btree (team_code, opponent_team_code, is_home);


--
-- Name: current_season_player_gamelogs_ibfk_1; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY current_season_player_gamelogs
    ADD CONSTRAINT current_season_player_gamelogs_ibfk_1 FOREIGN KEY (game_id) REFERENCES games(game_id) ON UPDATE SET NULL ON DELETE SET NULL;


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

