import sys
import cPickle
import re
import pprint
import time
import cStringIO
import traceback

import tools
import handFilters
from pokerConst import *
import handInfo
import playerStatistics

def loadDB(dbFile):
    with open(dbFile, 'rb') as rfp:
        while 1:
            try:
                yield cPickle.load(rfp)
            except EOFError:
                break


def printOneHand(db):
    pprint.pprint(db.next())


def CalculateEarnings(db, playerName):
    """
        Hero is first to raise from the button
        calculate earnings
        maybe some stats
    """
    db = handFilters.FilterGameType(db, C_HOLDEM)
    db = handFilters.FilterByBigBlindSize(db, C_2CENT)
    db = handFilters.FilterZOOMOnly(db)
    db = handFilters.FilterByTableSize(db, 9)
    #db = handFilters.FilterPlayerSeat(db, playerName, 1)

    tm = time.gmtime()
    lastMidnight = time.time() - tm.tm_sec - tm.tm_min*60 - tm.tm_hour*3600
    d = time.mktime((2014,10,22,0,0,0,0,0,0))
    #db = handFilters.FilterTime(db, d, time.time())
    db = handFilters.FilterStealingBlinds(db, playerName)

    total = 0
    earnings = handInfo.EarningsTracker()
    for hand in db:
        total += 1
        earnings.Update(hand)
        pprint.pprint(hand)
        raw_input()
    print playerName
    print earnings.GetPlayerEarnings(playerName)
    l = []
    for i, p in earnings.GetHandsWithPlayer(playerName):
        l.append(p[playerName])
    l.sort()
    print '+0.03', l.count(0.03), 'total:', l.count(0.03)*0.03
    print '-0.06', l.count(-0.06), 'total:', l.count(-0.06)*(-0.06)
    #print l
    print total

    
def TestStats(db, player):
    db = handFilters.FilterGameType(db, C_HOLDEM)
    db = handFilters.FilterByBigBlindSize(db, C_2CENT)
    db = handFilters.FilterZOOMOnly(db)
    db = handFilters.FilterByTableSize(db, 9)

    tm = time.gmtime()
    lastMidnight = time.time() - tm.tm_sec - tm.tm_min*60 - tm.tm_hour*3600
    d = time.mktime((2014,11,2,0,0,0,0,0,0))
    db = handFilters.FilterTime(db, d, time.time())
    counter = playerStatistics.PlayerActionCounter()
    h = 0
    for hand in db:
        h += 1
        c = playerStatistics.ActionsToCounter(player, hand['actions'])
        counter.MergeWithCounter(c)
    ps = playerStatistics.PlayerStats(counter)
    
    print 'hands', h
    print 'VPIP', ps.VPIP()
    print 'PFR', ps.PFR()
    pprint.pprint(counter)
    

def GetDBSize(db):
    total = 0
    for each in db:
        total += 1
    print 'db size:', total

@tools.errorhandling
@tools.timeit
def main():
    dbfile = 'f:\pokerstars\hand_history.pickle'
    db = loadDB(dbfile)
    #print GetTotalWins(db, 'eysispeisi')
    player = 'eysispeisi'
    #CalculateEarnings(db, player)
    TestStats(db, player)
    

if __name__ == "__main__":
    
    main()