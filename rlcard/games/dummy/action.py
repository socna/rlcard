import rlcard
import os

from enum import Enum

from rlcard.games.dummy.melding import get_card_str

ROOT_PATH = rlcard.__path__[0]


melds_id_path = os.path.join(ROOT_PATH, 'games/dummy/jsondata/meld_id.txt')
with open(melds_id_path, 'r') as f:
    ID_2_ACTION = f.readline().strip().split()


draw_card_action_id = 0
deposit_card_action_id = draw_card_action_id + 1
take_card_action_id = deposit_card_action_id + 329
meld_card_action_id  = take_card_action_id + 329
discard_action_id = meld_card_action_id + 329
knock_action_id = discard_action_id + 52

class Action(Enum):
    DRAW_CARD_ACTION = "draw_card"
    DEPOSIT_CARD_ACTION = "deposit_card"
    TAKE_CARD_ACTION = 'take_card'
    MELD_CARD_ACTION = 'meld_card'
    DISCARD_ACTION = 'discard'
    KNOCK_ACTION = "knock"

    UNKNOW_ACTION = "unknow"

def decode_action(action_id : int):
    if action_id == draw_card_action_id:
        return (Action.DRAW_CARD_ACTION, draw_card_action_id)
    elif action_id in range(deposit_card_action_id, take_card_action_id):
        return (Action.DEPOSIT_CARD_ACTION, action_id - deposit_card_action_id)
    elif action_id in range(take_card_action_id, meld_card_action_id):
        return (Action.TAKE_CARD_ACTION, action_id - take_card_action_id)
    elif action_id in range(meld_card_action_id, discard_action_id):
        return (Action.MELD_CARD_ACTION, action_id - meld_card_action_id)
    elif action_id in range(discard_action_id, knock_action_id):
        return (Action.DISCARD_ACTION, action_id - discard_action_id)
    elif action_id in range(knock_action_id, knock_action_id + 53):
        return (Action.KNOCK_ACTION, action_id - knock_action_id)
    else:
        raise Exception("decode_action: unknown action_id {}".format(action_id))

def get_action_str(action_id : int):
    (action, rank_id) = decode_action(action_id)

    name = action.value
    rank_str = ""
    if action == Action.DRAW_CARD_ACTION:
        pass
    elif action == Action.DISCARD_ACTION or action == Action.KNOCK_ACTION :
        if action == Action.KNOCK_ACTION  and rank_id == 52:
            pass
        else:
            rank_str =  get_card_str(rank_id)
    elif  action == Action.DEPOSIT_CARD_ACTION or action == Action.MELD_CARD_ACTION or action == Action.TAKE_CARD_ACTION:
        rank_str = "".join([ get_card_str(int(c)) for c  in ID_2_ACTION[rank_id].split(",")])
    else:
        pass

    return name + ":" + rank_str if rank_str != "" else name
