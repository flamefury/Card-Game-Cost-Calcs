import random
import math
import sys

# How many packs will it take to open 3 of every card in an expansion? (barring leaders)
# Note: this will not include getting both leaders since the average pack count to
#       get both leaders is more than the count to get 3 of all the other cards in expansion.

# Number of trials to go through, one trial being akin to one user's experience
# The more trials, the more accurate the average, but it'll also take a lot longer to run.
runs = 300000

# When prioritize animated is true, non-animated are first to be liquefied if number of copies exceed 3
# When prioritize animated is false, animated cards are first to be liquefied if number of copies exceed 3
# True for collectors and show-offs, False for fewer packs necessary
prioritizeAnimated = False
# If keep leader is true, then at most 1 copy of a leader card is kept if opened.
# If keep leader is false, they are liqueified without any further thought.
# True for collectors and show-offs, False for fewer packs necessary
keepLeader = False
leadersToKeep = 3

# Stats and rates, can be changed for each expac
leaderCount = 2
legendCount = 18
goldCount = 18
silverCount = 26
bronzeCount = 35

leaderRate = 0.0006
legendRate = 0.0144
goldRate = 0.06
silverRate = 0.25
silverEighthRate = 0.925
bronzeRate = 0.675

animatedRate = 0.08

vialsCraftLegend = 3500
vialsCraftGold = 1000
vialsCraftSilver = 200
vialsCraftBronze = 50

vialsLiquefyLegend = 1000
vialsLiquefyGold = 250
vialsLiquefySilver = 50
vialsLiquefyBronze = 10

vialsAnimatedLiquefyLegend = 2500
vialsAnimatedLiquefyGold = 600
vialsAnimatedLiquefySilver = 120
vialsAnimatedLiquefyBronze = 30

# Convenience variables
totalCount = leaderCount + legendCount + goldCount + silverCount + bronzeCount

individualLeaderRate = leaderRate / leaderCount
individualLegendRate = legendRate / legendCount
individualGoldRate = goldRate / goldCount
individualSilverRate = silverRate / silverCount
individualBronzeRate = bronzeRate / bronzeCount

leaderThreshold = leaderRate
legendThreshold = leaderThreshold + legendRate
goldThreshold = legendThreshold + goldRate
silverThreshold = goldThreshold + silverRate
bronzeThreshold = silverThreshold + bronzeRate

legendStartIndex = leaderCount
goldStartIndex = leaderCount + legendCount
silverStartIndex = leaderCount + legendCount + goldCount
bronzeStartIndex = leaderCount + legendCount + goldCount + silverCount

# Cost of an entire collection if you crafted everything
collectionVialCraftCost = 3 * (legendCount * vialsCraftLegend + goldCount * vialsCraftGold + silverCount * vialsCraftSilver + bronzeCount * vialsCraftBronze)

# Remaining vials necessary to craft the rest of your collection
necessaryVials = collectionVialCraftCost

# Current collection and animated collection progress
collection = []
for x in range(totalCount):
    collection.append(0)
animCollection = []
for x in range(totalCount):
    animCollection.append(0)

def subAnimCost(card):
    global necessaryVials
    if card < goldStartIndex:
        necessaryVials = necessaryVials - vialsAnimatedLiquefyLegend
    elif card < silverStartIndex:
        necessaryVials = necessaryVials - vialsAnimatedLiquefyGold
    elif card < bronzeStartIndex:
        necessaryVials = necessaryVials - vialsAnimatedLiquefySilver
    else:
        necessaryVials = necessaryVials - vialsAnimatedLiquefyBronze

def subCraftCost(card):
    global necessaryVials
    if card < goldStartIndex:
        necessaryVials = necessaryVials - vialsCraftLegend
    elif card < silverStartIndex:
        necessaryVials = necessaryVials - vialsCraftGold
    elif card < bronzeStartIndex:
        necessaryVials = necessaryVials - vialsCraftSilver
    else:
        necessaryVials = necessaryVials - vialsCraftBronze

def subLiquefyCost(card):
    global necessaryVials
    if card < goldStartIndex:
        necessaryVials = necessaryVials - vialsLiquefyLegend
    elif card < silverStartIndex:
        necessaryVials = necessaryVials - vialsLiquefyGold
    elif card < bronzeStartIndex:
        necessaryVials = necessaryVials - vialsLiquefySilver
    else:
        necessaryVials = necessaryVials - vialsLiquefyBronze

# When you pull a card, how do you affect vials remaining?
def getCard(card):
    global necessaryVials

    animated = False
    if random.uniform(0,1) < animatedRate:
        animated = True

    if animated:
        if card < legendStartIndex: # LEADER CARD
            if not keepLeader:
                necessaryVials = necessaryVials - vialsAnimatedLiquefyLegend
            elif prioritizeAnimated:
                if animCollection[card] == 1:
                    necessaryVials = necessaryVials - vialsAnimatedLiquefyLegend
                else:
                    # Leaders can't be crafted, so does not affect remaining vials
                    animCollection[card] = animCollection[card] + 1
                    if collection[card] == 1: # You can liquefy your non-anim leader
                        necessaryVials = necessaryVials - vialsLiquefyLegend
                        collection[card] = collection[card] - 1
            else:
                if collection[card] + animCollection[card] == 1:
                    necessaryVials = necessaryVials - vialsAnimatedLiquefyLegend
                else:
                    animCollection[card] = animCollection[card] + 1
        else:
            if prioritizeAnimated:
                if animCollection[card] == 3:
                    subAnimCost(card)
                else:
                    animCollection[card] = animCollection[card] + 1
                    if animCollection[card] + collection[card] == 4: # You can liquefy a non-anim
                        collection[card] = collection[card] - 1
                        subLiquefyCost(card)
                    else:
                        subCraftCost(card)
            else:
                if collection[card] + animCollection[card] == 3:
                    subAnimCost(card)
                else:
                    animCollection[card] = animCollection[card] + 1
                    subCraftCost(card)
                    
    else: # Not animated
        if card < legendStartIndex: # LEADER CARD
            if not keepLeader:
                necessaryVials = necessaryVials - vialsLiquefyLegend
            elif prioritizeAnimated:
                if animCollection[card] + collection[card] == 1:
                    necessaryVials = necessaryVials - vialsLiquefyLegend
                else:
                    # Leaders can't be crafted, so does not affect remaining vials
                    collection[card] = collection[card] + 1
            else:
                if collection[card] == 1:
                    necessaryVials = necessaryVials - vialsLiquefyLegend
                else:
                    collection[card] = collection[card] + 1
                    if animCollection[card] == 1:
                        animCollection[card] = animCollection[card] - 1
                        necessaryVials = necessaryVials - vialsAnimatedLiquefyLegend
        else:
            if prioritizeAnimated:
                if animCollection[card] + collection[card] == 3:
                    subLiquefyCost(card)
                else:
                    collection[card] = collection[card] + 1
                    subCraftCost(card)
            else:
                if collection[card] == 3:
                    subLiquefyCost(card)
                else:
                    collection[card] = collection[card] + 1
                    if animCollection[card] + collection[card] == 4:
                        animCollection[card] = animCollection[card] - 1
                        subAnimCost(card)
                    else:
                        subCraftCost(card)
                        

# Are you able to craft the rest of your collection?
def isCollectionComplete():
    if necessaryVials <= 0:
        return True
    return False


runningSum = 0.0
minPacks = sys.maxsize
maxPacks = 0
for x in range(runs):
    packsOpened = 0
    while True:
        packsOpened = packsOpened + 1
        for i in range(8):
            card = random.uniform(0,1)
            cardGot = -1
            if card < leaderThreshold:
                cardGot = random.randint(0, legendStartIndex - 1)
            elif card < legendThreshold:
                cardGot = random.randint(legendStartIndex, goldStartIndex - 1)
            elif card < goldThreshold:
                cardGot = random.randint(goldStartIndex, silverStartIndex - 1)
            elif card < silverThreshold or i == 7:
                cardGot = random.randint(silverStartIndex, bronzeStartIndex - 1)
            else:
                cardGot = random.randint(bronzeStartIndex, bronzeStartIndex + bronzeCount - 1)
            getCard(cardGot)

        if isCollectionComplete():
            break

    # Reset collection and vials remaining
    necessaryVials = collectionVialCraftCost
    for i in range(len(collection)):
        collection[i] = 0
        animCollection[i] = 0

    if packsOpened > maxPacks:
        maxPacks = packsOpened
    if packsOpened < minPacks:
        minPacks = packsOpened
    runningSum = packsOpened + runningSum

    # Uncomment if you wanna see the progress. It will slowdown total running time by a lot though.
    #print ("Runs: " + str(x+1) + ", Average Packs: " + str(runningSum / float(x+1)) + ", Max Packs: " + str(maxPacks) + ", Min Packs: " + str(minPacks))

print ("Runs: " + str(runs) + ", Average Packs: " + str(runningSum / float(runs)) + ", Max Packs: " + str(maxPacks) + ", Min Packs: " + str(minPacks))
