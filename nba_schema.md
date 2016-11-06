# nba.stats views

Overview of all of the views in the nba.stats schema.

TODO: I described a view as lastN, but it is really fixed at last3, last5, last10.

These views should refer to an underlying procedure that can be called for true last N.

## vw_cs_dk_points

Calculates draftkings points in database. Not needed when insertion scripts calculate dk_points

Fields:

    player_id, game_id, fg3m, reb, ast, stl, blk, tov, pts
    base_dk_points, dk_bonus, dk_points


## vw_cs_player_gl

Gamelogs joined with additional information about trends and opponent.

Fields:

    season, team_gamenum, player_gamenum, game_id, game_date,
    player_id, player_name, primary_position, position_group,
    team_id, team_code, opponent_team_id, opponent_team_code,
    min, min_delta, min_s, 
    fga, fgm, fta, ftm, fg3a, fg3m, reb, ast, stl, blk, tov, pts,
    dk_points, dk_delta, dk_s, dkpermin, dkpermin_delta, dkpermin_s
    opp_off_rating, opp_def_rating, opp_net_rating, opp_pie, opp_plus_minus


## vw_2015_player_gl

Gamelogs joined with additional information about trends and opponent.

Fields:

    season, team_gamenum, player_gamenum, game_id, game_date,
    player_id, player_name, primary_position, position_group,
    team_id, team_code, opponent_team_id, opponent_team_code,
    min, min_delta, min_s, 
    fga, fgm, fta, ftm, fg3a, fg3m, reb, ast, stl, blk, tov, pts,
    dk_points, dk_delta, dk_s, dkpermin, dkpermin_delta, dkpermin_s
    opp_off_rating, opp_def_rating, opp_net_rating, opp_pie, opp_plus_minus


## vw_today_games 

List of all games (from stats.cs_games) with game_date = today.

Fields:

    game_id, game_date, gamecode, visitor_team_id, visitor_team_code,
    home_team_id, home_team_code


## vw_today_player_gl 

Filters vw_cs_player_gl by players who have games today

Fields:

    season, team_gamenum, player_gamenum, game_id, game_date,
    player_id, player_name, primary_position, position_group,
    team_id, team_code, opponent_team_id, opponent_team_code,
    min, min_delta, min_s, 
    fga, fgm, fta, ftm, fg3a, fg3m, reb, ast, stl, blk, tov, pts,
    dk_points, dk_delta, dk_s, dkpermin, dkpermin_delta, dkpermin_s
    opp_off_rating, opp_def_rating, opp_net_rating, opp_pie, opp_plus_minus


## vw_today_player_gl_lastN 

Filters cs_player_gamelogs by players who have games today and only last N gamelogs

Fields:

    game_id, game_date, player_id, player_name, team_code, opponent_team_code,
    reb, ast, stl, blk, pts, min, min_s, dk, dk_s, dkpermin_s, date_rank


## vw_today_player_ids

List of nbacom_player_ids who have games today

Fields:

    nbacom_player_id


## vw_today_team_codes

List of team_codes of teams with games today

Fields:

    team_code


## vw_today_team_ids

List of team_ids of teams with games today

Fields:

    team_id


## vw_tomorrow_player_gl

Filters cs_player_gamelogs by players who have games tomorrow

Fields:

    game_date, player_id, player_name, team_code, opponent_team_code,
    min, min_s, reb, ast, stl, blk, pts, dk, dk_s, dkpermin, dkpermin_s


## vw_tomorrow_player_gl_last5 

Filters cs_player_gamelogs by players who have games today and only last 5 gamelogs

Fields:

    game_id, game_date, player_id, player_name, team_code, opponent_team_code,
    min, min_s, reb, ast, stl, blk, pts, dk, dk_s, dkpermin_s, date_rank
    

## vw_tomorrow_player_ids

List of nbacom_player_ids who have games tomorrow

Fields:

    nbacom_player_id


## vw_tomorrow_team_codes

List of team_codes of teams with games tomorrow

Fields:

    team_code
    

# dfs views

Overview of all of the views in the nba.dfs schema.

## vw_cs_features

Work-in-progress to collect gamelogs with all features relevant for machine learning model.
This is DraftKings-only at this point.

Fields:
    
    player_id, player_name, game_id, game_date, site_position, 
    salary, sal_delta, sal_mult, sal_mult_s,
    x3, x4, x5, x6, x7, x8

## vw_2015_features

Work-in-progress to collect gamelogs with all features relevant for machine learning model.
This is DraftKings-only at this point.

Fields:
    
    player_id, player_name, game_id, game_date, site_position, 
    salary, sal_delta, sal_mult, sal_mult_s,
    x3, x4, x5, x6, x7, x8


## vw_cs_dk_sal

DraftKings salaries from current NBA season

Fields:

    nbacom_player_id, source_player_name, game_date,
    site_position, salary
    

## vw_2015_dk_sal

DraftKings salaries from 2014-15 NBA season

Fields:

    nbacom_player_id, source_player_name, game_date,
    site_position, salary


## vw_multiples

Shows how productive the field was on a particular slate as a function of salary.

Fields:

    game_date, num_players,
    num_x5, num_x6, num_x7, num_x8,
    x5_pct, x6_pct, x7_pct, x8_pct
    

## vw_value_index

Provides single measure of "value" (after-the-fact) on a particular slate. Adds up all of the salaries of players that exceeded certain number of minutes with their production.

Fields:
    
    game_date, num_games, value_index
