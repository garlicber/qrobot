import random
import rgkit.rg as rg
from rgkit.run import Runner
import _collections

SIGHT = 3
HP_LOW = 1
HP_MEDIUM = 2
HP_HIGH = 3
HP_ALL = [HP_LOW, HP_MEDIUM, HP_HIGH]

FIELD_NORMAL = 1 << 1
FIELD_FRIEND = 1 << 2
FIELD_SPAWN = 1 << 3
FIELD_ENEMY = 1 << 4
FIELD_OBSTACLE = 1 << 5

ACTION_SUICIDE = 1
ACTION_MOVE = 2
ACTION_ATTACK = 3

REWARD_UNIT = 1

MOVE_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def hp2discrete(hp):
    if 50 > hp > 40:
        return HP_HIGH
    if 40 > hp > 15:
        return HP_MEDIUM
    else:
        return HP_LOW


def add_tuple(a, b):
    return map(sum, zip(a, b))


class Field:
    def __init__(self, player_id=0, hp=0, type = FIELD_NORMAL):
        self.player_id = player_id
        self.hp = 0
        self.type = type

    def set_robot(self, robot):
        self.hp = hp2discrete(robot.hp)
        self.player_id = robot.player_id
        if hasattr(robot, "robot_id"):
            self.type = FIELD_FRIEND
        else:
            self.type = FIELD_ENEMY

    def set_location_type(self, loc):
        loc_types = rg.loc_types(loc)
        if "invalid" in loc_types:
            self.type = FIELD_OBSTACLE
        elif "obstacle" in loc_types:
            self.type = FIELD_OBSTACLE
        elif "spawn" in loc_types:
            self.type = FIELD_SPAWN
        elif "normal" in loc_types:
            self.type = FIELD_NORMAL


class State:
    def __init__(self, hp, fields):
        self.hp = hp
        self.fields = fields

    @staticmethod
    def empty_state():
        fields = {}
        for x in range(-SIGHT, SIGHT + 1):
            for y in range(-SIGHT, SIGHT + 1):
                if abs(x) + abs(y) <= SIGHT and (x != 0 or y != 0):
                    fields[(x, y)] = Field(x, y)
        return State(0, fields)

    @staticmethod
    def from_game(robot_location, robot_hp, game):
        (loc_x, loc_y) = robot_location
        state = State.empty_state()
        for (fx, fy), field in state.fields.items():
            robot_loc = (loc_x + fx, loc_y + fy)
            if robot_loc in game.robots:
                state.fields[(fx, fy)].set_robot(game.robots[robot_loc])
            state.fields[(fx, fy)].set_location_type(robot_loc)
        state.hp = robot_hp
        return state

    def __str__(self):
        state_string = ""
        for x in range(-SIGHT, SIGHT + 1):
            for y in range(-SIGHT, SIGHT + 1):
                if abs(x) + abs(y) <= SIGHT and (x != 0 or y != 0):
                    field = self.fields[(x, y)]
                    if field.player_id == FIELD_ENEMY:
                        state_string += "[E]"
                    elif field.player_id == FIELD_FRIEND:
                        state_string += "[F]"
                    elif field.type == FIELD_SPAWN:
                        state_string += "[S]"
                    elif field.type != FIELD_OBSTACLE:
                        state_string += "[ ]"
                    else:
                        state_string += "[B]"
            state_string += "\n"
        return  state_string

class QLearning:
    DEFAULT_REWARD = 0
    q = {}

    _alpha = 0.5
    _gamma = 0.5

    def __init__(self, alpha=0.1, gamma=0.5):
        self.actions = self._actions()
        self._alpha = alpha
        self._gamma = gamma


    def __sizeof__(self):
        return len(self.q)

    def get_q(self, state, action):
        if (state, action) in self.q:
            return self.q[(state, action)]
        else:
            return self.DEFAULT_REWARD

    def set_q(self, state, action, reward):
        self.q[(state, action)] = reward

    @staticmethod
    def _actions():
        actions = [ACTION_SUICIDE]
        for cords in MOVE_DIRECTIONS:
            actions.append((ACTION_ATTACK, cords))
            actions.append((ACTION_MOVE, cords))
        return actions

    def predict(self, state):
        #print state
        action = max(self.actions, key=lambda a: self.get_q(state, a))
        return action

    def learn(self, delta_me, delta, state, new_state, action):
        reward = self.reward(delta_me, delta, action)
        old_q = self.get_q(state, action)
        optimal_future_value = max([self.get_q(new_state, a)
                                    for a in self.actions])
        q = old_q + self.alpha * \
            (reward + self.gamma * optimal_future_value - old_q)
        self.set_q(state, action, q)

    @staticmethod
    def map_action(action, loc):
        if action == ACTION_SUICIDE:
            return ["suicide"]

        (abs_x, abs_y) = add_tuple(loc, action[1])
        if action[0] == ACTION_ATTACK:
            return ["attack", (abs_x, abs_y)]
        if action[0] == ACTION_MOVE:
            return ["move", (abs_x, abs_y)]
        print "[error] no mapping for action"
        return "error"

    def reward(self, delta_me, delta, action):
        damage_dealt = 0
        damage_taken = 0

        if action[0] == ACTION_ATTACK:
            attack_loc = action[1]
            for dict in delta:
                if dict["loc_end"] == attack_loc and \
                        delta_me["player_id"] != delta["player_id"]:
                    damage_dealt += 9

        damage_taken = delta_me.hp - delta_me.hp_end

        # If suiccide makes more damage then the lifepoint lost then its a good
        # choice

        return (damage_dealt - damage_taken) * REWARD_UNIT

    def __eq__(self, other):
        return (self.q == other.q and
                self._alpha == other._alpha and
                self._gamma == other._gamma)

    def save(self, file_name="q.pickle"):
        import pickle
        with open(file_name, "w") as f:
            pickle.dump(self, f)

    @staticmethod
    def load(file_name="q.pickle"):
        import pickle
        with open(file_name, "r") as f:
            return pickle.load(f)


class Robot:
    game = None
    last_game = None
    last = _collections.defaultdict(dict)

    qlearning = QLearning()
    last_action = {}
    last_state = {}

    def __init__(self):
        self.last_hp = 50

    def act(self, game):
        new_robot = self.robot_id not in self.last

        self.state = State.from_game(self.location, self.hp, game)
        self.game = game

        # Explore
        if random.randint(0, 3) < 1:
            print("[Bot " + str(self.robot_id) + "] random action")
            # print self.state
            self.action = self.get_random_action()
        else:
            self.action = self.qlearning.predict(self.state)

        return QLearning.map_action(self.action, self.location)

    def count_enemys_in_range(self):
        count = 0
        for dir in MOVE_DIRECTIONS:
            attack_location = map(sum, zip(dir, self.location))
            if attack_location in self.game.robots and \
                    hasattr(self.game.robots[attack_location], 'robot_id'):
                count += 1
        return count

    def get_possible_actions(self):
        possible_moves = [ACTION_SUICIDE]
        for move in MOVE_DIRECTIONS:
            if self.state.fields[move].type != FIELD_OBSTACLE:
                possible_moves.append((ACTION_MOVE, move))
                possible_moves.append((ACTION_ATTACK, move))
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

    def delta_callback(self, delta, new_gamestate):
        future_game = new_gamestate.get_game_info(self.player_id)
        print "delta_callback calle"
        print("Size of Q: " + len())
        for (loc, robot) in self.game.robots:
            action = self.last[robot.robot_id]['action']

            for delta_me in delta:
                if delta_me['loc'] == loc:
                    future_state = State.from_game(delta_me.loc_end,
                                                   delta_me.hp_end,
                                                   future_game)
                    self.qlearning.learn(delta_me, delta, self.state,
                                         future_state, action)


if __name__ == "__main__":
    training_robot = Robot()
    robot2 = Robot()
    runner = Runner.from_robots(training_robot, robot2,
                                delta_callback=training_robot.delta_callback)
    runner.run()
