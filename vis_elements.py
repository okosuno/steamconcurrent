import yaml
import time
import datetime as dt
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table
from rich.layout import Layout
from rich.live import Live
from rich.align import Align
from rich import box
from class_defs import *
from data_proc import *
from searches import *

def display_func(path, mode):
    # var assign
    try: 
        with open(path + 'data/games.yaml', 'r') as f:
            games_yaml = yaml.safe_load(f)
        with open(path + 'data/config.yaml', 'r') as f:
            config_yaml = yaml.safe_load(f)
    except FileNotFoundError:
        rprint("[red]can't find {}... have you added any games yet?".format(path))
        quit()

    # open db connection
    conn,cur = open_hist_db_conn(path)
    
    # intervals from config
    log_interval = config_yaml['log_interval']
    refresh_interval = config_yaml['refresh_interval']
    steam_query_interval = config_yaml['steam_query_interval']
    polybar_interval = config_yaml['polybar_interval']
    avg_format = config_yaml['avg_format']

    cache_list = list()
    object_list = list() 
    
    refresh_int_track = dt.datetime.now()
    log_int_track = dt.datetime.now()
    polybar_int_track = dt.datetime.now()
    steam_query_track = dt.datetime.now()
    refresh_int_period = refresh_int_track + dt.timedelta(seconds=refresh_interval)
    log_int_period = log_int_track + dt.timedelta(seconds=log_interval)
    polybar_int_period = log_int_track + dt.timedelta(seconds=polybar_interval)
    steam_query_period = steam_query_track  + dt.timedelta(seconds=steam_query_interval)

    # build object_list from file's list
    for i in games_yaml.values():
        object_list.append(Game(path=path, 
                                appid=i['appid'],
                                name=i['name'],
                                entryid=i['entryid'],
                                tracked=i['tracked'],
                                thumbnail=i['thumbnail']))
    
    # check for down status before entering display mode
    steam_status_check(steam_query_interval)

    # enter display modes
    if mode == "display":
        min_term_display(conn, cur, log_interval, refresh_interval, avg_format,\
                         cache_list, object_list, refresh_int_track, refresh_int_period,\
                         log_int_track, log_int_period, steam_query_interval, steam_query_track, steam_query_period)
    if mode == "polybar":
        polybar_display(conn, cur, log_interval, refresh_interval, avg_format, \
                        cache_list, object_list, refresh_int_track, refresh_int_period, \
                        log_int_track, log_int_period, polybar_interval, polybar_int_track, polybar_int_period, \
                        steam_query_interval, steam_query_track, steam_query_period)

def polybar_display(conn, cur, log_interval, refresh_interval,\
                    avg_format, cache_list, object_list, refresh_int_track,\
                    refresh_int_period, log_int_track, log_int_period, \
                    polybar_interval, polybar_int_track, polybar_int_period, \
                    steam_query_interval, steam_query_track, steam_query_period):
    list_index = 0
    rprint(object_list[-1].display(format="polybar",af=avg_format))
    while True: 
        if dt.datetime.now() >= steam_query_period:
            steam_query_track = dt.datetime.now()
            steam_query_period = steam_query_track + dt.timedelta(seconds=steam_query_interval)
            steam_status_check(steam_query_interval)

        if dt.datetime.now() >= polybar_int_period:
            polybar_int_track = dt.datetime.now()
            polybar_int_period = polybar_int_track + dt.timedelta(seconds=polybar_interval)
            rprint(object_list[list_index].display(format="polybar",af=avg_format))
            list_index += 1
            if list_index == len(object_list):
                list_index = 0

        if dt.datetime.now() >= refresh_int_period:
            refresh_int_track = dt.datetime.now() 
            refresh_int_period = refresh_int_track + dt.timedelta(seconds=refresh_interval)
            # store data to submit to db later
            for i in object_list:
                cache_list.append(i.track_moment())

        if dt.datetime.now() >= log_int_period:
            log_int_track = dt.datetime.now()      
            log_int_period = log_int_track + dt.timedelta(seconds=log_interval)
            hist_db_exec(cache_list, conn, cur)
            cache_list[:] = []
            # we only want to read new avgs on log_interval
            for i in object_list:
                i.call_historical_avgs()
        time.sleep(1)

def min_term_display(conn, cur, log_interval, refresh_interval, avg_format, cache_list, \
                     object_list, refresh_int_track, refresh_int_period, log_int_track, log_int_period, \
                     steam_query_interval, steam_query_track, steam_query_period):
    # build layout
    layout = generate_layout(object_list,af=avg_format)

    # start display
    with Live(layout, transient=True, screen=True, refresh_per_second=4) as live:
        while True: 
            live.update(generate_layout(object_list,af=avg_format), refresh=True)
            if dt.datetime.now() >= steam_query_period:
                steam_query_track = dt.datetime.now()
                steam_query_period = steam_query_track + dt.timedelta(seconds=steam_query_interval)
                steam_status_check(steam_query_interval)

            if dt.datetime.now() >= refresh_int_period:
                refresh_int_track = dt.datetime.now() 
                refresh_int_period = refresh_int_track + dt.timedelta(seconds=refresh_interval)
                # store data to submit to db later
                for i in object_list:
                    cache_list.append(i.track_moment())

            if dt.datetime.now() >= log_int_period:
                log_int_track = dt.datetime.now()      
                log_int_period = log_int_track + dt.timedelta(seconds=log_interval)
                hist_db_exec(cache_list, conn, cur)
                cache_list[:] = []
                # we only want to read new avgs on log_interval
                for i in object_list:
                    i.call_historical_avgs()
            time.sleep(1)

def generate_layout(object_list,af='per'):
    # set up table
    table = Table(show_header=False, box=None, padding=1)
    table.add_column(justify="center", vertical="middle", style="cyan")

    # build table
    for i in object_list:
        # format list output
        output_data = i.display(format="simple",af=af)
        table.add_row(output_data)
        
    panel = Panel(table, expand=True, box=box.SIMPLE)
    layout = Layout(Align.center(panel, vertical="middle"))

    return layout

def list_games(path):
    # get games
    try:
        with open(path + 'data/games.yaml', 'r') as f:
            games_yaml = yaml.safe_load(f)
    except FileNotFoundError:
        rprint("[red]can't find {}... have you added any games yet?".format(path))
        quit()

    # prepare formatting
    game_panels = list()
    game_table = Table(box=None)
    game_table.add_column(justify="left", no_wrap=True)
    game_table.add_column(justify="left", style="cyan", no_wrap=True)

    for i in games_yaml.values():
        # create object
        # surely there is a better way to do this
        game_obj = Game(path,
                        appid=i['appid'],
                        name=i['name'],
                        entryid=i['entryid'],
                        tracked=i['tracked'],
                        thumbnail=i['thumbnail'])
        # format list output
        output_data = game_obj.dump()
        ansi_data = game_obj.dump(format="ansi",ansi_width=35)
        game_table = Table(box=None, expand=True, padding=(0,0,1,0))
        game_table.add_column(justify="left", vertical="middle",  no_wrap=True)
        game_table.add_column(justify="left", vertical="bottom", style="cyan", no_wrap=True)
        game_table.add_row(ansi_data, output_data)
        game_panels.append(Panel(game_table, width=70, box=box.SIMPLE))

    # print all panels in list
    for i in game_panels:
        rprint(i)
    
    return True

# enters into a loop and stays there while steam is down to prevent storing of bad data
def steam_status_check(steam_query_interval):
    while True:
        interval_countdown = steam_query_interval
        res = requests.Response()
        try: 
            res = requests.get("https://api.steampowered.com/ISteamUserStats/GetNumberOfCurrentPlayers/v1/?appid=400", 
                               stream = True)
        except:
            rprint('[red]request threw exception while checking steam status...')
            
        if res.status_code == 200:
            break
        else:
            while True:
                rprint("[red]steam web api is down, trying again in {}s. [yellow]{}s remaining".format(steam_query_interval,interval_countdown))
                interval_countdown -= 1
                time.sleep(1)
                if interval_countdown <= 0:
                    break
    return True
