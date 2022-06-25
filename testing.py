import unittest
import os
from data_proc import *
from vis_elements import list_games
from main_temp import * 

PATH = os.path.expanduser('~') + '/.config/playerpeep/'

class Tests(unittest.TestCase):
    # DB TESTING
    def test_destroy_game_list(self):
        result = destroy_game_list(PATH)
        self.assertTrue(result)

    def test_handle_game_list(self):
        result = handle_game_list(PATH)
        self.assertTrue(result)

    def test_process_game_list(self):
        result = process_game_list(PATH)
        self.assertTrue(result)
    
    # LIST TEST
    def test_lists(self):
        result = list_games(PATH)
        self.assertTrue(result)

    # ADD GAME 
    def test_add_game(self):
        # BY NAME
        result = main_search(name="Team Fortress 2", path=PATH)
        self.assertTrue(result)
        # BY ID
        result = main_search(id=400, path=PATH)
        self.assertTrue(result)
    
    # REMOVE BOTH GAMES 
    def test_rem_game(self):
        # BY NAME
        result = remove_game(PATH, query="Team Fortress 2")
        self.assertTrue(result)
        # BY ID
        result = remove_game(PATH, query=400)
        self.assertTrue(result)

    # STEAM STATUS CHECK
    def test_steam_status_check(self):
        result = steam_status_check(3)
        self.assertTrue(result)

if __name__ == "__main__":
    unittest.main()
