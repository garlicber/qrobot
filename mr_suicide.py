import rg


class Robot():
    def __init__(self):
        self.counter = 0
        self.q = Q_hash()

    def act(self, game):
        close_enemy = self.enemy_close(game)
        self.counter += 1
        hash_value = self.q.get_q('a', '1')
        self.q.set_q('a', '1', hash_value + 1)
        print self.q.get_q('a', '1')
        print(self.counter)

        if self.suicide_reason():
            return ['suicide']

        if close_enemy != 'none':
            return ['attack', close_enemy]

        if self.robot_on_position(game, self.add_to_defense()) != 'ally' \
                and self.location != rg.CENTER_POINT:
            return ['move', rg.toward(self.location, rg.CENTER_POINT)]
        return ['guard']

    def look_arounds(self):
        for loc in rg.locs_around(self.location):
            (rg.loc_types(loc))

    def enemy_close(self, game):
        for loc, bot in game.robots.iteritems():
            if bot.player_id != self.player_id:
                if rg.dist(loc, self.location) <= 1:
                    return loc
        return 'none'

    def add_to_defense(self):
        rg.toward(self.location, rg.CENTER_POINT)

    def robot_on_position(self, game, loc):
        for x, robot in game.robots.iteritems():
            if robot.location == loc:
                if robot.player_id == self.player_id:
                    return 'ally'
                if robot.player_id != self.player_id:
                    return 'enemy'
        return 'empty'

    def suicide_reason(self):
        if self.hp <= 10:
            return True
        else:
            return False


class Q_hash:
    hash_matrix = {}

    def __init__(self):
        self.hash_matrix = collections.defaultdict(float)

    def set_q(self, state, action, new_q):
        self.hash_matrix[(state, action)] = new_q

    def get_q(self, state, action):
        return self.hash_matrix[(state, action)]
