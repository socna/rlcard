from argparse import Action
from typing import TYPE_CHECKING

from rlcard.games.dummy.melding import RANK_STR, get_all_melds, get_rank_id, get_suit_id
if TYPE_CHECKING:
    from .game import DummyGame
    from .player import DummyPlayer
from .action import *

import numpy as np

class DummyJudge:

    def __init__(self, game: 'DummyGame') -> None:
        self._game = game

    def  get_legal_actions(self):
        failure_actions = []
        legal_actions  = []

        last_action_id = self._game.get_last_action()
        if last_action_id is None:
            last_action = None
        else:
            (last_action, _) = decode_action(last_action_id)

        current_player = self._game.round.get_player()
        current_hand = current_player.hand
        current_melds = current_player.all_melds

        num_stoke_pile = len(self._game.round.dealer.stock_pile)
        discard_pile = self._game.round.dealer.discard_pile


        if last_action is None or last_action == Action.DISCARD_ACTION:
            #draw
            if num_stoke_pile > 0:
                legal_actions.append(draw_card_action_id)

            #take
            temp_hand = current_hand + discard_pile
            # (run_melds, set_melds) = get_all_melds(temp_hand)
            all_melds = get_all_melds(temp_hand)

            for meld in all_melds:
                arr_index = np.nonzero(np.in1d(discard_pile,meld))[0]
                if len(arr_index) > 0 and len(arr_index) < len(meld):
                    index = np.min(arr_index)
                    take_card = [c for c in discard_pile[index:] if c not in meld]
                    hand_card = [card for card in current_hand if card  not in meld]

                    if len(take_card) + len(hand_card) > 0:
                        rank_str = ",".join([str(c) for c in meld])
                        action_id = ID_2_ACTION.index(rank_str) + take_card_action_id
                        legal_actions.append(action_id)

                        # print(meld, self._game.round._all_melds_depositable_speto)
                        if meld in self._game.round._all_melds_depositable_speto and len(current_melds) > 0:
                            # print("Take card")
                            failure_actions.append(action_id)
                            pass

        if last_action == Action.DRAW_CARD_ACTION or \
            last_action == Action.DEPOSIT_CARD_ACTION or \
            last_action == Action.MELD_CARD_ACTION or \
            last_action == Action.TAKE_CARD_ACTION:

            #discard
            action_ids = [card_id + discard_action_id for card_id in current_hand]

            for (deposit_cards, meld) in self._game.round._dangerous_discard_lv1[current_player.player_id]:
                for action_id in action_ids:
                    card_id = action_id - discard_action_id
                    if card_id in deposit_cards:
                        failure_actions.append(action_id)
                        # print("discard1")
            for action_id in action_ids:
                card_id = action_id - discard_action_id
                if card_id in self._game.round._dangerous_discard_lv2[current_player.player_id]:
                    failure_actions.append(action_id)
                    # print("discard2")

                if card_id in self._game.round._dangerous_discard_lv3[current_player.player_id]:
                    failure_actions.append(action_id)
                    # print("discard3")
            
            legal_actions += action_ids
            
            

                

        if last_action == Action.DRAW_CARD_ACTION or \
            last_action == Action.DEPOSIT_CARD_ACTION or \
            last_action == Action.MELD_CARD_ACTION or \
            last_action == Action.TAKE_CARD_ACTION:
            #meld
            
            if len(current_hand) > 3 and len(current_melds)> 0:
                all_melds = current_player.get_all_melds_in_hand()
                for meld in all_melds:
                    if len(meld) < len(current_hand):
                        rank_str = ",".join([str(c) for c in meld])
                        action_id = ID_2_ACTION.index(rank_str) + meld_card_action_id
                        legal_actions.append(action_id)

                        if meld in self._game.round._all_melds_depositable_speto:
                            failure_actions.append(action_id)
                            # print("meld card")
                            pass

        if last_action == Action.DRAW_CARD_ACTION or \
            last_action == Action.DEPOSIT_CARD_ACTION or \
            last_action == Action.MELD_CARD_ACTION or \
            last_action == Action.TAKE_CARD_ACTION:
            #deposit

            if len(current_hand) > 1 and len(current_melds) > 0:
                for (deposit_cards, meld) in self._game.round.dangerous_discard_lv1[current_player.player_id]:
                    for deposit_card in deposit_cards:
                        ranks  = ",".join([str(c) for c in sorted(meld + [deposit_card], key=lambda x: (get_rank_id(x), get_suit_id(x)))])
                        action_id = ID_2_ACTION.index(ranks) + deposit_card_action_id
                        legal_actions.append(action_id)

                        if deposit_card in self._game.round._dangerous_discard_lv4[current_player.player_id]:
                            failure_actions.append(action_id)
                            # print("deposit")
                        

        if last_action == Action.DEPOSIT_CARD_ACTION  or\
            last_action == Action.MELD_CARD_ACTION or \
            last_action == Action.TAKE_CARD_ACTION:
            
            if len(current_hand) == 1:
                return [knock_action_id + current_hand[0]]

        if  last_action == Action.DISCARD_ACTION:
            if num_stoke_pile == 0:
                return [knock_action_id + 52]

        if len(legal_actions) == 0 and last_action != Action.KNOCK_ACTION:
            print("last_action:", last_action)
            pass
        
       
       
        
        good_actions = [action_id for action_id in legal_actions if action_id not in failure_actions]

        
        
        # good_actions_str = ["{}-{}".format(action_id, get_action_str(action_id))  for action_id in good_actions]
        # failure_actions_str = ["{}-{}".format(action_id, get_action_str(action_id))  for action_id in failure_actions]
        # print(good_actions_str, failure_actions_str)
        if len(good_actions) == 0:
            return legal_actions
        else:
            return good_actions


    def get_payoffs(self):
        payoffs = [0 for _ in range(self._game.get_num_players())]
        for i in range(self._game.get_num_players()):
            player = self._game.round.get_player(i)
            payoff = self.get_payoff(player)
            payoffs[i] = payoff

        # _payoffs =  payoffs.copy()

        # for i in range(len(_payoffs)):
        #     payoffs[i] = sum([v for k ,v in enumerate(_payoffs) if k != i])

        return payoffs

    def get_payoff(self, player: 'DummyPlayer'):
        deadwood_score =  -sum([_get_deadwood_value(card, self._game.round.dealer.speto_cards) for card in player.hand])
        card_score = sum([_get_deadwood_value(card, self._game.round.dealer.speto_cards) for card in player.score_cards])
        if card_score == 0:
            deadwood_score *= 2
        tran_score = sum(player.transactions)
        return (deadwood_score + card_score + tran_score) / 500

rank_to_deadwood_value = {"A": 15, "2": 5, "3": 5, "4": 5, "5": 5, "6": 5, "7": 5, "8": 5, "9": 5,
                          "T": 10, "J": 10, "Q": 10, "K": 10}

def _get_deadwood_value(card, speto_cards):
    rank_id = get_rank_id(card)
    deadwood_value = rank_to_deadwood_value.get(RANK_STR[rank_id], 10)  # default to 10 is key does not exist
    if card in speto_cards:
        deadwood_value  = deadwood_value + 50
    return deadwood_value