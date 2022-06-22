import rapidfuzz
import sqlite3
from rich import print as rprint
from rich.table import Table
from rich.prompt import Confirm,IntPrompt,Prompt

def fuzzy_search(path, fz_query, g_limit=20, g_cutoff=50):
    conn = sqlite3.connect(path + 'data/game_list_db')
    cur = conn.cursor()
    game_names = list()

    # get names for search
    try:
        cur.execute("SELECT name FROM games;")
        game_names = cur.fetchall()
    except:
        print("database SELECT or fetchall() failed. does db exist?")

    # format string for rapidfuzz
    game_names = [ i[0] for i in game_names]

    matches = rapidfuzz.process.extract(
        fz_query, game_names, limit=g_limit, score_cutoff=g_cutoff)       

    # populate appids from entryids
    matches_appids = tuple()
    for i in matches:
        try:
            cur.execute("SELECT appid FROM games WHERE entryid = ?;", (i[2],))
            matches_appids = matches_appids + cur.fetchone()
        except:
            print("[red]sqlite error for appid population in fz_search")
            quit()
   
    # append appids to matches
    for i,v in enumerate(matches_appids):
       matches[i] += (v,)

    # (names, match_percentage, entryids, appids)
    return matches

def fuzzy_search_appid(path, fz_query, g_limit=20, g_cutoff=50):
    # get names for search
    conn = sqlite3.connect(path + 'data/game_list_db')
    cur = conn.cursor()
    game_appids = list()

    try:
        cur.execute("SELECT appid FROM games;")
        game_appids = cur.fetchall()
    except:
        rprint("[red]database SELECT or fetchall() failed. does db exist?")

    # format string for rapidfuzz
    game_appids = [ str(i[0]) for i in game_appids]

    matches = rapidfuzz.process.extract(
        str(fz_query), game_appids, limit=g_limit, score_cutoff=g_cutoff)

    # populate names from entryids
    matches_names = tuple()
    for i in matches:
        try:
            cur.execute("SELECT name FROM games WHERE entryid = ?;", (i[2],))
            matches_names = matches_names + cur.fetchone()
        except:
            rprint("[red]sqlite error for appid population in fz_search")
   
    # append appids to matches
    for i,v in enumerate(matches_names,):
       matches[i] += (v,)
    
    # (appids, match_percentage, entryids, names)
    return matches

def search_by_name(path, query):
    # vars
    j = 2
    results = fuzzy_search(path, query)
    results = results[0:10]
    selection = ["0","1"]
    select_appids = ["0","1"]

    # table build
    results_display = Table(box=None)
    results_display.add_column("#", justify="left", style="yellow", no_wrap=True)
    results_display.add_column("match%", justify="left", style="cyan", no_wrap=True)
    results_display.add_column("game title", justify="left", style="magenta", no_wrap=False)
    results_display.add_column("appid", justify="right", style="yellow", no_wrap=True)
    for i in results:
        results_display.add_row(str(j), str(float(f'{i[1]:.1f}')), str(i[0]), str(i[3]))
        selection.append(str(j))
        select_appids.append(i[3])
        j += 1
    rprint(results_display)

    # make selection
    rprint("[red]0 to search again, 1 to abandon search")
    while True:
        choice = IntPrompt.ask("[yellow]enter # ", choices=selection, show_choices=False)
        if choice == 0:
            new_query = Prompt.ask("[yellow]enter new game title: ")
            search_by_name(path, new_query)
            break
        elif choice == 1:
            quit()
        else:
            confirmation = Confirm.ask("would you like to add " + results[choice-2][0] + " to your list of games?")
            if confirmation:
                # returns tuple (appid, name)
                return (results[choice-2][3], results[choice-2][0])
            else: 
                rprint("[red]selection aborted...")
                continue

def search_by_appid(path, query):
    # vars
    j = 2
    results = fuzzy_search_appid(path, query)
    results = results[0:10]
    selection = ["0","1"]
    select_names = ["0","1"]
    
    # table build
    results_display = Table(box=None)
    results_display.add_column("#", justify="left", style="yellow", no_wrap=True)
    results_display.add_column("match%", justify="left", style="cyan", no_wrap=True)
    results_display.add_column("game title", justify="left", style="magenta", no_wrap=False)
    results_display.add_column("appid", justify="right", style="yellow", no_wrap=True)
    for i in results:
        select_names.append(i[3])
        results_display.add_row(str(j), str(float(f'{i[1]:.1f}')), str(i[3]), str(i[0]))
        selection.append(str(j))
        j += 1
    rprint(results_display)

    # make selection
    rprint("[red]0 to search again, 1 to abandon search")
    while True:
        choice = IntPrompt.ask("[yellow]enter # ", choices=selection, show_choices=False)
        if choice == 0:
            new_query = Prompt.ask("[yellow]enter new appid: ")
            search_by_appid(path, new_query)
            break
        elif choice == 1:
            quit()
        else:
            confirmation = Confirm.ask("would you like to add " + results[choice-2][3] + " to your list of games?")
            if confirmation:
                # gives tuples of (name, appid)
                return (results[choice-2][3], results[choice-2][0])
            else: 
                rprint("[red]selection aborted...")
                continue
