import unittest
from rgkit.run import Runner
from rgkit.settings import AttrDict
import rgkit.rg as rg

import qrobot as q
from qrobot import QLearning, Robot, ACTION_MOVE, ACTION_ATTACK, ACTION_SUICIDE


class TestQRobot(unittest.TestCase):
    def smoke_test_robot(self):
        robot1 = q.Robot()
        robot2 = q.Robot()
        runner = Runner.from_robots(robot1, robot2)
        #runner.settings.max_turns = 5
        scores = runner.run()
        assert type(scores) is list

    @unittest.skip
    def test_robot(self):
        training_robot = Robot()
        robot2 = Robot()
        delta = training_robot.delta_callback
        runner = Runner.from_robots(training_robot, robot2,
                                    delta_callback=delta)
        runner.run()

        assert training_robot.qlearning.q != robot2.qlearning.q


class TestQLearning(unittest.TestCase):
    def setUp(self):
        # needed to initialize global settings
        Runner.from_robots(Robot(), Robot())

    def test_pickle(self):
        qlearning = QLearning()
        qlearning.save("test_q.pickle")
        qlearning_load = QLearning.load("test_q.pickle")
        assert qlearning == qlearning_load

    def test_learning(self):
        qlearning = QLearning()
        old_state = q.State.empty_state()
        action = ACTION_SUICIDE
        new_state = q.State.empty_state()
        reward = 10
        old_reward = qlearning.get_q(old_state, action)
        qlearning.learn(old_state, new_state, action, reward)
        self.assertGreater(qlearning.get_q(old_state, action), old_reward)
