### Get a text-formatted list of scoring plays for a given game

> *Note*: This method is broken as of 7/25/2020 due to a change in the data returned by the `schedule` endpoint. Please update to v0.1.9 for the fix.

> *Note*: To retrieve the data used to build the formatted text, see [Function: game_scoring_play_data](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-game_scoring_play_data).

`statsapi.game_scoring_plays(gamePk)`

## Example

Print a list of scoring plays from the 4/28/2019 Marlins @ Phillies game

`print( statsapi.game_scoring_plays(567074) )`

### Output (truncated to show only the first and last records):

```
Rhys Hoskins doubles (6) on a sharp line drive to left fielder Isaac Galloway.   Bryce Harper scores.
Bottom 1 - Miami Marlins: 0, Philadelphia Phillies: 1

Rhys Hoskins walks.   Andrew McCutchen scores.    Jean Segura to 3rd.  Wild pitch by pitcher Tayron Guerrero.
Bottom 8 - Miami Marlins: 1, Philadelphia Phillies: 5
```