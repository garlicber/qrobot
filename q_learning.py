import state as s

REWARD_UNIT = 1


class QLearning:
    DEFAULT_REWARD = 0
    q = {}

    _alpha = 0.5
    _gamma = 0.5

    def __init__(self, alpha=0.1, gamma=0.5):
        self.actions = self._actions()
        self._alpha = alpha
        self._gamma = gamma

    def __sizeof__(self):
        return len(self.q)

    def get_q(self, state, action):
        if (state, action) in self.q:
            return self.q[(state, action)]
        else:
            return self.DEFAULT_REWARD

    def set_q(self, state, action, reward):
        self.q[(state, action)] = reward

    @staticmethod
    def _actions():
        actions = [s.ACTION_SUICIDE]
        for cords in s.MOVE_DIRECTIONS:
            actions.append((s.ACTION_ATTACK, cords))
            actions.append((s.ACTION_MOVE, cords))
        return actions

    def predict(self, state):
        #print state
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
    def map_action(action, loc):
        if action == ACTION_SUICIDE:
            return ["suicide"]

        (abs_x, abs_y) = add_tuple(loc, action[1])
        if action[0] == ACTION_ATTACK:
            return ["attack", (abs_x, abs_y)]
        if action[0] == ACTION_MOVE:
            return ["move", (abs_x, abs_y)]
        print "[error] no mapping for action"
        return "error"

    def reward(self, delta_me, delta, action):
        damage_dealt = 0
        damage_taken = 0

        if action[0] == ACTION_ATTACK:
            attack_loc = action[1]
            for dict in delta:
                if dict["loc_end"] == attack_loc and \
                        delta_me["player_id"] != delta["player_id"]:
                    damage_dealt += 9

        damage_taken = delta_me.hp - delta_me.hp_end

        # If suiccide makes more damage then the lifepoint lost then its a good
        # choice

        return (damage_dealt - damage_taken) * REWARD_UNIT

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
