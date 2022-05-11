import numpy as np
from .player import DummyPlayer as Player

class DummyDealer:
    _stock_pile: list
    _discard_pile: list
    _speto_cards: list
    def __init__(self, np_random: np.random.RandomState) -> None:
        self._stock_pile = [i for i in range(52)]
        np_random.shuffle(self._stock_pile)

        self._discard_pile = []
        self._speto_cards = [10, 13] # 2C, QS

    @property
    def stock_pile(self) -> list:
        return self._stock_pile

    @property
    def discard_pile(self) -> list:
        return self._discard_pile
    
    def set_discard_pile(self, cards):
        self._discard_pile = cards

    @property
    def speto_cards(self) -> list:
        return self._speto_cards



    def deal_cards(self,  player: Player, num_cards):
        for _ in range(num_cards):
            player.hand.append(self._stock_pile.pop())

        player.calculate_melds_in_hand()

    def deal_first_card(self):
        first_card = self.stock_pile.pop()
        if first_card not in self.speto_cards:
            self._speto_cards.append(first_card)

        self._discard_pile.append(first_card)