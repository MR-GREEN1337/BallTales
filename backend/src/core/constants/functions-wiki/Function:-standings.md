### Get formatted standings for a given league/division and season.

> *Note*: To retrieve the data used to build the formatted text, see [Function: standings_data](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-standings_data).

`statsapi.standings(leagueId="103,104", division="all", include_wildcard=True, season=None, standingsTypes=None, date=None)`

> *Note*: Using both leagueId and divisionId is fine, as long as the division belongs to the specified league

> *Note*: Return value will be a formatted table including division and wildcard standings, unless `include_wildcard`=`False`

Format for date = `MM/DD/YYYY`, e.g. `04/24/2019`

## Example

Print National League standings from 09/27/2008

`print( statsapi.standings(leagueId=104,date='09/27/2008') )`

### Output

```
National League Central
Rank Team                   W   L   GB  (E#) WC Rank WC GB (E#)
    1   Chicago Cubs          97  63   -    -      -      -    -
    2   Milwaukee Brewers     89  72  8.5   E      1      -    -
    3   Houston Astros        85  75  12.0  E      3     3.5   E
    4   St. Louis Cardinals   85  76  12.5  E      4     4.0   E
    5   Cincinnati Reds       74  87  23.5  E      7    15.0   E
    6   Pittsburgh Pirates    66  95  31.5  E     11    23.0   E

National League West
Rank Team                   W   L   GB  (E#) WC Rank WC GB (E#)
    1   Los Angeles Dodgers   84  77   -    -      -      -    -
    2   Arizona Diamondbacks  81  80  3.0   E      6     8.0   E
    3   Colorado Rockies      74  87  10.0  E      8    15.0   E
    4   San Francisco Giants  71  90  13.0  E     10    18.0   E
    5   San Diego Padres      63  98  21.0  E     12    26.0   E

National League East
Rank Team                   W   L   GB  (E#) WC Rank WC GB (E#)
    1   Philadelphia Phillies 91  70   -    -      -      -    -
    2   New York Mets         89  72  2.0   E      2      -    -
    3   Florida Marlins       83  77  7.5   E      5     5.5   E
    4   Atlanta Braves        72  89  19.0  E      9    17.0   E
    5   Washington Nationals  59  101 31.5  E     13    29.5   E
```
