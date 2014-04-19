#! /usr/bin/env python2

import argparse
import copy
import pickle

import qrobot
import q_learning
from rgkit.run import Runner
from state import State


def arg_parse():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('robot', type=argparse.FileType('r'),
                        help='path of the robot to analyse')

    parser.add_argument('opponent', type=argparse.FileType('r'),
                        help='path of the robot to play against')
    parser.add_argument('-n', '--number_of_games', default=1)
    parser.add_argument('-o', '--output_file')

    return parser


class Analyser:
    def __init__(self,
                 player_file_to_analyse,
                 opponent_file):
        self._history = []
        self.last_state = None
        self.last_turn = 0
        self.player_id = 0
        self.player_file = player_file_to_analyse
        self.opponent_file = opponent_file
        self.q = {}

    def _delta_callback(self, deltas, actions, new_state):
        # detect new games
        if new_state.turn > self.last_turn and self.last_state is not None:
            game_info = new_state.get_game_info(self.player_id)
            state_template = State.from_game(game_info, self.player_id)
            for d in deltas:
                # spawned robots have 0 hp and are not listed in actions
                # we ignore them
                if d.hp != 0:
                    assert d.loc in actions
                    action = q_learning.QLearning.to_hashable_action(
                        actions[d.loc])
                    state = copy.deepcopy(state_template)
                    state.robot_loc = d.loc
                    self.q[(state, action)] = qrobot.Robot.reward(d)

        self.last_turn = new_state.turn
        self.last_state = new_state

    def run(self, number_of_games=1):
        runner = Runner(player1_file=self.player_file,
                        player2_file=self.opponent_file,
                        delta_callback=self._delta_callback)
        runner.options.n_of_games = number_of_games
        runner.run()


def main():
    arg_parser = arg_parse()
    args = arg_parser.parse_args()

    analyser = Analyser(args.robot.name,
                        args.opponent.name)
    analyser.run(int(args.number_of_games))
    filename = args.output_file
    with open(filename, "w+") as f:
        pickle.dump(analyser.q, f)


if __name__ == "__main__":
    main()
