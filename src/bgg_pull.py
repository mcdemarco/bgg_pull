import requests
import bs4
import pandas
import time
import numpy as np
from xml.etree import ElementTree
import argparse
import errno
import sys
from io import BytesIO
from PIL import Image
import requests
import os
import logging
import json


'''
This module supports grabbing information from the board game geek website (https://boardgamegeek.com/),
output is a csv file.

- Unscrape to initialize for downloading all games.  It takes an argument of the current number of games, which you can see in the Browse menu at BGG.  To test your setup use a much smaller number.
- call GetFromApi, this should also take a while (~10 min) and gets the remaining information through API calls
'''


# for whatever reason this game has no rank and is missing data, could add code to delete, or whack manually
# https://boardgamegeek.com/boardgame/57161/showdown

# for easy lookup later we can pair the xml tags with the respective dataframe columns
tag_col_lookup = [('name', 'names'),
                 ('minplayers', 'min_players'),
                 ('maxplayers', 'max_players'),
                 ('playingtime', 'avg_time'),
                 ('minplaytime', 'min_time'),
                 ('maxplaytime', 'max_time'),
                 ('yearpublished', 'year'),
                 ('statistics/ratings/average', 'avg_rating'),
                 ('statistics/ratings/bayesaverage', 'geek_rating'),
                 ('statistics/ratings/usersrated', 'num_votes'),
                 ('statistics/ratings/ranks/rank', 'rank'),
                 ('image', 'image_url'),
                 ('thumbnail', 'thumb_url'),
                 ('age', 'age'),
                 ('boardgamemechanic', 'mechanic'),
                 ('statistics/ratings/owned', 'owned'),
                 ('boardgamecategory', 'category'),
                 ('boardgamedesigner', 'designer'),
                 ('boardgamepublisher', 'publisher'),
                 ('statistics/ratings/averageweight', 'weight')]

full_col_list = ['game_id','bgg_url']
for tag, col in tag_col_lookup:
    full_col_list.append(col)

current = 1

def GetFromApi(max=271300, loops=100, tags_cols=tag_col_lookup):
    '''
    :param max: the maximum index to try and grab; at time of writing was around 271280 (actual board game count 104599); lower it to test
    :param loops: how many games to try and grab at once: 100 is a good number
    :param tags_cols: 
    :param name_in: 
    :param name_out: 
    '''

    global current
    path = os.path.join(args.out_path, args.out_name)
    df = pandas.DataFrame([], columns = full_col_list)
    if os.path.isfile(path):
        # search through df for max game id and start from there.
        df = pandas.read_csv(path, encoding='utf8', float_precision='high')
        if int(df.iloc[-1,0]) >= current:
            current = int(df.iloc[-1,0]) + 1
 
    ids_todo = []
    for index in range(current,current + loops):
        if len(ids_todo) >= loops:
            break
        if index <= max:
            ids_todo.append(str(index))

    current = current + loops

    url = 'https://www.boardgamegeek.com/xmlapi/boardgame/{}?&stats=1&marketplace=1'.format(','.join(ids_todo))
    args.logger.info(f'Grabbing info from {url}')
    response = requests.get(url)
    if response.status_code != 200:
        args.logger.error(f'Problem grabbing from API:  {response.status_code}')
        sys.exit(1)

    # these tags will return multiple results, will need to be handled slightly differently
    multi_tags = ['mechanic', 'category', 'designer']
    tree = ElementTree.fromstring(response.content)
    for game in tree:
        if 'objectid' in game.attrib and not 'subtypemismatch' in game.attrib:
            id = game.attrib['objectid']
            df_dict = {'game_id':id, 'bgg_url':"https://boardgamegeek.com/boardgame/" + str(id)}
            for tag, var in tags_cols:
                # special case for grabbing english name
                if var == 'names':
                    for sub in game.findall(tag):
                        if 'primary' in sub.attrib: #grab the english name
                            df_dict[var] = sub.text if sub != None else 'none'
                            break
                # special case for grabbing rank (when not scraping)
                elif var == 'rank':
                    for sub in game.findall(tag):
                        if 'id' in sub.attrib and sub.attrib["id"] == '1': #grab the rank
                            df_dict[var] = sub.attrib["value"] if sub != None and sub.attrib["value"] != 'Not Ranked' else 'none'
                            break
                # multi tag items need to be handled slightly different
                elif var in multi_tags:
                    multi = []
                    for sub in game.findall(tag):
                        multi.append(sub.text if sub != None else 'none')
                        df_dict[var] = ', '.join(multi) if len(multi) else 'none'
                # all normal nodes handled here
                else:
                    node = game.find(tag)
                    df_dict[var] = node.text if node != None else 'none'

            df = df.append(df_dict, ignore_index = True)

        else:
            # check for a game not found error (vs. some other error)
            for sub in game.findall('error'):
                args.logger.info(sub)
                if 'message' in sub.attrib:
                    args.logger.info( sub.attrib["message"] )
                else:
                    args.logger.info('The server returned an error.')
                    
    # save results out
    args.logger.info('Saving...')
    path = os.path.join(args.out_path, args.out_name)
    df.to_csv(path, index=False)



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Collects information for games on BGG')
    parser.add_argument('-a', '--api', dest='api_grabs', type=int, default=50, help='how many groups of 100 to grab, keep doing this until db full')
    args = parser.parse_args()

    # add extra useful stuff
    args.cfgpath = "../config.json"
    with open(args.cfgpath, 'r') as file:
        args.config = json.load(file)
    args.thumb_w = args.config['thumb_w']
    args.thumb_h = args.config['thumb_h']
    args.n_rows = args.config['n_rows']
    args.n_cols = args.config['n_cols']
    args.n_total = args.n_rows * args.n_cols
    args.out_width = args.n_cols * args.thumb_w
    args.out_height = args.n_rows * args.thumb_h
    args.out_name = args.config['out_name']
    args.log_path = args.config['log_path']
    args.out_path = args.config['out_path']

    # critical - error - warning - info - debug
    args.logger = logging.getLogger(__name__)
    args.logger.setLevel(logging.DEBUG)
    # file handler
    path = os.path.join(args.log_path, 'log.txt')
    fh = logging.FileHandler(path, mode='a')
    fh.setLevel(logging.INFO)
    args.logger.addHandler(fh)
    # console handler
    sh = logging.StreamHandler()
    sh.setLevel(logging.INFO)
    args.logger.addHandler(sh)

    # log run commands 
    sep = '-' * 80
    arg_str = ' '.join(sys.argv)
    args.logger.info(f'{sep}\npython {arg_str}\n')

    # validate input
    if not 0 <= args.api_grabs <= 500:
        args.logger.error('invalid value for api_grabs [0, 50]')
        sys.exit(1)
    
    for i in range(args.api_grabs):
        args.logger.info(f'Api grab {i}')
        GetFromApi()
        time.sleep(5)

