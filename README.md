# bgg_pull

This python script grabs information from the BoardGameGeek website (https://boardgamegeek.com/), mostly using their (old) XML API.
The output is a csv file.  Games by rank is not available from the public API, so the script scrapes the game ranks from a search,
then uses the xml api to get more details on each game.

Some columns have been added to document reimplementations and expansions.
(This data will not be complete if there is more than one parent game or implementation.)

A separate process has been added to retrieve fan counts.

1. Call ScrapeRanks, which takes a while (~10 min) and gets the urls and rank of the top 5000 games by scraping
2. Call GetFromApi, which also takes a while (~10 min) and gets most game info through XML API calls
3. Optionally, call GetFans, which adds fans to the file, takes even longer (~3 hrs) and gets fan counts through undocumented API calls

## Usage

- -s or --scrape to get the names and id of the top 5K games
- -a or --api to get information about the top 5K games (with an argument of 50)
- -f or --fans to get fan counts for the top 5K games (with an argument of 51)

### Example

Using pip3, install any missing requirements.  (You'll see them when you try to run.)

From the command line in the src directory type:

	python3 bgg_pull.py -s
	python3 bgg_pull.py -a 50
	python3 bgg_pull.py -f 51

The third call is optional.  Your `python3` may be called `python` instead.

## Issues

Some game names are saved without quotes but with octothorpes (#) in their names (mostly Advanced Squad Leader);
you may need to quote the names manually to load the data into, say, R.

Some columns may end up as unexpected floats, especially during retrieval but possibly after you're done as well.

## Credits

Modified from https://github.com/mrpantherson/bgg_pull by M. C. DeMarco to retrieve fan counts, expansion/reimplementation status,
and to fix a bug or two.
