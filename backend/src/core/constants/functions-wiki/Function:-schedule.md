### Get list of games for a given date/range and/or team/opponent.

`statsapi.schedule(date=None, start_date=None, end_date=None, team="", opponent="", sportId=1, game_id=None)`

> *Note*: Include a game_id to get data for that game.

Output will be a list containing a dict for each game. Fields in the dict:

* `game_id`: unique MLB game id (primary key, or gamePk)
* `game_datetime`: date and timestamp in UTC (be careful if you truncate the time--the date may be the next day for a late game)
* `game_date`: date of game (`YYYY-MM-DD`)
* `game_type`: Preseason, Regular season, Postseason, etc. Look up possible values using the meta endpoint with type=gameTypes
* `status`: Scheduled, Warmup, In Progress, Final, etc. Look up possible values using the meta endpoint with `type=gameStatus`
* `away_name`: team name for the away team (e.g. `Philadelphia Phillies`)
* `home_name`: team name for the home team (e.g. `Philadelphia Phillies`)
* `away_id`: team id for the away team, e.g. `143`. Use this to look up other info about a team using the team endpoint with teamId=143
* `home_id`: team id for the home team, e.g. `143`. Use this to look up other info about a team using the team endpoint with teamId=143
* `doubleheader`: indicates if the game is part of a straight doubleheader (`Y`), a split doubleheader (`S`), or not part of a doubleheader (`N`)
* `game_num`: game sequence (`1`, `2`) if part of a doubleheader (will be `1` when not part of a doubleheader or split squad)
* `away_score`: runs scored by the away team (even when game is in progress)
* `home_score`: runs scored by the home team (even when game is in progress)
* `winning_team`: team name for the winning team, if the game is final (e.g. `Philadelphia Phillies`)
* `losing_team`: team name for the losing team, if the game is final (e.g. `Philadelphia Phillies`)
* `winning_pitcher`: full name of the winning pitcher, if the game is final and has a winner (not postponed/tied)
* `losing_pitcher`: full name of the losing pitcher, if the game is final and has a winner (not postponed/tied)
* `save_pitcher`: full name of the pitcher credited with a save, if the game is final and has a winner (not postponed/tied)
* `home_probable_pitcher`: full name of the probable pitcher for the home team, if available
* `away_probable_pitcher`: full name of the probable pitcher for the away team, if available
* `home_pitcher_note`: pitching report for the home team probable pitcher, if available
* `away_pitcher_note`: pitching report for the away team probable pitcher, if available
* `current_inning`: current inning (applies best to in-progress games)
* `inning_state`: state of current inning: `top`, `middle`, `bottom`, `end` (applies best to in-progress games)
* `venue_id`: id of the venue where the game is/was
* `venue_name`: name of the venue where the game is/was
* `national_broadcasts`: list of stations/services hosting a national broadcast, as well as `MLB.tv Free Game` when applicable
* `summary`:  if the game is final or in progress, the summary will include `<Date> - <Away Team Name> (<Away Score>) @ <Home Team Name> (<Home Score>) (<Game Status>)`. if the game has not started yet, the summary will include `<Date> - <Away Team Name> @ <Home Team Name> (<Game Status>)`

## Example

Games between Phillies and Mets in July 2018:

`games = statsapi.schedule(start_date='07/01/2018',end_date='07/31/2018',team=143,opponent=121)`

Print a list of those games with final score or game status:

```python
for x in games:
    print(x['summary'])
```

### Output

```
2018-07-09 - Philadelphia Phillies (3) @ New York Mets (4) (Final)
2018-07-09 - Philadelphia Phillies (3) @ New York Mets (1) (Final)
2018-07-10 - Philadelphia Phillies (7) @ New York Mets (3) (Final)
2018-07-11 - Philadelphia Phillies (0) @ New York Mets (3) (Final)
```

## Example

Print a list of decisions for those games:

```python
for x in games:
    print("%s Game %s - WP: %s, LP: %s" % (x['game_date'],x['game_num'],x['winning_pitcher'],x['losing_pitcher']))
```

### Output

```
2018-07-09 Game 1 - WP: Tim Peterson, LP: Victor Arano
2018-07-09 Game 2 - WP: Aaron Nola, LP: Corey Oswalt
2018-07-10 Game 1 - WP: Enyel De Los Santos, LP: Drew Gagnon
2018-07-11 Game 1 - WP: Robert Gsellman, LP: Mark Leiter Jr.
```
