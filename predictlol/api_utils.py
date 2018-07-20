import requests
from pprint import pprint
import config
import numpy as np

def get_summoner_data(summoner_name, api_key, region='na1'):
    response = requests.get("https://%s.api.riotgames.com/lol/summoner/v3/summoners/by-name/%s?api_key=%s" % (region, summoner_name, api_key))
    return response.json()

def get_summoner_ids(summoner_name, api_key, region='na1'):
    summoner_data = get_summoner_data(summoner_name, api_key, region)
    return summoner_name, summoner_data['id'], summoner_data['accountId']

def get_all_match_data(account_id, api_key, region='na1'):
    # Only from the season currently
    response = requests.get("https://%s.api.riotgames.com/lol/match/v3/matchlists/by-account/%s?api_key=%s" % (region, account_id, api_key))
    return response.json()

def get_match_by_id(account_id, match_index, api_key, region='na1'):
    all_match_data = get_all_match_data(account_id, api_key, region)
    match_id = all_match_data['matches'][match_index]['gameId']

    response = requests.get("https://%s.api.riotgames.com/lol/match/v3/matches/%s?api_key=%s" % (region, match_id, api_key))
    return response.json()

def get_current_match(summoner_id, api_key, region='na1'):
    response = requests.get("https://%s.api.riotgames.com/lol/spectator/v3/active-games/by-summoner/%s?api_key=%s" % (region, summoner_id, api_key))
    return response.json(), response.status_code

def queue_name(queue_id):
    if queue_id == 470:
        queue_type = 'RANKED_FLEX_TT'
    elif queue_id == 420:
        queue_type = 'RANKED_SOLO_5x5'
    elif queue_id == 440:
        queue_type = 'RANKED_FLEX_SR'
    else:
        queue_type = 'QUEUE ID NOT ACCOUNTED FOR'
    return queue_type

def get_ranking_data(summoner_id, api_key, region='na1'):
    response = requests.get('https://%s.api.riotgames.com/lol/league/v3/positions/by-summoner/%s?api_key=%s' % (region, summoner_id, api_key))
    return response.json()

def get_league_data(summoner_id, queue_type, api_key, region='na1'):
    all_league_data = get_ranking_data(summoner_id, api_key, region)
    return [elt for elt in all_league_data if elt['queueType'] == queue_type][0]

def get_league_stats(summoner_id, queue_type, api_key, region='na1'):
    league = get_league_data(summoner_id, queue_type, api_key, region)
    return league['wins'], league['losses'], league['tier'], league['rank']

def get_winrate(summoner_id, queue_type, api_key, region='na1'):
    wins, losses = get_league_stats(summoner_id, queue_type, api_key, region)[0:2]
    return wins / (wins + losses)
