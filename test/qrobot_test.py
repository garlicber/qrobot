import unittest
from rgkit.run import Runner
import qrobot as q

from qrobot import QLearning, Robot


class TestState(unittest.TestCase):
    def smoke_test_robot(self):
        robot1 = q.Robot()
        robot2 = q.Robot()
        runner = Runner.from_robots(robot1, robot2)
        runner.settings.max_turns = 5
        scores = runner.run()

    @unittest.skip
    def test_robot(self):
        training_robot = Robot()
        robot2 = Robot()
        delta = training_robot.delta_callback
        runner = Runner.from_robots(training_robot, robot2,
                                    delta_callback=delta)
        runner.run()

        assert training_robot.qlearning.q != robot2.qlearning.q

    def test_pickle(self):
        qlearning = QLearning()
        qlearning.save("test_q.pickle")
        qlearning_load = QLearning.load("test_q.pickle")
        assert qlearning == qlearning_load
