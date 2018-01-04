# coding: utf-8
from nba.db.nbapg import NBAPostgres
nbap = NBAPostgres(user='nbadb', password='cft0911', database='nbadb')
q = """
CREATE TEMPORARY TABLE tmptbl (
  id integer,
  player varchar(50),
  team varchar(5)
)
"""
d = {'id': 1, 'player': 'Joe Smith', 'team': 'CHI}
d = {'id': 1, 'player': 'Joe Smith', 'team': 'CHI'}
nbap._insert_dict(d, 'tmptbl')
nbap.execute(q)
nbap._insert_dict(d, 'tmptbl')
nbap.select_dict('select * from tmptbl')
ld = [{'id': i, 'player': random.choice(players), 'team': random.choice(teams)} for i in range(0,100)]
import random
teams = ['ATL', 'BOS', 'CHI', 'DET', 'OKC', 'ORL', 'NYK', 'PHI', 'POR', 'SAS', 'SAC', 'UTA', 'TOR', 'WAS']
players = ['James Harden', 'LeBron James', 'Russell Westbrook', 'Kevin Durant', 'Joel Embiid', 'Ben Simmons', 'Stephen Curry', 'Chris Paul', 'Karl-Anthony Towns', 'Kristaps Porzingis', 'Jimmy Butler', 'Kyrie Irving', 'John Wall', 'Kevin Love', 'Kyle Kuzma', 'Draymond Green', 'Bradley Beal', 'Lonzo Ball', 'Paul George', 'Al Horford', 'Clint Capela', 'Klay Thompson', 'Brandon Ingram', 'Dario Saric', 'Robert Covington', 'Enes Kanter', 'Jeff Teague', 'Isaiah Thomas', 'Tim Hardaway Jr.', 'Taj Gibson', 'Andrew Wiggins', 'Eric Gordon', 'Carmelo Anthony', 'Steven Adams', 'Jayson Tatum', 'Otto Porter Jr.', 'Jaylen Brown', 'Kentavious Caldwell-Pope', 'Julius Randle', 'JJ Redick', 'Michael Beasley', 'Trevor Ariza', 'Dwyane Wade', 'Marcin Gortat', 'Jordan Bell', 'Marcus Smart', 'Courtney Lee', 'Jordan Clarkson', 'P.J. Tucker', 'Marcus Morris', 'Jarrett Jack', 'Ryan Anderson', 'Mike Scott', 'Kelly Oubre Jr.', 'Larry Nance Jr.', 'Richaun Holmes', 'Markieff Morris', 'Brook Lopez', 'Omri Casspi', 'Trevor Booker', 'Terry Rozier', 'Jeff Green', 'T.J. McConnell', 'J.R. Smith', 'Jamal Crawford', 'Kyle O'Quinn', 'Frank Ntilikina', 'Andre Iguodala', 'Jerryd Bayless', 'Markelle Fultz', 'Nene Hilario', 'Jose Calderon', 'Tomas Satoransky', 'Tim Frazier', 'Aron Baynes', 'Josh Hart', 'Amir Johnson', 'Doug McDermott', 'Jerami Grant', 'Patrick McCaw', 'Shaun Livingston', 'Kyle Korver', 'Corey Brewer', 'Guillermo Hernangomez', 'David West', 'Jae Crowder', 'Tristan Thompson', 'Ian Mahinmi', 'Daniel Theis', 'Tyus Jones', 'Gorgui Dieng', 'Damyean Dotson', 'Andre Roberson', 'Kevon Looney', 'Iman Shumpert', 'Derrick Rose', 'Shane Larkin', 'Nemanja Bjelica', 'Shabazz Muhammad', 'Lance Thomas', 'Timothe Luwawu-Cabarrot', 'Ron Baker', 'Alex Abrines', 'Channing Frye', 'Zaza Pachulia', 'Nick Young', 'Semi Ojeleye', 'Ivica Zubac', 'Patrick Patterson', 'Luc Richard Mbah a Moute', 'JaVale McGee', 'Jodie Meeks', 'Ramon Sessions', 'Raymond Felton', 'Quinn Cook', 'Sheldon Mac', 'Chris McCullough', 'Devin Robinson', 'Jason Smith', 'Mike Young', 'Jabari Bird', 'Guerschon Yabusele', 'Kadeem Allen', 'Abdel Nader', 'Gordon Hayward', 'Anthony Brown', 'Cole Aldrich', 'Marcus Georges-Hunt', 'Aaron Brooks', 'Justin Patton', 'Thomas Bryant', 'Vander Blue', 'Tyler Ennis', 'Luol Deng', 'Andrew Bogut', 'Alex Caruso', 'Jacob Pullen', 'Justin Anderson', 'James Michael McAdoo', 'Furkan Korkmaz', 'Luke Kornet', 'Isaiah Hicks', 'Joakim Noah', 'Dakari Johnson', 'Daniel Hamilton', 'PJ Dozier', 'Terrance Ferguson', 'Josh Huestis', 'Kyle Singler', 'Nick Collison', 'Briante Weber', 'Bobby Brown', 'Demetrius Jackson', 'Tarik Black', 'Troy Williams', 'Chinanu Onuaku', 'Zhou Qi', 'Chris Boucher', 'Damian Jones', 'London Perrantes', 'John Holland', 'Ante Zizic', 'Cedi Osman']
players = ['James Harden', 'LeBron James', 'Russell Westbrook', 
'Kevin Durant', 'Joel Embiid', 'Ben Simmons', 'Stephen Curry', 
'Chris Paul', 'Karl-Anthony Towns', 'Kristaps Porzingis', 'Jimmy Butler', 
'Kyrie Irving', 'John Wall', 'Kevin Love', 'Kyle Kuzma', 'Draymond Green', 
'Bradley Beal', 'Lonzo Ball', 'Paul George', 'Al Horford', 'Clint Capela', 
'Klay Thompson', 'Brandon Ingram', 'Dario Saric', 'Robert Covington', 
'Enes Kanter', 'Jeff Teague', 'Isaiah Thomas', 'Tim Hardaway Jr.', 
'Taj Gibson', 'Andrew Wiggins', 'Eric Gordon', 'Carmelo Anthony', 
'Steven Adams', 'Jayson Tatum', 'Otto Porter Jr.', 'Jaylen Brown', 
'Kentavious Caldwell-Pope', 'Julius Randle', 'JJ Redick', 'Michael Beasley', 
'Trevor Ariza', 'Dwyane Wade', 'Marcin Gortat', 'Jordan Bell', 'Marcus Smart']
ld = [{'id': i, 'player': random.choice(players), 'team': random.choice(teams)} for i in range(0,100)]
ld
nbadb.insert_dicts(ld, 'tmptbl')
nbap.insert_dicts(ld, 'tmptbl')
nbap.select_dict('select * from tmptbl')
nbap.safe_insert_dicts(ld, 'tmptbl')
nbap.select_list('select * from tmptbl')
nbap.select_list('select player from tmptbl')
