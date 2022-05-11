from typing import List
import numpy as np
import itertools


RANK_STR = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
SUIT_STR = ['S', 'C', 'D', 'H']

def get_card(rank: str, suit: str) -> int:
    return RANK_STR.index(rank) + SUIT_STR.index(suit) * 13

def get_card_str(card_id: int):
    return get_rank_str(card_id) + get_suit_str(card_id)

def get_suit_id(card_id: int):
    return card_id // 13

def get_rank_id(card_id: int):
    return card_id % 13

def get_rank_str(card_id) -> str:
    return RANK_STR[get_rank_id(card_id)]

def get_suit_str(card_id) -> str:
    return SUIT_STR[get_suit_id(card_id)]


def get_all_melds(cards : List[int]):

    all_set_melds = []
    cards_by_rank = sorted(cards, key=lambda x: (get_rank_id(x), get_suit_id(x)))
    #set
    data = np.array(cards_by_rank)
    arr = np.split( data, np.where( np.diff(data) % 13 !=0 ) [0] + 1)
    
    for a in arr:
        if a.shape[0] >= 3:
            for i in range(3, a.shape[0] + 1):
                for subset in itertools.combinations(a, i):
                    all_set_melds.append(list(subset))


    #chain
    all_run_melds = []
    cards_by_suit = sorted(cards, key=lambda x: (get_suit_id(x), get_rank_id(x)))
    data = np.array(cards_by_suit)
    arr = np.split( data, np.where( np.diff(data) != 1 ) [0] + 1)
    for a in arr:
        
        if a.shape[0] >= 3:
            arr_rank = np.array([get_rank_id(c) for c in a])
            chains = np.split( a, np.where( np.diff(arr_rank) != 1 ) [0] + 1)
            for c in chains:
                if c.shape[0] >= 3:
                    for i in range(len(c) - 2):
                        for length in range(3, len(c) - i + 1):
                            all_run_melds.append(c[i: length + i].tolist())

    return all_set_melds + all_run_melds
    # return get_all_run_melds(cards) + get_all_set_melds(cards)


def is_run_meld(cards: List[int]):
    meld = sorted(cards, key=get_rank_id)
    
    i = 0
    while(i < len(meld) - 1):
        j = i+1
        if get_rank_id(meld[i]) + 1 != get_rank_id(meld[j]):
            return False
        if get_suit_id(meld[i]) != get_suit_id(meld[j]):
            return False
        i = i+1

    return True

def is_set_meld(cards: List[int]):

    i = 0
    while(i < len(cards) - 1):
        j = i+1
        if get_rank_id(cards[i])  != get_rank_id(cards[j]):
            return False
        i = i+1
    
    return True

def get_all_run_melds(cards : List[int]):
    card_count = len(cards)
    hand_by_suit = sorted(cards, key=lambda x: (get_suit_id(x), get_rank_id(x)))
    max_run_melds = []

    i = 0
    while(i < card_count - 2):
        card_i = hand_by_suit[i]
        j = i + 1
        card_j = hand_by_suit[j]

        while get_rank_id(card_j) == get_rank_id(card_i) + j - i and get_suit_id(card_i) == get_suit_id(card_j):
            j += 1
            if j < card_count:
                card_j = hand_by_suit[j]
            else:
                break

        max_run_meld = hand_by_suit[i:j]
        if len(max_run_meld) >= 3:
            max_run_melds.append(max_run_meld)
        i = j

    result = []
    for max_run_meld in max_run_melds:
        max_run_meld_count = len(max_run_meld)
        for i in range(max_run_meld_count - 2):
            for j in range(i + 3, max_run_meld_count + 1):
                result.append(max_run_meld[i:j])
    return result

def get_all_set_melds(cards: List[int]):
    hand_by_rank  = sorted(cards, key=get_rank_id)

    max_set_melds = []
    current_rank = None
    set_meld = []

    for card_id in hand_by_rank:
        if current_rank is None or current_rank == get_rank_id(card_id):
            set_meld.append(card_id)
        else:
            if len(set_meld) >= 3:
                max_set_melds.append(set_meld)
            set_meld = [card_id]
        current_rank = get_rank_id(card_id)

    if len(set_meld) >= 3:
        max_set_melds.append(set_meld)

    result = []
    for max_set_meld in max_set_melds:
        result.append(max_set_meld)
        if len(max_set_meld) == 4:
            for meld_card in max_set_meld:
                result.append([card for card in max_set_meld if card != meld_card])
    return result

def find_all_melds_depositable_by_speto(speto_cards: List[int]):
    lists = []
    for card in speto_cards:
        suit_id = get_suit_id(card)
        rank_id = get_rank_id(card)
        
        #set
        lists.append([get_card(RANK_STR[rank_id], SUIT_STR[i]) for i in range(4) if i  != suit_id])

        #chain
        cards = [get_card(RANK_STR[i], SUIT_STR[suit_id]) for i in range(13)]


        index = cards.index(card)

        arr = [cards[0:index], cards[index+ 1 :] ]
        if len(arr[0]) >= 3:
            for i in range(3, len(arr[0])):
                lists.append(arr[0][-i:])

        if len(arr[1]) >= 3:
            for i in range(3, len(arr[1])):
                lists.append(arr[1][:i])

    return lists

def find_all_relate_speto_meld(speto_cards: List[int], dead_cards: List[int]):
    all = []
    for speto_id in speto_cards:
        #set
        rank_id = get_rank_id(speto_id)
        m = [suit_id * 13 + rank_id for suit_id in range(4) ]

        m = [c for c in m if c not in dead_cards]
        if len(m) >= 3:
            for subset in itertools.combinations(m , 3):
                all.append(list(subset))


        #chain
        # -2 -> +2
        suit_id = get_suit_id(speto_id)
        for i in range(rank_id -2, rank_id + 2):
            if i >= 0 and i + 2 < 13:
                m = [j + suit_id * 13 for j in range(i, i+3)]
                m = [c for c in m if c not in dead_cards]
                if len(m) >= 3:
                    all.append(m)
    return all

def meld_2_str(meld : List[int]):
    return "".join([get_card_str(card_id) for card_id in meld])

    