from ffnet import ffnet, mlgraph


def convert_2_input(state, action):
    return [state] + [action]


class Q_nn:

    num_input = 16
    num_hidden = 16
    num_output = 1

    def __init__(self, dimension):
        self.num_input = self.num_hidden = dimension
        conec = mlgraph((self.num_input, self.num_hidden, self.num_output))
        self.net = ffnet(conec)

    def set_q(self, state, new_q):
        self.net.train_tnc(state, new_q, maxfun=1, messages=1)

    def get_q(self, state):
        return self.net.call(state)

    def mirror_hashmap(self, hashmap,):
        assert type(hashmap) == dict
        input = []
        target = []
        for key, value in hashmap.items():
            input.append(list(key))
            if type(value) == tuple:
                target.append(list(value))
            else:
                target.append([value])
        print target
        print input
        self.net.train_tnc(input, target, maxfun=1000, messages=0)
