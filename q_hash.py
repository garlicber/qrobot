import collections


class Q_hash:
    hash_matrix = {}

    def __init__(self):
        self.hash_matrix = collections.defaultdict(float)

    def set_q(self, state, action, new_q):
        self.hash_matrix[(state, action)] = new_q

    def get_q(self, state, action):
        return self.hash_matrix[(state, action)]
