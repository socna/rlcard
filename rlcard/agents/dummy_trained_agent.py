import rlcard
import os
import torch

class DummyAgent(object):
    def __init__(self, num_actions):
        ''' Initilize the human agent

        Args:
            num_actions (int): the size of the output action space
        '''
        self.use_raw = True
        self.num_actions = num_actions

    @staticmethod
    def step(state, ):


        ROOT_PATH = os.path.join(rlcard.__path__[0], 'models/pretrained')
        device = torch.device('cpu')

        model_path = os.path.join(ROOT_PATH, 'dummy_dmc', '{}_693344000.pth'.format(1))
        agent = torch.load(model_path, map_location=device)
        agent.set_device(device)
        action_id, _ = agent.eval_step(state)
        

        return action_id

    def eval_step(self, state):
        ''' Predict the action given the current state for evaluation. The same to step here.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
        '''
        return self.step(state), {}