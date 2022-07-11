from termcolor import colored
from rlcard.games.dummy.action import get_action_str
from rlcard.games.dummy.melding import RANK_STR, SUIT_STR, get_rank_id, get_suit_id
import rlcard
import os
import torch

class HumanAgent(object):

    def __init__(self, num_actions, position):
        self.use_raw = True
        self.num_actions = num_actions
        self.position = position


    @staticmethod
    def step(state, position = 1):
        _print_state(state['raw_obs'])
        print("[" +  ", ".join([ "{}-{}".format(lid, get_action_str(lid) )  for lid in state['legal_actions']]) + "]")


        # ROOT_PATH = os.path.join(rlcard.__path__[0], 'models/pretrained')
        # env = rlcard.make('dummy')
        # device = torch.device('cpu')

        # model_path = os.path.join(ROOT_PATH, 'dummy_dmc', '{}_115856000.pth'.format(position))
        # agent = torch.load(model_path, map_location=device)
        # agent.set_device(device)
        # action_id, info = agent.eval_step(state)
        # print(action_id, info)

        
        action_id = input('>> You choose action (integer): ')
        
        while( not action_id.isdigit()):
            action_id = input('>> You choose action (integer): ')
        action_id = int(action_id)

        while action_id not in state['legal_actions']:
            print('Action illegel...')
            action_id = int(input('>> Re-choose action (integer): '))

        

        return action_id

    def eval_step(self, state):
        ''' Predict the action given the current state for evaluation. The same to step here.

        Args:
            state (numpy.array): an numpy array that represents the current state

        Returns:
            action (int): the action predicted (randomly chosen) by the random agent
        '''
        return self.step(state, self.position), {}

def _print_state(state):

    # other_melds =                           state[-329:]
    # current_melds =                         state[:-329][-329:]
    # uknown_cards =                          state[:-329][:-329][-52:]
    # top_discard =                           state[:-329][:-329][:-52][-52:]
    # speto_cards =                           state[:-329][:-329][:-52][:-52][-52:]
    # other_known_cards =                     state[:-329][:-329][:-52][:-52][:-52][-52:]
    # opponent_ahead_known_cards =            state[:-329][:-329][:-52][:-52][:-52][:-52][-52:]
    # discard =                               state[:-329][:-329][:-52][:-52][:-52][:-52][:-52][-52:]
    # current_hand =                          state[:-329][:-329][:-52][:-52][:-52][:-52][:-52][:-52][-52:]
    # num_stoke_pile =                        state[:-329][:-329][:-52][:-52][:-52][:-52][:-52][:-52][:-52][-29:]
    # num_player =                            state[:-329][:-329][:-52][:-52][:-52][:-52][:-52][:-52][:-52][:-29][-4:]



    print(state)
    player_id = state['player_id']
    # opponent_id = (player_id + 1 ) % 2

    current_hand = state['current_hand']

    known_cards = [c for c in state['known_cards'] if c not in current_hand]

    # opponent_hand = [None for _ in range(state['opponent_card_left'] - len(known_cards))] + known_cards
    opponent_hand = state['up_opponent_hand']
    discard_pile = state['discard_pile']
    deck = [None] + discard_pile

    current_meld = state['current_meld']
    opponent_meld = state['up_opponent_melds']

    num_stoke_pile= state['num_stoke_pile']

    

    player_0_hand = current_hand if player_id == 0 else opponent_hand
    player_0_melds = current_meld if player_id == 0 else opponent_meld

    player_1_hand = current_hand if player_id == 1 else opponent_hand
    player_1_melds = current_meld if player_id == 1 else opponent_meld

    print("==================================== PLAYER 0 HAND ====================================")
    draw_player(player_0_hand, player_0_melds, 0)
    print("==================================== DISCARDS PILE ====================================")
    draw_deck(deck, num_stoke_pile)
    print("==================================== PLAYER 1 HAND ====================================")
    draw_player(player_1_hand, player_1_melds, 1)

def draw_player(hand, melds, o: int):
    if o == 0:
        print("{}\n{}".format(print_card([c for meld in melds for c in meld]), print_card(hand)))
    else:
        print("{}\n{}".format(print_card(hand), print_card([c for meld in melds for c in meld])))

def print_card(cards):
    ''' Nicely print a card or list of cards

    Args:
        card (string or list): The card(s) to be printed
    '''

    lines = [[] for _ in range(4)]

    for card in cards:
        if card is None:
            lines[0].append('┌────┐')
            lines[1].append('│░░░░│')
            lines[2].append('│░░░░│')
            lines[3].append('└────┘')
        else:
            elegent_card = elegent_form(card)
            suit = elegent_card[0]
            rank = elegent_card[1:]
            if len(elegent_card) == 3:
                space = ""

            else:
                space = ' '
            
            color = None if suit == "♠" or suit == "♣" else "red"

            lines[0].append(colored('┌────┐', color))
            lines[1].append(colored('│{}{} │'.format(rank + suit, space), color))
            lines[2].append(colored('│    │',color))
            lines[3].append(colored('└────┘', color))

    return "\n".join([''.join(line) for line in lines])
    # for line in lines:
    #     print ()


def elegent_form(card):
    ''' Get a elegent form of a card string

    Args:
        card (string): A card string

    Returns:
        elegent_card (string): A nice form of card
    '''

    rank_id = get_rank_id(card)
    suit_id = get_suit_id(card)
    card = SUIT_STR[suit_id] +  RANK_STR[rank_id]
    suits = {'S': '♠', 'H': '♥', 'D': '♦', 'C': '♣','s': '♠', 'h': '♥', 'd': '♦', 'c': '♣' }
    rank = '10' if card[1] == 'T' else card[1]

    return suits[card[0]] + rank

def draw_deck(cards, num_stock_pile):
    ''' Nicely print a card or list of cards

    Args:
        card (string or list): The card(s) to be printed
    '''

    lines = [[] for _ in range(4)]

    for card in cards:
        if card is None:
            lines[0].append('┌────┐ ')
            lines[1].append('│░{}░│ '.format(num_stock_pile))
            lines[2].append('│░░░░│ ')
            lines[3].append('└────┘ ')
        else:
            elegent_card = elegent_form(card)
            suit = elegent_card[0]
            rank = elegent_card[1:]
            if len(elegent_card) == 3:
                space = ""

            else:
                space = ' '
            
            color = None if suit == "♠" or suit == "♣" else "red"

            lines[0].append(colored('┌────┐', color))
            lines[1].append(colored('│{}{} │'.format(rank + suit, space), color))
            lines[2].append(colored('│    │',color))
            lines[3].append(colored('└────┘', color))

    print("\n".join([''.join(line) for line in lines]))