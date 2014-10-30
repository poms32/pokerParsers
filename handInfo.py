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
    for each in hand['preflop_actions']:
        if type(each) == type(dict()):
            names.append(each['player'])
    return names



class EarningsTracker:
    """
        !!! Not trusted, needs unit testing. date: 30.10.2014 !!! 
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
        """
            returns a list of player names and winings, losses
            [[player1, -0.2], [player2, 0.2]]
        """
        players = dict([[p, 0.0] for p in GetPlayers(hand)])

        #blinds
        # need to remove all formatting from this function
        for action in hand['preflop_actions']:
            if type(action) == type(str()) and 'posts' in action:
                name = action.rsplit(":", 1)[0]
                if 'posts big blind' in action:
                    amount = action.split('posts big blind')[-1]
                    amount = amount.split()[0] #inclase "$x.xx and is all-in"
                    amount = float(amount.strip(' $'))
                    players[name] -= amount
                elif 'posts small blind' in action:
                    amount = action.split('posts small blind')[-1]
                    amount = amount.split()[0] #inclase "$x.xx and is all-in"
                    amount = float(amount.strip(' $'))
                    players[name] -= amount

        raiseAmount = []
        for action  in hand['actions']:
            if len(action) > 1:
                if action[1] == C_RAISES:
                    if raiseAmount:
                        while raiseAmount:
                            p, a = raiseAmount.pop(-1)
                            players[p] -= a
                    raiseAmount.append([action[0], float(action[2])])
                    players[action[0]] -= float(action[3])-float(action[2])
                elif action[1] == C_BETS:
                    raiseAmount.append([action[0], float(action[2])])
                elif action[1] == C_CALLS:
                    players[action[0]] -= float(action[2])
                    if raiseAmount:
                        while raiseAmount:
                            p, a = raiseAmount.pop(-1)
                            players[p] -= a
                elif action[1] == C_COLLECTED:
                    players[action[0]] += float(action[2])

        for player, cash in players.iteritems():
            if cash:
                if player not in self.earnings:
                    self.earnings[player] = cash
                else:
                    self.earnings[player] += cash

