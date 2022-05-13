from rlcard.games.dummy.action import get_action_str, ID_2_ACTION
from rlcard.games.dummy.game import DummyGame as Game
import unittest
import numpy as np

from rlcard.envs.dummy import DEFAULT_GAME_CONFIG
from rlcard.games.dummy.melding import RANK_STR, SUIT_STR, find_all_melds_depositable_by_speto, find_all_relate_speto_meld, get_all_melds, get_card, get_rank_id, get_suit_id
from  itertools import permutations
from rlcard.games.dummy.player import DummyPlayer as Player

from collections import OrderedDict

from  heapq import nlargest

from rlcard.games.dummy.action import take_card_action_id

import os
import rlcard
import torch


class TestDummyGame(unittest.TestCase):
    def test_get_num_players(self):
        game = Game()
        game.configure(DEFAULT_GAME_CONFIG)
        num_players = game.get_num_players()
        self.assertEqual(num_players, 2)

    def test_init_game(self):
        game = Game()
        game.configure(DEFAULT_GAME_CONFIG)
        state, current_player_id = game.init_game()
        self.assertEqual(current_player_id, 0)

    def test_calculate_dangerous_cards(self):
        # 36,37,38,39
        game = Game()
        game.configure(DEFAULT_GAME_CONFIG)

        game.init_game()

        curr_player = game.round.get_player()
        curr_player._hand = [39,38,20,9,42,35,30,28]
        curr_player.add_melds([29, 30 ,31])
        curr_player.add_melds([6, 7, 8])

        game.round.dealer.set_discard_pile([19,43,18,48])
        game.round.dealer._speto_cards = [13,10,27]

        curr_player.calculate_melds_in_hand()

        opponent = game.round.get_player(1)
        opponent.add_melds([4,2,3])
        opponent.add_melds([13,26,0])

        # opponent.score_cards.append(get_card("4", "S"))
        # opponent.score_cards.append(get_card("4", "C"))
        # opponent.score_cards.append(get_card("4", "H"))

        game.round._calculate_dangerous_discard_lv1(curr_player)
        game.round._calculate_dangerous_discard_lv2(curr_player, game.round.dealer.speto_cards)
        game.round._calculate_dangerous_discard_lv3(curr_player, game.round.dealer.discard_pile)


        # print(game.round.dangerous_discard_lv1)
        # print(game.round.dangerous_discard_lv2)
        # print(game.round.dangerous_discard_lv3)
        # print(game.round.dangerous_discard_lv4)

        game._actions.append(0)
        legal_actions = game.judge.get_legal_actions()

        for a in legal_actions:
            print(a, get_action_str(a))

        game.step(271)

    def _1test_proceed_game(self):
        game = Game()
        game.configure(DEFAULT_GAME_CONFIG)
        game.init_game()
        while not game.is_over():
            legal_actions = game.judge.get_legal_actions()

            action = np.random.choice(legal_actions)
            state, _ = game.step(action)

    def _1test_get_all_melds(self):
        cards = [get_card("K", "C"),get_card("A", "C"),get_card("2", "D")]
        self.assertEqual(get_all_melds(cards), [])
        # print(find_all_relate_speto_meld([10, 13, 30]))
        # speto_cards = [10, 13]

    def _test_play_failure(self):
        
        #meld 
        game = Game()
        game.configure(DEFAULT_GAME_CONFIG)
        game.init_game()

        curr_player = game.round.get_player()
        curr_player.add_melds([3,4,5])
        game.round.dealer._speto_cards = [10,13, 40]
        game.round.dealer.set_discard_pile([ 6, 8])
        curr_player._hand = [27, 14, 10, 15, 1]

        curr_player.calculate_melds_in_hand()

        game.round._calculate_dangerous_discard_lv1(curr_player)
        game.round._calculate_dangerous_discard_lv2(curr_player, game.round.dealer.speto_cards)
        game.round._calculate_dangerous_discard_lv3(curr_player, game.round.dealer.speto_cards)

        game._actions.append(0)
        legal_actions = game.judge.get_legal_actions()

        self.assertEqual(legal_actions, [1015, 1002, 998, 1003, 989, 699])
        # print(["{}:{}".format(a, get_action_str(a)) for a in legal_actions])

        state, id = game.step(699)

        self.assertEqual(id, 0)

        #take

        game = Game()
        game.configure(DEFAULT_GAME_CONFIG)
        game.init_game()

        curr_player = game.round.get_player()
        game.round.dealer._speto_cards = [40, 10, 13]
        game.round.dealer.set_discard_pile([41, 40, 6, 8])
        curr_player._hand = [7, 9, 20, 21, 42, 43]

        curr_player.calculate_melds_in_hand()

        game.round._calculate_dangerous_discard_lv1(curr_player)
        game.round._calculate_dangerous_discard_lv2(curr_player, game.round.dealer.speto_cards)
        game.round._calculate_dangerous_discard_lv3(curr_player, game.round.dealer.speto_cards)

        # game._actions.append(0)
        legal_actions = game.judge.get_legal_actions()

        # print(["{}:{}".format(a, get_action_str(a)) for a in legal_actions])
        self.assertEqual(legal_actions, [0, 599, 600, 619, 469, 470, 506])

        state, id = game.step(506)
        self.assertEqual(id, 0)

        
        #discard 
        game = Game()
        game.configure(DEFAULT_GAME_CONFIG)
        game.init_game()

        curr_player = game.round.get_player()
        game.round.dealer._speto_cards = [40, 10, 13]
        
        game.round.dealer.set_discard_pile([41, 40, 8])
        curr_player._hand = [6, 7, 9, 20, 21, 42, 43]
        curr_player.add_melds([3,4,5])

        curr_player.calculate_melds_in_hand()

        game.round._calculate_dangerous_discard_lv1(curr_player)
        game.round._calculate_dangerous_discard_lv2(curr_player, game.round.dealer.speto_cards)
        game.round._calculate_dangerous_discard_lv3(curr_player, game.round.dealer.speto_cards)

        game._actions.append(0)
        legal_actions = game.judge.get_legal_actions()

        # print(["{}:{}".format(a, get_action_str(a)) for a in legal_actions])

        state, id = game.step(994)
        self.assertEqual(id, 1)

        
        game = Game()
        game.configure(DEFAULT_GAME_CONFIG)
        game.init_game()

        curr_player = game.round.get_player()
        game.round.dealer._speto_cards = [10, 13]
        
        game.round.dealer.set_discard_pile([41, 8, 43])
        curr_player._hand = [20, 21, 42]
        curr_player.add_melds([3,4,5])

        curr_player.calculate_melds_in_hand()

        game.round._calculate_dangerous_discard_lv1(curr_player)
        game.round._calculate_dangerous_discard_lv2(curr_player, game.round.dealer.speto_cards)
        game.round._calculate_dangerous_discard_lv3(curr_player, game.round.dealer.discard_pile)

        game._actions.append(0)
        legal_actions = game.judge.get_legal_actions()

        # print(["{}:{}".format(a, get_action_str(a)) for a in legal_actions])

        state, id = game.step(1030)
        # self.assertEqual(id, 1)

    def _1test_model(self):

        game = Game()

        state, current_player_id =  game.init_game()

        curr_player = game.round.get_player()
        curr_player._hand = [39,38,20,12,42,35,30,11]
        curr_player.add_melds([1,14,27,40])
        curr_player.add_melds([8,21,34])
        curr_player.add_melds([6,5,7])
        curr_player.add_melds([15,28,41])

        curr_player._known_cards = [15,8,42,30]

        game.round.dealer.set_discard_pile([16,19,43,18,48])
        game.round.dealer._speto_cards = [13,10,27]
        game.round.dealer._stock_pile = game.round.dealer.stock_pile[:15]


        opponent = game.round.get_player(1)
        opponent.add_melds([4,2,3])
        opponent.add_melds([13,26,0])
        opponent._hand = [1,1,1,1,1]

        game._actions.append(0)


        curr_player.calculate_melds_in_hand()

        game.round._calculate_dangerous_discard_lv1(curr_player)
        game.round._calculate_dangerous_discard_lv2(curr_player, game.round.dealer.speto_cards)
        game.round._calculate_dangerous_discard_lv3(curr_player, game.round.dealer.discard_pile)

        '''
        game  = Game()
        state, current_player_id =  game.init_game()

        current_player = game.round.get_player(current_player_id)
        opponent = game.round.get_player((current_player_id + 1) % 2)

        game.round.dealer._stock_pile = game.round.dealer.stock_pile[:23]
        game.round.dealer._speto_cards = [10, 13, 39]
        game.round.dealer._discard_pile = [39, 28]


        current_player._known_cards = [17, 43, 50]

        current_player._hand = [0,16,8,9,47,19,24,17,43,50]
        current_player.calculate_melds_in_hand()

        current_player.add_melds([5,18,44])
        current_player.add_melds([13,15,14])

        opponent._hand = [1,1,1,1,1,1,1,1,1,1,1]
        opponent._known_cards = []

        game._actions.append(take_card_action_id - 100)

        game.round._calculate_dangerous_discard_lv1(current_player)
        game.round._calculate_dangerous_discard_lv2(current_player, game.round.dealer.speto_cards)
        game.round._calculate_dangerous_discard_lv3(current_player, game.round.dealer.discard_pile)

        '''

        state = game.get_state(current_player_id)
        
        state['actions'] = game.judge.get_legal_actions()
        state = _extract_state(state)

        ROOT_PATH = os.path.join(rlcard.__path__[0], 'models/pretrained')
        device = torch.device('cpu')



        model_path = os.path.join(ROOT_PATH, 'dummy_dmc', '{}.pth'.format("1_337676800"))
        agent = torch.load(model_path, map_location=device)
        agent.set_device(device)
        action, info = agent.eval_step(state)
       

        actions = nlargest(30, info['values'], key=info['values'].get)

        print(info)
        print(action,get_action_str(action))

        game.step(1008)





def _extract_state(state):
    
    legal_action = _get_legal_actions(state['actions'])
    num_stoke_pile  = state['num_stoke_pile']
    discard_pile = state['discard_pile']
    speto_cards = state['speto_cards']
    known_cards = state['known_cards']

    dangerous_lv1 =  state['dangerous_lv1'] 
    dangerous_lv2 = state['dangerous_lv2'] 
    dangerous_lv3 = state['dangerous_lv3'] 


    current_hand = state['current_hand']
    current_meld = state['current_meld']

    up_opponent_known = state['up_opponent_known']
    up_opponent_hand_left = state['up_opponent_hand_left']
    up_opponent_melds  = state['up_opponent_melds']

    num_stoke_pile_rep = _get_one_hot_array(num_stoke_pile, 29)
    discard_pile_rep = _encode_cards(discard_pile)
    known_cards_rep = _encode_cards(known_cards)

    dangerous_lv1_rep = _encode_cards(dangerous_lv1)
    dangerous_lv2_rep = _encode_cards(dangerous_lv2)
    dangerous_lv3_rep = _encode_cards(dangerous_lv3)

    current_hand_rep = _encode_cards(current_hand)
    current_meld_rep = _encode_melds(current_meld)

    up_opponent_known_rep = _encode_cards(up_opponent_known)
    up_opponent_hand_left_rep = _get_one_hot_array(up_opponent_hand_left, 40)
    up_opponent_melds_rep = _encode_melds(up_opponent_melds)

    
    obs = np.concatenate((
        num_stoke_pile_rep,
        discard_pile_rep,
        known_cards_rep,
        dangerous_lv1_rep,
        dangerous_lv2_rep,
        dangerous_lv3_rep,
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

def _get_legal_actions(legal_actions):
    ''' Get all legal actions for current state

    Returns:
        legal_actions (list): a list of legal actions' id
    '''
    legal_actions_ids =  {action: None for action in legal_actions}
    return OrderedDict(legal_actions_ids)

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

def _encode_melds(melds: list):

    plane = np.zeros(329, dtype=int)
    for meld in melds:
        meld = sorted(meld)
        meld_id = ID_2_ACTION.index(",".join([str(c) for c in meld]))

        plane[meld_id] = 1

    return plane

            
if __name__ == '__main__':
    unittest.main()


