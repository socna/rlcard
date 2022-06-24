import rlcard
import torch
import os

ROOT_PATH = os.path.join(rlcard.__path__[0], 'models/pretrained')

env = rlcard.make('demo')
device = torch.device('cpu')

model_path = os.path.join(ROOT_PATH, 'demo_dmc', '{}.pth'.format("0_643200"))
agent = torch.load(model_path, map_location=device)
agent.set_device(device)

env.set_agents([agent])

while (True):
    print(">> Start a new game")
    trajectories, payoffs = env.run(is_training=False)

    print(trajectories, payoffs)

    input("Press any key to continue...")


