import rgkit.rg as rg
from rgkit.settings import settings

import q_learning

FIELD_NORMAL = 1 << 1
FIELD_FRIEND = 1 << 2
FIELD_SPAWN = 1 << 3
FIELD_ENEMY = 1 << 4
FIELD_OBSTACLE = 1 << 5

ACTION_SUICIDE = 1
ACTION_MOVE = 2
ACTION_ATTACK = 3
ACTION_GUARD = 4

MOVE_DIRECTIONS = [(1, 0), (-1, 0), (0, 1), (0, -1)]


class State:
    OFFSET = settings.robot_hp / 5
    MAX_HP = OFFSET + settings.robot_hp

    # number of block fields on the map for left
    MAP_LEFT_OFFSETS = [6, 4, 2, 2, 1, 1, 0, 0, 0,
                        0, 0, 1, 1, 2, 2, 4, 6]
    assert len(MAP_LEFT_OFFSETS) == 17

    MAP_MAX_X = 17
    MAP_MAX_Y = MAP_MAX_X

    MAP_X_TO_FIELDS = []
    # integral over all x offsets
    for x in xrange(MAP_MAX_X + 1):
        if x == 0:
            line_before = 0
            this_line = 0
        else:
            line_before = MAP_X_TO_FIELDS[x-1]
            this_line = MAP_MAX_X - 2*MAP_LEFT_OFFSETS[x - 1]
        MAP_X_TO_FIELDS.append(this_line + line_before)

    MAP_RIGHT_OFFSETS = [MAP_MAX_X - left for left in MAP_LEFT_OFFSETS]

    TOTAL_FIELDS = MAP_X_TO_FIELDS[-1] + MAP_MAX_Y - MAP_LEFT_OFFSETS[-1] -\
        MAP_RIGHT_OFFSETS[-1]
    assert TOTAL_FIELDS == 225

    ENEMY = 1
    FRIEND = -1

    def __init__(self, robot_loc, fields):
        self.robot_loc = robot_loc
        self.fields = fields

    @staticmethod
    def from_game(game, my_player_id, robot_loc=(9, 9)):
        # my_player
        fields = [0] * State.TOTAL_FIELDS
        for loc, robot in game.robots.items():
            if robot.player_id == my_player_id:
                fields[State._loc_to_field_i(loc)] = \
                    - (robot.hp + State.OFFSET) / State.MAX_HP
            else:
                fields[State._loc_to_field_i(loc)] = \
                    (robot.hp + State.OFFSET) / State.MAX_HP
        return State(robot_loc, tuple(fields))

    @staticmethod
    def _loc_to_field_i(loc):
        x, y = loc
        return State.MAP_X_TO_FIELDS[x-1] + y - State.MAP_LEFT_OFFSETS[x-1] - 1

    def field(self, loc):
        return self.fields[self._loc_to_field_i(loc)]

    def __str__(self):
        state_string = ""
        for x in xrange(State.MAP_MAX_X):
            for y in xrange(State.MAP_MAX_Y):
                if(x < State.MAP_LEFT_OFFSETS[x] or
                        x > State.MAP_RIGHT_OFFSETS[x]):
                    state_string += "[X]"
                    pass
                else:
                    field = self.fields((x, y))

                    if field > 0:
                        state_string += "[E]"
                    elif field < 0:
                        state_string += "[F]"
                    else:  # field == 0
                        state_string += "[ ]"
            state_string += "\n"
        return state_string

    @staticmethod
    def map_action(action, loc):
        if action == ACTION_SUICIDE:
            return ["suicide"]
        (action_code, loc) = action
        if action_code == ACTION_ATTACK:
            return ["attack", loc]
        if action_code == ACTION_MOVE:
            return ["move", loc]

        return "error"
