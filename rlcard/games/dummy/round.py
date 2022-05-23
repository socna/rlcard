from rlcard.games.dummy.action import ID_2_ACTION
from rlcard.games.dummy.melding import  find_all_melds_depositable_by_speto, find_all_relate_speto_meld, get_all_melds, get_rank_id, get_suit_id, is_run_meld, is_set_meld
from .player import DummyPlayer as Player
from .dealer import DummyDealer as Dealer
import numpy as np
class DummyRound:
    def __init__(self, dealer_id: int, num_players: int, np_random) -> None:
        self._current_player_id = dealer_id
        self._num_players = num_players
        self._np_random = np_random
        self._is_over = False
        self._dealer = Dealer(self._np_random)

        self._players = [ Player(i) for i in range(num_players)]

        self._dangerous_discard_lv1 = {i : [] for i in range(num_players)}
        self._dangerous_discard_lv2 = {i : [] for i in range(num_players)}
        self._dangerous_discard_lv3 = {i : [] for i in range(num_players)}
        self._dangerous_discard_lv4 = {i : [] for i in range(num_players)}
        self._all_melds_depositable_speto = []

    @property
    def current_player_id(self) -> int:
        return self._current_player_id

    @property
    def dealer(self) -> Dealer:
        return self._dealer

    @property
    def num_players(self) -> int:
        return self._num_players

    @property
    def is_over(self) -> int:
        return self._is_over

    @property
    def dangerous_discard_lv1(self) -> dict:
        return self._dangerous_discard_lv1

    @property
    def dangerous_discard_lv2(self) -> dict:
        return self._dangerous_discard_lv2
    
    @property
    def dangerous_discard_lv3(self) -> dict:
        return self._dangerous_discard_lv3

    @property
    def dangerous_discard_lv4(self) -> dict:
        return self._dangerous_discard_lv4
        

    @property
    def all_players(self):
        return self._players
        
    def get_player(self, player_id: int = None) -> Player:
        if player_id == None:
            player_id = self._current_player_id
        return self._players[player_id]


    def _calculate_dangerous_discard_lv1(self, player: Player):
        '''
            Tìm card có thể gửi được
        '''
        set_melds = [meld for p in self._players for meld in p.set_melds]
        run_melds = [meld for p in self._players for meld in p.run_melds]

        list_depositable_cards = []
        ##set
        for meld in set_melds:
            depositable_cards = [c for c in player.hand if get_rank_id(c) == get_rank_id(meld[0])]
            if len(depositable_cards) > 0:
                list_depositable_cards.append((depositable_cards, meld))

        ##chain
        for meld in run_melds:
            
            depositable_cards = []
            for card in player.hand:
                
                if get_suit_id(meld[0]) == get_suit_id(card):
                    if get_rank_id(card) + 1 == get_rank_id(meld[0]) or get_rank_id(card) == get_rank_id(meld[-1]) + 1:
                        depositable_cards.append(card)
            if len(depositable_cards) > 0:
                list_depositable_cards.append((depositable_cards, meld))
        self._dangerous_discard_lv1[player.player_id] = list_depositable_cards


        self._calculate_dangerous_discard_lv4(player)

    def _calculate_dangerous_discard_lv4(self, player):
        lists = set()
        depositable = self._dangerous_discard_lv1[player.player_id]


        for (cards, m) in depositable:
            for c in cards:
                speto = self._get_speto_depositable()
                for s in speto:
                    meld = sorted(m + [c, s])
                    if is_run_meld(meld):
                        if (meld[-1] == s and meld[-2] == c) or meld[0] == s and meld[1] == c:
                            lists.add(c)

        self._dangerous_discard_lv4[player.player_id] = list(lists)
                    
    def _calculate_melds_depositable_by_speto(self):
        speto = self._get_speto_depositable()
        self._all_melds_depositable_speto = find_all_melds_depositable_by_speto(speto)



    def _calculate_dangerous_discard_lv2(self, player: Player, speto_cards: list):
        '''
            Tìm card trên tay khi đánh ra có thể bị ăn speto
        ''' 

        hand = player.hand

        lists = set()

        dead_cards = [c for p in self.all_players for c in p.score_cards]
        all_melds = find_all_relate_speto_meld(speto_cards, dead_cards)
        for meld in all_melds:
            cm1 = [c for c in meld if c in hand]
            cm2 = [c for c in meld if c in self._dealer.discard_pile]
            if len(cm1) == len(cm2) == 1:
                lists.add(cm1[0])

        self._dangerous_discard_lv2[player.player_id] = list(lists)

    def _calculate_dangerous_discard_lv3(self, player: Player, discard_pile):
        '''
            Tìm card trên tay khi đánh ra vào phỏm
        '''
        lists = set()
        all_melds = get_all_melds(discard_pile + player.hand)
        all_melds = [meld for meld in all_melds if len(meld) == 3]

        
        for meld in all_melds:
            cm = [c for c in meld if c in player.hand ]
            if len(cm) == 1:
                lists.add(cm[0])

        
        self._dangerous_discard_lv3[player.player_id] = list(lists)


    def draw_card(self):
        current_player = self.get_player()
        card = self.dealer.stock_pile.pop()

        current_player.add_card_to_hand(card)

        self._calculate_dangerous_discard_lv1(current_player)
        self._calculate_dangerous_discard_lv2(current_player, self._dealer.speto_cards)
        self._calculate_dangerous_discard_lv3(current_player, self._dealer.discard_pile)

    def deposit_card(self, rank_id):
        current_player = self.get_player()
        cards = [int(c) for c  in ID_2_ACTION[rank_id].split(",")]
        card_deposit = None 
        for card in cards :
            if card in current_player.hand:
                card_deposit = card
                break

        if card_deposit in self._dangerous_discard_lv4[current_player.player_id]:
            current_player.add_transation(-30)

        current_player.remove_card_from_hand(card_deposit)
        cards.remove(card_deposit)

        if card_deposit in current_player.known_cards:
            current_player.known_cards.remove(card_deposit)

        
        #add card to meld
        all_melds = [meld for p in self._players for meld in p.all_melds if sorted(meld) == sorted(cards)]

        all_melds[0].append(card_deposit)

        current_player.score_cards.append(card_deposit)

        self._calculate_dangerous_discard_lv1(current_player)
        self._calculate_dangerous_discard_lv2(current_player, self._dealer.speto_cards)
        self._calculate_dangerous_discard_lv3(current_player, self._dealer.discard_pile)



    def meld_card(self, rank_id):
        current_player = self.get_player()
        cards = [int(c) for c  in ID_2_ACTION[rank_id].split(",")]

        if cards in self._all_melds_depositable_speto:
            #TODO trừ điểm
            # print("tru diem 1")
            current_player.add_transation(-45)
            pass

        current_player.add_melds(cards)
        for c in cards:
            current_player.score_cards.append(c)

        for c in cards:
            current_player.remove_card_from_hand(c)
            if c in current_player.known_cards:
                current_player.known_cards.remove(c)
        
        

        self._calculate_dangerous_discard_lv1(current_player)
        self._calculate_dangerous_discard_lv2(current_player, self.dealer.speto_cards)
        self._calculate_dangerous_discard_lv3(current_player, self.dealer.speto_cards)
        self._calculate_melds_depositable_by_speto()

        

    def take_card(self, rank_id):
        current_player = self.get_player()
        cards = [int(c) for c  in ID_2_ACTION[rank_id].split(",")]

        if cards in self._all_melds_depositable_speto:
            #TODO trừ điểm
            # print("tru diem 2")
            current_player.add_transation(-45)
            pass

        #add to score cards
        for c in cards:
            current_player.score_cards.append(c)

        cards_in_hand =  [c for c in cards if c in current_player.hand]
        cards_in_discard = [c for c in cards if c in self.dealer.discard_pile]

        current_player.add_melds(cards)

        for c in cards_in_hand:
            current_player.remove_card_from_hand(c)
            if c in current_player.known_cards:
                current_player.known_cards.remove(c)

        index = np.min(np.where(np.isin(self.dealer.discard_pile,cards_in_discard)))

        cards_take_discard = [c for c in self.dealer.discard_pile[index:] if c not in cards_in_discard]
        self.dealer.set_discard_pile(self.dealer.discard_pile[:index])

        for c in cards_take_discard:
            current_player.known_cards.append(c)
            current_player.add_card_to_hand(c)

        self._calculate_dangerous_discard_lv1(current_player)
        self._calculate_dangerous_discard_lv2(current_player, self.dealer.speto_cards)
        self._calculate_dangerous_discard_lv3(current_player, self.dealer.speto_cards)
        self._calculate_melds_depositable_by_speto()
        

    def discard(self, card_id):
        current_player = self.get_player()

        for (deposit_cards, meld) in self._dangerous_discard_lv1[current_player.player_id]:
            if card_id in deposit_cards:
                #TODO trừ điểm
                # print("tru diem 3")
                current_player.add_transation(-50)
                break

        if card_id in self._dangerous_discard_lv2[current_player.player_id]:
            #TODO trừ điểm
            # print("tru diem 4")
            current_player.add_transation(-30)
            pass

        if card_id in self._dangerous_discard_lv3[current_player.player_id]:
            #TODO trừ điểm
            current_player.add_transation(-50)
            pass


        current_player.remove_card_from_hand(card_id)

        if card_id in current_player.known_cards:
            current_player.known_cards.remove(card_id)

        self.dealer.discard_pile.append(card_id)

        self._calculate_dangerous_discard_lv1(current_player)
        self._calculate_dangerous_discard_lv2(current_player, self.dealer.speto_cards)
        self._calculate_dangerous_discard_lv3(current_player, self.dealer.speto_cards)
        self._calculate_melds_depositable_by_speto()

        #Đổi lượt chơi
        self._current_player_id = (self._current_player_id + 1) % self.num_players

    def knock(self, card_id):
        current_player = self.get_player()
        if card_id == 52:
            #hhet loc
            pass
        else:
            current_player.remove_card_from_hand(card_id)
            if card_id in self._dangerous_discard_lv1:
                current_player.add_transation(50)
            
            current_player.add_transation(50)
        
        self._is_over = True


    def _get_speto_depositable(self):
        all_score_cards = [c for p in self._players for c in p.score_cards]
        if len(self.dealer.discard_pile) > 0:

            return [c for c in self._dealer.speto_cards if c not in all_score_cards and c != self.dealer.discard_pile[0]]
        else:
            return [c for c in self._dealer.speto_cards if c not in all_score_cards]




        


        

    