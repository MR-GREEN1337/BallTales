### Get the highlight video links for a given game

> *Note*: To retrieve the data used to build the formatted text, see [Function: game_highlight_data](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-game_highlight_data).

`statsapi.game_highlights(gamePk)`

## Example

Print the highlight links for the most recent Phillies game:

`print( statsapi.game_highlights( statsapi.last_game(143) ) )`

Output (truncated to only include the first two highlights):

```
Hoskins' RBI double (00:00:16)
Rhys Hoskins belts a double off the left-center-field wall to score Bryce Harper and give the Phillies a 1-0 lead in the bottom of the 1st
https://cuts.diamond.mlb.com/FORGE/2019/2019-04/28/b1117503-3df11d8d-6df0dd65-csvm-diamondx64-asset_1280x720_59_4000K.mp4

Phanatic has birthday party (00:01:15)
Kids and fellow mascots were at Citizens Bank Park to celebrate the Phillie Phanatic's birthday before the game against the Marlins
https://cuts.diamond.mlb.com/FORGE/2019/2019-04/28/7d978385-db13f22d-f68c304f-csvm-diamondx64-asset_1280x720_59_4000K.mp4
```
