### Returns a Python dict containing data about pace of game for a given season (back to 1999).

> *Note*: To retrieve a formatted text version, see [Function: game_pace](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-game_pace).

`statsapi.game_pace_data(season=datetime.now().year, sportId=1)`

> *Note*: The `season` parameter will default to the current calendar year. From January 1 until each season starts, this may result in unexpected results. Therefore, it is best to include the season parameter explicitly.