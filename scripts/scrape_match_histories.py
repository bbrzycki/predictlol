import sys
import os
import errno
import time
import traceback
import json
# from pymongo import MongoClient

import argparse
import requests
from pprint import pprint
import numpy as np

sys.path.append("../")
import predictlol as pl
import config

start = time.time()

def get_all_stats(summoner_name, account_id, api_key, region='na1', queue_id=420, start_index=0, limit=100):

    time.sleep(2)
    response = requests.get("https://%s.api.riotgames.com/lol/match/v3/matchlists/by-account/%s?queue=%s&beginIndex=%s&endIndex=%s&api_key=%s" % (region, account_id, queue_id, start_index, start_index + limit, api_key))
    matchlist = response.json()['matches']

    all_stats = []
    for index, match in enumerate(matchlist):

        time.sleep(2.5)
        match_data = pl.get_match_by_id(match['gameId'], api_key)
        try:
            for participant in match_data['participantIdentities']:
                if participant['player']['summonerName'] == summoner_name:
                    participant_id = participant['participantId']

            for key in match.keys():
                match_data[key] = match[key]

            stats = match_data['participants'][int(participant_id) - 1]
            for key in stats.keys():
                match_data[key] = stats[key]

            all_stats.append(match_data)

            now = time.time()
            delay = (now - start)
            h = int(np.floor(delay / 3600.))
            m = int(np.floor((delay - 3600. * h) / 60.))
            s = (delay - 3600. * h - 60. * m)
            print('Player %s; Game %s/%s: t = %02d:%02d:%06.3f' % (summoner_name, index+1, len(matchlist), h, m, s))
        except Exception as e:
            now = time.time()
            delay = (now - start)
            h = int(np.floor(delay / 3600.))
            m = int(np.floor((delay - 3600. * h) / 60.))
            s = (delay - 3600. * h - 60. * m)
            print('Player %s; Game %s/%s: t = %02d:%02d:%06.3f -- MATCH NOT FOUND' % (summoner_name, index+1, len(matchlist), h, m, s))
    return all_stats

def scrape(queue_id, num_games, account_id, api_key):
    try:

        d = '../data/%s/' % queue_id
        try:
            os.makedirs(d)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise

        # Set up database
        # client = MongoClient('mongodb://localhost:27017')
        # db = client['predictlol']

        # Handle delphinus6 data
        try:
            with open('../data/%s/%s.json' % (queue_id, account_id), 'r') as fn:
                ranked_games = json.load(fn)
        except Exception as e:
            # Load from all match data
            with open('../data/delphinus6.json', 'r') as fn:
                all_stats = json.load(fn)

            index = 0
            games = 0
            ranked_games = []
            while games < num_games:
                stats = all_stats[index]
                if stats['queue'] == queue_id:
                    ranked_games.append(stats)
                    games += 1
                index += 1
            with open('../data/%s/%s.json' % (queue_id, account_id), 'w') as fn:
                json.dump(ranked_games, fn)

        game_ids = [game['gameId'] for game in ranked_games]
        print(len(game_ids), len(ranked_games))

        print('Have game ids for %s...' % queue_id)
        # Get all users
        try:
            with open('../data/%s/users.json' % queue_id, 'r') as fn:
                users = json.load(fn)
            print('Player list loaded for queue %s' % queue_id)
            print('%s total unique users' % len(users))
        except Exception as e:
            # Load from all match data
            users = []
            for index, game_id in enumerate(game_ids):
                now = time.time()
                delay = (now - start)
                h = int(np.floor(delay / 3600.))
                m = int(np.floor((delay - 3600. * h) / 60.))
                s = (delay - 3600. * h - 60. * m)
                print('Game %s, %s out of %s, t = %02d:%02d:%06.3f' % (game_id, index+1, len(game_ids), h, m, s))

                time.sleep(2)
                match = pl.get_match_by_id(game_id, api_key)
                participants = match['participantIdentities']
                for i, participant in enumerate(participants):
                    username = participant['player']['summonerName']
                    try:
                        time.sleep(2)
                        user = pl.get_summoner_ids(username, api_key)
                        users.append(user)
                        print(i, user[0])
                    except Exception as e:
                        pass
            users = list(set(users))
            with open('../data/%s/users.json' % queue_id, 'w') as fn:
                json.dump(users, fn)
            print('Player list loaded for queue %s' % queue_id)
            print('%s total unique users' % len(users))

        for index, (summoner_name, summoner_id, account_id) in enumerate(users):
            print('Working on user %s; user %s out of %s' % (summoner_name, index + 1, len(users)))
            needs_data = False
            try:
                with open('../data/%s/%s.json' % (queue_id, account_id), 'r') as fn:
                    stats = json.load(fn)
                    # if len(stats) < 100:
                    #     needs_data = True
                    pass
            except Exception as e:
                needs_data = True
            if needs_data:
                try:
                    ranked_stats = get_all_stats(summoner_name, account_id, api_key, queue_id=queue_id, limit=100)
                    with open('../data/%s/%s.json' % (queue_id, account_id), 'w') as fn:
                        json.dump(ranked_stats, fn)
                    print('Finished saving %s\'s data (account number %s, queue %s)' % (summoner_name, account_id, queue_id))
                except Exception as e:
                    print('No data found for %s! (account number %s, queue %s)' % (summoner_name, account_id, queue_id))
            else:
                print('%s\'s data (account number %s, queue %s) is already saved!' % (summoner_name, account_id, queue_id))
        #     ranked_stats_collection = db[str(account_id)]
        #     for stats in ranked_stats:
        #         result = ranked_stats_collection.update(stats, stats, upsert=True)
        #     print('Finished saving %s\'s data (account number %s)' % (summoner_name, account_id))
    except Exception as e:
        error = traceback.format_exc()
        notification = 'Script stopped on user %s; user %s out of %s\n' % (summoner_name, index + 1, len(users))
        notification += 'Runtime: %02d:%02d:%06.3f\n\n' % (h, m, s)
        notifictaion += error
        pl.email('bryan6brzycki@gmail.com', '[predictlol] Match History Scraping Notification', error)
        print(error)

if __name__ == '__main__':
    api_key = config.api_key

    username = 'delphinus6'
    # account_id = '234507298'
    region = 'na1'
    # match_index = 0

    try:
        summoner_name, summoner_id, account_id = pl.get_summoner_ids(username, api_key, region)
    except Exception as e:
        error = traceback.format_exc()
        error += 'API key has likely expired!'
        # pl.email('bryan6brzycki@gmail.com', '[predictlol] Match History Scraping Notification', error)
        print(error)
    else:
        scrape(420, 120, account_id, api_key)
        scrape(470, 120, account_id, api_key)

        notification = 'Scraping has finished!'
        pl.email('bryan6brzycki@gmail.com', '[predictlol] Match History Scraping Notification', notification)
        print(notification)
