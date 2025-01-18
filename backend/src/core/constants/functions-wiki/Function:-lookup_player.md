### Get data about players based on first, last, or full name.

`statsapi.lookup_player(lookup_value, gameType="R", season=None, sportId=1)`

## Example

Look up player id for Aaron Nola
> *Note*: if using a full last name as the lookup_value and that last name could be part of another player's lastname, e.g. `Nola` is part of `Nolan`, include a comma on the end of the last name in order to match on the `initLastName` field which looks like `Nola, A`

```python
player = statsapi.lookup_player('nola,')
print(player[0]['id']) #assume only 1 record returned for demo purposes
```

### Output

`605400`

## Example

Print full name and position for all players named Harper

```python
for player in statsapi.lookup_player('Harper'):
    print('Full name: {}, Position: {}'.format(player['fullName'], player['primaryPosition']['abbreviation']))
```

### Output

```
Full name: Bryce Harper, Position: RF
Full name: Ryne Harper, Position: P
```