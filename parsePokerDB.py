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
    db = handFilters.FilterTime(db, d, time.time())

    total = 0
    earnings = handInfo.EarningsTracker()
    for hand in db:
        total += 1
        earnings.Update(hand)
    print playerName
    print earnings.GetPlayerEarnings(playerName)
    print total


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
    CalculateEarnings(db, player)
    

if __name__ == "__main__":
    
    main()