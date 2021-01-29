from bs4 import BeautifulSoup
import pandas as pd
import requests
import numpy as np

url = ["https://resultados.as.com/resultados/ficha/equipo/real_madrid/1/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/alaves/4/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/athletic/5/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/atletico/42/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/barcelona/3/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/betis/171/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/cadiz/91/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/celta/6/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/eibar/108/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/elche/121/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/getafe/172/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/granada/347/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/huesca/864/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/levante/136/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/osasuna/13/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/r_sociedad/16/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/sevilla/53/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/valencia/17/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/valladolid/18/calendario/",
       "https://resultados.as.com/resultados/ficha/equipo/villarreal/19/calendario/"]

dfs = []

for url in url:
    req = requests.get(url)
    soup = BeautifulSoup(req.content, 'html.parser')

    team = soup.find("div", {"class":"hdr-ficha-info s-left"}).find_all("a")[1].contents[0]

    results = soup.find_all("div", {"class":"cont-modulo resultados competicion-home"})

    game_list = []
    for game in results:
        if game.find("span", {"class":"fecha-evento"}).contents[0] == "LaLiga Santander":
            result_game = game.find("div", {"class":"cont-resultado finalizado"})
            if result_game != None:
                home_team = game.find("div", {"class":"equipo-local"}).find("span", {"class":"nombre-equipo"}).contents[0]
                away_team = game.find("div", {"class":"equipo-visitante"}).find("span", {"class":"nombre-equipo"}).contents[0]
                result_game = result_game.find("a").contents[0]
                home_goals = result_game.split("-")[0].replace(" ", "")
                away_goals = result_game.split("-")[1].replace(" ", "")
                if home_goals < away_goals:
                    winner = "away"
                elif home_goals > away_goals:
                    winner = "home"
                else:
                    winner = "draw"

                if winner == "home":
                    if home_team == team:
                        points = 3
                    else:
                        points = 0
                elif winner == "away":
                    if away_team == team:
                        points = 3
                    else:
                        points = 0
                else: points = 1

                game_list.append({'home': home_team,
                            'away': away_team,
                            'home_goals': int(home_goals),
                            "away_goals": int(away_goals),
                            "winner": winner,
                            "points": points})

    df_games = pd.DataFrame(game_list, columns = ['home', 'away', 'home_goals', "away_goals", "winner", "points"])

    df_games["previous_home"] = np.nan
    df_games["previous3_home"] = np.nan
    df_games["previous_away"] = np.nan
    df_games["previous3_away"] = np.nan

    for i in range(1, len(df_games)):
        if df_games.loc[i, 'home'] == team:
            df_games.loc[i, 'previous_home'] = df_games.loc[i - 1, 'points']
            #df_games.loc[i, 'previous_away'] = 0
        else:
            df_games.loc[i, 'previous_away'] = df_games.loc[i - 1, 'points']
            #df_games.loc[i, 'previous_home'] = 0


    for i in range(3, len(df_games)):
        if df_games.loc[i, 'home'] == team:
            df_games.loc[i, 'previous3_home'] = df_games.loc[i - 1, 'points'] + df_games.loc[i - 2, 'points'] + df_games.loc[i - 3, 'points']
            #df_games.loc[i, 'previous3_away'] = 0
        else:
            df_games.loc[i, 'previous3_away'] = df_games.loc[i - 1, 'points'] + df_games.loc[i - 2, 'points'] + df_games.loc[i - 3, 'points']
            #df_games.loc[i, 'previous3_home'] = 0

    df_games.drop('points', axis=1, inplace=True)

    dfs.append(df_games)

dfs_together = pd.concat(dfs)

df_final = dfs_together.groupby(by=["home", "away", "winner"]).sum(min_count=1).reset_index()

df_final["home_goals"], df_final["away_goals"] = df_final["home_goals"] / 2, df_final["away_goals"]/2

df_final.to_csv("final_tabla.csv", index=False, encoding='iso-8859-1')
