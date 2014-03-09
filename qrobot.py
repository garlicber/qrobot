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
ACTION_MOVE = 1
ACTION_ATTACK = 1

MOVE_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


def hp2discrete(hp):
    if 50 > hp > 40:
        return HP_HIGH
    if 40 > hp > 15:
        return HP_MEDIUM
    else:
        return HP_LOW


def sum_tuple(a, b):
    return map(sum, zip(a, b))


class Field:
    def __init__(self, player_id=0, hp=0, type=FIELD_NORMAL):
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
        elif "normal" in loc_types:
            self.type = FIELD_NORMAL
        elif "obstacle" in loc_types:
            self.type = FIELD_OBSTACLE
        elif "spawn" in loc_types:
            self.type = FIELD_SPAWN


class State:
    def __init__(self, hp, fields):
        self.hp = hp
        self.fields = fields

    @staticmethod
    def empty_state():
        fields = {}
        for x in range(-SIGHT, SIGHT + 1):
            for y in range(-SIGHT, SIGHT + 1):
                if abs(x) + abs(y) <= SIGHT and (x != 0 and y != 0):
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
        for x in range(-SIGHT, SIGHT + 1):
            for y in range(-SIGHT, SIGHT + 1):
                field = self.fields[(x, y)]
                if field.player_id == 'enemy':
                    print("[E]"),
                elif field.player_id == 'friend':
                    print("[F]"),
                elif field.type == 'spawn':
                    print("[S]"),
                elif field.type != 'blocked':
                    print("[ ]"),
                print("")

    @staticmethod
    def map_action(action, loc):
        if action == ACTION_SUICIDE:
            return ["suicide"]

        (action_code, rel) = action
        (abs_x, abs_y) = QLearning.map_location(loc, rel)
        if action_code == ACTION_ATTACK:
            return ["attack", (abs_x, abs_y)]
        if action_code == ACTION_MOVE:
            return ["move", (abs_x, abs_y)]

        return "error"


class QLearning:
    DEFAULT_REWARD = 0
    q = {}

    _alpha = 0.5
    _gamma = 0.5

    def __init__(self, alpha=0.1, gamma=0.5):
        self.actions = self._actions()
        self._alpha = alpha
        self._gamma = gamma

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
        action = max(self.actions, key=lambda a: self.get_q(state, a))
        return action

    def learn(self, state, new_state, action, reward):
        old_q = self.get_q(state, action)
        optimal_future_value = max([self.get_q(new_state, a)
                                    for a in self.actions])
        q = old_q + self._alpha * \
            (reward + self._gamma * optimal_future_value - old_q)
        self.set_q(state, action, q)

    @staticmethod
    def map_location(absolute_loc, relative_loc):
        (rel_x, rel_y) = relative_loc
        (abs_x, abs_y) = absolute_loc
        return rel_x + abs_x, rel_y + abs_y

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

        self.current_state = State.from_game(self.location, self.hp, game)
        self.game = game

        # Explore
        if random.randint(0, 3) < 1:
            action = self.get_random_action()
        else:
            action = self.qlearning.predict(self.current_state)

        if not new_robot:
            self.learn()

        self.last_states[self.robot_id] = self.current_state
        self.last_action[self.robot_id] = action

        return State.map_action(action, self.location)

    def get_possible_actions(self):
        possible_moves = []
        for move in MOVE_DIRECTIONS:
            if self.current_state.fields[move].type != FIELD_OBSTACLE:
                possible_moves.append(move)

        return possible_moves

    def get_random_action(self):
        possible_action = self.get_possible_actions()
        return possible_action[random.randint(0, len(possible_action))]

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

    def delta_callback(self, delta):
        self.delta = delta


if __name__ == "__main__":
    training_robot = Robot()
    robot2 = Robot()
    runner = Runner.from_robots(training_robot, robot2,
                                delta_callback=training_robot.delta_callback)
    runner.run()
