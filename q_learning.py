import state as s
import q_hash


class QLearning:
    DEFAULT_REWARD = 0
    q = q_hash.Q_hash()

    _alpha = 0.5
    _gamma = 0.5

    def __init__(self, alpha=0.1, gamma=0.5):
        self.actions = self._actions()
        self._alpha = alpha
        self._gamma = gamma

    def __sizeof__(self):
        return len(self.q)

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
        old_q = self.q.get_q(state, action)
        optimal_future_value = max([self.q.get_q(new_state, a)
                                    for a in self.actions])
        q = old_q + self._alpha * \
            (reward + self._gamma * optimal_future_value - old_q)
        self.q.set_q(state, action, q)

    @staticmethod
    def map_action(action, loc):
        if action == s.ACTION_SUICIDE:
            return ["suicide"]

        (abs_x, abs_y) = s.add_tuple(loc, action[1])
        if action[0] == s.ACTION_ATTACK:
            return ["attack", (abs_x, abs_y)]
        if action[0] == s.ACTION_MOVE:
            return ["move", (abs_x, abs_y)]
        print "[error] no mapping for action"
        return "error"

    def map_location(self, absolute_loc, relative_loc):
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
