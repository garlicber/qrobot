import unittest
import rgkit.gamestate as gamestate
from state import State


class TestState(unittest.TestCase):
    def test_loc_to_field_mapping(self):
        gstate = gamestate.GameState()
        friend_id = 1
        enemy_id = 2
        friends = [(1, 8), (3, 3), (17, 9), (9, 1), (17, 11)]
        enemies = [(1, 9), (4, 3), (16, 9), (10, 1)]
        robots = friends + enemies

        for f_loc in friends:
            gstate.add_robot(f_loc, friend_id)
        for e_loc in enemies:
            gstate.add_robot(e_loc, enemy_id)

        game = gstate.get_game_info(friend_id)
        s = State.from_game(game, friends[0], friend_id)

        for f_loc in friends:
            self.assertEqual(s.field(f_loc), State.FRIEND)
        for e_loc in enemies:
            self.assertEqual(s.field(e_loc), State.ENEMY)
