import handInfo
import handFilters

def StealingBlinds(db, playerName):
    """
        Hero is first to raise from the button
        calculate earnings
        maybe some stats
        !! should display in big blinds instead of chips !!
    """
    db = handFilters.FilterStealingBlinds(db, playerName)

    total = 0
    earnings = handInfo.EarningsTracker()
    for hand in db:
        total += 1
        earnings.Update(hand)
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
