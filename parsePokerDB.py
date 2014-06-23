"""
{'Table': {'button': '1',
           'play_money': '',
           'table_name': 'McNaught',
           'table_size': '9'},
 'actions': [('Dealt', 'eysispeisi', '2c 3s'),
             ('osorare', 'calls', '0.02'),
             ('Deinonych', 'folds'),
             ('funnystory', 'folds'),
             ('oorbel', 'raises', '0.08', '0.10'),
             ('eysispeisi', 'folds'),
             ('pablojarg', 'folds'),
             ('Crying calll', 'folds'),
             ('fikfah', 'folds'),
             ('cirebackward', 'folds'),
             ('osorare', 'folds'),
             ('Uncalled bet', '0.08', 'oorbel'),
             ('oorbel', 'collected', '0.07', 'pot'),
             ('oorbel', "doesn't show hand")],
 'betting_structure': 'No Limit',
 'big_blind': '0.02',
 'currency': '',
 'game_type': "Hold'em",
 'hand_id': '112410990391',
 'is_zoom': 'Zoom',
 'players': {},
 'preflop_actions': ['Seat 1: Crying calll ($2 in chips) ',
                     'Seat 2: fikfah ($2.79 in chips) ',
                     'Seat 3: cirebackward ($2.13 in chips) ',
                     'Seat 4: osorare ($2.08 in chips) ',
                     'Seat 5: Deinonych ($2.70 in chips) ',
                     'Seat 6: funnystory ($2.07 in chips) ',
                     'Seat 7: oorbel ($1 in chips) ',
                     'Seat 8: eysispeisi ($2 in chips) ',
                     'Seat 9: pablojarg ($2 in chips) ',
                     'fikfah: posts small blind $0.01',
                     'cirebackward: posts big blind $0.02'],
 'small_blind': '0.01',
 'summary': {'board': "1: Crying calll (button) folded before Flop (didn't bet)",
             'rake': '0',
             'total_pot': '0.07'},
 'time': 1393372117.0,
 'time_zone': 'UTC',
 'timestr': '2014/02/25 23:48:37'}
"""

import sys
import cPickle
import re
import pprint


def traceback(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            pprint.pprint(*args, **kwargs)
            raise
    return wrapper


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


def GetShownHands(hand):
    """
        hands shown by player are excluded
    """
    shownHands = []
    for action in hand['actions']:
        if len(action) > 1 and action[1] == 'shows':
            shownHands.append(action[0:4])
    return shownHands

def GetPlayersSeeingStreet(hand, street):
    """
        returns a list of players seeing street
        ['playerA', 'playerB']
    """
    players = GetPlayers(hand)
    for action in hand['actions']:
        if action:
            if action[0] in players and action[1] == 'folds':
                players.remove(action[0])
            elif action[0] == 'Uncalled bet' and action[-1] in players:
                players.remove(action[-1])
            if action[0] == street.upper():
                break
    return players


def GetPlayersSeeingFlop(hand):
    return GetPlayersSeeingStreet(hand, 'FLOP')


def GetPlayersSeeingTurn(hand):
    return GetPlayersSeeingStreet(hand, 'TURN')


def GetPlayersSeeingRiver(hand):
    return GetPlayersSeeingStreet(hand, 'RIVER')


def GetPlayersSeeingShowDown(hand):
    return GetPlayersSeeingStreet(hand, 'SHOW DOWN')


def FilterEarnings(db, playerName):
    totalAmount = 0.0
    for hand in db:
        for action in hand['actions']:
            if len(action) > 2:
                try:
                    if action[0] == playerName and action[1] == 'collected':
                        totalAmount += float(action[2])
                        yield hand
                except:
                    print action
                    raise


def GetPlayers(hand):
    """
        returns a list of players sitting at table
    """
    names = []
    for each in hand['preflop_actions']:
        if type(each) == type(dict()):
            names.append(each['player'])
    return names


@traceback
def GetEarnings(hand):
    """
        returns a list of player names and winings, losses
        [[player1, -0.2], [player2, 0.2]]
    """
    players = dict([[p, 0.0] for p in GetPlayers(hand)])
    
    #blinds
    for action in hand['preflop_actions']:
        if type(action) == type(str()) and 'posts' in action:
            name = action.split(":", 1)[0]
            if 'posts big blind' in action:
                amount = action.split('posts big blind')[-1]
                amount = float(amount.strip(' $'))
                players[name] -= amount
            elif 'posts small blind' in action:
                amount = action.split('posts small blind')[-1]
                amount = float(amount.strip(' $'))
                players[name] -= amount

    # not finished
    raiseAmount = []
    for action  in hand['actions']:
        if len(action) > 1:
            if action[1] == 'raises':
                if raiseAmount:
                    while raiseAmount:
                        p, a = raiseAmount.pop(-1)
                        players[p] -= a
                raiseAmount.append([action[0], float(action[2])])
                players[action[0]] -= float(action[3])-float(action[2])
            elif action[1] == 'bets':
                raiseAmount.append([action[0], float(action[2])])
            elif action[1] == 'calls':
                players[action[0]] -= float(action[2])
                if raiseAmount:
                    while raiseAmount:
                        p, a = raiseAmount.pop(-1)
                        players[p] -= a
            elif action[1] == 'collected':
                players[action[0]] += float(action[2])
    return players


def loadDB(dbFile):
    with open(dbFile, 'rb') as rfp:
        while 1:
            try:
                yield cPickle.load(rfp)
            except EOFError:
                break


def printOneHand(db):
    pprint.pprint(db.next())


if __name__ == "__main__":
    dbfile = 'f:\pokerstars\hand_history.pickle'
    db = loadDB(dbfile)
    #print GetTotalWins(db, 'eysispeisi')
    player = 'eysispeisi'
    n = 0
    errors = 0
    players = {}
    shownHands = []
    for hand in db:
        x = GetShownHands(hand)
        if x:
            shownHands.extend(x)

    for each in shownHands:
        print each
        sys.stdout.flush()