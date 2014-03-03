import itertools
import rgkit.rg as rg

SIGHT = 3
HP_LOW = 1
HP_MEDIUM = 2
HP_HIGH = 3
HP_ALL = [HP_LOW, HP_MEDIUM, HP_HIGH]

FIELD_NORMAL = 1 << 1
FIELD_FRIEND = 1 << 2
FIELD_SPAWN = 1 << 3
FIELD_ENEMY = 1 << 4
FIELD_OBSTACLE = 1 << 1

def hp2discrete(hp):
    if 50 > hp >40:
        return HP_HIGH
    if 40> hp > 15:
        return HP_MEDIUM
    else:
        return HP_LOW

class Field:
    def __init__(self, player_id=0, hp=0, tpe=FIELD_NORMAL):
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
        self.type = rg.loc_types(loc);

class State:
    def __init__(self, hp, fields):
        self.hp = hp
        self.fields = fields

    @staticmethod
    def empty_state():
        fields = {}
        for x in range(-SIGHT, SIGHT+1):
            for y in range(-SIGHT, SIGHT+1):
                if abs(x)+abs(y) <= SIGHT and (x != 0 and y != 0):
                    fields[(x, y)] = Field(x, y)
        return State(0, fields)

    @staticmethod
    def from_game(robot):
        game = robot.game
        (loc_x, loc_y) = robot.location
        state = State.empty_state()
        for (fx, fy), field in state.fields.items():
            robot_loc = (loc_x + fx, loc_y + fy)
            if robot_loc in game.robots:
                state.fields[(fx, fy)].set_robot(game.robots[robot_loc])
            state.fields[(fx, fy)].set_location_type(robot_loc)
        state.hp = robot.hp
        return state

    def __str__(self):
        for x in range(-SIGHT, SIGHT +1):
            for y in range (-SIGHT, SIGHT +1):
                field = self.fields[(x,y)]
                if field.player_id == 'enemy':
                    print "[E]",
                elif field.player_id == 'friend':
                    print "[F]",
                elif field.type == 'spawn':
                    print "[S]",
                elif field.type != 'blocked':
                    print "[ ]",
                print ""


class QTable:
    DEFAULT_REWARD = 0
    q = {}

    def __init__(self):
        self.actions = self._actions()

    def getQ(self, state, action):
        if (state, action) in self.q:
            return self.q[(state, action)]
        else:
            return self.DEFAULT_REWARD



    @staticmethod
    def _actions():
        actions = [["suicide"]]
        for x in [-1, 1]:
            for y in [-1, 1]:
                actions.append(["move", (x, y)])
                actions.append(["attack", (x, y)])
        return actions

    def predict(self, robot):
        state = State.from_game(robot)
        action = max([self.getQ(state, a) for a in self.actions])
        return action

    def learn(self, robot):
        return


class Robot:
    game = None
    qlearning = QTable()
    last_actions = {}

    def act(self, game):
        if self.robot_id not in self.last_actions:
            self.last_actions[self.robot_id] = []

        self.game = game
      #  action = self.qlearning.predict(self)
      #  self.last_actions[self.robot_id].append(action)
      #  self.qlearning.learn()
      #  return action
        return ["guard"]
