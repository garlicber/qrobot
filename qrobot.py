SIGHT = 3
HP_LOW = 1
HP_MEDIUM = 2
HP_HIGH = 3

def hp2discrete(hp):
    return HP_HIGH

class Field:
    def __init__(self, x, y, player_id = 0, hp = 0):
        self.x = x
        self.y = y
        self.player_id = player_id
        self.hp = 0


class State:
    def __init__(self, hp, fields):
        self.hp
        self.fields = fields


    @staticmethod
    def fromGame(robot, game):
        # XXX
        return State()


class QTable:
    def __init__(self):
        self.states = self._generate_all_states()
        self.actions = _actions()
        self.Q = {}

    def _generate_all_states(self):
        fields = []
        for x in range(-SIGHT, SIGHT+1):
            for y in range(-SIGHT, SIGHT+1):
                if abs(x)+abs(y) <= SIGHT and (x != 0 and y != 0):
                    fields.append(Field(x,y))


        for f in fields:
            f.player_id = {1, -1}

    def _actions():
        return [["suicide"]]

    def predict(self, robot, game):
        state = State.formGame(robot, game)
        action = max([self.Q(state, a) for a in actions])
        return action