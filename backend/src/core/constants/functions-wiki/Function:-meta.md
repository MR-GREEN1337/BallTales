Get available values from StatsAPI for use in other queries, or look up descriptions for values found in API results.

`statsapi.meta(type, fields=None)`

Limit the fields returned by providing a comma-separated list in the `fields` parameter. Get the field names from the un-limited response for the same `type`.

## Example

To get a list of leader categories to use when calling the [team_leaders function](https://github.com/toddrob99/MLB-StatsAPI/wiki/Function:-team_leaders):

`statsapi.meta('leagueLeaderTypes')`

## Known `type`s
* `awards`
* `baseballStats`
* `eventTypes`
* `gameStatus`
* `gameTypes`
* `hitTrajectories`
* `jobTypes`
* `languages`
* `leagueLeaderTypes`
* `logicalEvents`
* `metrics`
* `pitchCodes`
* `pitchTypes`
* `platforms`
* `positions`
* `reviewReasons`
* `rosterTypes`
* `scheduleEventTypes`
* `situationCodes`
* `sky`
* `standingsTypes`
* `statGroups`
* `statTypes`
* `windDirection`
