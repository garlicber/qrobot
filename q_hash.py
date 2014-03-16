import collections


class Q_hash:
    hash_matrix = {}

    def __init__(self):
        self.hash_matrix = collections.defaultdict(float)

    def set_q(self, state, action, new_q):
        self.hash_matrix[(state, action)] = new_q

    def get_q(self, state, action):
        return self.hash_matrix[(state, action)]

    def __eq__(self, other):
        return (self.hash_matrix == other.hash_matrix and
                len(self.hash_matrix) == len(other.hash_matrix))
