### Get a python list of stat leader data for a given team.

> *Note*: To retrieve a formatted text version, see [Function: team_leaders](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-team_leaders).

`statsapi.team_leader_data(teamId, leaderCategories, season=datetime.now().year, leaderGameTypes="R", limit=10)`

> *Note*: Get a list of available leaderCategories by calling the meta endpoint with type=leagueLeaderTypes