### Get a text-formatted list about pace of game for a given season (back to 1999).

> *Note*: To retrieve the data used to build the formatted text, see [Function: game_pace_data](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-game_pace_data).

`statsapi.game_pace(season=datetime.now().year, sportId=1)`

> *Note*: The `season` parameter will default to the current calendar year. From January 1 until each season starts, this may result in unexpected results. Therefore, it is best to include the season parameter explicitly.

## Example

Print the pace of game stats for 2008, in order to determine the number and average time of extra inning games:

`print(statsapi.game_pace(2008))`

### Output:
```
    2008 Game Pace Stats
    hitsPer9Inn: 18.26
    runsPer9Inn: 9.38
    pitchesPer9Inn: 297.72
    plateAppearancesPer9Inn: 77.89
    hitsPerGame: 18.11
    runsPerGame: 9.3
    inningsPlayedPerGame: 8.96
    pitchesPerGame: 295.36
    pitchersPerGame: 7.83
    plateAppearancesPerGame: 77.28
    totalGameTime: 7086:06:00
    totalInningsPlayed: 21748.0
    totalHits: 43972
    totalRuns: 22585
    totalPlateAppearances: 187630
    totalPitchers: 19012
    totalPitches: 717131
    totalGames: 2428
    total9InnGames: 2428
    totalExtraInnGames: 208
    timePerGame: 02:55:07
    timePerPitch: 00:00:36
    timePerHit: 00:09:40
    timePerRun: 00:18:50
    timePerPlateAppearance: 00:02:16
    timePer9Inn: 02:56:30
    timePer77PlateAppearances: 02:54:29
    totalExtraInnTime: 775:10:00
    timePer7InnGameWithoutExtraInn: 00:00:00
    total9InnGamesCompletedEarly: 3
    total9InnGamesWithoutExtraInn: 2217
    total9InnGamesScheduled: 2428
    hitsPerRun: 1.947
    pitchesPerPitcher: 37.72
    total7InnGames: 3
    total9InnGames: 2217
    totalExtraInnGames: 208
    timePer7InnGame: 01:54:40
    timePer9InnGame: 02:50:38
    timePerExtraInnGame: 03:43:36
```
