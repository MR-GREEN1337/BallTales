### Get a python list of stat leaders overall or for a given league (103=AL, 104=NL).

> *Note*: To retrieve a formatted text version, see [Function: league_leaders](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-league_leaders).

`statsapi.league_leader_data(leaderCategories, season=None, limit=10, statGroup=None, leagueId=None, gameTypes=None, playerPool=None, sportId=1, statType=None)`

> *Note*: StatsAPI does not appear to be supporting the statType=statsSingleSeason at this time,
despite this appearing in the documentation as a best practice for all time leaders.
Be sure to specify a season or other statType such as 'career', or the default will be current season leaders.

> *Note*: Get a list of available leaderCategories by calling the meta endpoint with type=leagueLeaderTypes

> *Note*: Get a list of available statGroups by calling the meta endpoint with type=statGroups
Note that excluding statGroup may return unexpected results. For example leaderCategories='earnedRunAverage'
will return different results with statGroup='pitching' and statGroup='catching'.

> *Note*: Get a list of available gameTypes by calling the meta endpoint with type=gameTypes

> *Note*: Get a list of available statTypes by calling the meta endpoint with type=statTypes

> *Note*: Available playerPool values: ['all','qualified','rookies'] (default is qualified)