import logging
import warnings

import pandas as pd

logger = logging.getLogger(__name__)


def get_teams(file_path, output_path):
    """Get the teams dataframe
        Args:
            file_path(str): file path of input csv
            output_path(str): file path for the output csv
        Returns:
            teams(pd.Dataframe): teams dataframe
    """
    if type(file_path) != str:
        logger.error('Invalid input value')
        raise TypeError('The file path you entered is invalid')
    if type(output_path) != str:
        logger.error('Invalid input value')
        raise TypeError('The file path you entered is invalid')
    teams = pd.read_csv(file_path)
    teams = teams[['TeamID', 'TeamName']]
    teams.to_csv(output_path)
    logger.info('Got teams dataframe')
    return teams


def get_regular_season_average(file_path, output_path):
    """Get the regular season average dataframe
        Args:
            file_path(str): file path of input csv
            output_path(str): file path for the output csv
        Returns:
            regular_avg(pd.Dataframe): regular season average dataframe
    """
    if type(file_path) != str:
        logger.error('Invalid input value')
        raise TypeError('The file path you entered is invalid')
    if type(output_path) != str:
        logger.error('Invalid input value')
        raise TypeError('The file path you entered is invalid')
    regular_games = pd.read_csv(file_path)
    regular_wins = regular_games[['Season', 'WTeamID','WScore', 'WFGM', 'WFGA', 'WFGM3', 'WFGA3', 'WFTM', 'WFTA', 'WOR', 'WDR', 'WAst', 'WTO', 'WStl', 'WBlk', 'WPF']]
    regular_wins.columns = ['Season', 'Team', 'Score', 'FGM', 'FGA', 'FGM3', 'FGA3', 'FTM', 'FTA', 'OR', 'DR', 'Ast', 'TO', 'Stl', 'Blk', 'PF']
    regular_losses = regular_games[['Season', 'LTeamID', 'LScore', 'LFGM', 'LFGA', 'LFGM3', 'LFGA3', 'LFTM', 'LFTA', 'LOR', 'LDR', 'LAst', 'LTO', 'LStl', 'LBlk', 'LPF']]
    regular_losses.columns = ['Season', 'Team', 'Score', 'FGM', 'FGA', 'FGM3', 'FGA3', 'FTM', 'FTA', 'OR', 'DR', 'Ast', 'TO', 'Stl', 'Blk', 'PF']
    regular = pd.concat([regular_wins, regular_losses])
    regular['GP'] = 1
    regular_agg = regular.groupby(['Season', 'Team']).sum()
    regular_agg['FGP'] = regular_agg['FGM'] / regular_agg['FGA']
    regular_agg['FG3P'] = regular_agg['FGM3'] / regular_agg['FGA3']
    regular_agg['FTP'] = regular_agg['FTM'] / regular_agg['FTA']
    regular_avg = regular_agg
    regular_avg[['Score', 'FGM', 'FGA', 'FGM3', 'FGA3', 'FTM', 'FTA', 'OR', 'DR', 'Ast', 'TO', 'Stl', 'Blk', 'PF']] = regular_avg[['Score', 'FGM', 'FGA', 'FGM3', 'FGA3', 'FTM', 'FTA', 'OR', 'DR', 'Ast', 'TO', 'Stl', 'Blk', 'PF']].div(regular_avg['GP'].values,axis=0)
    regular_avg = regular_avg.reset_index()
    regular_avg.to_csv(output_path)
    logger.info('Got regular season average dataframe')
    return regular_avg


def get_seed(seed):
    """Extract the integer type tourney seed from a string of seed information
        Args:
            seed(str): untransformed seed information
        Returns:
            int(result)(int): seed number
    """
    result = seed[1:]
    if result.endswith('a') or result.endswith('b'):
        result = result[:-1]
    return int(result)


def get_tourney_seeds(file_path, output_path):
    """Get the tourney seeds dataframe
        Args:
            file_path(str): file path of input csv
            output_path(str): file path for the output csv
        Returns:
            seeds(pd.Dataframe): tourney seeds dataframe
    """
    if type(file_path) != str:
        logger.error('Invalid input value')
        raise TypeError('The file path you entered is invalid')
    if type(output_path) != str:
        logger.error('Invalid input value')
        raise TypeError('The file path you entered is invalid')
    seeds = pd.read_csv(file_path)
    seeds['Seed'] = seeds['Seed'].apply(get_seed)
    seeds.to_csv(output_path)
    logger.info('Got tourney seeds dataframe')
    return seeds


def get_tourney_result(file_path, output_path):
    """Get the tourney result dataframe
        Args:
            file_path(str): file path of input csv
            output_path(str): file path for the output csv
        Returns:
            tourney_result(pd.Dataframe): tourney result dataframe
    """
    if type(file_path) != str:
        logger.error('Invalid input value')
        raise TypeError('The file path you entered is invalid')
    if type(output_path) != str:
        logger.error('Invalid input value')
        raise TypeError('The file path you entered is invalid')
    tourney = pd.read_csv(file_path)
    tourney_result = tourney[['Season', 'WTeamID', 'LTeamID']]
    tourney_result.to_csv(output_path)
    logger.info('Got tourney result dataframe')
    return tourney_result


def get_tourney_delta(regular_avg, tourney_result, seeds, output_path):
    """Get dataframe of the difference of a tourney match's two teams' regular season average stats
        Args:
            regular_avg(pd.Dataframe): regular season average dataframe
            tourney_result(pd.Dataframe): tourney result dataframe
            seeds(pd.Dataframe): tourney seeds dataframe
            output_path(str): file path for the output csv
        Returns:
            tourney_delta(pd.Dataframe): dataframe of the difference of a tourney match's two teams' regular season average stats
    """
    warnings.filterwarnings("ignore")
    tourney_join_win = pd.merge(left=tourney_result, right=regular_avg, left_on=['Season', 'WTeamID'],
                                right_on=['Season', 'Team'])
    tourney_join_win = pd.merge(left=tourney_join_win, right=seeds, left_on=['Season', 'WTeamID'],
                                right_on=['Season', 'TeamID'])
    tourney_join_win = tourney_join_win.rename(columns={'Seed': 'WSeed'})
    tourney_join_win = tourney_join_win.drop(['Team', 'GP', 'TeamID'], axis=1)
    tourney_join_win = pd.merge(left=tourney_join_win, right=seeds, left_on=['Season', 'LTeamID'],
                                right_on=['Season', 'TeamID'])
    tourney_join_win = tourney_join_win.drop(['TeamID'], axis=1)
    tourney_join_win = tourney_join_win.rename(columns={'Seed': 'LSeed'})
    tourney_join_win.columns = ['Season', 'WTeamID', 'LTeamID', 'WScore', 'WFGM', 'WFGA', 'WFGM3', 'WFGA3', 'WFTM',
                                'WFTA', 'WOR', 'WDR', 'WAst', 'WTO', 'WStl', 'WBlk', 'WPF', 'WFGP', 'WFG3P', 'WFTP',
                                'WSeed', 'LSeed']
    tourney_join_win_loss = pd.merge(left=tourney_join_win, right=regular_avg, left_on=['Season', 'LTeamID'],
                                     right_on=['Season', 'Team'])
    tourney_join_win_loss = tourney_join_win_loss.drop(['Team', 'GP'], axis=1)
    tourney_join_win_loss.columns = ['Season', 'WTeamID', 'LTeamID', 'WScore', 'WFGM', 'WFGA', 'WFGM3', 'WFGA3', 'WFTM',
                                     'WFTA', 'WOR', 'WDR', 'WAst', 'WTO', 'WStl', 'WBlk', 'WPF', 'WFGP', 'WFG3P',
                                     'WFTP', 'WSeed', 'LSeed', 'LScore', 'LFGM', 'LFGA', 'LFGM3', 'LFGA3', 'LFTM',
                                     'LFTA', 'LOR', 'LDR', 'LAst', 'LTO', 'LStl', 'LBlk', 'LPF', 'LFGP', 'LFG3P',
                                     'LFTP']
    tourney_delta_wins = tourney_join_win_loss[['Season']]
    tourney_delta_wins['Score'] = tourney_join_win_loss['WScore'] - tourney_join_win_loss['LScore']
    tourney_delta_wins['FGM'] = tourney_join_win_loss['WFGM'] - tourney_join_win_loss['LFGM']
    tourney_delta_wins['FGA'] = tourney_join_win_loss['WFGA'] - tourney_join_win_loss['LFGA']
    tourney_delta_wins['FGM3'] = tourney_join_win_loss['WFGM3'] - tourney_join_win_loss['LFGM3']
    tourney_delta_wins['FGA3'] = tourney_join_win_loss['WFGA3'] - tourney_join_win_loss['LFGA3']
    tourney_delta_wins['FTM'] = tourney_join_win_loss['WFTM'] - tourney_join_win_loss['LFTM']
    tourney_delta_wins['FTA'] = tourney_join_win_loss['WFTA'] - tourney_join_win_loss['LFTA']
    tourney_delta_wins['OR'] = tourney_join_win_loss['WOR'] - tourney_join_win_loss['LOR']
    tourney_delta_wins['DR'] = tourney_join_win_loss['WDR'] - tourney_join_win_loss['LDR']
    tourney_delta_wins['Ast'] = tourney_join_win_loss['WAst'] - tourney_join_win_loss['LAst']
    tourney_delta_wins['TO'] = tourney_join_win_loss['WTO'] - tourney_join_win_loss['LTO']
    tourney_delta_wins['Stl'] = tourney_join_win_loss['WStl'] - tourney_join_win_loss['LStl']
    tourney_delta_wins['Blk'] = tourney_join_win_loss['WBlk'] - tourney_join_win_loss['LBlk']
    tourney_delta_wins['PF'] = tourney_join_win_loss['WPF'] - tourney_join_win_loss['LPF']
    tourney_delta_wins['FGP'] = tourney_join_win_loss['WFGP'] - tourney_join_win_loss['LFGP']
    tourney_delta_wins['FG3P'] = tourney_join_win_loss['WFG3P'] - tourney_join_win_loss['LFG3P']
    tourney_delta_wins['FTP'] = tourney_join_win_loss['WFTP'] - tourney_join_win_loss['LFTP']
    tourney_delta_wins['Seed'] = tourney_join_win_loss['WSeed'] - tourney_join_win_loss['LSeed']
    tourney_delta_wins['Win'] = 1
    tourney_delta_losses = tourney_delta_wins.copy()
    tourney_delta_losses.iloc[:, 1:-1] = tourney_delta_losses.iloc[:, 1:-1] * -1
    tourney_delta_losses['Win'] = 0
    tourney_delta = pd.concat([tourney_delta_wins, tourney_delta_losses])
    tourney_delta = tourney_delta.drop('Season', axis=1)
    tourney_delta.to_csv(output_path)
    logger.info('Got tourney delta dataframe')
    return tourney_delta