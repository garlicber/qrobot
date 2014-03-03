import ast
import unittest
import pkg_resources
import rgkit.game as game
import rgkit.settings
import rgkit.rg as rg
import qrobot as q

def mock_game(robot1, robot2=None):
    if robot2 is None:
        robot2 = robot1

    rg.set_settings(rgkit.settings.settings)

    map_file = open(pkg_resources.resource_filename('rgkit', 'maps/default.py'))
    map_data = ast.literal_eval(map_file.read())
    game.init_settings(map_data)

    player1 = game.Player(None, robot1)
    player2 = game.Player(None, robot2)
    return game.Game(player1, player2)


def play(robot, turns = 5):
    g = mock_game(robot, robot)
    for i in xrange(5):
        g.run_turn()
    return g.get_scores()


class TestState(unittest.TestCase):
    def test_from_game(self):
        robot = q.Robot()
        g = mock_game(robot)
        g.run_turn()
        g.run_turn()
        robot1 = g._player1._robot
        print(dir(robot1))
        state = q.State.from_game(robot1, g._state)

if __name__ == '__main__':
    unittest.main()