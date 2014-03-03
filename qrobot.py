import itertools

SIGHT = 3
HP_LOW = 1
HP_MEDIUM = 2
HP_HIGH = 3

def hp2discrete(hp):
    return HP_HIGH

class Field:
    def __init__(self, x, y, player_id = 0, hp = 0, type):
        self.player_id = player_id
        self.hp = 0
        self.type = type


class State:
    def __init__(self, hp, fields):
        self.hp
        self.fields = fields
        # fields = {(x,y) = Field


    @staticmethod
    def fromGame(robot, game):
        # XXX
        return State()

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




    def _actions():
        return [["suicide"]]

    def predict(self, robot, game):
        state = State.formGame(robot, game)
        action = max([self.Q(state, a) for a in actions])
        return action

