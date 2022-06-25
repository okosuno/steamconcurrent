import requests
import shutil
import climage
import sqlite3
import os
import yaml
import math
import textwrap
from rich import print as rprint
from rich.text import Text
from rich.prompt import Confirm
from searches import fuzzy_search
from data_proc import *
from datetime import datetime

class Game:
    appid = int()
    name = str()
    entryid = int()
    player_count = 0
    player_avg = 0
    test_val = 10
    tracked = True
    thumbnail = str()
    path = ''

    def __init__(self, path, appid=None, name=None, entryid=None, tracked=None, thumbnail=None):
        self.appid = appid
        self.name = name
        self.entryid = entryid
        self.tracked = tracked
        self.thumbnail = thumbnail
        self.path = path    

        if self.appid is None and self.entryid is None and self.name is None:
            rprint('[red]not enough parameters to create object')
            quit()

        # get entryid from name
        if self.appid is None and self.entryid is None:
                search_result = fuzzy_search(self.path, self.name)
                self.entryid = search_result[0][2]
                self.name = search_result[0][0]

        # get appid from entryid
        if self.appid is None:
            try:
                conn = sqlite3.connect(self.path + 'data/game_list_db')
                cur = conn.cursor()
                cur.execute("SELECT appid FROM games WHERE entryid = ?;", (self.entryid,))
                appid = cur.fetchone()
            except:
                rprint("[red]sqlite error for obj [bold]" + self.name)
                quit()
            try:
                self.appid = appid[0]
            except:
                rprint('[red]did not find {} in {}'.format(self.appid,'entryid'))
                quit()
            
            conn.close()
        
        # get entryid from appid
        if self.entryid is None and self.appid is not None:
            try:
                conn = sqlite3.connect(self.path + 'data/game_list_db')
                cur = conn.cursor()
                cur.execute("SELECT entryid FROM games WHERE appid = ?;", (self.appid,))
                entryid = cur.fetchone()
            except:
                rprint("[red]sqlite error for obj [bold]" + self.name)
                quit()
            try:
                self.entryid = entryid[0]
            except:
                rprint('[red]did not find {} in {}'.format(self.appid,'entryid'))
                quit()
            
            conn.close()

        # get name from appid
        if self.name is None:
            try:
                conn = sqlite3.connect(self.path + 'data/game_list_db')
                cur = conn.cursor()
                cur.execute("SELECT name FROM games WHERE appid = ?;", (self.appid,))
                name = cur.fetchone()
            except:
                rprint("[red]sqlite error for obj [bold]" + self.name)
                quit()
            try:
                self.name = name[0]
            except:
                rprint('[red]did not find {} in {}'.format(self.name,'name'))
                quit()
            
            conn.close()

        # get and save thumbnail image
        thumbnail_url = "https://cdn.cloudflare.steamstatic.com/steam/apps/" + str(self.appid) + "/header.jpg"
        self.thumbnail = thumbnail_url

        if os.path.exists(thumbnail_url) is False:
            res = requests.Response()
            try: 
                res = requests.get(self.thumbnail, stream = True)
            except:
                rprint('[red]thumbnail request threw exception, are you connected to the internet?')
                
            if res.status_code == 200:
                with open(self.path + 'data/' + self.name + '-header.jpg','wb') as f:
                    shutil.copyfileobj(res.raw, f)
            else:
                rprint("[red]unsuccessful at retrieving header image for " + self.name)
                self.thumbnail = None

        # get player count
        self.update_player_count()

        # delete self if unsuccessful at fetching data
        if self.player_count is None and self.thumbnail is None:
            rprint("[red]this game could not produce neither a player_count or thumbnail\n" + \
            "this likely means this app entry does not track this information\n" + \
            "object will now be deleted...")
            del self
            quit()
        
        # check config file for default tracked status 
        if os.path.exists(self.path + 'data/config.yaml'):
            with open(self.path + 'data/config.yaml', 'r') as f:
                config_yaml = yaml.safe_load(f)
            self.tracked = config_yaml['track_games']
        elif os.path.exists(self.path + 'data.config.yaml') == False:
            self.tracked = True
            rprint(self.name + ' cannot find config file, reverting to tracked = ' + str(self.tracked))

        # construct the historical log table 
        conn = sqlite3.connect(self.path + 'data/historical_data')
        cur = conn.cursor()    
        cur.execute(""" CREATE TABLE IF NOT EXISTS historical_data(
            appid       INT,
            timestamps  TEXT,
            players     INT);
            """)
        conn.commit()    
        hist_db_exec( [self.track_moment(),], conn, cur)
        self.call_historical_avgs()
        conn.close()
        
    def dump(self, format="default", ansi_width=70):
        if format == "default":
            return (
                "[blue]entryid: [yellow][bold]" + str(self.entryid) + "[/bold]\n" + 
                "[blue]appid: [yellow][bold]" + str(self.appid) + "[/bold]\n" + 
                "[blue]name: [yellow][bold]" + textwrap.shorten(self.name,width=20) + "[/bold]\n" + 
                "[blue]tracked: [yellow][bold]" + str(self.tracked) + "[/bold]\n" +
                "[blue]current players: [yellow][bold]" + str(self.player_count) + "[/bold]\n"
            ) 
        elif format == "essential":
            return (
                "[blue]name  [yellow][bold]" + self.name + "[/bold]\n" + 
                "[blue]appid  [yellow][bold]" + str(self.appid) + "[/bold]\n" + 
                "[blue]current players [yellow][bold]" + str(self.player_count)
            )
        elif format == "ansi":
            if os.path.exists(self.path + 'data/' + self.name + '-header.jpg'):
                return Text.from_ansi(climage.convert(self.path + 'data/' + self.name + '-header.jpg', is_unicode=True, width=ansi_width))
            else:
                return "[no image found]"
        else: return("[red]invalid dump format.")

    
    # display modes
    def display(self, format=None, af='per'):
        avg_variance = str()
        avg_value = int()
        sign = ""
        avg = self.player_avg
        
        # format average calculations 
        if self.player_count is not None:
            if af == 'per' and avg != 0:
                avg_value = math.trunc(((self.player_count - avg) / avg) * 100)
                sign = "%"   
            else:
                avg_value = (self.player_count - avg)

        if avg_value > 0:
            color = "#00ff00"
        elif avg_value == 0 :
            color = "#ffffff"
        else:
            color = "#ff0000"
        
        avg_variance = "[{0}]({1:+}{2})[/{0}]".format(color,avg_value,sign)  

        # return requested display type
        if format == "display":
            return ("[yellow]{}[/yellow] has [yellow]{}[/yellow] {} players online.".format(self.name, self.player_count, avg_variance))
        elif format == "polybar":
            return ("{}: {} {}".format(self.name, self.player_count, avg_variance))

        return "no matching display modes..."

    # query steam web api for new player count
    def update_player_count(self):
        try:
            r_players = requests.get(
                "https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?",
                params={'appid': self.appid} )

            if r_players.status_code == 200:
                r_players = r_players.json()        
                g_players = r_players['response']['player_count']
                self.player_count = g_players
            else: 
                rprint("[red]could not fetch player count, response: " + str(r_players) )
                self.player_count = None
                time.sleep(1)
        except:
            rprint("there was an issue completing this request.")
            pass

    
    # return timestamped tuple for SQL entries
    def track_moment(self) -> (tuple):
        self.update_player_count()
        moment = (int(self.appid), str(datetime.now()), self.player_count)
        return moment

    def test_funct(self,test_val):
        self.test_val = test_val

    # get every single piece of sql data for this object
    def call_historical_data(self):
        conn = sqlite3.connect(self.path + 'data/historical_data')
        cur = conn.cursor()
        cur.execute("SELECT * FROM historical_data WHERE appid = ?;", (self.appid,))
        live_data = cur.fetchall()
        cur.close()
        conn.close()
        return live_data

    # get player_count averages for this object
    def call_historical_avgs(self):
        conn = sqlite3.connect(self.path + 'data/historical_data')
        cur = conn.cursor()
        cur.execute("SELECT AVG(players) FROM historical_data WHERE appid = ?;", (self.appid,))
        live_data = cur.fetchone()
        cur.close()
        conn.close()
        self.player_avg = int(live_data[0])
        return live_data

    # should be called on destruction 
    def remove(self):
        # remove header image
        header_path = self.path + 'data/' + self.name + '-header.jpg'
        if os.path.exists(header_path):
            os.remove(header_path)
        else:
            rprint('[red]could not find header image to delete...')

        # remove games_yaml entry
        with open(self.path + 'data/games.yaml','r') as f:
            games_yaml = yaml.safe_load(f)
        
        games_yaml.pop(self.entryid)

        # remove historical data
        select = Confirm.ask("[yellow]would you like to remove ALL historical data tracked for this item? ", \
                    default=False)

        if not select:
            rprint("[yellow]you can change this later by adding the game again and removing it the same way...")
        else: 
            conn, cur = open_hist_db_conn(self.path)
            cur.execute("DELETE FROM historical_data WHERE appid = ?;", (self.appid, ) )
            conn.commit()
            conn.close()
            
        with open(self.path + 'data/games.yaml','w') as f:
            yaml.safe_dump(games_yaml,f)

