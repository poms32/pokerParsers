from collections import defaultdict
import pprint
from pokerConst import *


def GetHeroName(hand):
    """
        returns the name of the hero
    """
    return hand['actions'][0][1]


def GetPlayerSeat(hand, player):
    """
        returns seat number of player
        'Seat 1: Crying calll ($2 in chips) '
    """
    for seat in hand['preflop_actions']:
        if player == seat['player']:
            return seat['seat']


def GetShownHands(hand):
    """
        hands shown by player are excluded
    """
    shownHands = []
    for action in hand['actions']:
        if len(action) > 1 and action[1] == C_SHOWS:
            shownHands.append(action[0:4])
    return shownHands


def GetPlayersSeeingStreet(hand, street):
    """
        returns a list of players seeing street ['playerA', 'playerB']
        for street names use constants C_FLOP, C_TURN, C_RIVER, C_SHOW_DOWN
    """
    players = GetPlayers(hand)
    for action in hand['actions']:
        if action:
            if action[0] in players and action[1] == C_FOLDS:
                players.remove(action[0])
            elif action[0] == C_UNCALLED_BET and action[-1] in players:
                players.remove(action[-1])
            if action[0] == street.upper():
                break
    return players


def GetPlayers(hand):
    """
        returns a list of players sitting at table
    """
    names = []
    for each in hand['players']:
        names.append(each[0])
    return names



class EarningsTracker:
    """
        calculate earnings of each player in a hand
    """

    def __init__(self):
        self.earnings = {}

    def GetPlayers(self):
        return self.earnings.keys()

    def GetPlayerEarnings(self, player):
        if player in self.earnings:
            return self.earnings[player]
        else:
            return 0.0

    def Update(self, hand):
        playerNames = GetPlayers(hand)
        GetPlayerDict = lambda: dict([[p, 0] for p in playerNames])
        dgt = lambda s: int(round(float(s)*100))
        flt = lambda s: float(s)/100

        players = GetPlayerDict()
        roundAmounts = GetPlayerDict()
        for action  in hand['actions']:
            if len(action) > 1:
                if action[1] in (C_POSTS_SMALL_BLIND, C_POSTS_BIG_BLIND, C_POSTS_SMALL_AND_BIG_BLIND):
                    roundAmounts[action[0]] = dgt(action[2])

                elif action[1] == C_RAISES:
                    roundAmounts[action[0]] = dgt(action[3])

                elif action[1] in (C_BETS, C_CALLS):
                    roundAmounts[action[0]] += dgt(action[2])

                elif action[0] in (C_FLOP, C_TURN, C_RIVER, C_SHOW_DOWN):
                    for p, a in roundAmounts.iteritems():
                        players[p] -= a
                    roundAmounts = GetPlayerDict()

                elif action[0] == C_UNCALLED_BET:
                    players[action[2]] += dgt(action[1])

                elif action[1] == C_COLLECTED:
                    for p, a in roundAmounts.iteritems():
                        players[p] -= a
                    roundAmounts = GetPlayerDict()
                    players[action[0]] += dgt(action[2])

        for player, cash in players.iteritems():
            if cash:
                if player not in self.earnings:
                    self.earnings[player] = flt(cash)
                else:
                    self.earnings[player] += flt(cash)

