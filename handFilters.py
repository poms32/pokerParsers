import time

from pokerConst import *
import handInfo

##########################################################################################
### Basic game type filters
###


def FilterGameType(db, gameType):
    for hand in db:
        if hand['game']['type'] == gameType:
            yield hand


def FilterByBigBlindSize(db, size):
    for hand in db:
        if hand['game']['bigBlind'] == size:
            yield hand


def FilterZOOMOnly(db):
    for hand in db:
        if hand['game']['isZoom']:
            yield hand


def FilterByTableSize(db, seats):
    for hand in db:
        tableSize = int(hand['table']['size'])
        if tableSize == int(seats):
            yield hand


def FilterPlayerSeat(db, player, seat):
    for hand in db:
        playerSeat = handInfo.GetPlayerSeat(hand, player)
        if int(playerSeat) == int(seat):
            yield hand


def FilterTime(db, fromDate=None, toDate=None):
    if fromDate is None:
        fromDate = 0
    if toDate is None:
        toDate = time.time()
    for hand in db:
        handTime = hand['game']['time']
        if fromDate <= handTime < toDate:
            yield hand


##########################################################################################
### Action sequence filters
###

def FilterStealingBlinds(db, player):
    """
        player seat is nr. 1
        no action around table, player is first to act and raises
    """
    for hand in db:
        button = hand['table']['buttonSeat']
        if hand['players'][0][0] == player and hand['players'][0][1] == '1':
            for action in hand['actions']:
                if len(action) > 1:
                    if action[1] == C_CALLS:
                        break
                    elif action[1] == C_RAISES:
                        if action[0] == player:
                            yield hand
                        break


def FilterPlayerRaises(db, player):
    for hand in db:
        for action in hand['actions']:
            if action and player == action[0] and action[1] == C_RAISES:
                yield hand


def FilterOnePreflopCall(db, player, bb=3):
    """
        player raises preflop bb number of big blinds
        one player calls
    """
    for hand in db:
        gotRaise = False
        gotCall = False
        yieldHand = False
        bigBlind = float(hand['game']['bigBlind'])
        for action in hand['actions']:
            if len(action) < 2:
                continue

            if gotCall and action[1] == C_CALLS:
                # second call
                yieldHand = False
                break

            if gotRaise:
                if action[1] == C_RAISES:
                    break
                if action[1] == C_CALLS:
                    gotCall = True
                    yieldHand = True

            if player == action[0] and action[1] == C_RAISES:
                if bb*bigBlind == float(action[3]):
                    gotRaise = True

        if yieldHand:
            yield hand




