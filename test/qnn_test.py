import unittest
from q_nn import Q_nn

__author__ = 'jakob'


class ann_test(unittest.TestCase):
    def xor_test(self):
        nn = Q_nn(2)
        hashmap = {(0., 0.): 0.,
                   (0., 1.): 0.,
                   (1., 0.): 0.,
                   (1., 1.): 1., }

        nn.mirror_hashmap(hashmap)
        test_input = [[0., 0.], [0., 1.], [1., 0.], [1., 1.]]
        test_target = [0., 0., 0., 1.]
        epsilon = 0.2
        for x in range(len(test_input)):
            print nn.get_q(test_input[x])
            assert test_target[x] - epsilon \
                < nn.get_q(test_input[x]) \
                < test_target[x] + epsilon
