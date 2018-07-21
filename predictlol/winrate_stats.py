import numpy as np

def total_wins(match_winrates):
    # Accepts dictionary of match winrates
    team1_sum = 0
    team2_sum = 0
    for player in match_winrates['team1']:
        team1_sum += player['wins']
    for player in match_winrates['team2']:
        team2_sum += player['wins']
    return team1_sum, team2_sum

def total_games(match_winrates):
    # Accepts dictionary of match winrates
    team1_sum = 0
    team2_sum = 0
    for player in match_winrates['team1']:
        team1_sum += player['wins'] + player['losses']
    for player in match_winrates['team2']:
        team2_sum += player['wins'] + player['losses']
    return team1_sum, team2_sum

def get_winrates(match_winrates):
    # Accepts dictionary of match winrates
    team1 = []
    team2 = []
    for player in match_winrates['team1']:
        team1.append(player['winrate'])
    for player in match_winrates['team2']:
        team2.append(player['winrate'])
    return np.array(team1), np.array(team2)

def mean_winrates(match_winrates):
    # Accepts dictionary of match winrates
    team1, team2 = get_winrates(match_winrates)
    return np.mean(team1), np.mean(team2)

def mean_predictions(match_winrates):
    team1_mean, team2_mean = mean_winrates(match_winrates)
    ratio = team1_mean / team2_mean
    return ratio / (1 + ratio), 1 / (1 + ratio)

def all_ratios(match_winrates, team='team1'):
    team1, team2 = get_winrates(match_winrates)
    ratios = []
    for x in team1:
        for y in team2:
            if team == 'team1':
                ratios.append(x/y)
            elif team == 'team2':
                ratios.append(y/x)
            else:
                raise Exception('Invalid team name.')
    return np.array(ratios)

def mean_ratio_predictions(match_winrates, team='team1'):
    ratio = np.mean(all_ratios(match_winrates, team))
    if team == 'team1':
        return ratio / (1 + ratio), 1 / (1 + ratio)
    elif team == 'team2':
        return 1 / (1 + ratio), ratio / (1 + ratio)
    else:
        raise Exception('Invalid team name.')


def carry_potential(match_winrates, team='team1'):
    ratios = all_ratios(match_winrates, team)
    team_carry = np.max(ratios)
    other_carry = 1 / np.min(ratios)
    min_carry = min(team_carry, other_carry)
    if team == 'team1':
        return team_carry / min_carry, other_carry / min_carry
    elif team == 'team2':
        return other_carry / min_carry, team_carry / min_carry
    else:
        raise Exception('Invalid team name.')
