from class_defs import *
import os
import argparse
from rich import print as rprint
from data_proc import *
from searches import *
from vis_elements import *
from config_files import *

def main():
    par = argparse.ArgumentParser(description=__doc__)
    conf = par.add_argument_group('configuration')
    disp = par.add_argument_group('display')
    q_type = par.add_mutually_exclusive_group()
    conf.add_argument('-c','--config-path', help='where you want steamconcurrent to put files (if not default)')
    conf.add_argument('-s','--setup', action="store_true", help='configure program settings')
    conf.add_argument('-f', '--refresh-source', action='store_true', help='forces a rebuild of the game_list file')
    par.add_argument('-q','--query', action='store_true', help='search for game [--name or --id]')
    q_type.add_argument('-n','--name', help='add game to config using best match from name')
    q_type.add_argument('-i','--id', help='add game to config from appid')
    par.add_argument('-r','--remove', help='remove game by appid, name, or entryid')
    disp.add_argument('-l','--list', action='store_true', help='output pretty info list about all saved games')
    disp.add_argument('-d','--display', action='store_true', help='terminal display & tracking')
    disp.add_argument('-p', '--polybar', action='store_true', help='polybar display & tracking')
    args = par.parse_args()
    
    # DEFAULT FILE OPERATIONS
    path = os.path.expanduser('~') + '/.config/steamconcurrent/'

    if args.config_path:
        path = args.config + "/"

    if not os.path.exists(path):
        try:
            os.mkdir(path)
            os.mkdir(path + "data/")
            config_config_yaml(path)
        except PermissionError:
            rprint('inadequate permissions to create file at {}'.format(path))
        except:
            rprint('[red]cannot find or use file location \'{}\''.format(path))
            quit()

    if args.setup:
        config_config_yaml(path, config_menu=True)

    # CHECK INTERNET CONNECTIVITY
    try: 
        requests.get('https://www.google.com/', stream = True)
    except:
        rprint('[red]cannot reach google.com, assuming lack of internet connectivity...\
        \nrunning this program without internet connectivity will tank db accuracy, exiting.') 
        quit()

    # SQLITE DB
    if not os.path.exists(path + 'data/game_list_db'):
        handle_game_list(path)
        process_game_list(path)

    if args.refresh_source:
        destroy_game_list(path)
        handle_game_list(path)
        process_game_list(path)

    # REMOVE
    if args.remove:
        remove_game(path, args.remove)

    # DISPLAY OPTIONS
    if args.list:
        list_games(path)

    if args.display:
        mode = "display"
        display_func(path, mode)
    
    if args.polybar:
        mode = "polybar"
        display_func(path, mode)
    
    # SEARCHING
    if args.query or args.name or args.id:
        main_search(args.query, args.name, args.id, path)

# SEARCHES
def main_search(query=None, name=None, id=None, path=None):
    if query:
        if name:
            output = search_by_name(path, name)
            output = Game(path, appid=output[0], name=output[1])
        elif id:
            output = search_by_appid(path, id)
            output = Game(path, name=output[0], appid=output[1])
        else:
            new_query = Prompt.ask("[yellow]enter name of game: ")
            output = search_by_name(path, new_query)
            output = Game(path,name=output)
    else:
        # make game object from args
        if id is not None:
            id = int(id)
        output = Game(path, appid=id, name=name)
        # file operations

    rprint(output.dump(format="default"))
    ansi = output.dump(format="ansi")
    rprint(ansi)
    config_games_yaml(path, output)
    return True

if __name__ == "__main__":
    main()
