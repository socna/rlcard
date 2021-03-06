import unittest
import numpy as np

import rlcard
from rlcard.agents.random_agent import RandomAgent

class TestDummyEnv(unittest.TestCase):
    def test_run(self):
        env = rlcard.make('dummy')
        env.set_agents([RandomAgent(env.num_actions) for _ in range(env.num_players)])
        print(env.num_players, env.num_actions)
        print(env.state_shape) # [[2]]
        print(env.action_shape) # [None]
        trajectories, payoffs = env.run(is_training=False)

        print(payoffs)
if __name__ == '__main__':
    unittest.main()