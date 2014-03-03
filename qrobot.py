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
    return HP_HIGH


class Field:
    def __init__(self, x, y, player_id=0, hp=0, tpe=FIELD_NORMAL):
        self.player_id = player_id
        self.hp = 0
        self.type = tpe

    def set_robot(self, robot):
        self.hp = hp2discrete(robot.hp)
        self.player_id = robot.player_id
        if hasattr(robot, "robot_id"):
            self.type = FIELD_FRIEND
        else:
            self.type = FIELD_ENEMY

        loc_types = rg.loc_types(robot.location)
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
    def from_game(robot, game):
        (loc_x, loc_y) = robot.location
        state = State.empty_state()
        for (fx, fy), field in state.fields.items():
            robot_loc = (loc_x + fx, loc_y + fy)
            if robot_loc in game.robots:
                state.fields[(fx, fy)].set_robot(game.robots[robot_loc])

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
    def __init__(self):
        self.states = self._generate_all_states()
        self.actions = self._actions()
        self.Q = {}

    def _generate_all_states(self):
        fields = []
        for x in range(-SIGHT, SIGHT+1):
            for y in range(-SIGHT, SIGHT+1):
                if abs(x)+abs(y) <= SIGHT and (x != 0 and y != 0):
                    fields.append(Field(x,y))


        for f in fields:
            f.player_id = {1, -1}

        totalFields = 24
        permutString = []

        for enemies in range (0, totalFields + 1):
            fieldsLeftFriends = totalFields - enemies
            for friends in range (0, fieldsLeftFriends + 1):
                fieldsLeftNeutral = fieldsLeftFriends - friends
                for neutral in range (0, fieldsLeftNeutral + 1):
                    fieldsLeftBlocked = fieldsLeftNeutral - neutral
                    for blocked in range(0, fieldsLeftBlocked):
                        stateString = 'E'* enemies + 'F' * friends + 'N' * neutral + 'B' * blocked
                        for state in itertools.permutations(stateString):
                            permutString.append(state)
        print(len(permutString))

        fields.append()




    def _actions(self):
        return [["suicide"]]

    def predict(self, robot):
        state = State.formGame(robot)
        action = max([self.Q[(state, a)] for a in self.actions])
        return action

class Robot:
    def act(self, game):
        self.game = game
        return ["guard"]
