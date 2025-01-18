Call MLB StatsAPI and return JSON data.

This function is for advanced querying of the MLB StatsAPI, and is used by the functions in this library.

`statsapi.get(endpoint, params, force=False)`

`endpoint` is one of the keys in the [ENDPOINT dict](https://github.com/toddrob99/MLB-StatsAPI/wiki/Endpoints).

`params` is a dict of parameters, as defined in the `ENDPOINT` dict for each endpoint. Defaults to empty dict (`{}`) as of v1.8.

`force=True` will force unrecognized parameters into the query string, and ignore parameter requirements. 
> *Note*: results from Stats API may not be as expected when forcing.

## Example
`statsapi.get('team', {'teamId':143})` will call the team endpoint for teamId=143 (Phillies)

Return value will be the raw response from MLB Stats API in json format.