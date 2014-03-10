import random
from rgkit.run import Runner

from q_learning import QLearning
from state import State
import state as s


def add_tuple(a, b):
    return map(sum, zip(a, b))


class Robot:
    game = None
    last_game = None

    current_state = None
    last_states = {}
    last_action = {}

    qlearning = QLearning()
    delta = None

    # Keep track of all our robot_ids. Will be useful to detect new robots.
    robot_ids = set()

    # default values - will get overridden by rgkit
    location = (0, 0)
    hp = 0
    player_id = 0
    robot_id = 0

    def __init__(self):
        pass

    def act(self, game):
        new_robot = self.robot_id in self.robot_ids
        self.robot_ids.add(self.robot_id)

        self.current_state = State.from_game(game, self.location,
                                             self.player_id)
        self.game = game

        # Explore
        if random.randint(0, 3) < 1:
            print("[Bot " + str(self.robot_id) + "] random action")
            # print self.state
            self.action = self.get_random_action()
        else:
            action = self.qlearning.predict(self.current_state)

        if not new_robot:
            self.learn()

        self.last_states[self.robot_id] = self.current_state
        self.last_action[self.robot_id] = action

        return State.map_action(action, self.location)

    def get_possible_actions(self):
        possible_moves = [s.ACTION_SUICIDE]
        for move in s.MOVE_DIRECTIONS:
            if self.state.fields[move].type != s.FIELD_OBSTACLE:
                possible_moves.append((s.ACTION_MOVE, move))
                possible_moves.append((s.ACTION_ATTACK, move))
        return possible_moves

    def get_random_action(self):
        possible_action = self.get_possible_actions()
        return possible_action[random.randint(0, len(possible_action)-1)]

    # delta = [AttrDict{
    #    'loc': loc,
    #    'hp': hp,
    #    'player_id': player_id,
    #    'loc_end': loc_end,
    #    'hp_end': hp_end
    # }]
    # returns new GameState
    def learn(self):
        my_delta = [d for d in self.delta if d.loc == self.location]

        damage_taken = my_delta.hp - my_delta.hp_end
        reward = my_delta.damage_caused - damage_taken

        last_state = self.last_states[self.robot_id]
        action = self.last_action[self.robot_id]
        future_state = self.current_state
        self.qlearning.learn(last_state, future_state, action, reward)

    def delta_callback(self, delta, new_gamestate):
        future_game = new_gamestate.get_game_info(self.player_id)
        print "delta_callback calle"
        print("Size of Q: " + len())
        for (loc, robot) in self.game.robots:
            action = self.last[robot.robot_id]['action']

            for delta_me in delta:
                if delta_me['loc'] == loc:
                    future_state = State.from_game(future_game,
                                                   delta_me.loc_end,
                                                   self.player_id)
                    self.qlearning.learn(delta_me, delta, self.state,
                                         future_state, action)


if __name__ == "__main__":
    training_robot = Robot()
    robot2 = Robot()
    runner = Runner.from_robots(training_robot, robot2,
                                delta_callback=training_robot.delta_callback)
    runner.run()
