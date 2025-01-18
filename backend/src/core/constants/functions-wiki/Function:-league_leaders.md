### Get stat leaders overall or for a given league (103=AL, 104=NL).

> *Note*: To retrieve the data used to build the formatted text, see [Function: league_leader_data](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-league_leader_data).

`statsapi.league_leaders(leaderCategories, season=None, limit=10, statGroup=None, leagueId=None, gameTypes=None, playerPool=None, sportId=1, statType=None)`

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

## Example

Print a list of the top 10 pitchers by career earned run average

`print( statsapi.league_leaders('earnedRunAverage',statGroup='pitching',limit=10,statType='career') )`

### Output

```
Rank Name                 Team                    Value
    1   Al Spalding          Chicago White Stockings 1.78
    2   Ed Walsh             Chicago White Sox       1.82
    3   Addie Joss           Cleveland Naps          1.89
    4   Jim Devlin           Louisville Grays        1.89
    5   Craig Kimbrel        Atlanta Braves          2.00
    5   Laurie Reis          Chicago White Stockings 2.00
    7   Jack Pfiester        Pittsburgh Pirates      2.02
    8   Joe Wood             Cleveland Indians       2.03
    9   Christy Mathewson    New York Giants         2.13
    10  Walter Johnson       Washington Senators     2.17
```

## Example

Print a list of the top 5 batters in 2018 by OPS

`print( statsapi.league_leaders('onBasePlusSlugging',statGroup='hitting',limit=5,season=2018) )`

### Output

```
Rank Name                 Team                    Value
    1   Mike Trout           Los Angeles Angels      1.088
    2   Mookie Betts         Boston Red Sox          1.078
    3   J.D. Martinez        Boston Red Sox          1.031
    4   Christian Yelich     Milwaukee Brewers       1.000
    5   Jose Ramirez         Cleveland Indians       .939
```

## Example

Print a list of the 10 American League players with the most errors in 2017

`print( statsapi.league_leaders('errors',statGroup='fielding',limit=10,season=2017,leagueId=103) )`

### Output

```
Rank Name                 Team                   Value
    1   Tim Anderson         Chicago White Sox       28
    2   Rougned Odor         Texas Rangers           19
    3   Tim Beckham          Baltimore Orioles       18
    3   Nicholas Castellanos Detroit Tigers          18
    3   Jorge Polanco        Minnesota Twins         18
    6   Elvis Andrus         Texas Rangers           17
    6   Xander Bogaerts      Boston Red Sox          17
    6   Jean Segura          Seattle Mariners        17
    9   Alcides Escobar      Kansas City Royals      15
    9   Jonathan Schoop      Baltimore Orioles       15
```

## Example

Print a list of top 10 all time career leader in triples

`print( statsapi.league_leaders('triples',statGroup='hitting',limit=10,sportId=1,statType='career') )`

```
Rank Name                 Team                    Value
    1   Sam Crawford         Detroit Tigers           309
    2   Ty Cobb              Philadelphia Athletics   297
    3   Tristram Speaker     Washington Senators      222
    4   Paul Waner           New York Yankees         191
    5   Bid McPhee           Cincinnati Reds          188
    6   Eddie Collins        Chicago White Sox        187
    7   Sam Rice             Washington Senators      184
    8   Rabbit Maranville    Boston Braves            177
    8   Stan Musial          St. Louis Cardinals      177
    10  Goose Goslin         Washington Senators      173
```
