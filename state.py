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

MOVE_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]

def hp2discrete(hp):
    if 50 > hp > 40:
        return HP_HIGH
    if 40 > hp > 15:
        return HP_MEDIUM
    else:
        return HP_LOW


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