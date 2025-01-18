### Get data about the latest season for a given sportId. (Added in v1.5)

`statsapi.latest_season(sportId=1)`

## Example

Get the latest season for MLB, sportId=1 (default)

```python
season_data = statsapi.latest_season()
print(season_data['seasonId'])
```

### Output

`2022`
