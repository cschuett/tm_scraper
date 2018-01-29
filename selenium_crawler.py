from selenium import webdriver
import pandas as pd
import numpy as np
import re
import time
import random


YEAR_START = 2000
YEAR_STOP = 2017

bundesliga = ['Deutschland_1_Bundesliga', '1-bundesliga', 'L1']



# Start selenium with the configured binary
# additional help for setting up firefox as headless browser:
# https://stackoverflow.com/questions/40208051/selenium-using-python-geckodriver-executable-needs-to-be-in-path
driver = webdriver.Firefox()
random.seed()

df = pd.DataFrame(columns=['WD', 'Date', 'Time', 'Saison', 'MatchDay', 'HomeTeamRank', 'HomeTeam', 'Result', 'AwayTeam', 'AwayTeamRank'])

def get_ordered_unique(temp_list):
    uni_temp, ind = np.unique(temp_list, return_index=True)
    uni_list = uni_temp[np.argsort(ind)]
    return uni_list

def scrape_matches(liga):
    for year in range(YEAR_START, YEAR_STOP):
        driver.get("https://www.transfermarkt.de/{}/gesamtspielplan/wettbewerb/{}/saison_id/{}".format(liga[1], liga[2], str(year)))

        df_teams = pd.DataFrame()

        home_teams = driver.find_elements_by_class_name('no-border-rechts')
        home_teams_list = [x.text for x in home_teams]
        home_teams_list = [x for x in home_teams_list if x != '']

        home_team_rank_list = [int(re.search(r'\d+', x).group()) for x in home_teams_list]
        home_team_name = [x.split('  ')[1] for x in home_teams_list]

        teams_list = driver.find_elements_by_class_name('vereinprofil_tooltip')
        for attr in ['id', 'href']:
            temp_list = [x.get_attribute(attr) for x in teams_list]
            temp_list = temp_list[::4]
            uni_temp = get_ordered_unique(temp_list)
            df_teams[attr] = uni_temp
        df_teams['id'] = df_teams['id'].apply(lambda x: int(x))
        df_teams['href'] = df_teams['href'].apply(lambda x: x.split('/')[3])


        uni_home_team_list = get_ordered_unique(home_team_name)
        df_teams['team'] = uni_home_team_list

        df_teams.to_excel('Deutschland_TeamIDs.xlsx')

        away_teams = driver.find_elements_by_class_name('no-border-links')
        away_teams_list = [x.text for x in away_teams]
        away_teams_list = [x for x in away_teams_list if x != '']

        away_team_rank_list = [int(re.search(r"([0-9_]+)", x.split('  ')[-1]).group()) for x in away_teams_list]
        away_team_name = [x.split('  ')[0] for x in away_teams_list]

        result = driver.find_elements_by_class_name('ergebnis-link')
        result_list = [x.text for x in result]

        n = random.random()
        print("sleep for seconds: " + str(n * 10))
        time.sleep(n * 10)

        match_day = [int((x / 9) + 1) for x in range(len(result_list))]

        result_df = pd.DataFrame(
            {'HomeTeam': home_team_name,
             'Result': result_list,
             'AwayTeam': away_team_name,
             'MatchDay': match_day,
             'HomeTeamRank': home_team_rank_list,
             'AwayTeamRank': away_team_rank_list
             })
        result_df['Saison'] = saison

        date_str = driver.find_elements_by_class_name('large-6')
        date_list = [x.text for x in date_str]
        date_list = [x for x in date_list if x != '']

        df_date = pd.DataFrame(columns=['WD', 'Date', 'Time'])
        for day in date_list:
            info = day.split('\n')
            info = [x for x in info if x != ' ']
            # print(info[-1])
            match_day = int(re.search(r'\d+', info[0]).group())
            combi_list = [[int(i / 2 - 1), x[:3], x[4:14], x[15:]] for i, x in enumerate(info) if
                          any(k in x for k in ['Mo.', 'Di.', 'Mi.', 'Do.', 'Fr.', 'Sa.', 'So.'])]
            df_temp = pd.DataFrame(columns=['WD', 'Date', 'Time'], data=np.zeros((9, 3)))
            df_temp = df_temp.replace(0.0, np.nan)
            for elem in combi_list:
                df_temp.loc[elem[0], ['WD', 'Date', 'Time']] = elem[1:]
                df_temp.fillna(method='ffill', inplace=True)
            df_date = pd.concat([df_date, df_temp])
        df_date.reset_index(inplace=True)

        result_df = pd.concat([df_date, result_df], axis=1)
        result_df = result_df[df.columns]
        df = pd.concat([df, result_df])

    df.reset_index(inplace=True)
    df.to_excel('{}_{}_{}.xlsx'.format(liga[0], YEAR_START, YEAR_STOP))

