# bgg_pull

This script supports grabbing board game information from the board game geek website (https://boardgamegeek.com/) using its (older) XML API.
The output is a csv file written to the out/ directory.

## Usage

From the command line in the src directory, use the following argument; the output of this is a dataframe, converted to csv.

	python3 bgg_pull.py -a 272000

or

	python3 bgg_pull.py --api 272000

The argument (272000) is the highest ID you want to check.  To see if that ID has been used yet, go to

https://www.boardgamegeek.com/xmlapi/boardgame/272000

It should return Item not found; if it doesn't, poke around for a bigger value.

You can continue on a partial file at any time (e.g., when the API flakes out and you need to restart the program).

## Credits

Modified from https://github.com/mrpantherson/bgg_pull by M. C. DeMarco to retrieve all games (but not rpg or video games).

Some extra functionality has been removed for clarity.

### To Do

Some columns should be added to document reimplementations and expansions.
(This data may not be complete if there is more than one parent game or implementation.)
