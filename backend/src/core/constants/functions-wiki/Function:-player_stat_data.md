### Get a Python dict of current season or career stat data for a given player.

> *Note*: To retrieve a formatted text version, see [Function: player_stats](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-player_stats).

`statsapi.player_stat_data(personId, group="[hitting,pitching,fielding]", type="season", sportId=1)`

> *Note*: For group use `hitting`, `pitching`, or `fielding`. Include multiple groups in the following format (this is a string, not actually a list): `group='[hitting,pitching]'`

> *Note*: For type use `career` or `season` or `yearByYear` (as of v0.1.7). Include multiple types in the following format (this is a string, not actually a list): `group='[career,season,yearByYear]'`
