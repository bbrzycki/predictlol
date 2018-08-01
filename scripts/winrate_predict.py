import sys
import os

import argparse
import numpy as np

sys.path.append("../")
import predictlol as pl
import config

def main(username, region='na1', match_index=0, live=False):

    api_key = config.api_key

    try:
        summoner_name, summoner_id, account_id = pl.get_summoner_ids(username, api_key, region)
    except KeyError:
        print('ERROR: Invalid request. Make sure username, region, and api_key are correct!')
        return 1

    if live:
        match_data, status_code = pl.get_current_match(summoner_id, api_key, region)
        if status_code == 404:
            raise Exception('Summoner not currently in game!')
    else:
        match_data = pl.get_match_by_index(account_id, match_index, api_key, region)

    match_winrates = pl.get_match_winrates(match_data, live, api_key, region)

    queue_type = match_winrates['queue_type']
    print()
    print('Queue type: %s' % queue_type)
    print('------------%s' % ('-' * len(queue_type)))
    print()
    # print('----')

    print('{0:8}  {1:<16}  {2:^9}  {3:8}  {4:<12}  {5:5}'.format('', 'Username', 'Record', 'Winrate', 'Rank', 'Streak'))
    print('{0:8}  {1:<16}  {2:^9}  {3:8}  {4:<12}  {5:5}'.format('', '--------', '------', '-------', '----', '------'))
    # print('Team 1')
    # print('------')
    for i, player in enumerate(match_winrates['team1']):
        if i == 0:
            first_col = 'Team 1'
        else:
            first_col = ''

        if player['streak']:
            streak_string = '(X)'
        else:
            streak_string = ''

        print('{0:8}  {1:<16}  {2:>4}/{3:<4}  {4:8}  {5:<12}  {6:^5}'.format(first_col,
            player['summoner_name'],
            '%s' % player['wins'],
            '%s' % (player['wins'] + player['losses']),
            '(%.02f%%)' % (player['winrate'] * 100),
            '%s %s' % (player['tier'], player['rank']),
            '%s' % streak_string))

    print()
    # print('Team 2')
    # print('------')
    for i, player in enumerate(match_winrates['team2']):
        if i == 0:
            first_col = 'Team 2'
        else:
            first_col = ''

        if player['streak']:
            streak_string = '(X)'
        else:
            streak_string = ''

        print('{0:8}  {1:<16}  {2:>4}/{3:<4}  {4:8}  {5:<12}  {6:^5}'.format(first_col,
            player['summoner_name'],
            '%s' % player['wins'],
            '%s' % (player['wins'] + player['losses']),
            '(%.02f%%)' % (player['winrate'] * 100),
            '%s %s' % (player['tier'], player['rank']),
            '%s' % streak_string))

    # print('----')
    print()
    print('Predictions (Team 1 vs Team 2):')
    print()
    print('    {0:<40}  {1:6}  {2:6}'.format('Statistic', 'Team 1', 'Team 2'))
    print('    {0:<40}  {1:6}  {2:6}'.format('---------', '------', '------'))


    team1_mean, team2_mean = pl.mean_winrates(match_winrates)
    print('    {0:<40}  {1:6}  {2:6}'.format('Mean winrates',
                                          '%.02f%%' % (team1_mean*100),
                                          '%.02f%%' % (team2_mean*100)))


    predict1, predict2 = pl.mean_predictions(match_winrates)
    print('    {0:<40}  {1:6}  {2:6}'.format('Win likelihood from means',
                                          '%.02f%%' % (predict1*100),
                                          '%.02f%%' % (predict2*100)))

    predict1, predict2 = pl.mean_ratio_predictions(match_winrates, team='team1')
    print('    {0:<40}  {1:6}  {2:6}'.format('Win likelihood from ratio means (Team 1)',
                                          '%.02f%%' % (predict1*100),
                                          '%.02f%%' % (predict2*100)))
    predict1, predict2 = pl.mean_ratio_predictions(match_winrates, team='team2')
    print('    {0:<40}  {1:6}  {2:6}'.format('Win likelihood from ratio means (Team 2)',
                                          '%.02f%%' % (predict1*100),
                                          '%.02f%%' % (predict2*100)))

    # map_diff = 0.026
    # print('    After map side difference (%.02f%%): %.02f%% vs %.02f%%' % (map_diff, max_lh_1 * (1 - map_diff), max_lh_2 * (1 + map_diff)))

    carry1, carry2 = pl.carry_potential(match_winrates, team='team1')
    print('    {0:<40}  {1:^6}  {2:^6}'.format('Solo carry likelihood',
                                          '%.02f' % (carry1),
                                          '%.02f' % (carry2)))

    if not live:
        team1_win = pl.get_match_result(match_data)
        if team1_win:
            winner = 'Team 1'
        else:
            winner = 'Team 2'
        print()
        print('Actual result: %s won!' % winner)
    print('')
    return 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate League of Legends winrate statistics')
    parser.add_argument('username', help='League of Legends username')
    parser.add_argument('-r', '--region', default='na1',
                        help='League of Legends server name (e.g. na1)')
    parser.add_argument('-m', '--match-index', type=int, default=0,
        help='Match index starting from latest match')
    parser.add_argument('-l', '--live', action='store_true',
        help='Option to predict live game')

    args = parser.parse_args()

    sys.exit(main(args.username, region=args.region.lower(),
        match_index=args.match_index, live=args.live))
