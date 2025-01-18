## Returns a python dict containing boxscore data for a given game.

> *Note*: To retrieve a formatted text version of the box score, see [Function: boxscore](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-boxscore).

> *Note*: This function uses the game endpoint instead of game_box, because game_box does not contain the players' names as they should be displayed in the box score (e.g. Last name only or Last, F)

`statsapi.boxscore_data(gamePk, timecode=None)`

It is possible to get the boxscore as it existed at a specific time by including the timestamp in the timecode parameter.
The timecode should be in the format `YYYYMMDD_HHMMSS`, and in the UTC timezone
For example, 4/24/19 10:32:40 EDT (-4) would be: `20190425_012240`
A list of timestamps for game events can be found through the game_timestamps endpoint (using the [get function](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-get)):
`statsapi.get('game_timestamps',{'gamePk':565997})`
