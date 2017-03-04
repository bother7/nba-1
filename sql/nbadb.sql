--
-- PostgreSQL database dump
--

-- Dumped from database version 9.5.5
-- Dumped by pg_dump version 9.5.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

--
-- Name: refreshallmaterializedviews(text, boolean); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION refreshallmaterializedviews(_schema text DEFAULT '*'::text, _concurrently boolean DEFAULT false) RETURNS integer
    LANGUAGE plpgsql
    AS $$
  DECLARE
    r RECORD;
  BEGIN
    RAISE NOTICE 'Refreshing materialized view(s) in % %', CASE WHEN _schema = '*' THEN 'all schemas' ELSE 'schema "'|| _schema || '"' END, CASE WHEN _concurrently THEN 'concurrently' ELSE '' END;
    IF pg_is_in_recovery() THEN 
      RETURN 0;
    ELSE    
      FOR r IN SELECT schemaname, matviewname FROM pg_matviews WHERE schemaname = _schema OR _schema = '*' 
      LOOP
        RAISE NOTICE 'Refreshing materialized view "%"."%"', r.schemaname, r.matviewname;
        EXECUTE 'REFRESH MATERIALIZED VIEW ' || CASE WHEN _concurrently THEN 'CONCURRENTLY ' ELSE '' END || '"' || r.schemaname || '"."' || r.matviewname || '"'; 
      END LOOP;
    END IF;
    RETURN 1;
  END 
$$;


ALTER FUNCTION public.refreshallmaterializedviews(_schema text, _concurrently boolean) OWNER TO postgres;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: games; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE games (
    game_id integer NOT NULL,
    season smallint,
    game_date date NOT NULL,
    gamecode character varying(30),
    visitor_team_id integer,
    visitor_team_code character varying(3),
    home_team_id integer,
    home_team_code character varying(3),
    game_type character varying(10)
);


ALTER TABLE games OWNER TO nbadb;

--
-- Name: cs_games; Type: MATERIALIZED VIEW; Schema: public; Owner: nbadb
--

CREATE MATERIALIZED VIEW cs_games AS
 SELECT games.game_id,
    games.season,
    games.game_date,
    games.gamecode,
    games.visitor_team_id,
    games.visitor_team_code,
    games.home_team_id,
    games.home_team_code
   FROM games
  WHERE (games.season = ( SELECT max(games_1.season) AS max
           FROM games games_1))
  WITH NO DATA;


ALTER TABLE cs_games OWNER TO nbadb;

--
-- Name: player_gamelogs; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE player_gamelogs (
    player_gamelogs_id integer NOT NULL,
    game_id integer,
    nbacom_player_id integer,
    player_name character varying(50),
    team_id integer,
    team_code character varying(3),
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
    fd_points numeric
);


ALTER TABLE player_gamelogs OWNER TO nbadb;

--
-- Name: cs_player_gamelogs; Type: MATERIALIZED VIEW; Schema: public; Owner: nbadb
--

CREATE MATERIALIZED VIEW cs_player_gamelogs AS
 SELECT player_gamelogs.player_gamelogs_id,
    player_gamelogs.game_id,
    player_gamelogs.nbacom_player_id,
    player_gamelogs.player_name,
    player_gamelogs.team_id,
    player_gamelogs.team_code,
    player_gamelogs.min,
    player_gamelogs.fgm,
    player_gamelogs.fga,
    player_gamelogs.fg_pct,
    player_gamelogs.fg3m,
    player_gamelogs.fg3a,
    player_gamelogs.fg3_pct,
    player_gamelogs.ftm,
    player_gamelogs.fta,
    player_gamelogs.ft_pct,
    player_gamelogs.oreb,
    player_gamelogs.dreb,
    player_gamelogs.reb,
    player_gamelogs.ast,
    player_gamelogs.tov,
    player_gamelogs.stl,
    player_gamelogs.blk,
    player_gamelogs.pf,
    player_gamelogs.pts,
    player_gamelogs.plus_minus,
    player_gamelogs.dk_points,
    player_gamelogs.fd_points
   FROM player_gamelogs
  WHERE (player_gamelogs.game_id IN ( SELECT cs_games.game_id
           FROM cs_games))
  WITH NO DATA;


ALTER TABLE cs_player_gamelogs OWNER TO nbadb;

--
-- Name: team_gamelogs; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE team_gamelogs (
    team_gamelogs_id integer NOT NULL,
    team_id integer,
    team_code character varying(3),
    game_id integer,
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


ALTER TABLE team_gamelogs OWNER TO nbadb;

--
-- Name: cs_team_gamelogs; Type: MATERIALIZED VIEW; Schema: public; Owner: nbadb
--

CREATE MATERIALIZED VIEW cs_team_gamelogs AS
 SELECT team_gamelogs.team_gamelogs_id,
    team_gamelogs.team_id,
    team_gamelogs.team_code,
    team_gamelogs.game_id,
    team_gamelogs.minutes,
    team_gamelogs.fgm,
    team_gamelogs.fga,
    team_gamelogs.fg_pct,
    team_gamelogs.fg3m,
    team_gamelogs.fg3a,
    team_gamelogs.fg3_pct,
    team_gamelogs.ftm,
    team_gamelogs.fta,
    team_gamelogs.ft_pct,
    team_gamelogs.oreb,
    team_gamelogs.dreb,
    team_gamelogs.reb,
    team_gamelogs.ast,
    team_gamelogs.tov,
    team_gamelogs.stl,
    team_gamelogs.blk,
    team_gamelogs.pf,
    team_gamelogs.pts,
    team_gamelogs.plus_minus,
    team_gamelogs.opponent_pts
   FROM team_gamelogs
  WHERE (team_gamelogs.game_id IN ( SELECT cs_games.game_id
           FROM cs_games))
  WITH NO DATA;


ALTER TABLE cs_team_gamelogs OWNER TO nbadb;

--
-- Name: teamgames; Type: MATERIALIZED VIEW; Schema: public; Owner: nbadb
--

CREATE MATERIALIZED VIEW teamgames AS
 SELECT games.season,
    games.game_id,
    games.game_date,
    games.gamecode,
    games.visitor_team_id AS team_id,
    games.visitor_team_code AS team_code,
    games.home_team_id AS opponent_team_id,
    games.home_team_code AS opponent_team_code,
    false AS is_home
   FROM games
UNION ALL
 SELECT games.season,
    games.game_id,
    games.game_date,
    games.gamecode,
    games.home_team_id AS team_id,
    games.home_team_code AS team_code,
    games.visitor_team_id AS opponent_team_id,
    games.visitor_team_code AS opponent_team_code,
    true AS is_home
   FROM games
  ORDER BY 4 DESC, 3
  WITH NO DATA;


ALTER TABLE teamgames OWNER TO nbadb;

--
-- Name: cs_teamgames; Type: MATERIALIZED VIEW; Schema: public; Owner: nbadb
--

CREATE MATERIALIZED VIEW cs_teamgames AS
 SELECT teamgames.season,
    teamgames.game_id,
    teamgames.game_date,
    teamgames.gamecode,
    teamgames.team_id,
    teamgames.team_code,
    teamgames.opponent_team_id,
    teamgames.opponent_team_code,
    teamgames.is_home
   FROM teamgames
  WHERE (teamgames.game_id IN ( SELECT cs_games.game_id
           FROM cs_games))
  WITH NO DATA;


ALTER TABLE cs_teamgames OWNER TO nbadb;

--
-- Name: dfs_salaries; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE dfs_salaries (
    nbacom_player_id integer,
    source_player_name character varying(50) NOT NULL,
    team_code character varying,
    game_date date NOT NULL,
    season smallint,
    source character varying(20) NOT NULL,
    source_player_id integer,
    source_position character(2) DEFAULT NULL::bpchar,
    salary smallint NOT NULL,
    dfs_position character varying,
    dfs_site character varying,
    salaries_id integer NOT NULL
);


ALTER TABLE dfs_salaries OWNER TO nbadb;

--
-- Name: dfs_salaries_salaries_id_seq; Type: SEQUENCE; Schema: public; Owner: nbadb
--

CREATE SEQUENCE dfs_salaries_salaries_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE dfs_salaries_salaries_id_seq OWNER TO nbadb;

--
-- Name: dfs_salaries_salaries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nbadb
--

ALTER SEQUENCE dfs_salaries_salaries_id_seq OWNED BY dfs_salaries.salaries_id;


--
-- Name: dkpoints; Type: MATERIALIZED VIEW; Schema: public; Owner: nbadb
--

CREATE MATERIALIZED VIEW dkpoints AS
 WITH t1 AS (
         SELECT cs_player_gamelogs.nbacom_player_id,
            cs_player_gamelogs.player_name,
            count(cs_player_gamelogs.player_name) AS gp,
            sum(cs_player_gamelogs.min) AS mintot,
            round(((sum(cs_player_gamelogs.min) / count(cs_player_gamelogs.player_name)))::numeric, 1) AS mpg,
            round((sum(cs_player_gamelogs.dk_points) / (count(cs_player_gamelogs.player_name))::numeric), 2) AS dkpg,
            round((sum(cs_player_gamelogs.dk_points) / (sum(cs_player_gamelogs.min))::numeric), 2) AS dkmin,
            round(((sum(cs_player_gamelogs.pts))::numeric / sum(cs_player_gamelogs.dk_points)), 3) AS ptspct,
            round((((sum(cs_player_gamelogs.reb))::numeric * 1.25) / sum(cs_player_gamelogs.dk_points)), 3) AS rebpct,
            round((((sum(cs_player_gamelogs.ast))::numeric * 1.5) / sum(cs_player_gamelogs.dk_points)), 3) AS astpct,
            round((((sum(cs_player_gamelogs.stl) * 2))::numeric / sum(cs_player_gamelogs.dk_points)), 3) AS stlpct,
            round((((sum(cs_player_gamelogs.blk) * 2))::numeric / sum(cs_player_gamelogs.dk_points)), 3) AS blkpct,
            round((((sum(cs_player_gamelogs.tov))::numeric * '-0.5'::numeric) / sum(cs_player_gamelogs.dk_points)), 3) AS tovpct,
            round((((sum(cs_player_gamelogs.fg3m))::numeric * 0.5) / sum(cs_player_gamelogs.dk_points)), 3) AS tpmpct
           FROM cs_player_gamelogs
          GROUP BY cs_player_gamelogs.nbacom_player_id, cs_player_gamelogs.player_name
        )
 SELECT t1.nbacom_player_id,
    t1.player_name,
    t1.gp,
    t1.mintot,
    t1.mpg,
    t1.dkpg,
    t1.dkmin,
    t1.ptspct,
    t1.rebpct,
    t1.astpct,
    t1.stlpct,
    t1.blkpct,
    t1.tovpct,
    t1.tpmpct,
    ((1)::numeric - ((((((t1.ptspct + t1.rebpct) + t1.astpct) + t1.stlpct) + t1.blkpct) + t1.tovpct) + t1.tpmpct)) AS bonuspct
   FROM t1
  ORDER BY t1.dkmin DESC
  WITH NO DATA;


ALTER TABLE dkpoints OWNER TO nbadb;

--
-- Name: games_meta; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE games_meta (
    games_meta_id integer NOT NULL,
    gamecode character(15) NOT NULL,
    game_date date NOT NULL,
    team_code character varying(3) NOT NULL,
    days_last_game smallint,
    back_to_back boolean,
    three_in_four boolean,
    four_in_five boolean,
    is_ot boolean,
    q1 smallint,
    q2 smallint,
    q3 smallint,
    q4 smallint,
    ot1 smallint,
    ot2 smallint,
    ot3 smallint,
    ot4 smallint,
    opening_spread numeric,
    opening_game_ou numeric,
    opening_implied_total numeric,
    consensus_spread numeric,
    consensus_game_ou numeric,
    consensus_implied_total numeric,
    ref1 character varying(30) DEFAULT NULL::character varying,
    ref2 character varying(30) DEFAULT NULL::character varying,
    s smallint,
    ref3 character varying(40)
);


ALTER TABLE games_meta OWNER TO nbadb;

--
-- Name: games_meta_games_meta_id_seq; Type: SEQUENCE; Schema: public; Owner: nbadb
--

CREATE SEQUENCE games_meta_games_meta_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE games_meta_games_meta_id_seq OWNER TO nbadb;

--
-- Name: games_meta_games_meta_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nbadb
--

ALTER SEQUENCE games_meta_games_meta_id_seq OWNED BY games_meta.games_meta_id;


--
-- Name: models; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE models (
    models_id integer NOT NULL,
    game_date date NOT NULL,
    data jsonb NOT NULL,
    model_name character varying(20)
);


ALTER TABLE models OWNER TO nbadb;

--
-- Name: seasons; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE seasons (
    nbacom_season_id integer NOT NULL,
    season smallint NOT NULL,
    season_code character(7),
    season_start date NOT NULL,
    season_end date NOT NULL
);


ALTER TABLE seasons OWNER TO nbadb;

--
-- Name: missing_models; Type: VIEW; Schema: public; Owner: nbadb
--

CREATE VIEW missing_models AS
 SELECT DISTINCT games.game_date
   FROM games
  WHERE ((games.season = ( SELECT max(seasons.season) AS max
           FROM seasons)) AND (games.game_date <= (now())::date) AND ((games.game_type)::text = 'regular'::text) AND (NOT (games.game_date IN ( SELECT DISTINCT models.game_date
           FROM models))))
  ORDER BY games.game_date DESC;


ALTER TABLE missing_models OWNER TO nbadb;

--
-- Name: ownership; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE ownership (
    ownership_id integer NOT NULL,
    game_date date NOT NULL,
    data jsonb NOT NULL
);


ALTER TABLE ownership OWNER TO nbadb;

--
-- Name: missing_ownership; Type: VIEW; Schema: public; Owner: nbadb
--

CREATE VIEW missing_ownership AS
 SELECT DISTINCT games.game_date
   FROM games
  WHERE ((games.season = ( SELECT max(seasons.season) AS max
           FROM seasons)) AND (games.game_date < (now())::date) AND ((games.game_type)::text = 'regular'::text) AND (NOT (games.game_date IN ( SELECT DISTINCT ownership.game_date
           FROM ownership))))
  ORDER BY games.game_date DESC;


ALTER TABLE missing_ownership OWNER TO nbadb;

--
-- Name: missing_playergl; Type: VIEW; Schema: public; Owner: nbadb
--

CREATE VIEW missing_playergl AS
 SELECT DISTINCT games.game_date
   FROM games
  WHERE ((NOT (games.game_id IN ( SELECT DISTINCT cs_player_gamelogs.game_id
           FROM cs_player_gamelogs))) AND (games.game_date < (now())::date) AND (games.season = ( SELECT max(seasons.season) AS max
           FROM seasons)) AND ((games.game_type)::text = 'regular'::text))
  ORDER BY games.game_date DESC;


ALTER TABLE missing_playergl OWNER TO nbadb;

--
-- Name: playerstats_daily; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE playerstats_daily (
    as_of date,
    season smallint,
    nbacom_player_id integer,
    player_name character varying(50),
    team_id integer,
    age numeric,
    ast smallint,
    ast_rank smallint,
    blk smallint,
    blka smallint,
    blka_rank smallint,
    blk_rank smallint,
    dd2 smallint,
    dd2_rank smallint,
    dreb smallint,
    dreb_rank smallint,
    fg3a smallint,
    fg3a_rank smallint,
    fg3m smallint,
    fg3m_rank smallint,
    fg3_pct numeric,
    fg3_pct_rank smallint,
    fga smallint,
    fga_rank smallint,
    fgm smallint,
    fgm_rank smallint,
    fg_pct numeric,
    fg_pct_rank smallint,
    fta smallint,
    fta_rank smallint,
    ftm smallint,
    ftm_rank smallint,
    ft_pct numeric,
    ft_pct_rank smallint,
    gp smallint,
    gp_rank smallint,
    l smallint,
    l_rank smallint,
    min numeric,
    min_played numeric,
    min_rank smallint,
    oreb smallint,
    oreb_rank smallint,
    pf smallint,
    pfd smallint,
    pfd_rank smallint,
    pf_rank smallint,
    plus_minus smallint,
    plus_minus_rank smallint,
    pts smallint,
    pts_rank smallint,
    reb smallint,
    reb_rank smallint,
    sec_played numeric,
    stl smallint,
    stl_rank smallint,
    td3 smallint,
    td3_rank smallint,
    tov smallint,
    tov_rank smallint,
    w smallint,
    w_pct numeric,
    w_pct_rank smallint,
    w_rank smallint,
    reb_pct_rank smallint,
    reb_pct numeric,
    oreb_pct numeric,
    dreb_pct numeric,
    usg_pct numeric,
    ast_pct numeric,
    ast_ratio_rank smallint,
    dreb_pct_rank smallint,
    dreb_rating_rank smallint,
    def_rating_rank smallint,
    ts_pct_rank smallint,
    ast_to_rank smallint,
    tm_tov_pct_rank smallint,
    ast_ratio smallint,
    pace_rank smallint,
    fgm_pg_rank smallint,
    net_rating numeric,
    ts_pct numeric,
    tm_tov_pct numeric,
    efg_pct_rank numeric,
    fga_pg numeric,
    oreb_pct_rank smallint,
    off_rating numeric,
    off_rating_rank smallint,
    pace numeric,
    def_rating numeric,
    pie numeric,
    ast_to numeric,
    team_code character varying(10),
    efg_pct numeric,
    fga_pg_rank smallint,
    fgm_pg smallint,
    net_rating_rank smallint,
    ast_pct_rank smallint,
    usg_pct_rank smallint,
    pie_rank smallint,
    playerstats_daily_id integer NOT NULL
);


ALTER TABLE playerstats_daily OWNER TO nbadb;

--
-- Name: missing_playerstats; Type: VIEW; Schema: public; Owner: nbadb
--

CREATE VIEW missing_playerstats AS
 SELECT DISTINCT games.game_date
   FROM games
  WHERE ((games.season = ( SELECT max(seasons.season) AS max
           FROM seasons)) AND (games.game_date < (now())::date) AND ((games.game_type)::text = 'regular'::text) AND (NOT (games.game_date IN ( SELECT DISTINCT playerstats_daily.as_of
           FROM playerstats_daily))))
  ORDER BY games.game_date DESC;


ALTER TABLE missing_playerstats OWNER TO nbadb;

--
-- Name: missing_salaries; Type: VIEW; Schema: public; Owner: nbadb
--

CREATE VIEW missing_salaries AS
 SELECT DISTINCT games.game_date
   FROM games
  WHERE ((games.season = ( SELECT max(seasons.season) AS max
           FROM seasons)) AND (games.game_date <= (now())::date) AND ((games.game_type)::text = 'regular'::text) AND (NOT (games.game_date IN ( SELECT DISTINCT dfs_salaries.game_date
           FROM dfs_salaries))))
  ORDER BY games.game_date DESC;


ALTER TABLE missing_salaries OWNER TO nbadb;

--
-- Name: missing_salaries_ids; Type: VIEW; Schema: public; Owner: nbadb
--

CREATE VIEW missing_salaries_ids AS
 SELECT DISTINCT dfs_salaries.source_player_name AS n,
    dfs_salaries.source_player_id AS id
   FROM dfs_salaries
  WHERE (dfs_salaries.nbacom_player_id IS NULL);


ALTER TABLE missing_salaries_ids OWNER TO nbadb;

--
-- Name: team_opponent_dashboard; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE team_opponent_dashboard (
    team_opponent_dashboard_id integer NOT NULL,
    team_id integer,
    as_of date,
    gp smallint,
    gp_rank smallint,
    l smallint,
    l_rank smallint,
    min numeric,
    min_rank smallint,
    opp_ast numeric,
    opp_ast_rank smallint,
    opp_blk numeric,
    opp_blk_rank smallint,
    opp_blka numeric,
    opp_blka_rank smallint,
    opp_dreb numeric,
    opp_dreb_rank smallint,
    opp_fg3_pct numeric,
    opp_fg3_pct_rank smallint,
    opp_fg3a numeric,
    opp_fg3a_rank smallint,
    opp_fg3m numeric,
    opp_fg3m_rank smallint,
    opp_fg_pct numeric,
    opp_fg_pct_rank smallint,
    opp_fga numeric,
    opp_fga_rank smallint,
    opp_fgm numeric,
    opp_fgm_rank smallint,
    opp_ft_pct numeric,
    opp_ft_pct_rank smallint,
    opp_fta numeric,
    opp_fta_rank smallint,
    opp_ftm numeric,
    opp_ftm_rank smallint,
    opp_oreb numeric,
    opp_oreb_rank smallint,
    opp_pf numeric,
    opp_pf_rank smallint,
    opp_pfd numeric,
    opp_pfd_rank smallint,
    opp_pts numeric,
    opp_pts_rank smallint,
    opp_reb numeric,
    opp_reb_rank smallint,
    opp_stl numeric,
    opp_stl_rank smallint,
    opp_tov numeric,
    opp_tov_rank smallint,
    plus_minus numeric,
    plus_minus_rank smallint,
    w smallint,
    w_pct numeric,
    w_pct_rank smallint,
    w_rank smallint
);


ALTER TABLE team_opponent_dashboard OWNER TO nbadb;

--
-- Name: missing_team_opponent_dashboard; Type: VIEW; Schema: public; Owner: nbadb
--

CREATE VIEW missing_team_opponent_dashboard AS
 SELECT DISTINCT games.game_date
   FROM games
  WHERE ((games.season = ( SELECT max(seasons.season) AS max
           FROM seasons)) AND (games.game_date < (now())::date) AND ((games.game_type)::text = 'regular'::text) AND (NOT (games.game_date IN ( SELECT DISTINCT team_opponent_dashboard.as_of
           FROM team_opponent_dashboard))))
  ORDER BY games.game_date DESC;


ALTER TABLE missing_team_opponent_dashboard OWNER TO nbadb;

--
-- Name: missing_teamgl; Type: VIEW; Schema: public; Owner: nbadb
--

CREATE VIEW missing_teamgl AS
 SELECT DISTINCT games.game_date
   FROM games
  WHERE ((NOT (games.game_id IN ( SELECT DISTINCT cs_team_gamelogs.game_id
           FROM cs_team_gamelogs))) AND (games.game_date < (now())::date) AND (games.season = ( SELECT max(seasons.season) AS max
           FROM seasons)) AND ((games.game_type)::text = 'regular'::text))
  ORDER BY games.game_date DESC;


ALTER TABLE missing_teamgl OWNER TO nbadb;

--
-- Name: teamstats_daily; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE teamstats_daily (
    teamstats_daily_id integer NOT NULL,
    as_of date NOT NULL,
    team_id integer,
    ast numeric,
    ast_pct numeric,
    ast_pct_rank smallint,
    ast_rank smallint,
    ast_ratio numeric,
    ast_ratio_rank smallint,
    ast_to numeric,
    ast_to_rank smallint,
    blk numeric,
    blka numeric,
    blka_rank smallint,
    blk_rank smallint,
    def_rating numeric,
    def_rating_rank smallint,
    dreb numeric,
    dreb_pct numeric,
    dreb_pct_rank smallint,
    dreb_rank smallint,
    efg_pct numeric,
    efg_pct_rank smallint,
    fg3a numeric,
    fg3a_rank smallint,
    fg3m numeric,
    fg3m_rank smallint,
    fg3_pct numeric,
    fg3_pct_rank smallint,
    fga numeric,
    fga_rank smallint,
    fgm numeric,
    fgm_rank smallint,
    fg_pct numeric,
    fg_pct_rank smallint,
    fta numeric,
    fta_rank smallint,
    ftm numeric,
    ftm_rank smallint,
    ft_pct numeric,
    ft_pct_rank smallint,
    gp smallint,
    gp_rank smallint,
    l smallint,
    l_rank smallint,
    min numeric,
    min_rank smallint,
    net_rating numeric,
    net_rating_rank smallint,
    off_rating numeric,
    off_rating_rank smallint,
    oreb numeric,
    oreb_pct numeric,
    oreb_pct_rank smallint,
    oreb_rank smallint,
    pace numeric,
    pace_rank smallint,
    pf numeric,
    pfd numeric,
    pfd_rank smallint,
    pf_rank smallint,
    pie numeric,
    pie_rank smallint,
    plus_minus numeric,
    plus_minus_rank smallint,
    pts numeric,
    pts_rank smallint,
    reb numeric,
    reb_pct numeric,
    reb_pct_rank smallint,
    reb_rank smallint,
    stl numeric,
    stl_rank smallint,
    tm_tov_pct numeric,
    tm_tov_pct_rank smallint,
    tov numeric,
    tov_rank smallint,
    ts_pct numeric,
    ts_pct_rank smallint,
    w smallint,
    w_pct numeric,
    w_pct_rank smallint,
    w_rank smallint,
    season smallint
);


ALTER TABLE teamstats_daily OWNER TO nbadb;

--
-- Name: missing_teamstats; Type: VIEW; Schema: public; Owner: nbadb
--

CREATE VIEW missing_teamstats AS
 SELECT DISTINCT games.game_date
   FROM games
  WHERE ((games.season = ( SELECT max(seasons.season) AS max
           FROM seasons)) AND (games.game_date < (now())::date) AND ((games.game_type)::text = 'regular'::text) AND (NOT (games.game_date IN ( SELECT DISTINCT teamstats_daily.as_of
           FROM teamstats_daily))))
  ORDER BY games.game_date DESC;


ALTER TABLE missing_teamstats OWNER TO nbadb;

--
-- Name: models_models_id_seq; Type: SEQUENCE; Schema: public; Owner: nbadb
--

CREATE SEQUENCE models_models_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE models_models_id_seq OWNER TO nbadb;

--
-- Name: models_models_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nbadb
--

ALTER SEQUENCE models_models_id_seq OWNED BY models.models_id;


--
-- Name: ownership_ownership_id_seq; Type: SEQUENCE; Schema: public; Owner: nbadb
--

CREATE SEQUENCE ownership_ownership_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE ownership_ownership_id_seq OWNER TO nbadb;

--
-- Name: ownership_ownership_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nbadb
--

ALTER SEQUENCE ownership_ownership_id_seq OWNED BY ownership.ownership_id;


--
-- Name: player_boxscores_combined; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE player_boxscores_combined (
    player_boxscores_combined_id integer NOT NULL,
    player_id integer,
    player_name character varying,
    game_id integer,
    team_id integer,
    ast smallint,
    ast_pct numeric,
    ast_ratio numeric,
    ast_tov numeric,
    blk smallint,
    blka smallint,
    comment character varying,
    def_rating numeric,
    dreb smallint,
    dreb_pct numeric,
    efg_pct numeric,
    fg3a smallint,
    fg3m smallint,
    fg3_pct numeric,
    fga smallint,
    fgm smallint,
    fg_pct numeric,
    fta smallint,
    ftm smallint,
    ft_pct numeric,
    min character varying(10),
    min_played smallint,
    net_rating numeric,
    off_rating numeric,
    opp_pts_2nd_chance smallint,
    opp_pts_fb smallint,
    opp_pts_off_tov smallint,
    opp_pts_paint smallint,
    oreb smallint,
    oreb_pct numeric,
    pace numeric,
    pct_ast numeric,
    pct_ast_2pm numeric,
    pct_ast_3pm numeric,
    pct_ast_fgm numeric,
    pct_blk numeric,
    pct_blka numeric,
    pct_dreb numeric,
    pct_fg3a numeric,
    pct_fg3m numeric,
    pct_fga numeric,
    pct_fga_2pt numeric,
    pct_fga_3pt numeric,
    pct_fgm numeric,
    pct_fta numeric,
    pct_ftm numeric,
    pct_oreb numeric,
    pct_pf numeric,
    pct_pfd numeric,
    pct_pts numeric,
    pct_pts_2pt numeric,
    pct_pts_2pt_mr numeric,
    pct_pts_3pt numeric,
    pct_pts_fb numeric,
    pct_pts_ft numeric,
    pct_pts_off_tov numeric,
    pct_pts_paint numeric,
    pct_reb numeric,
    pct_stl numeric,
    pct_tov numeric,
    pct_uast_2pm numeric,
    pct_uast_3pm numeric,
    pct_uast_fgm numeric,
    pf smallint,
    pfd smallint,
    pie numeric,
    plus_minus numeric,
    pts smallint,
    pts_2nd_chance smallint,
    pts_fb smallint,
    pts_off_tov smallint,
    pts_paint smallint,
    reb smallint,
    reb_pct numeric,
    sec_played smallint,
    start_position character varying,
    stl smallint,
    tm_tov_pct numeric,
    tov smallint,
    ts_pct numeric,
    usg_pct numeric
);


ALTER TABLE player_boxscores_combined OWNER TO nbadb;

--
-- Name: player_boxscores_combined_player_boxscores_combined_id_seq; Type: SEQUENCE; Schema: public; Owner: nbadb
--

CREATE SEQUENCE player_boxscores_combined_player_boxscores_combined_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE player_boxscores_combined_player_boxscores_combined_id_seq OWNER TO nbadb;

--
-- Name: player_boxscores_combined_player_boxscores_combined_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nbadb
--

ALTER SEQUENCE player_boxscores_combined_player_boxscores_combined_id_seq OWNED BY player_boxscores_combined.player_boxscores_combined_id;


--
-- Name: player_gamelogs_player_gamelogs_id_seq; Type: SEQUENCE; Schema: public; Owner: nbadb
--

CREATE SEQUENCE player_gamelogs_player_gamelogs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE player_gamelogs_player_gamelogs_id_seq OWNER TO nbadb;

--
-- Name: player_gamelogs_player_gamelogs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nbadb
--

ALTER SEQUENCE player_gamelogs_player_gamelogs_id_seq OWNED BY player_gamelogs.player_gamelogs_id;


--
-- Name: player_xref; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE player_xref (
    player_xref_id integer NOT NULL,
    nbacom_player_id integer NOT NULL,
    source character varying(30) NOT NULL,
    source_player_name character varying(50) NOT NULL,
    source_player_id integer,
    source_player_code character varying(50)
);


ALTER TABLE player_xref OWNER TO nbadb;

--
-- Name: player_xref_player_xref_id_seq; Type: SEQUENCE; Schema: public; Owner: nbadb
--

CREATE SEQUENCE player_xref_player_xref_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE player_xref_player_xref_id_seq OWNER TO nbadb;

--
-- Name: player_xref_player_xref_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nbadb
--

ALTER SEQUENCE player_xref_player_xref_id_seq OWNED BY player_xref.player_xref_id;


--
-- Name: players; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE players (
    players_id integer NOT NULL,
    nbacom_player_id integer NOT NULL,
    first_name character varying(25) NOT NULL,
    last_name character varying(25) NOT NULL,
    display_first_last character varying(50) NOT NULL,
    nbacom_position character varying(20) DEFAULT NULL::character varying,
    primary_position character varying(2) DEFAULT NULL::character varying,
    position_group character varying(5) DEFAULT NULL::character varying,
    birthdate date,
    school character varying(50) DEFAULT NULL::character varying,
    country character varying(50) DEFAULT NULL::character varying,
    last_affiliation character varying(50) DEFAULT NULL::character varying,
    height smallint,
    weight smallint,
    jersey character varying(3) DEFAULT NULL::character varying,
    from_year smallint,
    to_year smallint,
    draft_number smallint,
    draft_round smallint,
    draft_year smallint
);


ALTER TABLE players OWNER TO nbadb;

--
-- Name: players_players_id_seq; Type: SEQUENCE; Schema: public; Owner: nbadb
--

CREATE SEQUENCE players_players_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE players_players_id_seq OWNER TO nbadb;

--
-- Name: players_players_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nbadb
--

ALTER SEQUENCE players_players_id_seq OWNED BY players.players_id;


--
-- Name: playerstats_daily_playerstats_daily_id_seq; Type: SEQUENCE; Schema: public; Owner: nbadb
--

CREATE SEQUENCE playerstats_daily_playerstats_daily_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE playerstats_daily_playerstats_daily_id_seq OWNER TO nbadb;

--
-- Name: playerstats_daily_playerstats_daily_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nbadb
--

ALTER SEQUENCE playerstats_daily_playerstats_daily_id_seq OWNED BY playerstats_daily.playerstats_daily_id;


--
-- Name: playerstats_season; Type: MATERIALIZED VIEW; Schema: public; Owner: nbadb
--

CREATE MATERIALIZED VIEW playerstats_season AS
 SELECT playerstats_daily.as_of,
    playerstats_daily.season,
    playerstats_daily.nbacom_player_id,
    playerstats_daily.player_name,
    playerstats_daily.team_id,
    playerstats_daily.age,
    playerstats_daily.ast,
    playerstats_daily.ast_rank,
    playerstats_daily.blk,
    playerstats_daily.blka,
    playerstats_daily.blka_rank,
    playerstats_daily.blk_rank,
    playerstats_daily.dd2,
    playerstats_daily.dd2_rank,
    playerstats_daily.dreb,
    playerstats_daily.dreb_rank,
    playerstats_daily.fg3a,
    playerstats_daily.fg3a_rank,
    playerstats_daily.fg3m,
    playerstats_daily.fg3m_rank,
    playerstats_daily.fg3_pct,
    playerstats_daily.fg3_pct_rank,
    playerstats_daily.fga,
    playerstats_daily.fga_rank,
    playerstats_daily.fgm,
    playerstats_daily.fgm_rank,
    playerstats_daily.fg_pct,
    playerstats_daily.fg_pct_rank,
    playerstats_daily.fta,
    playerstats_daily.fta_rank,
    playerstats_daily.ftm,
    playerstats_daily.ftm_rank,
    playerstats_daily.ft_pct,
    playerstats_daily.ft_pct_rank,
    playerstats_daily.gp,
    playerstats_daily.gp_rank,
    playerstats_daily.l,
    playerstats_daily.l_rank,
    playerstats_daily.min,
    playerstats_daily.min_played,
    playerstats_daily.min_rank,
    playerstats_daily.oreb,
    playerstats_daily.oreb_rank,
    playerstats_daily.pf,
    playerstats_daily.pfd,
    playerstats_daily.pfd_rank,
    playerstats_daily.pf_rank,
    playerstats_daily.plus_minus,
    playerstats_daily.plus_minus_rank,
    playerstats_daily.pts,
    playerstats_daily.pts_rank,
    playerstats_daily.reb,
    playerstats_daily.reb_rank,
    playerstats_daily.sec_played,
    playerstats_daily.stl,
    playerstats_daily.stl_rank,
    playerstats_daily.td3,
    playerstats_daily.td3_rank,
    playerstats_daily.tov,
    playerstats_daily.tov_rank,
    playerstats_daily.w,
    playerstats_daily.w_pct,
    playerstats_daily.w_pct_rank,
    playerstats_daily.w_rank,
    playerstats_daily.reb_pct_rank,
    playerstats_daily.reb_pct,
    playerstats_daily.oreb_pct,
    playerstats_daily.dreb_pct,
    playerstats_daily.usg_pct,
    playerstats_daily.ast_pct,
    playerstats_daily.ast_ratio_rank,
    playerstats_daily.dreb_pct_rank,
    playerstats_daily.dreb_rating_rank,
    playerstats_daily.def_rating_rank,
    playerstats_daily.ts_pct_rank,
    playerstats_daily.ast_to_rank,
    playerstats_daily.tm_tov_pct_rank,
    playerstats_daily.ast_ratio,
    playerstats_daily.pace_rank,
    playerstats_daily.fgm_pg_rank,
    playerstats_daily.net_rating,
    playerstats_daily.ts_pct,
    playerstats_daily.tm_tov_pct,
    playerstats_daily.efg_pct_rank,
    playerstats_daily.fga_pg,
    playerstats_daily.oreb_pct_rank,
    playerstats_daily.off_rating,
    playerstats_daily.off_rating_rank,
    playerstats_daily.pace,
    playerstats_daily.def_rating,
    playerstats_daily.pie,
    playerstats_daily.ast_to,
    playerstats_daily.team_code,
    playerstats_daily.efg_pct,
    playerstats_daily.fga_pg_rank,
    playerstats_daily.fgm_pg,
    playerstats_daily.net_rating_rank,
    playerstats_daily.ast_pct_rank,
    playerstats_daily.usg_pct_rank,
    playerstats_daily.pie_rank,
    playerstats_daily.playerstats_daily_id
   FROM playerstats_daily
  WHERE (playerstats_daily.as_of IN ( SELECT max(playerstats_daily_1.as_of) AS max
           FROM playerstats_daily playerstats_daily_1
          GROUP BY playerstats_daily_1.season))
  ORDER BY playerstats_daily.season DESC
  WITH NO DATA;


ALTER TABLE playerstats_season OWNER TO nbadb;

--
-- Name: starters; Type: VIEW; Schema: public; Owner: nbadb
--

CREATE VIEW starters AS
 SELECT g.game_id,
    g.game_date,
    pbc.player_name,
    pbc.team_id,
    pbc.start_position,
        CASE
            WHEN (pbc.start_position IS NULL) THEN false
            ELSE true
        END AS is_starter
   FROM (player_boxscores_combined pbc
     JOIN games g ON ((pbc.game_id = g.game_id)))
  ORDER BY g.game_date, pbc.team_id, pbc.start_position;


ALTER TABLE starters OWNER TO nbadb;

--
-- Name: team_boxscores_combined; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE team_boxscores_combined (
    team_boxscores_combined_id integer NOT NULL,
    game_id integer,
    team_id integer,
    team_code character varying(3),
    ast smallint,
    ast_pct numeric,
    ast_ratio numeric,
    ast_tov numeric,
    blk smallint,
    blka smallint,
    def_rating numeric,
    dreb smallint,
    dreb_pct numeric,
    efg_pct numeric,
    fg3a smallint,
    fg3m smallint,
    fg3_pct numeric,
    fga smallint,
    fgm smallint,
    fg_pct numeric,
    fta smallint,
    ftm smallint,
    ft_pct numeric,
    min_played smallint,
    net_rating numeric,
    off_rating numeric,
    opp_pts_2nd_chance smallint,
    opp_pts_fb smallint,
    opp_pts_off_tov smallint,
    opp_pts_paint smallint,
    oreb smallint,
    oreb_pct numeric,
    pace numeric,
    pct_ast_2pm numeric,
    pct_ast_3pm numeric,
    pct_ast_fgm numeric,
    pct_fga_2pt numeric,
    pct_fga_3pt numeric,
    pct_pts_2pt numeric,
    pct_pts_2pt_mr numeric,
    pct_pts_3pt numeric,
    pct_pts_fb numeric,
    pct_pts_ft numeric,
    pct_pts_off_tov numeric,
    pct_pts_paint numeric,
    pct_uast_2pm numeric,
    pct_uast_3pm numeric,
    pct_uast_fgm numeric,
    pf smallint,
    pfd smallint,
    pie numeric,
    plus_minus numeric,
    pts smallint,
    pts_2nd_chance smallint,
    pts_fb smallint,
    pts_off_tov smallint,
    pts_paint smallint,
    reb smallint,
    reb_pct numeric,
    stl smallint,
    tm_tov_pct numeric,
    tov smallint,
    ts_pct numeric,
    usg_pct numeric
);


ALTER TABLE team_boxscores_combined OWNER TO nbadb;

--
-- Name: team_boxscores_combined_team_boxscores_combined_id_seq; Type: SEQUENCE; Schema: public; Owner: nbadb
--

CREATE SEQUENCE team_boxscores_combined_team_boxscores_combined_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE team_boxscores_combined_team_boxscores_combined_id_seq OWNER TO nbadb;

--
-- Name: team_boxscores_combined_team_boxscores_combined_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nbadb
--

ALTER SEQUENCE team_boxscores_combined_team_boxscores_combined_id_seq OWNED BY team_boxscores_combined.team_boxscores_combined_id;


--
-- Name: team_gamelogs_team_gamelogs_id_seq; Type: SEQUENCE; Schema: public; Owner: nbadb
--

CREATE SEQUENCE team_gamelogs_team_gamelogs_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE team_gamelogs_team_gamelogs_id_seq OWNER TO nbadb;

--
-- Name: team_gamelogs_team_gamelogs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nbadb
--

ALTER SEQUENCE team_gamelogs_team_gamelogs_id_seq OWNED BY team_gamelogs.team_gamelogs_id;


--
-- Name: team_opponent_dashboard_team_opponent_dashboard_id_seq; Type: SEQUENCE; Schema: public; Owner: nbadb
--

CREATE SEQUENCE team_opponent_dashboard_team_opponent_dashboard_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE team_opponent_dashboard_team_opponent_dashboard_id_seq OWNER TO nbadb;

--
-- Name: team_opponent_dashboard_team_opponent_dashboard_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nbadb
--

ALTER SEQUENCE team_opponent_dashboard_team_opponent_dashboard_id_seq OWNED BY team_opponent_dashboard.team_opponent_dashboard_id;


--
-- Name: teams; Type: TABLE; Schema: public; Owner: nbadb
--

CREATE TABLE teams (
    teams_id integer NOT NULL,
    nbacom_team_id integer NOT NULL,
    team_code character varying(3) NOT NULL,
    team_city character varying(50) NOT NULL,
    team_name character varying(50) NOT NULL
);


ALTER TABLE teams OWNER TO nbadb;

--
-- Name: teams_teams_id_seq; Type: SEQUENCE; Schema: public; Owner: nbadb
--

CREATE SEQUENCE teams_teams_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE teams_teams_id_seq OWNER TO nbadb;

--
-- Name: teams_teams_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nbadb
--

ALTER SEQUENCE teams_teams_id_seq OWNED BY teams.teams_id;


--
-- Name: teamstats_daily_teamstats_daily_id_seq; Type: SEQUENCE; Schema: public; Owner: nbadb
--

CREATE SEQUENCE teamstats_daily_teamstats_daily_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE teamstats_daily_teamstats_daily_id_seq OWNER TO nbadb;

--
-- Name: teamstats_daily_teamstats_daily_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: nbadb
--

ALTER SEQUENCE teamstats_daily_teamstats_daily_id_seq OWNED BY teamstats_daily.teamstats_daily_id;


--
-- Name: teamstats_season; Type: MATERIALIZED VIEW; Schema: public; Owner: nbadb
--

CREATE MATERIALIZED VIEW teamstats_season AS
 SELECT teamstats_daily.teamstats_daily_id,
    teamstats_daily.as_of,
    teamstats_daily.team_id,
    teamstats_daily.ast,
    teamstats_daily.ast_pct,
    teamstats_daily.ast_pct_rank,
    teamstats_daily.ast_rank,
    teamstats_daily.ast_ratio,
    teamstats_daily.ast_ratio_rank,
    teamstats_daily.ast_to,
    teamstats_daily.ast_to_rank,
    teamstats_daily.blk,
    teamstats_daily.blka,
    teamstats_daily.blka_rank,
    teamstats_daily.blk_rank,
    teamstats_daily.def_rating,
    teamstats_daily.def_rating_rank,
    teamstats_daily.dreb,
    teamstats_daily.dreb_pct,
    teamstats_daily.dreb_pct_rank,
    teamstats_daily.dreb_rank,
    teamstats_daily.efg_pct,
    teamstats_daily.efg_pct_rank,
    teamstats_daily.fg3a,
    teamstats_daily.fg3a_rank,
    teamstats_daily.fg3m,
    teamstats_daily.fg3m_rank,
    teamstats_daily.fg3_pct,
    teamstats_daily.fg3_pct_rank,
    teamstats_daily.fga,
    teamstats_daily.fga_rank,
    teamstats_daily.fgm,
    teamstats_daily.fgm_rank,
    teamstats_daily.fg_pct,
    teamstats_daily.fg_pct_rank,
    teamstats_daily.fta,
    teamstats_daily.fta_rank,
    teamstats_daily.ftm,
    teamstats_daily.ftm_rank,
    teamstats_daily.ft_pct,
    teamstats_daily.ft_pct_rank,
    teamstats_daily.gp,
    teamstats_daily.gp_rank,
    teamstats_daily.l,
    teamstats_daily.l_rank,
    teamstats_daily.min,
    teamstats_daily.min_rank,
    teamstats_daily.net_rating,
    teamstats_daily.net_rating_rank,
    teamstats_daily.off_rating,
    teamstats_daily.off_rating_rank,
    teamstats_daily.oreb,
    teamstats_daily.oreb_pct,
    teamstats_daily.oreb_pct_rank,
    teamstats_daily.oreb_rank,
    teamstats_daily.pace,
    teamstats_daily.pace_rank,
    teamstats_daily.pf,
    teamstats_daily.pfd,
    teamstats_daily.pfd_rank,
    teamstats_daily.pf_rank,
    teamstats_daily.pie,
    teamstats_daily.pie_rank,
    teamstats_daily.plus_minus,
    teamstats_daily.plus_minus_rank,
    teamstats_daily.pts,
    teamstats_daily.pts_rank,
    teamstats_daily.reb,
    teamstats_daily.reb_pct,
    teamstats_daily.reb_pct_rank,
    teamstats_daily.reb_rank,
    teamstats_daily.stl,
    teamstats_daily.stl_rank,
    teamstats_daily.tm_tov_pct,
    teamstats_daily.tm_tov_pct_rank,
    teamstats_daily.tov,
    teamstats_daily.tov_rank,
    teamstats_daily.ts_pct,
    teamstats_daily.ts_pct_rank,
    teamstats_daily.w,
    teamstats_daily.w_pct,
    teamstats_daily.w_pct_rank,
    teamstats_daily.w_rank,
    teamstats_daily.season
   FROM teamstats_daily
  WHERE (teamstats_daily.as_of IN ( SELECT max(teamstats_daily_1.as_of) AS max
           FROM teamstats_daily teamstats_daily_1
          GROUP BY teamstats_daily_1.season))
  ORDER BY teamstats_daily.season DESC
  WITH NO DATA;


ALTER TABLE teamstats_season OWNER TO nbadb;

--
-- Name: salaries_id; Type: DEFAULT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY dfs_salaries ALTER COLUMN salaries_id SET DEFAULT nextval('dfs_salaries_salaries_id_seq'::regclass);


--
-- Name: games_meta_id; Type: DEFAULT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY games_meta ALTER COLUMN games_meta_id SET DEFAULT nextval('games_meta_games_meta_id_seq'::regclass);


--
-- Name: models_id; Type: DEFAULT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY models ALTER COLUMN models_id SET DEFAULT nextval('models_models_id_seq'::regclass);


--
-- Name: ownership_id; Type: DEFAULT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY ownership ALTER COLUMN ownership_id SET DEFAULT nextval('ownership_ownership_id_seq'::regclass);


--
-- Name: player_boxscores_combined_id; Type: DEFAULT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_boxscores_combined ALTER COLUMN player_boxscores_combined_id SET DEFAULT nextval('player_boxscores_combined_player_boxscores_combined_id_seq'::regclass);


--
-- Name: player_gamelogs_id; Type: DEFAULT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_gamelogs ALTER COLUMN player_gamelogs_id SET DEFAULT nextval('player_gamelogs_player_gamelogs_id_seq'::regclass);


--
-- Name: player_xref_id; Type: DEFAULT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_xref ALTER COLUMN player_xref_id SET DEFAULT nextval('player_xref_player_xref_id_seq'::regclass);


--
-- Name: players_id; Type: DEFAULT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY players ALTER COLUMN players_id SET DEFAULT nextval('players_players_id_seq'::regclass);


--
-- Name: playerstats_daily_id; Type: DEFAULT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY playerstats_daily ALTER COLUMN playerstats_daily_id SET DEFAULT nextval('playerstats_daily_playerstats_daily_id_seq'::regclass);


--
-- Name: team_boxscores_combined_id; Type: DEFAULT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY team_boxscores_combined ALTER COLUMN team_boxscores_combined_id SET DEFAULT nextval('team_boxscores_combined_team_boxscores_combined_id_seq'::regclass);


--
-- Name: team_gamelogs_id; Type: DEFAULT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY team_gamelogs ALTER COLUMN team_gamelogs_id SET DEFAULT nextval('team_gamelogs_team_gamelogs_id_seq'::regclass);


--
-- Name: team_opponent_dashboard_id; Type: DEFAULT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY team_opponent_dashboard ALTER COLUMN team_opponent_dashboard_id SET DEFAULT nextval('team_opponent_dashboard_team_opponent_dashboard_id_seq'::regclass);


--
-- Name: teams_id; Type: DEFAULT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY teams ALTER COLUMN teams_id SET DEFAULT nextval('teams_teams_id_seq'::regclass);


--
-- Name: teamstats_daily_id; Type: DEFAULT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY teamstats_daily ALTER COLUMN teamstats_daily_id SET DEFAULT nextval('teamstats_daily_teamstats_daily_id_seq'::regclass);


--
-- Name: dfs_salaries_nbacom_player_id_game_date_dfs_site_key; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY dfs_salaries
    ADD CONSTRAINT dfs_salaries_nbacom_player_id_game_date_dfs_site_key UNIQUE (nbacom_player_id, game_date, dfs_site);


--
-- Name: dfs_salaries_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY dfs_salaries
    ADD CONSTRAINT dfs_salaries_pkey PRIMARY KEY (salaries_id);


--
-- Name: games_gamecode_key; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY games
    ADD CONSTRAINT games_gamecode_key UNIQUE (gamecode);


--
-- Name: games_meta_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY games_meta
    ADD CONSTRAINT games_meta_pkey PRIMARY KEY (games_meta_id);


--
-- Name: games_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY games
    ADD CONSTRAINT games_pkey PRIMARY KEY (game_id);


--
-- Name: models_game_date_key; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY models
    ADD CONSTRAINT models_game_date_key UNIQUE (game_date);


--
-- Name: models_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY models
    ADD CONSTRAINT models_pkey PRIMARY KEY (models_id);


--
-- Name: ownership_game_date_key; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY ownership
    ADD CONSTRAINT ownership_game_date_key UNIQUE (game_date);


--
-- Name: ownership_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY ownership
    ADD CONSTRAINT ownership_pkey PRIMARY KEY (ownership_id);


--
-- Name: pid_source; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_xref
    ADD CONSTRAINT pid_source UNIQUE (nbacom_player_id, source);


--
-- Name: player_boxscores_combined_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_boxscores_combined
    ADD CONSTRAINT player_boxscores_combined_pkey PRIMARY KEY (player_boxscores_combined_id);


--
-- Name: player_gamelogs_game_id_nbacom_player_id_key; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_gamelogs
    ADD CONSTRAINT player_gamelogs_game_id_nbacom_player_id_key UNIQUE (game_id, nbacom_player_id);


--
-- Name: player_gamelogs_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_gamelogs
    ADD CONSTRAINT player_gamelogs_pkey PRIMARY KEY (player_gamelogs_id);


--
-- Name: player_xref_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_xref
    ADD CONSTRAINT player_xref_pkey PRIMARY KEY (player_xref_id);


--
-- Name: players_nbacom_player_id_key; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY players
    ADD CONSTRAINT players_nbacom_player_id_key UNIQUE (nbacom_player_id);


--
-- Name: players_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY players
    ADD CONSTRAINT players_pkey PRIMARY KEY (players_id);


--
-- Name: playerstats_daily_as_of_nbacom_player_id_key; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY playerstats_daily
    ADD CONSTRAINT playerstats_daily_as_of_nbacom_player_id_key UNIQUE (as_of, nbacom_player_id);


--
-- Name: playerstats_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY playerstats_daily
    ADD CONSTRAINT playerstats_daily_pkey PRIMARY KEY (playerstats_daily_id);


--
-- Name: seasons_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY seasons
    ADD CONSTRAINT seasons_pkey PRIMARY KEY (nbacom_season_id);


--
-- Name: seasons_season_key; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY seasons
    ADD CONSTRAINT seasons_season_key UNIQUE (season);


--
-- Name: team_boxscores_combined_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY team_boxscores_combined
    ADD CONSTRAINT team_boxscores_combined_pkey PRIMARY KEY (team_boxscores_combined_id);


--
-- Name: team_gamelogs_game_id_team_id_key; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY team_gamelogs
    ADD CONSTRAINT team_gamelogs_game_id_team_id_key UNIQUE (game_id, team_id);


--
-- Name: team_gamelogs_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY team_gamelogs
    ADD CONSTRAINT team_gamelogs_pkey PRIMARY KEY (team_gamelogs_id);


--
-- Name: team_opponent_dashboard_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY team_opponent_dashboard
    ADD CONSTRAINT team_opponent_dashboard_pkey PRIMARY KEY (team_opponent_dashboard_id);


--
-- Name: teams_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY teams
    ADD CONSTRAINT teams_pkey PRIMARY KEY (teams_id);


--
-- Name: teamstats_daily_as_of_team_id_key; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY teamstats_daily
    ADD CONSTRAINT teamstats_daily_as_of_team_id_key UNIQUE (as_of, team_id);


--
-- Name: teamstats_daily_pkey; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY teamstats_daily
    ADD CONSTRAINT teamstats_daily_pkey PRIMARY KEY (teamstats_daily_id);


--
-- Name: tid_asof; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY team_opponent_dashboard
    ADD CONSTRAINT tid_asof UNIQUE (team_id, as_of);


--
-- Name: tid_gid; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY team_boxscores_combined
    ADD CONSTRAINT tid_gid UNIQUE (team_id, game_id);


--
-- Name: uq_game_date_dfs_site_source_player_id; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY dfs_salaries
    ADD CONSTRAINT uq_game_date_dfs_site_source_player_id UNIQUE (game_date, dfs_site, source_player_id);


--
-- Name: uq_gamecode_team_code; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY games_meta
    ADD CONSTRAINT uq_gamecode_team_code UNIQUE (gamecode, team_code);


--
-- Name: uq_pid_gid; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_boxscores_combined
    ADD CONSTRAINT uq_pid_gid UNIQUE (player_id, game_id);


--
-- Name: uq_spc_source; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_xref
    ADD CONSTRAINT uq_spc_source UNIQUE (source, source_player_code);


--
-- Name: uq_spid_source; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_xref
    ADD CONSTRAINT uq_spid_source UNIQUE (source, source_player_id);


--
-- Name: uq_team_code; Type: CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY teams
    ADD CONSTRAINT uq_team_code UNIQUE (team_code);


--
-- Name: idx_btree_models_data; Type: INDEX; Schema: public; Owner: nbadb
--

CREATE INDEX idx_btree_models_data ON models USING gin (data);


--
-- Name: idx_btree_playerid; Type: INDEX; Schema: public; Owner: nbadb
--

CREATE INDEX idx_btree_playerid ON ownership USING gin (data);


--
-- Name: playerstats_season_season_nbacom_player_id_idx; Type: INDEX; Schema: public; Owner: nbadb
--

CREATE INDEX playerstats_season_season_nbacom_player_id_idx ON playerstats_season USING btree (season, nbacom_player_id);


--
-- Name: teamstats_season_season_team_id_idx; Type: INDEX; Schema: public; Owner: nbadb
--

CREATE INDEX teamstats_season_season_team_id_idx ON teamstats_season USING btree (season, team_id);


--
-- Name: dfs_salaries_nbacom_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY dfs_salaries
    ADD CONSTRAINT dfs_salaries_nbacom_player_id_fkey FOREIGN KEY (nbacom_player_id) REFERENCES players(nbacom_player_id);


--
-- Name: dfs_salaries_season_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY dfs_salaries
    ADD CONSTRAINT dfs_salaries_season_fkey FOREIGN KEY (season) REFERENCES seasons(season);


--
-- Name: dfs_salaries_team_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY dfs_salaries
    ADD CONSTRAINT dfs_salaries_team_code_fkey FOREIGN KEY (team_code) REFERENCES teams(team_code);


--
-- Name: games_home_team_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY games
    ADD CONSTRAINT games_home_team_code_fkey FOREIGN KEY (home_team_code) REFERENCES teams(team_code);


--
-- Name: games_meta_gamecode_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY games_meta
    ADD CONSTRAINT games_meta_gamecode_fkey FOREIGN KEY (gamecode) REFERENCES games(gamecode);


--
-- Name: games_meta_team_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY games_meta
    ADD CONSTRAINT games_meta_team_code_fkey FOREIGN KEY (team_code) REFERENCES teams(team_code);


--
-- Name: games_season_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY games
    ADD CONSTRAINT games_season_fkey FOREIGN KEY (season) REFERENCES seasons(season);


--
-- Name: games_visitor_team_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY games
    ADD CONSTRAINT games_visitor_team_code_fkey FOREIGN KEY (visitor_team_code) REFERENCES teams(team_code);


--
-- Name: player_boxscores_combined_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_boxscores_combined
    ADD CONSTRAINT player_boxscores_combined_game_id_fkey FOREIGN KEY (game_id) REFERENCES games(game_id);


--
-- Name: player_boxscores_combined_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_boxscores_combined
    ADD CONSTRAINT player_boxscores_combined_player_id_fkey FOREIGN KEY (player_id) REFERENCES players(nbacom_player_id);


--
-- Name: player_gamelogs_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_gamelogs
    ADD CONSTRAINT player_gamelogs_game_id_fkey FOREIGN KEY (game_id) REFERENCES games(game_id);


--
-- Name: player_gamelogs_nbacom_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_gamelogs
    ADD CONSTRAINT player_gamelogs_nbacom_player_id_fkey FOREIGN KEY (nbacom_player_id) REFERENCES players(nbacom_player_id);


--
-- Name: player_gamelogs_team_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_gamelogs
    ADD CONSTRAINT player_gamelogs_team_code_fkey FOREIGN KEY (team_code) REFERENCES teams(team_code);


--
-- Name: player_xref_nbacom_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY player_xref
    ADD CONSTRAINT player_xref_nbacom_player_id_fkey FOREIGN KEY (nbacom_player_id) REFERENCES players(nbacom_player_id);


--
-- Name: playerstats_daily_nbacom_player_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY playerstats_daily
    ADD CONSTRAINT playerstats_daily_nbacom_player_id_fkey FOREIGN KEY (nbacom_player_id) REFERENCES players(nbacom_player_id);


--
-- Name: team_boxscores_combined_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY team_boxscores_combined
    ADD CONSTRAINT team_boxscores_combined_game_id_fkey FOREIGN KEY (game_id) REFERENCES games(game_id);


--
-- Name: team_boxscores_combined_team_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY team_boxscores_combined
    ADD CONSTRAINT team_boxscores_combined_team_code_fkey FOREIGN KEY (team_code) REFERENCES teams(team_code);


--
-- Name: team_gamelogs_game_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY team_gamelogs
    ADD CONSTRAINT team_gamelogs_game_id_fkey FOREIGN KEY (game_id) REFERENCES games(game_id);


--
-- Name: team_gamelogs_team_code_fkey; Type: FK CONSTRAINT; Schema: public; Owner: nbadb
--

ALTER TABLE ONLY team_gamelogs
    ADD CONSTRAINT team_gamelogs_team_code_fkey FOREIGN KEY (team_code) REFERENCES teams(team_code);


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

