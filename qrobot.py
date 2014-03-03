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
FIELD_OBSTACLE = 1 << 5

ACTION_SUICIDE = 1
ACTION_MOVE = 1
ACTION_ATTACK = 1

def hp2discrete(hp):
    if 50 > hp > 40:
        return HP_HIGH
    if 40 > hp > 15:
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

    def setQ(self, state, action, reward):
        self.q[(state, action)] = reward

    @staticmethod
    def _actions():
        actions = [ACTION_SUICIDE]
        for x in [-1, 1]:
            for y in [-1, 1]:
                actions.append((ACTION_ATTACK, (x, y)))
                actions.append((ACTION_MOVE, (x, y)))
        return actions

    def predict(self, state):
        action = max(self.actions, key=lambda a: self.getQ(state, a))
        return action

    def learn(self, state, action, new_state):
        return

    @staticmethod
    def map_action(action, loc):
        if action == ACTION_SUICIDE:
            return ["suicide"]

        (action_code,(rel_x, rel_y)) = action
        (loc_x, loc_y) = loc
        (abs_x, abs_y) = (rel_x + loc_x, rel_y + loc_y)
        if action_code == ACTION_ATTACK:
            return ["attack", (abs_x, abs_y)]
        if action_code == ACTION_MOVE:
            return ["move", (abs_x, abs_y)]

        return "error"

class Robot:
    game = None
    last_game = None

    qlearning = QTable()
    last_action = {}
    last_state = {}

    def act(self, game):
        self.game = game
        new_robot = self.robot_id not in self.last_action

        state = State.from_game(self)
        action = self.qlearning.predict(state)

        if not new_robot:
            self.qlearning.learn(self.last_state[self.robot_id], self.last_action[self.robot_id], state)

        self.last_state[self.robot_id] = state
        self.last_action[self.robot_id] = action
        self.last_game = game
        return QTable.map_action(action, self.location)
