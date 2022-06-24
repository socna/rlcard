from collections import OrderedDict
from rlcard.envs import Env
import numpy as np
import random

class Game:
    def __init__(self) -> None:
        self.num_players = 1
        self.np_random = np.random.RandomState()

    def init_game(self):
        current_player_id = 0
        self.turn = 0
        self.nums_played = set()
        self._is_over  = False

        self.target = np.random.choice([i for i in range(0, 100)])


        state = self.get_state(player_id=current_player_id)
        return state, current_player_id

    def get_state(self, player_id: int):
        state = {}
        state['turn'] = self.turn
        state['nums_played'] = list(self.nums_played)
        state['target'] = self.target
        return state

    def get_num_actions(self):
        return 100

    def get_num_players(self):
        return self.num_players

    def step(self, action_id: int):
        if action_id == self.target or self.turn == 100:
            self._is_over = True
        else:
            self.nums_played.add(action_id)
            self.turn = self.turn + 1

        # print(action_id, self.turn, self.nums_played)

        next_player_id = 0
        next_state = self.get_state(player_id=next_player_id)
        return next_state, next_player_id 

    def is_over(self):
        return self._is_over

    def get_player_id(self):
        return 0

def get_one_hot_array(num_left_cards, max_num_cards):
    one_hot = np.zeros(max_num_cards, dtype=np.int8)

    if num_left_cards >= 1:
        one_hot[num_left_cards - 1] = 1
    return one_hot

def encode_cards(cards) -> np.ndarray:
    plane = np.zeros(100, dtype=int)
    for card_id in cards:
        plane[card_id] = 1
    return plane



class DemoEnv(Env):
    def __init__(self, config):

        self.name = "demo"
        self.game = Game()
        super().__init__(config=config)

        self.state_shape = [[100] for _ in range(self.num_players)]
        self.action_shape = [None for _ in range(self.num_players)]

    def get_payoffs(self):
        is_game_complete = False
        if self.game.is_over():
            is_game_complete = True
        payoffs = [0 for _ in range(self.num_players)] if not is_game_complete else [(100 - self.game.turn) / 100]
        return np.array(payoffs)

    def _decode_action(self, action_id):
        return action_id

    def _extract_state(self, state):

        # if self.game.is_over():
        #     obs = np.array([get_one_hot_array(0, 100) for _ in range(2)])
        #     extracted_state = {'obs': obs, 'legal_actions': self._get_legal_actions()}
        #     extracted_state['raw_legal_actions'] = list(self._get_legal_actions().keys())
        #     extracted_state['raw_obs'] = state
        # else:
        turn  = state['turn']
        nums_played = state['nums_played']
        # turn_rep = get_one_hot_array(turn, 100)
        nums_played_rep = encode_cards(nums_played)

        obs = np.array([
            # turn_rep,
            nums_played_rep
        ])

        extracted_state = {'obs': obs, 'legal_actions': self._get_legal_actions()}
        extracted_state['raw_obs'] = state
        extracted_state['raw_legal_actions'] = list(self._get_legal_actions().keys())

        return extracted_state

    def _get_legal_actions(self):
        ''' Get all legal actions for current state

        Returns:
            legal_actions (list): a list of legal actions' id
        '''
        legal_actions = [i for i in range(100)]

        legal_actions_ids =  {action: None for action in legal_actions}
        return OrderedDict(legal_actions_ids)