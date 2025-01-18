### Get a dict of standings data for a given league/division and season.

> *Note*: To retrieve a formatted text version, see [Function: standings](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-standings).

`statsapi.standings_data(leagueId="103,104", division="all", include_wildcard=True, season=None, standingsTypes=None, date=None)`

> *Note*: Using both leagueId and divisionId is fine, as long as the division belongs to the specified league

> *Note*: Format for date = `MM/DD/YYYY`, e.g. `04/24/2019`

> *Note*: The `division` parameter accepts `all` or a specific division abbreviation or id (string or integer), e.g. `nle`, `alw`, 200, 204, etc.

> *Note*: Return value will be a dict including division and wildcard standings, regardless of include_wildcard value (parameter still included to avoid breaking anyone's code, even though it does not do anything)