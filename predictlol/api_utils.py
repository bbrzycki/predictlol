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

def get_match_by_id(match_id, api_key, region='na1'):
    response = requests.get("https://%s.api.riotgames.com/lol/match/v3/matches/%s?api_key=%s" % (region, match_id, api_key))
    return response.json()

def get_match_by_index(account_id, match_index, api_key, region='na1'):
    all_match_data = get_all_match_data(account_id, api_key, region)
    match_id = all_match_data['matches'][match_index]['gameId']
    return get_match_by_id(match_id, api_key, region)

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
    try:
        league_data = [elt for elt in all_league_data if elt['queueType'] == queue_type][0]
    except IndexError:
        league_data = None
    return league_data

def get_league_stats(summoner_id, queue_type, api_key, region='na1'):
    league = get_league_data(summoner_id, queue_type, api_key, region)
    if league is None:
        raise Exception('No ranked data available!')
    return league['wins'], league['losses'], league['tier'], league['rank'], league['hotStreak']

def get_winrate(summoner_id, queue_type, api_key, region='na1'):
    try:
        wins, losses = get_league_stats(summoner_id, queue_type, api_key, region)[0:2]
        return wins / (wins + losses)
    except Exception as e:
        return None

def get_match_result(match_data):
    return match_data['teams'][0]['win'] == 'Win'

def get_match_winrates(match_data, live, api_key, region='na1'):
    # Takes match_data as json

    if live:
        participants = match_data['participants']
        queue_id = match_data['gameQueueConfigId']
    else:
        participants = match_data['participantIdentities']
        queue_id = match_data['queueId']

    num_players = len(participants)/2
    queue_type = queue_name(queue_id)

    team1 = []
    team2 = []

    for i, participant in enumerate(participants):

        if live:
            summoner_name = participant['summonerName']
            summoner_id = participant['summonerId']
        else:
            summoner_name = participant['player']['summonerName']
            summoner_id = participant['player']['summonerId']

        # Get league stats *for the same queue type*
        try:
            wins, losses, tier, rank, streak = get_league_stats(summoner_id, queue_type, api_key, region)
            winrate = wins / (wins + losses)

            summoner_info = {'summoner_name': summoner_name,
                             'summoner_id': summoner_id,
                             'wins': wins,
                             'losses': losses,
                             'winrate': winrate,
                             'tier': tier,
                             'rank': rank,
                             'streak': streak}

            # if match_data['teams'][0]['teamId'] == match_data['participants'][i]['teamId']:
            if i < num_players:
                team1.append(summoner_info)
            else:
                team2.append(summoner_info)
        except Exception:
            # If summoner has no queue data, ignore them for now
            # summoner_info = {'summoner_name': summoner_name,
            #                  'summoner_id': summoner_id,
            #                  'wins': wins,
            #                  'losses': losses,
            #                  'winrate': winrate,
            #                  'tier': tier,
            #                  'rank': rank}
            pass
    return {'team1': team1, 'team2': team2, 'queue_type': queue_type}
