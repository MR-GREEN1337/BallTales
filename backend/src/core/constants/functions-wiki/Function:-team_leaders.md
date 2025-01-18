### Get stat leaders for a given team.

> *Note*: To retrieve the data used to build the formatted text, see [Function: team_leader_data](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-team_leader_data).

`statsapi.team_leaders(teamId, leaderCategories, season=datetime.now().year, leaderGameTypes="R", limit=10)`

> *Note*: Get a list of available leaderCategories by calling the meta endpoint with type=leagueLeaderTypes

## Example

Print the top 5 team leaders in walks for the 2008 Phillies

`print(statsapi.team_leaders(143,'walks',limit=5,season=2008))`

### Output

```
Rank Name                 Value
    1   Pat Burrell           102
    2   Ryan Howard           81
    3   Chase Utley           64
    4   Jimmy Rollins         58
    5   Jayson Werth          57
```
