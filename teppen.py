import random
import math
import sys

# How many packs will it take to open 3 of every card in an expansion?
# (barring legends, which is one)

# Total card count of each rarity, can be changed for each expac
# Legendary - 4 for 4 colours, can only have 1 of each
legendCount = 16
# Epic - 7 for 4 colours, 3 of each
epicCount = 28
# Rare - 14 for 4 colours, 3 of each
rareCount = 56
# Common - 20 for 4 colours, 3 of each
commonCount = 80

# Teppen's fatigue timer.
# Auto-get legend as final card if you don't open one after this many charges
legendaryMaxCharge = 30

# Soul Counts
# Golden conversion not included because I don't know how often they appear.
# Secrets also not included for the same reason.
commonReap = 10
rareReap = 50
epicReap = 200
legendReap = 800

commonCraft = 50
rareCraft = 200
epicCraft = 800
legendCraft = 3200

# Number of trials to go through, one trial being akin to one user's experience
# The more trials, the more accurate the average, but it'll also take a lot longer to run.
runs = 300000

# Rates, can be changed for each expac
commonRate = 0.65
rareRate = 0.28
rareSixthRate = 0.93 # Not really needed but I keep it here for reference anyway
epicRate = 0.06
legendRate = 0.01

# Convenience variables
totalCount = legendCount + epicCount + rareCount + commonCount

individualEpicRate = epicRate / epicCount
individualRareRate = rareRate / rareCount
individualCommonRate = commonRate / commonCount

legendThreshold = legendRate
epicThreshold = legendThreshold + epicRate
rareThreshold = epicThreshold + rareRate
commonThreshold = rareThreshold + commonRate

epicStartIndex = legendCount
rareStartIndex = legendCount + epicCount
commonStartIndex = legendCount + epicCount + rareCount

# Cost of an entire collection if you crafted everything
collectionSoulCraftCost = legendCount * legendCraft + 3 * (epicCraft * epicCount + rareCraft * rareCount + commonCraft * commonCount)

# Remaining souls necessary to craft the rest of your collection
necessarySouls = collectionSoulCraftCost

# Current collection and animated collection progress
currentLegends = 0
collection = []
for x in range(totalCount): # Legends are the starting indices even though we don't use it. Bad on space usage, easier reading.
    collection.append(0)

def subCraftCost(card):
    global necessarySouls
    if card < epicStartIndex:
        necessarySouls = necessarySouls - legendCraft
    elif card < rareStartIndex:
        necessarySouls = necessarySouls - epicCraft
    elif card < commonStartIndex:
        necessarySouls = necessarySouls - rareCraft
    else:
        necessarySouls = necessarySouls - commonCraft

def subReapCost(card):
    global necessarySouls
    if card < epicStartIndex:
        necessarySouls = necessarySouls - legendReap
    elif card < rareStartIndex:
        necessarySouls = necessarySouls - epicReap
    elif card < commonStartIndex:
        necessarySouls = necessarySouls - rareReap
    else:
        necessarySouls = necessarySouls - commonReap

# When you pull a card, how do you affect souls remaining?
def getCard(card):
    global necessarySouls
    global currentLegends
    if card < epicStartIndex: # Legend
        # Legend is always one that you don't have in collection. If you have them all, then you can liquefy.
        if currentLegends == legendCount:
            subReapCost(card)
        else:
            currentLegends = currentLegends + 1
            subCraftCost(card)
    else: # Not legend
        if collection[card] == 3:
            subReapCost(card)
        else:
            collection[card] = collection[card] + 1
            subCraftCost(card)

# Are you able to craft the rest of your collection?
def isCollectionComplete():
    if necessarySouls <= 0:
        return True
    return False


runningSum = 0.0
minPacks = sys.maxsize
maxPacks = 0
for x in range(runs):
    packsOpened = 0
    legendCharges = 0
    while True:
        packsOpened = packsOpened + 1
        legendCharges = legendCharges + 1
        for i in range(6):
            # Guaranteed legend on last card in pack when at full charge.
            # NOTE: Don't know if this happens on full charge or one after.
            #       Currently assuming on full charge.
            if i == 5 and legendCharges == legendaryMaxCharge:
                legendCharges = 0
                getCard(0)
            else:
                card = random.uniform(0,1)
                cardGot = -1
                if card < legendThreshold:
                    cardGot = 0 # Which legend doesn't matter since you always open one you don't have
                    legendCharges = 0
                elif card < epicThreshold:
                    cardGot = random.randint(epicStartIndex, rareStartIndex - 1)
                elif card < rareThreshold or i == 5:
                    cardGot = random.randint(rareStartIndex, commonStartIndex - 1)
                else:
                    cardGot = random.randint(commonStartIndex, commonStartIndex + commonCount - 1)
                getCard(cardGot)

        if isCollectionComplete():
            break

    # Reset collection and souls remaining
    necessarySouls = collectionSoulCraftCost
    for i in range(len(collection)):
        collection[i] = 0

    if packsOpened > maxPacks:
        maxPacks = packsOpened
    if packsOpened < minPacks:
        minPacks = packsOpened
    runningSum = packsOpened + runningSum

    # This slows down the execution a lot, but it'll let you keep track as it goes.
    # print ("Runs: " + str(x+1) + ", Average Packs: " + str(runningSum / float(x+1)) + ", Max Packs: " + str(maxPacks) + ", Min Packs: " + str(minPacks))

print ("Runs: " + str(runs) + ", Average Packs: " + str(runningSum / float(runs)) + ", Max Packs: " + str(maxPacks) + ", Min Packs: " + str(minPacks))
