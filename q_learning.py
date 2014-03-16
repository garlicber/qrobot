import random
import sys
import state as s
import q_hash


class QLearning:
    DEFAULT_REWARD = 0

    _alpha = 0.5
    _gamma = 0.5

    def __init__(self, alpha=0.1, gamma=0.5):
        self.actions = self._actions()
        self._alpha = alpha
        self._gamma = gamma
        self.q = q_hash.Q_hash()

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
        action = max(self.actions, key=lambda a: self.q.get_q(state, a))
        return action

    def find_best_action(self, state):
        max_q = -sys.maxint - 1
        action_list = []
        for action in self.actions:
            current_q = self.q.get_q(state, a)
            if max_q == current_q:
                action_list.append(action)
            elif max_q < current_q:
                action_list = [action]
                max_q = current_q
        assert len(action_list) > 0
        if len(action_list) == 1:
            return action
        return random.choice(action_list)

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
