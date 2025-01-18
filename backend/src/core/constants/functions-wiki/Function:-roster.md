### Get the roster for a given team.

`statsapi.roster(teamId, rosterType=None, season=datetime.now().year, date=None)`

> *Note*: Get a list of available rosterTypes by calling the meta endpoint with type=rosterTypes. Default `rosterType=active`

> *Note*: Format for date = `MM/DD/YYYY`, e.g. `04/24/2019`

## Example

Print the current Phillies active roster:

`print( statsapi.roster(143) )`

### Output

```
#23  CF  Aaron Altherr
#27  P   Aaron Nola
#46  P   Adam Morgan
#15  C   Andrew Knapp
#22  RF  Andrew McCutchen
#3   RF  Bryce Harper
#16  2B  Cesar Hernandez
#25  RF  Dylan Cozens
#61  P   Edubray Ramos
#51  P   Enyel De Los Santos
#50  P   Hector Neris
#10  C   J.T. Realmuto
#49  P   Jake Arrieta
#48  P   Jerad Eickhoff
#52  P   Jose Alvarez
#12  P   Juan Nicasio
#7   3B  Maikel Franco
#5   RF  Nick Williams
#93  P   Pat Neshek
#9   2B  Phil Gosselin
#17  1B  Rhys Hoskins
#13  2B  Sean Rodriguez
#58  P   Seranthony Dominguez
#21  P   Vince Velasquez
#56  P   Zach Eflin
```
