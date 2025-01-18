### Get a formatted boxscore for a given game.

> *Note*: To retrieve the data used to build the formatted text, see [Function: boxscore_data](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-boxscore_data).

> *Note*: This function uses the game endpoint instead of game_box,
because game_box does not contain the players' names as they should be
displayed in the box score (e.g. Last name only or Last, F)

`statsapi.boxscore(gamePk, battingBox=True, battingInfo=True, fieldingInfo=True, pitchingBox=True, gameInfo=True, timecode=None)`

It is possible to get the boxscore as it existed at a specific time by including the timestamp in the timecode parameter.
The timecode should be in the format `YYYYMMDD_HHMMSS`, and in the UTC timezone
For example, 4/24/19 10:32:40 EDT (-4) would be: `20190425_012240`
A list of timestamps for game events can be found through the game_timestamps endpoint (using the [get function](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-get)):
`statsapi.get('game_timestamps',{'gamePk':565997})`

Which sections are included can be customized using the `battingBox`, `battingInfo`, `pitchingBox`, and `gameInfo `parameters
All default to `True`; set to `False `to exclude from the results
For example, to retrieve only the batting box: `statsapi.boxscore(565997,battingInfo=False,fieldingInfo=False,pitchingBox=False,gameInfo=False)`

## Example:

Print the full box score for Phillies @ Mets game on 4/24/2019 (gamePk=565997):

`print( statsapi.boxscore(565997) )`

### Output:

    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    Phillies Batters                         AB   R   H  RBI BB   K  LOB AVG   OPS  | Mets Batters                             AB   R   H  RBI BB   K  LOB AVG   OPS
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    1 McCutchen  LF                           5   0   1   0   0   1   3  .250 .830  | 1 McNeil  LF                              4   0   1   0   0   0   1  .363 .928
    2 Realmuto  C                             3   1   1   0   1   1   2  .282 .786  | 2 Conforto  RF                            3   0   0   0   1   1   1  .292 .986
    3 Harper  RF                              4   1   1   1   1   3   4  .261 .909  | 3 Canó  2B                                3   0   3   0   1   0   0  .272 .758
    4 Hoskins  1B                             4   2   2   2   1   1   3  .273 .982  | 4 Ramos, W  C                             4   0   0   0   0   3   6  .278 .687
    5 Franco  3B                              5   1   1   1   0   0   3  .271 .905  | 5 Smith, Do  1B                           2   0   0   0   1   1   2  .400 .996
    6 Hernández, C  2B                        5   1   1   0   0   1   2  .267 .730  |     c-Alonso, P  1B                       1   0   0   0   0   1   1  .306 1.086
    7 Rodríguez, S  SS                        4   0   1   0   0   1   1  .250 .750  | 6 Frazier, T  3B                          3   0   0   0   0   0   4  .182 .705
    8 Velasquez  P                            1   0   0   0   0   0   0  .167 .453  | 7 Rosario, A  SS                          4   0   1   0   0   0   1  .261 .676
        a-Williams, N  PH                     1   0   0   0   0   0   1  .150 .427  | 8 Lagares  CF                             2   0   0   0   0   1   1  .244 .653
        Neshek  P                             0   0   0   0   0   0   0  .000 .000  |     a-Nimmo  CF                           2   0   0   0   0   0   1  .203 .714
        Domínguez  P                          0   0   0   0   0   0   0  .000 .000  | 9 Vargas  P                               2   0   0   0   0   1   1  .000 .000
        b-Gosselin  PH                        1   0   1   1   0   0   0  .211 .474  |     Lugo, S  P                            0   0   0   0   0   0   0  .000 .000
        Morgan  P                             0   0   0   0   0   0   0  .000 .000  |     Zamora  P                             0   0   0   0   0   0   0  .000 .000
        c-Knapp  PH                           1   0   0   0   0   1   1  .222 .750  |     b-Guillorme  PH                       1   0   1   0   0   0   0  .167 .378
        Nicasio  P                            0   0   0   0   0   0   0  .000 .000  |     Gsellman  P                           0   0   0   0   0   0   0  .000 .000
    9 Quinn  CF                               4   0   1   1   0   1   1  .120 .305  |     Rhame  P                              0   0   0   0   0   0   0  .000 .000
        1-Altherr  CF                         0   0   0   0   0   0   0  .042 .163  |     d-Davis, J  PH                        1   0   0   0   0   1   0  .276 .865
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    Totals                                   38   6  10   6   3  10  21             | Totals                                   32   0   6   0   3   9  19
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    a-Popped out for Velasquez in the 6th.                                          | a-Flied out for Lagares in the 6th.
    b-Singled for Domínguez in the 8th.                                             | b-Singled for Zamora in the 7th.
    c-Struck out for Morgan in the 9th.                                             | c-Struck out for Smith, Do in the 8th.
    1-Ran for Quinn in the 8th.                                                     | d-Struck out for Rhame in the 9th.
                                                                                    |
    BATTING                                                                         | BATTING
    2B: Harper (7, Vargas); Rodríguez, S (1, Rhame); Realmuto (4, Vargas).          | TB: Canó 3; Guillorme; McNeil; Rosario, A.
    3B: Hoskins (1, Gsellman).                                                      | Runners left in scoring position, 2 out: Frazier, T 2; Vargas; Smith, Do 2.
    HR: Hoskins (7, 9th inning off Rhame, 1 on, 0 out).                             | GIDP: McNeil.
    TB: Franco; Gosselin; Harper 2; Hernández, C; Hoskins 7; McCutchen; Quinn;      | Team RISP: 0-for-6.
        Realmuto 2; Rodríguez, S 2.                                                 | Team LOB: 9.
    RBI: Franco (19); Gosselin (4); Harper (15); Hoskins 2 (20); Quinn (1).         |
    Runners left in scoring position, 2 out: Hoskins; Hernández, C; Knapp; Realmuto | FIELDING
        2; McCutchen.                                                               | E: Canó (3, fielding); Rosario, A 2 (7, throw, throw).
    SAC: Rodríguez, S; Velasquez.                                                   |
    Team RISP: 4-for-13.                                                            |
    Team LOB: 11.                                                                   |
                                                                                    |
    FIELDING                                                                        |
    DP: (Hernández, C-Rodríguez, S-Hoskins).                                        |
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    Phillies Pitchers                            IP   H   R  ER  BB   K  HR   ERA   | Mets Pitchers                                IP   H   R  ER  BB   K  HR   ERA
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    Velasquez  (W, 1-0)                         5.0   3   0   0   3   6   0   1.99  | Vargas  (L, 1-1)                            4.2   3   1   1   2   4   0   7.20
    Neshek  (H, 2)                              1.0   1   0   0   0   0   0   2.70  | Lugo, S                                     2.0   0   0   0   0   2   0   4.60
    Domínguez  (H, 3)                           1.0   1   0   0   0   0   0   4.32  | Zamora                                      0.1   0   0   0   0   1   0   0.00
    Morgan                                      1.0   1   0   0   0   2   0   0.00  | Gsellman                                    1.0   5   3   3   0   1   0   4.20
    Nicasio                                     1.0   0   0   0   0   1   0   5.84  | Rhame                                       1.0   2   2   2   1   2   1   8.10
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    Totals                                      9.0   6   0   0   3   9   0         | Totals                                      9.0  10   6   6   3  10   1
    ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------
    WP: Velasquez; Gsellman.
    HBP: Realmuto (by Vargas); Frazier, T (by Velasquez).
    Pitches-strikes: Velasquez 97-53; Neshek 13-8; Domínguez 9-6; Morgan 14-10; Nicasio 15-10; Vargas 89-53; Lugo, S 32-23; Zamora 5-3; Gsellman 25-17; Rhame 19-12.
    Groundouts-flyouts: Velasquez 6-3; Neshek 1-2; Domínguez 1-1; Morgan 1-0; Nicasio 2-0; Vargas 8-3; Lugo, S 3-2; Zamora 0-0; Gsellman 1-1; Rhame 0-0.
    Batters faced: Velasquez 22; Neshek 4; Domínguez 3; Morgan 4; Nicasio 3; Vargas 21; Lugo, S 8; Zamora; Gsellman 8; Rhame 6.
    Inherited runners-scored: Lugo, S 2-0; Zamora 1-0.
    Umpires: HP: Brian Gorman. 1B: Jansen Visconti. 2B: Mark Carlson. 3B: Scott Barry.
    Weather: 66 degrees, Clear.
    Wind: 12 mph, L To R.
    First pitch: 7:11 PM.
    T: 3:21.
    Att: 27,685.
    Venue: Citi Field.
    April 24, 2019
    -----------------------------------------------------------------------------------------------------------------------------------------------------------------
