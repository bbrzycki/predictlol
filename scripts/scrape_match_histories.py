import sys
import os

import argparse
import requests
from pprint import pprint
import numpy as np

sys.path.append("../")
import predictlol as pl
import config

import json
# from pymongo import MongoClient
import time
import os, sys, errno

start = time.time()

def get_all_stats(summoner_name, account_id, api_key, region='na1', queue=420, limit=100):
    matchlist = []
    start_index = 0

    response = requests.get("https://%s.api.riotgames.com/lol/match/v3/matchlists/by-account/%s?queue=%s&beginIndex=%s&endIndex=%s&api_key=%s" % (region, account_id, queue, start_index, start_index + limit, api_key))
    matchlist_packet = response.json()

    all_stats = []
    for match in matchlist:
        time.sleep(2)
        match_data = pl.get_match_by_id(match['gameId'], api_key)
        for participant in match_data['participantIdentities']:
            if participant['player']['summonerName'] == summoner_name:
                participant_id = participant['participantId']

        stats = match_data['participants'][int(participant_id) - 1]['stats']
        for key in match.keys():
            stats[key] = match[key]
        all_stats.append(stats)

        now = time.time()
        delay = (now - start)
        h = int(np.floor(delay / 3600.))
        m = int(np.floor((delay - 3600. * h) / 60.))
        s = (delay - 3600. * h - 60. * m)
        print('Player %s; Game %s: t = %02d:%02d:%2.3f' % (summoner_name, total, h, m, s))
    return all_stats

if __name__ == '__main__':

    api_key = config.api_key

    username = 'delphinus6'
    # account_id = '234507298'
    region = 'na1'
    # match_index = 0

    summoner_name, summoner_id, account_id = pl.get_summoner_ids(username, api_key, region)

    d = '../data/420/'
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
        with open('../data/420/%s.json' % account_id, 'r') as fn:
            ranked_solos = json.load(fn)
    except Exception as e:
        # Load from all match data
        with open('../data/delphinus6.json', 'r') as fn:
            all_stats = json.load(fn)

        games = 0
        ranked_solos = []
        while games < 100:
            for stats in all_stats:
                if stats['queue'] == 420:
                    ranked_solos.append(stats)
                    games += 1
        with open('../data/420/%s.json' % account_id, 'w') as fn:
            json.dump(ranked_solos, fn)

    game_ids = [game['gameId'] for game in ranked_solos]

    # Get all users
    users = []
    for game_id in game_ids:
        time.sleep(2)
        match = pl.get_match_by_id(game_id, api_key)
        for i, participant in enumerate(participants):
            username = participant['player']['summonerName']
            user = pl.get_summoner_ids(username, api_key)
            users.append(user)
    users = list(set(users))
    print('%s total users' % len(users))

    for summoner_name, summoner_id, account_id in users:
        needs_data = False
        try:
            with open('../data/420/%s.json' % account_id, 'r') as fn:
                stats = json.load(fn)
                if len(stats) < 100:
                    needs_data = True
        except Exception as e:
            needs_data = True
        if needs_data:
            ranked_stats = get_all_stats(summoner_name, account_id, api_key, queue='420', limit=100)
            with open('../data/420/%s.json' % account_id, 'w') as fn:
                json.dump(ranked_stats, fn)
            print('Finished saving %s\'s data (account number %s)' % (summoner_name, account_id))
        else:
            print('%s\'s data (account number %s) is already saved!' % (summoner_name, account_id))
    #     ranked_stats_collection = db[str(account_id)]
    #     for stats in ranked_stats:
    #         result = ranked_stats_collection.update(stats, stats, upsert=True)
    #     print('Finished saving %s\'s data (account number %s)' % (summoner_name, account_id))
