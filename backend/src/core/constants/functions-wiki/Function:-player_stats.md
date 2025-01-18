### Get current season or career stats for a given player.

> *Note*: To retrieve the data used to build the formatted text, see [Function: player_stat_data](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-player_stat_data).

`statsapi.player_stats(personId, group="[hitting,pitching,fielding]", type="season")`

> *Note*: For group use `hitting`, `pitching`, or `fielding`. Include multiple groups in the following format (this is a string, not actually a list): `group='[hitting,pitching]'`

> *Note*: For type use `career` or `season`. Include multiple types in the following format (this is a string, not actually a list): `group='[career,season]'`

## Example

Print Chase Utley's career hitting stats (using sports_players endpoint to look up person id)

`print( statsapi.player_stats(next(x['id'] for x in statsapi.get('sports_players',{'season':2008,'gameType':'W'})['people'] if x['fullName']=='Chase Utley'), 'hitting', 'career') )`

### Output

```
Chase "Silver Fox" Utley, 2B (2003-2018)

Career Hitting
gamesPlayed: 1937
groundOuts: 1792
runs: 1103
doubles: 411
triples: 58
homeRuns: 259
strikeOuts: 1193
baseOnBalls: 724
intentionalWalks: 62
hits: 1885
hitByPitch: 204
avg: .275
atBats: 6857
obp: .358
slg: .465
ops: .823
caughtStealing: 22
stolenBases: 154
groundIntoDoublePlay: 93
numberOfPitches: 31043
plateAppearances: 7863
totalBases: 3189
rbi: 1025
leftOnBase: 2780
sacBunts: 6
sacFlies: 72
babip: .297
groundOutsToAirouts: 0.84
```
