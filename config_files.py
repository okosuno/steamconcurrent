import os
import yaml
from rich import print as rprint
from rich.table import Table
from class_defs import *
from data_proc import *
from searches import *
from vis_elements import *

CONFIG_DEFAULTS = {
'refresh_interval' : 120,
'log_interval' : 600,
'sparklines' : False,
'track_games' : True,
'avg_format' : 'per',
'polybar_interval' : 15,
}

def config_config_yaml(path, config_menu=False):
    # defaults   
    # initialize config 
    if os.path.exists(path + 'data/config.yaml') == False:
        try:
            try:
                os.mkdir(path + 'data')
            except:
                pass
            os.mknod(path + 'data/config.yaml')
        except PermissionError:
            rprint('[red]insufficient permissions to create config.yaml...')
        except:
            rprint('[red]could not create config.yaml...')
        # write default
        with open(path + 'data/config.yaml', 'w') as f:
            yaml.safe_dump(CONFIG_DEFAULTS,f)

    # get config options
    if config_menu == True:
        while True:
            config = dict()
            config['refresh_interval'] = \
            IntPrompt.ask("[yellow]enter time between player count queries in seconds ", \
            default=CONFIG_DEFAULTS['refresh_interval'])
            config['log_interval'] = \
            IntPrompt.ask("[yellow]enter time between log reads or writes in seconds ", \
            default=CONFIG_DEFAULTS['log_interval'])
            config['polybar_interval'] = \
            IntPrompt.ask("[magenta](polybar)[yellow] time to cycle between games in seconds? ", \
            default=CONFIG_DEFAULTS['polybar_interval'])
            config['sparklines'] = \
            Confirm.ask("[yellow](unimplemented) would you like to display sparklines? ", \
            default=CONFIG_DEFAULTS['sparklines'])
            config['track_games'] = \
            Confirm.ask("[yellow]would you like to track all games by default? ", \
            default=CONFIG_DEFAULTS['track_games'])
            config['avg_format'] = \
            Prompt.ask("[yellow]display average variance as a percentage or integer? ", \
            default=CONFIG_DEFAULTS['avg_format'], choices=['per','int'])
            # confirm choices
            config_display = Table(box=None)
            config_display.add_column("config", justify="left", style="blue", no_wrap=True)
            config_display.add_column("value", justify="right", style="cyan", no_wrap=True)
            for i in config:
                config_display.add_row(i, str(config[i]))
            rprint(config_display)
            decision = Confirm.ask("[magenta]confirm these choices? ", default=True)
            if not decision: continue
            # write choices
            with open(path + 'data/config.yaml', 'w') as f:
                yaml.safe_dump(config,f)
                rprint('[green]wrote choices to config.yaml!')
            break

def config_games_yaml(path, new_game):
    # initialize config 
    if not os.path.exists(path + 'data/games.yaml'):
        games_yaml = dict()
        # create games.yaml file
        try:
            os.mknod(path + 'data/games.yaml')
        except PermissionError:
            rprint('[red]insufficient permissions to create games.yaml...')
        except:
            rprint('[red]could not create games.yaml...')
        # write first entry
        games_yaml = { new_game.entryid : new_game.__dict__ }
        with open(path + 'data/games.yaml', 'w') as f:
            yaml.safe_dump(games_yaml,f)
    else:

        # load config
        with open(path + 'data/games.yaml', 'r') as f:
            games_yaml = yaml.safe_load(f)
        
    # create new entry
    if new_game is not None: 
        games_yaml[new_game.entryid] = new_game.__dict__
        # write config
        with open(path + 'data/games.yaml', 'w') as f:
            yaml.safe_dump(games_yaml,f)

    rprint('[green]\nsuccessfully added new game!')

def remove_game(path, query=None):
    rprint('[yellow]loading config file...')
    # first load all configured games
    try:
        with open(path + 'data/games.yaml', 'r') as f:
            games_yaml = yaml.safe_load(f)
    except FileNotFoundError:
        rprint("[red]can't find {}... have you added any games yet?".format(path))
        quit()

    rprint('[yellow]building objects...')
    # then load into objects
    objects = [ i for i in games_yaml.values() ]
    objects = [ Game(path=i['path'],appid=i['appid'],entryid=i['entryid'],name=i['name']) for i in objects ]   

    rprint('[yellow]searching...')
    for i in objects:
            if str(i.appid) == str(query) or str(i.entryid) == str(query) or str(i.name) == str(query):
                i.remove()
                rprint('[green]successfully removed {}'.format(i.name))
                return True

    rprint('[red]couldn\'t find anything matching {}'.format(query))
    return True
