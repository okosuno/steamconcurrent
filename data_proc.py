"""
trying to contain non-class sqlite ops to this document
"""
import requests
import os
import time
import json
import sqlite3
from rich import print

# returns dict of all games & writes it game_list_raw
def handle_game_list(path):
    age_flag = False     
    file_age = 0
    file_stats = 0
    refresh_age = 86400 # one day
    game_list_raw_data = 0

    # load game_list_raw metadata
    if os.path.exists(path + "data/game_list_raw"):
        file_stats = os.stat(path + "data/game_list_raw")
        file_age   = (time.time()-file_stats.st_mtime)

    # age filter
    if file_age > refresh_age:
        print('[magenta]game_list_raw age > recommended refresh age')
        age_flag = True;

    # conditions check
    if age_flag == False and file_stats == True:
        pass
    else:
        try:
           with open(path + "data/game_list_raw", 'w') as game_list:
                try:
                    print('[yellow]downloading list of steam games...')
                    game_list_raw_data = requests.get(
                    "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
                    )
                except:
                    print("could not complete request.")
                print('[yellow]writing list to file...')
                game_list_raw_data = game_list_raw_data.json()
                json.dump(game_list_raw_data, game_list, indent = 3)
        except:
            print("[red]could not process requested data.")
            quit()
    return game_list_raw_data

def destroy_game_list(path):
    if os.path.exists(path + "data/game_list_db"):
        try:
            os.remove(path + "data/game_list_db")
        except:
            print('[red]could not delete game_list_db. check file permissions.') ## EXCEPTION
    else:
        print('[red]game_list_db file does not exist or is inaccessible.')
    return True

def process_game_list(path, **kwargs):
    # get either game_list_raw file or existing game_list_data variable 
    game_list_raw_data = kwargs.get('game_list_data', dict())
     
    if game_list_raw_data == dict():
        try:
            with open(path + "data/game_list_raw", 'r') as game_list:
                print('[yellow]reading game list file...')
                game_list_raw_data = json.load(game_list)
        except:
            print("[red]could not open 'data/game_list_raw' file. \
                  \ndoes path exist?")

    # extract names & appids into sqlite acceptable list of tuples
    print('[yellow]processing list...')
    raw_entryid = [ i for i, _ in enumerate(game_list_raw_data['applist']['apps']) ]
    raw_names = [ str(i['name']) for i in game_list_raw_data['applist']['apps'] ]  
    raw_appids = [ int(i['appid']) for i in game_list_raw_data['applist']['apps'] ]  
    processed_list = [ list(i) for i in zip(raw_entryid,raw_appids,raw_names) ]
    
    # since data being processed is new, remove old sqlite database
    if os.path.exists(path + 'data/game_list_db'):
            try:
                os.remove(path + 'data/game_list_db')
            except:
                print(path + 'data/game_list_db exists but is inaccessible...')

    ### create and populate sqlite database 
    print('[yellow]building database...')
    conn = sqlite3.connect(path + 'data/game_list_db')
    cur = conn.cursor()
    cur.execute(""" CREATE TABLE IF NOT EXISTS games(
        entryid INT     PRIMARY KEY,
        appid   INT,
        name    TEXT);
        """)
    conn.commit()
    cur.executemany("INSERT INTO games VALUES(?, ?, ?);", processed_list )
    conn.commit()
    conn.close()
  
    # remove game_list_raw file since we have a working db
    os.remove(path + 'data/game_list_raw')

    print('[green]done!')
    return True

def open_hist_db_conn(path):
    conn = sqlite3.connect(path + 'data/historical_data')
    cur = conn.cursor()
    return conn,cur

def hist_db_exec(exec_list, conn, cur) -> (bool):
    cur.executemany('''INSERT INTO historical_data(appid, timestamps, players) VALUES(?, ?, ?);''', \
                exec_list)
    conn.commit()
    return True
