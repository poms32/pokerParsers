import re
import time
import cPickle
import os
import tools



P = {
    'money': '[\$]{0,1}([\d.]+)',
    'cards': '\[([\dAKQJT hsdc]+)\]',
    'dollar': '[\$]{0,1}',
    }



def GetGameInfo(hand):
    """
    PokerStars Hand #89153008615: Tournament #642836638, $0.23+$0.02 USD Hold'em No Limit - Level I (10/20) - 2012/11/12 18:33:59 ET
    "PokerStars Hand #89422277261:  Hold'em No Limit (5/10) - 2012/11/18 6:28:43 ET"
    "PokerStars Hand #88903694647:  Hold'em Limit ($0.02/$0.04 USD) - 2012/11/07 20:16:54 ET"
    "PokerStars Hand #112225863883:  Hold'em Limit ($0.02/$0.04 USD) - 2014/02/22 15:29:57 UTC [2014/02/22 10:29:57 ET]"
    "PokerStars Zoom Hand #124146287119:  Hold'em No Limit ($0.01/$0.02) - 2014/10/30 0:17:41 UTC [2014/10/29 20:17:41 ET]"
    """
    line = hand.split('\n', 1)[0]
    p = (
        "PokerStars[ ]*(?P<isZoom>Zoom|)[ ]*Hand #(?P<id>[\d]+):[ ]+"
        "(?P<type>Hold'em|Omaha|5 Card Draw) (?P<bettingStructure>No Limit|Limit|Pot Limit|Fixed Limit) "
        "\(%(dollar)s(?P<smallBlind>[\.\d]+)/(?P<currency2>%(dollar)s)(?P<bigBlind>[\.\d]+)[ ]*(?P<currency>USD|EUR|)\) - "
        "(?P<timestr1>[\d/ :\w]+) (?P<time_zone1>ET|UTC) \[(?P<timestr2>[\d/ :\w]+) (?P<time_zone2>ET|UTC)\]"
        )
    m = re.match(p%P, line)
    header = m.groupdict()
    
    for x in xrange(1, 3):
        if ('time_zone%d'%x) in header:
            if header[('time_zone%d'%x)] == 'ET':
                header['time'] = time.mktime(time.strptime(header['timestr%d'%x], '%Y/%m/%d %H:%M:%S'))
            elif header[('time_zone%d'%x)] == 'UTC':
                header['timeUTC'] = time.mktime(time.strptime(header['timestr%d'%x], '%Y/%m/%d %H:%M:%S'))
        del header['time_zone%d'%x]
        del header['timestr%d'%x]

    if not header['currency']:
        if header['currency2'] == '$':
            header['currency'] = 'USD'
    del header['currency2']
    
    return header



def GetTableInfo(hand):
    line = hand.splitlines()[1]
    p = (
        "Table '(?P<name>[\w -]+)' "
        "(?P<size>[\d]+)-max "
        "(?P<playMoney>\(Play Money\)|)[ ]*"
        "Seat #(?P<buttonSeat>[\d]+) is the button"
        )
    m = re.match(p%P, line)
    header = m.groupdict()
    return header




def GetPlayers(hand, handinfo):
    players = []
    p = (
        "Seat (?P<seat>[\d]+): "
        "(?P<name>.+) "
        "\(%(dollar)s(?P<stack>[\d\.]+) in chips\)[ ]*"
        )
    lines = hand.splitlines()
    for n, line in enumerate(lines[2:]):
        if re.match("^Seat [\d]+: .*", line):
            m = re.match(p%P, line)
            players.append(m.groupdict())
        else:
            break
    #dictorialize the players list
    ret = []
    for p in players:
        tmp = (p['name'], p['seat'], p['stack'])
        ret.append(tmp)
    return ret


def GetPlayerActions(hand, handInfo):
    """
    Actions taken by players after cards are dealt
    """
    lines = hand.splitlines()
    i = len(handInfo['players']) + 2
    patterns = [
        '(.+): (sits out)',
        '(.+) (will be allowed to play after the button)',
        '(.+): (posts small blind) %(money)s',
        '(.+): (posts big blind) %(money)s',
        '(.+): (posts small & big blinds) %(money)s',
        '(.+): (posts the ante) %(money)s',
        '(.+): (calls) %(money)s',
        '(.+): (folds)',
        '(.+): (bets) %(money)s',
        '(.+): (raises) %(money)s to %(money)s',
        '(.+): (shows) %(cards)s \((.+)\)',
        '(.+): (shows) %(cards)s',
        '(.+): (mucks) hand',
        '(.+): (checks)',
        "(.+): (doesn't show hand)",
        "(.+): (discards) ([\d]+) card[ |s]{0,1}",
        "(.+): (discards) ([\d]+) card[ |s]{0,1} %(cards)s",
        '(.+): (stands pat)',
        #'(.+): (.+)',
        '\*\*\* (HOLE CARDS) \*\*\*',
        '\*\*\* (DEALING HANDS) \*\*\*',
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
                print "parse failure:", line
                #raise Exception("parse failure:", line)

    return actions

def GetSummary(hand, handInfo):
    """
    """
    hands = hand.splitlines()
    summary = {}
    
    i = hands.index('*** SUMMARY ***') + 1
    
    patterns = [
        "Total pot %(dollar)s(?P<potSize>[\d.]+)",
        "Rake %(dollar)s(?P<rake>[\d.]+)",
        "Side pot %(dollar)s(?P<sidePot>[\d.]+)\.",
        ]
    for p in patterns:
        m = re.search(p%P, hands[i])
        if m:
            summary.update(m.groupdict())

    summary['board'] = ''
    if hands[i+1].startswith('Board '):
        summary['board'] = hands[i+1].split(' ', 1)[-1].strip('[]')
    
    return summary


def GetHandInfosFromFile(file):
    ret = []
    with open(file, 'r') as fp:
        fp.read(3) # remove BOM
        hands = [x.strip() for x in fp.read().split('\n\n\n') if x.strip()]
        hands = [x for x in hands if "Tournament" not in x]
    for hand in hands:
        handInfo = {}
        handInfo['game'] = GetGameInfo(hand)
        handInfo['table'] = GetTableInfo(hand)
        handInfo['players'] = GetPlayers(hand, handInfo)
        handInfo['actions'] = GetPlayerActions(hand, handInfo)
        handInfo['summary'] = GetSummary(hand, handInfo)
        #handInfo['text'] = hand
        ret.append(handInfo)
        
    return ret


def GetHandInfosFromFolder(folder):
    for file in tools.iterfiles(folder):
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

@tools.errorhandling
def main():
    import pprint
    path = r'F:\pokerstars\processed'
    
    #path = r'F:\pokerstars\test'
    f = r"""F:\pokerstars\processed\2014\01-26\HH20140125 McNaught #41 - $0.01-$0.02 - USD No Limit Hold'em.txt"""
    f = r"""F:\pokerstars\processed\2014\10-30\HH20141029 McNaught #6 - $0.01-$0.02 - USD No Limit Hold'em.txt"""
    db = 'f:\pokerstars\hand_history.pickle'


    if 0:
        hi = GetHandInfosFromFile(f)[102]
        pprint.pprint(hi)
        print hi['text']

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

if __name__ == '__main__':
    main()