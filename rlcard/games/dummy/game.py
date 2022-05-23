import numpy as np

from rlcard.games.dummy.melding import get_card_str, meld_2_str
from .round import DummyRound as Round
from .action import *
from .judge import DummyJudge as Judge
class DummyGame:

    _round: Round
    def __init__(self, allow_step_back=False):
        ''' Initialize the class Blackjack Game
        '''
        self._allow_step_back = allow_step_back
        self._np_random = np.random.RandomState()
        self._judge = Judge(game= self)

        self.num_players = 2

    def configure(self, game_config):
        ''' Specifiy some game specific parameters, such as number of players
        '''
        self.num_players = game_config['game_num_players']

    def init_game(self):
        dealer_id = 0
        self._actions = []
        self._round = Round(dealer_id, self.num_players, self._np_random)
        
        #chia bai
        num_hand_cards = 11 if self.num_players == 2 else 9 if self.num_players == 3 else 7
        for i in range(self.num_players):
            self._round.dealer.deal_cards(self._round.get_player(i), num_hand_cards)


        #Lật cây bài đầu
        self._round.dealer.deal_first_card()


        current_player_id = self._round.current_player_id
        state = self.get_state(player_id=current_player_id)
        return state, current_player_id

    def get_num_players(self) -> int:
        return self.num_players

    def get_num_actions(self):
        return 1093
        
    def get_player_id(self):
        return self._round.current_player_id

    def is_over(self):
        return self._round.is_over

        
    def get_state(self, player_id: int):
        player = self._round.get_player(player_id=player_id)
        up_opponent_id =  (player_id + 1) % self.num_players
        up_opponent = self.round.get_player(up_opponent_id)


        state = {}
        state['player_id'] = player_id
        state['last_action'] = self.get_last_action()
        state['num_stoke_pile'] = len(self._round.dealer.stock_pile)
        state['discard_pile'] = self._round.dealer.discard_pile
        state['speto_cards'] = self._round.dealer.speto_cards
        state['is_over'] = self._round.is_over
        

        dangerous_lv1 = set()
        for (cards, _) in self.round.dangerous_discard_lv1[player.player_id]:
            dangerous_lv1.update(cards)
        state['dangerous_lv1'] = list(dangerous_lv1)
        state['dangerous_lv2'] = self.round.dangerous_discard_lv2[player.player_id]
        state['dangerous_lv3'] = self.round.dangerous_discard_lv3[player.player_id]
        state['dangerous_lv4'] = self.round.dangerous_discard_lv4[player.player_id]
        # state['melds_depositable_speto'] = [meld for meld in self.round._all_melds_depositable_speto]

        #take
        take_ids = [ID_2_ACTION.index(",".join([str(c) for c in meld])) + take_card_action_id  for meld in self.round._all_melds_depositable_speto]
        meld_ids = [ID_2_ACTION.index(",".join([str(c) for c in meld])) + meld_card_action_id  for meld in self.round._all_melds_depositable_speto]
        state['melds_depositable_speto'] = take_ids + meld_ids


        state['current_hand'] = player.hand
        state['current_meld'] = player.all_melds
        state['known_cards'] =  player.known_cards #[c for p in self.round.all_players for c in p.known_cards]

        state['up_opponent_hand'] = up_opponent.hand # Sự dụng để simulator
        state['trans'] = [player.transactions for player in self.round.all_players]
        
        state['up_opponent_known'] = up_opponent.known_cards
        state['up_opponent_hand_left'] = len(up_opponent.hand)
        state['up_opponent_melds'] = up_opponent.all_melds





        return state


    def step(self, action_id): 
        player  = self._round.get_player()
        (action, rank_id) = decode_action(action_id)


        if action == Action.DRAW_CARD_ACTION:
            self._round.draw_card()
        elif action == Action.DEPOSIT_CARD_ACTION:
            self._round.deposit_card(rank_id)
        elif action == Action.MELD_CARD_ACTION:
            self._round.meld_card( rank_id)
        elif action == Action.TAKE_CARD_ACTION:
            self._round.take_card( rank_id)
        elif action == Action.DISCARD_ACTION:
            self._round.discard(rank_id)

        elif action == Action.KNOCK_ACTION:
            self._round.knock(rank_id)
       
        else:
            raise Exception('Unknown step action={}'.format(action_id))

        self._actions.append(action_id)

        # print("uid: {uid}, melds: {meld}, action: {action}, hand: {hand}, discard_pile: {discard_pile}, stoke_pile: {stock}, know_card= {know_card}".format(
        #     uid=player.player_id,
        #     meld=  ",".join([meld_2_str(meld) for meld in player.all_melds]), 
        #     action= "None" if self.get_last_action() == None else get_action_str(self.get_last_action()), 
        #     hand= ",".join([get_card_str(c) for c in player.hand]), 
        #     discard_pile=",".join([get_card_str(c) for c in self.round.dealer.discard_pile]), 
        #     stock=len(self.round.dealer.stock_pile), 
        #     know_card = ",".join([get_card_str(c) for c in player.known_cards])
        #     ))

        next_player_id = self._round.current_player_id
        next_state = self.get_state(player_id=next_player_id)
        return next_state, next_player_id

    def get_last_action(self):
        return self._actions[-1] if len(self._actions) > 0 else None

    @property
    def round(self) -> Round:
        return self._round


    @property
    def judge(self) -> Judge:
        return self._judge


        
   