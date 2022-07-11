import rlcard
import torch
import os
from rlcard.agents.human_agents.human_agent import HumanAgent


ROOT_PATH = os.path.join(rlcard.__path__[0], 'models/pretrained')


env = rlcard.make('dummy')
device = torch.device('cpu')

model_path = os.path.join(ROOT_PATH, 'dummy_dmc', '{}.pth'.format("1_802172800"))
agent = torch.load(model_path, map_location=device)
agent.set_device(device)




human_agent_0 = HumanAgent(env.num_actions, 0)

human_agent_1 = HumanAgent(env.num_actions, 1)

env.set_agents([human_agent_0, agent])

while (True):
    print(">> Start a new game")
    trajectories, payoffs = env.run(is_training=False)

    print(payoffs)

    input("Press any key to continue...")