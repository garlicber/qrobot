import unittest
from rgkit.run import Runner
import qrobot as q

from qrobot import QLearning


class TestState(unittest.TestCase):
    def test_from_game(self):
        robot1 = q.Robot()
        robot2 = q.Robot()
        runner = Runner.from_robots(robot1, robot2)
        runner.settings.max_turns = 5
        runner.run()
        print(dir(robot1))
        print(robot1.game)

    def test_pickle(self):
        qlearning = QLearning()
        qlearning.save("test_q.pickle")
        qlearning_load = QLearning.load("test_q.pickle")
        assert qlearning == qlearning_load
