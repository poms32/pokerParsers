import re
import time
import cPickle

import os

def iterfiles(folder):
    for r,d,f in os.walk(folder):
        for fn in f:
            yield os.path.join(r, fn)

P = {
    'money': '[\$]{0,1}([\d.]+)',
    'cards': '\[([\dAKQJT hsdc]+)\]',
    'dollar': '[\$]{0,1}',
    }



def GetHandInfo(hand):
    """
    PokerStars Hand #89153008615: Tournament #642836638, $0.23+$0.02 USD Hold'em No Limit - Level I (10/20) - 2012/11/12 18:33:59 ET
    "PokerStars Hand #89422277261:  Hold'em No Limit (5/10) - 2012/11/18 6:28:43 ET"
    "PokerStars Hand #88903694647:  Hold'em Limit ($0.02/$0.04 USD) - 2012/11/07 20:16:54 ET"
    "PokerStars Hand #112225863883:  Hold'em Limit ($0.02/$0.04 USD) - 2014/02/22 15:29:57 UTC [2014/02/22 10:29:57 ET]"
    """
    line = hand.split('\n', 1)[0]
    p = (
        "PokerStars[ ]*(?P<is_zoom>Zoom|)[ ]*Hand #(?P<hand_id>[\d]+):[ ]+"
        "(?P<game_type>Hold'em|Omaha) (?P<betting_structure>No Limit|Limit|Pot Limit) "
        "\(%(dollar)s(?P<small_blind>[\.\d]+)/%(dollar)s(?P<big_blind>[\.\d]+)[ ]*(?P<currency>USD|EUR|)\) - "
        "(?P<timestr>[\d/ :\w]+) (?P<time_zone>ET|UTC).*"
        )
    m = re.match(p%P, line)
    try:
        header = m.groupdict()
    except AttributeError:
        print "hand:", hand
        print "%r"%line
        print line
        raise
    header['time'] = time.mktime(time.strptime(header['timestr'], '%Y/%m/%d %H:%M:%S'))
    return header



def GetTableInfo(hand):
    line = hand.splitlines()[1]
    p = (
        "Table '(?P<table_name>[\w -]+)' "
        "(?P<table_size>[\d]+)-max "
        "(?P<play_money>\(Play Money\)|)[ ]*"
        "Seat #(?P<button>[\d]+) is the button"
        )
    m = re.match(p%P, line)
    try:
        header = m.groupdict()
    except AttributeError:
        print "table:", hand
        print "%r"%line
        print line
        raise
    return header




def GetPlayers(hand, handinfo):
    players = []
    p = (
        "Seat (?P<seat>[\d]+): "
        "(?P<name>.+) "
        "\(%(dollar)s(?P<stack>[\d\.]+) in chips\)"
        )
    lines = hand.splitlines()
    for n, line in enumerate(lines[2:]):
        if re.match("^Seat: [1-9]{1}: .*", line):
            m = re.match(p%P, line)
            try:
                players.append(m.groupdict())
            except Exception:
                print "hand:", hand
                print "line:", line
                raise
        else:
            break
    #dictorialize the players list
    ret = {}
    for p in players:
        ret[p.pop('name')] = p
    return ret


def GetPreActions(hand, handInfo):
    """
    posting blinds
    players sitting out
    """
    lines = hand.splitlines()
    i = len(handInfo['players']) + 2
    actions = []
    for line in lines[i:]:
        if line == '*** HOLE CARDS ***':
            break
        
            
        actions.append(line)
    return actions


def GetPlayerActions(hand, handInfo):
    """
    Actions taken by players after cards are dealt
    """
    lines = hand.splitlines()
    i = len(handInfo['players']) + 2 + len(handInfo['preflop_actions']) + 1
    patterns = [
        '(.+): (calls) %(money)s',
        '(.+): (folds)',
        '(.+): (bets) %(money)s',
        '(.+): (raises) %(money)s to %(money)s',
        '(.+): (shows) %(cards)s \((.+)\)',
        '(.+): (shows) %(cards)s',
        '(.+): (mucks) hand',
        '(.+): (checks)',
        "(.+): (doesn't show hand)",
        #'(.+): (.+)',
        '\*\*\* (FLOP) \*\*\* %(cards)s',
        '\*\*\* (FIRST FLOP) \*\*\* %(cards)s',
        '\*\*\* (SECOND FLOP) \*\*\* %(cards)s',
        '\*\*\* (TURN|RIVER) \*\*\* %(cards)s %(cards)s',
        '\*\*\* (FIRST TURN|FIRST RIVER) \*\*\* %(cards)s %(cards)s',
        '\*\*\* (SECOND TURN|SECOND RIVER) \*\*\* %(cards)s %(cards)s',
        '\*\*\* (SHOW DOWN) \*\*\*',
        '\*\*\* (FIRST SHOW DOWN) \*\*\*',
        '\*\*\* (SECOND SHOW DOWN) \*\*\*',
        '(.+) (collected) %(money)s from (.+)',
        '(.+) (leaves) the table',
        '(Uncalled bet) \(%(money)s\) returned to (.+)',
        '(.+) (joins the table at seat #[\d]+)',
        'Betting is capped',
        '(.+) (said), "(.*)"',
        '(.+) (has timed out)',
        '(.+) (is [\w]+)',
        '(.+) was removed from the table for failing to post',
        '(Dealt) to (.+) %(cards)s',
        ]
    hero = {}
    actions = []
    for line in lines[i:]:
        if line == '*** SUMMARY ***':
            break
        else:
            for p in patterns:
                m = re.match(p%P, line)
                if m:
                    actions.append(m.groups())
                    break
            else:
                print hand
                raise Exception("parse failure:", line)

    return actions

def GetSummary(hand, handInfo):
    """
    """
    hands = hand.splitlines()
    summary = {}
    
    i = hands.index('*** SUMMARY ***') + 1
    
    patterns = [
        "Total pot %(dollar)s(?P<total_pot>[\d.]+)",
        "Rake %(dollar)s(?P<rake>[\d.]+)",
        "Side pot %(dollar)s(?P<side_pot>[\d.]+)\.",
        ]
    for p in patterns:
        m = re.search(p%P, hands[i])
        if m:
            summary.update(m.groupdict())

    summary['board'] = hands[i+1].split(' ', 1)[-1].strip('[]')
    
    return summary


def GetHandInfosFromFile(file):
    ret = []
    with open(file, 'r') as fp:
        fp.read(3) # remove BOM
        hands = [x.strip() for x in fp.read().split('\n\n\n') if x.strip()]
        hands = [x for x in hands if "Tournament" not in x]
    for hand in hands:
        handInfo = GetHandInfo(hand)
        handInfo['Table'] = GetTableInfo(hand)
        handInfo['players'] = GetPlayers(hand, handInfo)
        handInfo['preflop_actions'] = GetPreActions(hand, handInfo)
        handInfo['actions'] = GetPlayerActions(hand, handInfo)
        handInfo['summary'] = GetSummary(hand, handInfo)
        ret.append(handInfo)
    return ret


def GetHandInfosFromFolder(folder):
    for file in tools.iterfiles(path):
        for hinfo in GetHandInfosFromFile(file): 
            yield hinfo


def ReadHandInfosFromPickle(rfp):
    while 1:
        try:
            yield cPickle.load(rfp)
        except EOFError:
            break


def IterHandInfoFromPickle(fileName):
    with open(fileName, 'rb') as rfp:
        while 1:
            try:
                yield cPickle.load(rfp)
            except EOFError:
                break


if __name__ == '__main__':
    import pprint
    path = r'F:\pokerstars\processed'
    f = r"""F:\pokerstars\processed\2014\01-26\HH20140125 McNaught #41 - $0.01-$0.02 - USD No Limit Hold'em.txt"""
    db = 'f:\pokerstars\hand_history.pickle'


    if 0:
        pprint.pprint(GetHandInfosFromFile(f)[10])
        exit()

    if 1:
        c = 0
        with open(db, 'wb') as wfp:
            for each in GetHandInfosFromFolder(path):
                cPickle.dump(each, wfp)
                c += 1
        print 'Total hands written to file:', c

    else:
        hands = []
        with open(db, 'rb') as rfp:
            while 1:
                try:
                    hands.append(cPickle.load(rfp))
                    [cPickle.load(rfp) for x in xrange(22)]
                    pprint.pprint(cPickle.load(rfp))
                    break
                except EOFError:
                    break
        print len(hands)