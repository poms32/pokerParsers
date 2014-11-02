from pokerConst import *

def ActionsToCounter(player, actions):
    counter = PlayerActionCounter()
    round = 'PreFlop'
    counter['HandsPlayed'] = 1
    DidRaisePreFlop = False
    PutMoneyInPot = False
    walk = True
    winners = []
    for action in actions:
        if action[0] == C_FLOP:
            round = 'Flop'
        elif action[0] == C_TURN:
            round = 'Turn'
        elif action[0] == C_RIVER:
            round = 'River'
        elif len(action) > 1:
            if action[1] == C_RAISES:
                walk = False
                if action[0] == player:
                    counter[round+'Raise'] += 1
                    if round == 'PreFlop':
                        PutMoneyInPot = True
                        DidRaisePreFlop = True
            
            elif action[1] == C_FOLDS:
                if action[0] == player:
                    counter[round+'Fold'] += 1
            
            elif action[1] == C_BETS:
                walk = False
                if action[0] == player:
                    counter[round+'Bet'] += 1
            
            elif action[1] == C_CALLS:
                walk = False
                if action[0] == player:
                    counter[round+'Call'] += 1
                    if round == 'PreFlop':
                        PutMoneyInPot = True

            elif action[1] == C_CHECKS:
                if action[0] == player:
                    counter[round+'Check'] += 1
            
            elif action[1] == C_COLLECTED:
                winners.append(action[0])

    if DidRaisePreFlop:
        counter['DidRaisePreFlop'] = 1
    if PutMoneyInPot:
        counter['PutMoneyInPot'] = 1
    if walk and player in winners:
        counter['Walk'] = 1
                    
    return counter

class PlayerActionCounter(dict):
    def __init__(self):
        f = 0.0
        dict.__init__(self, {
            'HandsPlayed': f, 'PutMoneyInPot': f, 'Walk' : f, 'DidRaisePreFlop': f,
            'PreFlopFold': f, 'PreFlopCall': f, 'PreFlopRaise': f, 'PreFlopCheck': f,
            'FlopFold': f, 'FlopCall': f, 'FlopRaise': f, 'FlopBet': f, 'FlopCheck': f,
            'TurnFold': f, 'TurnCall': f, 'TurnRaise': f, 'TurnBet': f, 'TurnCheck': f,
            'RiverFold': f, 'RiverCall': f, 'RiverRaise': f, 'RiverBet': f, 'RiverCheck': f,
            })

    def GetStatNames(self):
        return self.keys()
            
    def GetStat(self, stat):
        return self[stat]

    def AddToStat(self, stat, value=1):
        self[stat] += value

    def MergeWithCounter(self, counter):
        for statName, value in counter.iteritems():
            self[statName] += value


class PlayerStats:
    
    def __init__(self, counter):
        """
        """
        self.counter = counter

    def VPIP(self):
        """
        Stat: Voluntarily Put Money into Pot % preflop
        
        Percentage of the time that a player voluntarily contributed money to the pot, 
        given that he had a chance to do so.

        Formula: Number of Times Player Put Money In Pot / (Number of Hands - Number of Walks)
        """
        op = self.counter['HandsPlayed'] - self.counter['Walk']
        if op > 0:
            return self.counter['PutMoneyInPot']/op
        return 0.0

    def PFR(self):
        """
        Stat: Pre Flop Raise %
        
        Percentage of the time that a player put in any raise preflop, given that he had a 
        chance to do so.

        Formula: Number of Times Player Raised Preflop / (Number of Hands - Number of Walks)
        """
        op = self.counter['HandsPlayed'] - self.counter['Walk']
        if op > 0:
            return self.counter['DidRaisePreFlop']/op
        return 0.0

    def AFq(self):
        """
        Stat: Total Aggression Frequency

        Percentage of non-checking postflop actions that were aggressive. For example, a 
        player with an AFq of 40 made a bet or raise 40% of the time he bet, raised, called, 
        or folded.

        Formula: (Number of Times Player Bet on the Flop + Number of Times Player Raised on 
        the Flop + Number of Times Player Bet on the Turn + Number of Times Player Raised on 
        the Turn + Number of Times Player Bet on the River + Number of Times Player Raised 
        on the River) / (Number of Times Player Called on the Flop + Number of Times Player 
        Folded on the Flop + Number of Times Player Bet on the Flop + Number of Times Player 
        Raised on the Flop + Number of times Player Called on the Turn + Number of Times 
        Player Folded on the Turn + Number of Times Player Bet on the Turn + Number of Times 
        Player Raised on the Turn + Number of Times Player Called on the River + Number of 
        Times Player Folded on the River + Number of Times Player Bet on the River + Number 
        of Times Player Raised on the River)
        """

    def WTSD(self):
        """
        Stat: Went to Showdown %

        Percentage of the time that a player went to showdown, given that he saw the flop.

        Formula: Number of Times Player Went to Showdown / Number of Times Player Saw the Flop
        """

    def WSD(self):
        """
        Stat: Won Money at Showdown %

        Percentage of the time that a player won some money at showdown, given that he got to showdown.

        Formula: Number of Times Player Won Money at Showdown / Number of Times Player Went to Showdown
        """

        
    