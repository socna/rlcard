from rlcard.games.dummy.melding import get_all_melds, is_run_meld, is_set_meld


class DummyPlayer:
    _hand: list
    _run_melds: list
    _set_melds: list
    _known_cards : list

    _score_cards : list

    _all_hand_melds: list
    _transactions: list

    def __init__(self, player_id : int) -> None:
        self.player_id = player_id
        self._hand = []
        self._known_cards = []
        self._melds = []
        self._score_cards = []

        self._run_melds = []
        self._set_melds = []

        self._all_hand_melds = []

        self._transactions = []
        

    @property
    def hand(self) -> list:
        return self._hand

    @property
    def all_melds(self) -> list:
        return self._run_melds + self._set_melds

    @property
    def run_melds(self) -> list:
        return self._run_melds

    @property
    def set_melds(self) -> list:
        return self._set_melds

    @property
    def score_cards(self):
        return self._score_cards
        
    def calculate_melds_in_hand(self) -> list:
        self._all_hand_melds =  get_all_melds(self._hand)

    def get_all_melds_in_hand(self) -> list:
        return self._all_hand_melds

    @property
    def known_cards(self) -> list:
        return self._known_cards

    def add_melds(self, cards) -> list:
        if is_run_meld(cards):
            self._run_melds.append(sorted(cards))
        elif is_set_meld(cards):
            self._set_melds.append(sorted(cards))
        else:
            raise Exception("add wrong melds")
        
        
    def add_card_to_hand(self, card_id):
        self.hand.append(card_id)
        self.calculate_melds_in_hand()

    def remove_card_from_hand(self, card_id):
        self.hand.remove(card_id)
        self.calculate_melds_in_hand()

    def add_transation(self, score : int):
        self._transactions.append(score)

    @property
    def transactions(self):
        return self._transactions

    
        