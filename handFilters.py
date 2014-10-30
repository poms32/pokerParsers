

import pprint
from pokerConst import *
import parsePokerDB
import handInfo

##########################################################################################
### Basic game type filters
###


def FilterGameType(db, gameType):
    for hand in db:
        if hand['game_type'] == gameType:
            yield hand


def FilterByBigBlindSize(db, size):
    for hand in db:
        if hand['big_blind'] == size:
            yield hand


def FilterZOOMOnly(db):
    for hand in db:
        if hand['is_zoom'] == C_ZOOM:
            yield hand


def FilterByTableSize(db, seats):
    for hand in db:
        tableSize = int(hand['Table']['table_size'])
        if tableSize == int(seats):
            yield hand


def FilterPlayerSeat(db, player, seat):
    for hand in db:
        playerSeat = handInfo.GetPlayerSeat(hand, player)
        if int(playerSeat) == int(seat):
            yield hand


##########################################################################################
### Action sequence filters
###


def FilterPlayerRaises(db, player):
    for hand in db:
        try:
            for action in hand['actions']:
                if action and player == action[0] and action[1] == 'raises':
                    yield hand
        except:
            pprint.pprint(hand)
            raise


def FilterOnePreflopCall(db, player, bb=3):
    """
        player raises preflop bb number of big blinds
        one player calls
    """
    for hand in db:
        gotRaise = False
        gotCall = False
        yieldHand = False
        bigBlind = float(hand['big_blind'])
        for action in hand['actions']:
            if len(action) < 2:
                continue

            if gotCall and action[1] == 'calls':
                # second call
                yieldHand = False
                break

            if gotRaise:
                if action[1] == 'raises':
                    break
                if action[1] == 'calls':
                    gotCall = True
                    yieldHand = True

            if player == action[0] and action[1] == 'raises':
                if bb*bigBlind == float(action[3]):
                    gotRaise = True

        if yieldHand:
            yield hand




