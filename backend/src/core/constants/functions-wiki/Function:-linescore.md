### Get formatted linescore for a given game.

`statsapi.linescore(gamePk, timecode=None)`

> *Note*: This function uses the game endpoint instead of game_linescore, because game_linescore does not contain the team names or game status and it's better to make one call instead of two. All of this data can also be retrieved through the schedule endpoint using hydrate=linescore, but the schedule endpoint does not support the timecode parameter.

> *Note*: It is possible to get the linescore as it existed at a specific time by including the timestamp in the `timecode` parameter. The timecode should be in the format `YYYYMMDD_HHMMSS`, and in the UTC timezone For example, 4/24/19 10:32:40 EDT (-4) would be: 20190425_012240 A list of timestamps for game events can be found through the game_timestamps endpoint: `statsapi.get('game_timestamps',{'gamePk':565997})`

## Example

Print the linescore for the Phillies/Mets game on 4/25/19:

`print( statsapi.linescore(565997) )`

Output:

```
Final    1 2 3 4 5 6 7 8 9  R   H   E
Phillies 1 0 0 0 0 0 0 3 2  6   10  0
Mets     0 0 0 0 0 0 0 0 0  0   6   3
```
