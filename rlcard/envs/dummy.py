from typing import List
import numpy as np
from collections import OrderedDict

from rlcard.envs import Env
from rlcard.games.dummy.action import ID_2_ACTION
from rlcard.games.dummy.game import DummyGame as Game

DEFAULT_GAME_CONFIG = {
        'game_num_players': 2,
        }

class DummyEnv(Env):
    ''' Dummy Environment
    '''

    def __init__(self, config):
        ''' Initialize the Dummy environment
        '''
        self.name = 'dummy'
        self.default_game_config = DEFAULT_GAME_CONFIG
        self.game = Game()
        super().__init__(config)

        self.state_shape = [[self._get_state_shape_size()] for _ in range(self.num_players)]
        self.action_shape = [None for _ in range(self.num_players)]


    def _get_state_shape_size(self):
        if self.num_players == 2:
            return 935
        elif self.num_players == 3:
            return 1564
        elif self.num_players == 4:
            return 1985

    def _extract_state(self, state):
        ''' Encode state

        Args:
            state (dict): dict of original state

        Returns:
            numpy array: 
                        num_stoke_pile: Số bài trên lọc (29)
                        discard_pile:
                        speto_cards:

                        dangerous_cards_lv1: đánh ra bài có thể bị ăn speto
                        dangerous_cards_lv2: đánh ra bài có thẻ gửi
                        dangerous_cards_lv3: đánh ra bài tạo thành phỏm

                        current_hand:
                        current_melds:
                        current_known:

                        up_opponent_hand_left
                        up_opponent_known
                        up_opponent_melds


                        down__opponent_hand_left
                        down_opponent_known
                        down_opponent_melds
        '''

        legal_action = self._get_legal_actions()

        # if self.game.is_over():
        #     obs =  np.zeros(self._get_state_shape_size(), dtype=int)
        
        #     extracted_state = {'obs': obs, 'legal_actions': legal_action}
        #     extracted_state['raw_legal_actions'] = list(legal_action.keys())
        #     extracted_state['raw_obs'] = state
        # else:

        num_stoke_pile  = state['num_stoke_pile']
        discard_pile = state['discard_pile']
        # speto_cards = state['speto_cards']
        known_cards = state['known_cards']

        # dangerous_lv1 =  state['dangerous_lv1'] 
        # dangerous_lv2 = state['dangerous_lv2'] 
        # dangerous_lv3 = state['dangerous_lv3'] 
        # dangerous_lv4 = state['dangerous_lv4'] 
        # melds_depositable_speto = state['melds_depositable_speto']


        current_hand = state['current_hand']
        current_meld = state['current_meld']

        up_opponent_known = state['up_opponent_known']
        up_opponent_hand_left = state['up_opponent_hand_left']
        up_opponent_melds  = state['up_opponent_melds']

        num_stoke_pile_rep = _get_one_hot_array(num_stoke_pile, 29)
        discard_pile_rep = _encode_cards(discard_pile)
        known_cards_rep = _encode_cards(known_cards)

        # dangerous_lv1_rep = _encode_cards(dangerous_lv1)
        # dangerous_lv2_rep = _encode_cards(dangerous_lv2)
        # dangerous_lv3_rep = _encode_cards(dangerous_lv3)
        # dangerous_lv4_rep = _encode_cards(dangerous_lv4)
        # melds_depositable_speto_rep = _encode_actions(melds_depositable_speto, self.num_actions)

        current_hand_rep = _encode_cards(current_hand)
        current_meld_rep = _encode_melds(current_meld)

        up_opponent_known_rep = _encode_cards(up_opponent_known)
        up_opponent_hand_left_rep = _get_one_hot_array(up_opponent_hand_left, 40)
        up_opponent_melds_rep = _encode_melds(up_opponent_melds)

     
        obs = np.concatenate((
            num_stoke_pile_rep,
            discard_pile_rep,
            known_cards_rep,
            # dangerous_lv1_rep,
            # dangerous_lv2_rep,
            # dangerous_lv3_rep,
            # dangerous_lv4_rep,
            # melds_depositable_speto_rep,
            current_hand_rep,
            current_meld_rep,
            up_opponent_known_rep,
            up_opponent_hand_left_rep,
            up_opponent_melds_rep
        ))


        extracted_state = OrderedDict({'obs': obs, 'legal_actions': legal_action})
        extracted_state['raw_obs'] = state
        extracted_state['raw_legal_actions'] = list(legal_action.keys())
        return extracted_state


    def _decode_action(self, action_id: int):
        return action_id

    def _get_legal_actions(self):
        ''' Get all legal actions for current state

        Returns:
            legal_actions (list): a list of legal actions' id
        '''
        legal_actions = self.game.judge.get_legal_actions()
        legal_actions_ids =  {action: None for action in legal_actions}
        return OrderedDict(legal_actions_ids)

    def get_payoffs(self):

        is_game_complete = False
        if self.game.round:
            if self.game.is_over():
                is_game_complete = True
        payoffs = [0 for _ in range(self.num_players)] if not is_game_complete else self.game.judge.get_payoffs()
        return np.array(payoffs)

def _get_one_hot_array(num_left_cards, max_num_cards):
    one_hot = np.zeros(max_num_cards, dtype=np.int8)

    if num_left_cards >= 1:
        one_hot[num_left_cards - 1] = 1
    return one_hot

def _encode_cards(cards) -> np.ndarray:
    plane = np.zeros(52, dtype=int)
    for card_id in cards:
        plane[card_id] = 1
    return plane

def _encode_melds(melds: List[int]):

    plane = np.zeros(329, dtype=int)
    for meld in melds:
        meld = sorted(meld)
        meld_id = ID_2_ACTION.index(",".join([str(c) for c in meld]))

        plane[meld_id] = 1

    return plane

def _encode_actions(actions: list, num_actions: int):
    plane = np.zeros(num_actions, dtype=int)
    for action_id in actions:
        plane[action_id] = 1

    return plane