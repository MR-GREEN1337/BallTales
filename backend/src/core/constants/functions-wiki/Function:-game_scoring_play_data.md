### Returns a python dict of scoring plays for a given game.

> *Note*: This method is broken as of 7/25/2020 due to a change in the data returned by the `schedule` endpoint. Please update to v0.1.9 for the fix.

> *Note*: To retrieve a formatted text version, see [Function: game_scoring_plays](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-game_scoring_plays).

`statsapi.game_scoring_play_data(gamePk)`

Will return a dict containing 3 keys:

* home - home team data
* away - away team data
* plays - sorted list of scoring play data

