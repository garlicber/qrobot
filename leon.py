import random
import rg

class Around:
    def __init__(self, robot, game):
        self.robot = robot
        self.game = game
        self.locs = rg.locs_around(robot.location, filter_out=('invalid', 'obstacle'))
        self.robots = {loc: game.robots[loc] for loc in self.locs if loc in game.robots}
        self.free_locs = [l for l in self.locs if l not in self.robots]
        self.opponents = {loc: r for loc,r in self.robots.items() if r.player_id != robot.player_id}
        self.friends = {loc: r for loc,r in self.robots.items() if r.player_id == robot.player_id}

def robots_hp(robots):
        return sum([r.hp for l,r in robots.items()])

class Robot:
    def __init__(self):
        self.last_fields = []
        self.last_actions = []

    def next_loc(self):
        possible_locs = [loc for loc in self.around.free_locs if loc not in self.last_fields]
        if not possible_locs:
            possible_locs = self.around.locs

        loc = random.choice(possible_locs)
        self.last_fields.append(loc)
        return loc

    def next_action(self, game):
        if self.hp + 15 < 15*len(self.around.opponents):
            return ['suicide']

        if len(self.around.opponents) > 1:
            (location, opponent) = random.choice(self.around.opponents.items())
            return ['attack', location];

        if len(self.around.friends) >= 2:
            return ['guard']

        return ['move', self.next_loc()]

    def act(self, game):
        around = Around(self, game)
        self.around = around
        action = self.next_action(game)
        self.last_actions.append(action)
        return action
