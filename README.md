# bgg_pull

This module supports grabbing board game information from the board game geek website (https://boardgamegeek.com/) using its xml api.
The output is a csv file written to the out/ directory.

You can continue on a partial file at any time.

## usage

From the command line use the following argument; the output of this is a dataframe, converted to csv.

python3 bgg_pull.py -a 50
python3 bgg_pull.py --api 50

## credits

Modified from https://github.com/mrpantherson/bgg_pull by M. C. DeMarco to retrieve all games (but not rpg or video games).
