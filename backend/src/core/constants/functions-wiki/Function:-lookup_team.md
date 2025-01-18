### Get a info about a team or teams based on the team name, city, abbreviation, or file code.

`statsapi.lookup_team(lookup_value, activeStatus="Y", season=None, sportIds=1)`

> *Note*: Values for activeStatus: `Y`, `N`, `B` (Both)

> *Note*: Return value will be a list of teams matching the lookup_value. If no matches are found, an empty list will be returned.

## Example

Get teamId for team with code cwa

```python
team = statsapi.lookup_team('chn')
print(team[0]['id']) #assume only 1 record returned for demo purposes
```

### Output

`112`

## Example

Get info about all teams from NY

```python
for team in statsapi.lookup_team('ny'):
    print(team)
```

### Output

```
{'id': 147, 'name': 'New York Yankees', 'teamCode': 'nya', 'fileCode': 'nyy', 'teamName': 'Yankees', 'locationName': 'Bronx', 'shortName': 'NY Yankees'}
{'id': 121, 'name': 'New York Mets', 'teamCode': 'nyn', 'fileCode': 'nym', 'teamName': 'Mets', 'locationName': 'New York', 'shortName': 'NY Mets'}
```