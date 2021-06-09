import pandas as pd
import pytest

from src.data_cleaning import get_regular_season_average


def test_get_regular_season_average_happy():
    df_in_values = [[2003, 22, 1102, 72, 1391, 43, 'H', 0, 26, 46, 15, 28, 5, 7, 5,
                    22, 19, 9, 6, 8, 13, 15, 48, 2, 7, 11, 15, 12, 15, 5, 11, 5, 0,
                    12],
                   [2003, 25, 1102, 57, 1117, 52, 'A', 0, 16, 36, 7, 20, 18, 22, 3,
                    24, 10, 10, 5, 3, 20, 16, 43, 6, 14, 14, 21, 7, 17, 8, 8, 3, 0,
                    19]]
    df_in_index = [1, 2]
    df_in_columns = ['Season', 'DayNum', 'WTeamID', 'WScore', 'LTeamID', 'LScore', 'WLoc',
                       'NumOT', 'WFGM', 'WFGA', 'WFGM3', 'WFGA3', 'WFTM', 'WFTA', 'WOR', 'WDR',
                       'WAst', 'WTO', 'WStl', 'WBlk', 'WPF', 'LFGM', 'LFGA', 'LFGM3', 'LFGA3',
                       'LFTM', 'LFTA', 'LOR', 'LDR', 'LAst', 'LTO', 'LStl', 'LBlk', 'LPF']
    df_in = pd.DataFrame(df_in_values, index=df_in_index, columns=df_in_columns)
    df_in.to_csv('data/test_df_in_happy.csv')
    df_true = pd.DataFrame([[2003, 1102, 64.5, 21, 41, 11, 24, 11.5, 14.5, 4, 23, 14.5, 9.5, 5.5, 5.5, 16.5, 2, 21/41, 11/24, 11.5/14.5],
                            [2003, 1117, 52.0, 16.0, 43.0, 6.0, 14.0, 14.0, 21.0, 7.0, 17.0, 8.0, 8.0, 3.0, 0.0, 19.0, 1, 16/43, 6/14, 14/21],
                             [2003, 1391, 43.0, 15.0, 48.0, 2.0, 7.0, 11.0, 15.0, 12.0, 15.0, 5.0, 11.0, 5.0, 0.0, 12.0, 1, 15/48, 2/7, 11/15]],
                            index=[0,1,2],
                            columns=['Season', 'Team', 'Score', 'FGM', 'FGA', 'FGM3', 'FGA3', 'FTM', 'FTA', 'OR', 'DR', 'Ast', 'TO', 'Stl', 'Blk', 'PF', 'GP', 'FGP', 'FG3P', 'FTP']
                            )
    df_test = get_regular_season_average('data/test_df_in_happy.csv', 'data/test_output_happy.csv')
    assert df_test.equals(df_true)

def test_get_regular_season_average_unhappy():
    with pytest.raises(TypeError):
        df_test = get_regular_season_average(1, 2)