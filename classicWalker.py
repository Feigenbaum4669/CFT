import math
import random
import os
import json
#from qiskit.tools.visualization import plot_histogram
import numpy as np
import matplotlib.pyplot as plt
import numpy.ma as ma


def incr(cs,n):
    if(cs<n-1):
        return cs+1
    else:
        return 0

def decr(cs,n):
    if(cs>0):
        return cs-1
    else:
        return n-1

def coin(d):
    return random.randint(0,d-1)

def normalizeCounts(dict, shots):
    keys = dict.keys()
    for key in keys:
        dict[key] = dict[key] / shots
    return dict

def getHistoZeros(n):
    histo=dict()
    for i in range(n):
        histo[i]=0
    return histo

def getHistoStrKeys(histo, n,N):
    for i in range(n):
        histo[('{0:0'+repr(N)+'b}').format(i)]=histo.pop(i)
    return histo

def getNewStateCycle(currState,n):
    if (coin(2) == 0):
        currState = decr(currState, n)
    else:
        currState = incr(currState, n)
    return currState

def getNewStateClique(n):
    return coin(n)

def getNewStateLollipop(currState,N):
    cliqueSize=math.pow(2,N)
    connNode =cliqueSize-1
    lastNode=cliqueSize*2-1
    if(currState<connNode):
        return coin(cliqueSize)
    elif(currState==connNode):
        return coin(cliqueSize+1)
    elif(currState>connNode and currState<lastNode):
        if(coin(2) == 0):
            currState = currState + 1
        else:
            currState = currState - 1
    else:
        currState=currState-1
    return currState

def modGroverCoin(cliqueSize,currState, subState):
    if(subState>=cliqueSize):
        print("ERROR: wrong subState for modGrover coin!")
        return None, None
    n=cliqueSize+1
    probDiag=(2.0/n-1)*(2.0/n-1)
    U=1000000
    R=probDiag*U
    I=random.randint(0,U)
    if(I<=R):
        return subState, currState
    else:
        avStates=list(range(int(subState)))+list(range(int(subState+1),int(cliqueSize+1)))
        newState=random.choice(avStates)
        return newState, currState

def getNewStateLollipopMod(currState,subState,N):
    cliqueSize=math.pow(2,N)
    connNode =cliqueSize-1
    lastNode=cliqueSize*2-1
    if(currState<connNode):
        return coin(cliqueSize), currState
    elif(currState==connNode):
        return modGroverCoin(cliqueSize,currState, subState)
    elif(currState>connNode and currState<lastNode):
        if(coin(2) == 0):
            currState = currState + 1
        else:
            currState = currState - 1
    else:
        currState=currState-1
    return currState, subState








def classicWalkCycleHT(N,startState, avgSteps,targetState):
    n=int(math.pow(2,N))
    hits=0
    totalSteps=0
    while hits<avgSteps:
        steps = 0
        currState = startState
        while currState!=targetState:
            steps=steps+1
            currState=getNewStateCycle(currState,n)
        hits=hits+1
        totalSteps=totalSteps+steps
    hittingTime=totalSteps/hits
    return hittingTime

def classicWalkCyclePD(N,startState,walkSteps, avgSteps):
    n=int(math.pow(2,N))
    histo=getHistoZeros(n)
    walks=0
    while walks<avgSteps:
        steps=0
        currState = startState

        while steps<walkSteps:
            steps=steps+1
            currState = getNewStateCycle(currState, n)
        walks=walks+1

        histo[currState]=histo[currState]+1
    nHisto=normalizeCounts(histo,walks)
    nHistoStrKeys=getHistoStrKeys(nHisto,n,N)
    return nHistoStrKeys


def classicWalkCliqueHT(N,startState, avgSteps,targetState):
    n=int(math.pow(2,N))
    hits=0
    totalSteps=0
    while hits<avgSteps:
        steps = 0
        currState = startState
        while currState!=targetState:
            steps=steps+1
            currState=getNewStateClique(n)
        hits=hits+1
        totalSteps=totalSteps+steps
    hittingTime=totalSteps/hits
    return hittingTime

def classicWalkCliquePD(N,startState,walkSteps, avgSteps):
    n=int(math.pow(2,N))
    histo=getHistoZeros(n)
    walks=0
    while walks<avgSteps:
        steps=0
        currState = startState

        while steps<walkSteps:
            steps=steps+1
            currState = getNewStateClique(n)
        walks=walks+1

        histo[currState]=histo[currState]+1
    nHisto=normalizeCounts(histo,walks)
    nHistoStrKeys=getHistoStrKeys(nHisto,n,N)
    return nHistoStrKeys

def classicWalkLollipopHT(N,startState, avgSteps,targetState):
    n=int(math.pow(2,N+1))
    hits=0
    totalSteps=0
    while hits<avgSteps:
        steps = 0
        currState = startState
        while currState!=targetState:
            steps=steps+1
            currState=getNewStateLollipop(currState,N)
        hits=hits+1
        totalSteps=totalSteps+steps
    hittingTime=totalSteps/hits
    return hittingTime

def classicWalkLollipopPD(N,startState,walkSteps, avgSteps):
    n=int(math.pow(2,N+1))
    histo=getHistoZeros(n)
    walks=0
    while walks<avgSteps:
        steps=0
        currState = startState

        while steps<walkSteps:
            steps=steps+1
            currState = getNewStateLollipop(currState,N)
        walks=walks+1

        histo[currState]=histo[currState]+1
    nHisto=normalizeCounts(histo,walks)
    nHistoStrKeys=getHistoStrKeys(nHisto,n,N+1)
    return nHistoStrKeys

def classicWalkLollipopModHT(N,startState,startSumState, avgSteps,targetState):
    n=int(math.pow(2,N+1))
    hits=0
    totalSteps=0
    while hits<avgSteps:
        steps = 0
        currState = startState
        subState = startSumState
        while currState!=targetState:
            steps=steps+1
            currState, subState=getNewStateLollipopMod(currState,subState,N)
        hits=hits+1
        totalSteps=totalSteps+steps
    hittingTime=totalSteps/hits
    return hittingTime

def classicWalkLollipopModPD(N,startState,startSumState,walkSteps, avgSteps):
    n=int(math.pow(2,N+1))
    histo=getHistoZeros(n)
    walks=0
    while walks<avgSteps:
        steps=0
        currState = startState
        subState = startSumState

        while steps<walkSteps:
            steps=steps+1
            currState, subState = getNewStateLollipopMod(currState,subState,N)
        walks=walks+1

        histo[currState]=histo[currState]+1
    nHisto=normalizeCounts(histo,walks)
    nHistoStrKeys=getHistoStrKeys(nHisto,n,N+1)
    return nHistoStrKeys

def convTresh(no, tr):
    if(no>tr):
        return no-2*tr
    else:
        return no

def toNumber(str, N):
    full=math.pow(2,N-1)
    return [convTresh(int(el,2),full) for el in str]

def toNumberNoTresh(str):
    print([int(el,2) for el in str])
    return [int(el,2) for el in str]

def plotBar(hist,N,col):
    plt.bar(toNumber(hist.keys(), N), hist.values(),color=col)
    plt.xlabel("położenie x")
    plt.ylabel("prawdopodobieństwo P(x)")
    plt.show()

def plotBarNoTresh(hist,col):
    plt.bar(toNumberNoTresh(hist.keys()), hist.values(),color=col)
    plt.xlabel("położenie x")
    plt.ylabel("prawdopodobieństwo P(x)")
    plt.show()

def append_record(record, file):
    with open(file, 'a') as f:
        json.dump(record, f)
        f.write(os.linesep)

def zero_to_nan(values):
    """Replace every 0 with 'nan' and return a copy."""
    return [float('nan') if x==0 else x for x in values]

def histoFromFileTresh(file1,N):

    with open(file1) as f1:
        line1=f1.readline()
        hist1 = json.loads(line1)
        x1=toNumber(hist1.keys(), N)
        y1=list(hist1.values())


    plt.bar(x1,y1,color='blue')
    plt.xlabel("położenie x")
    plt.ylabel("prawdopodobieństwo P(x)")
    plt.show()


def histoFromFileNoTresh(file1):

    with open(file1) as f1:
        line1=f1.readline()
        hist1 = json.loads(line1)
        x1=toNumberNoTresh(hist1.keys())
        y1=list(hist1.values())


    plt.bar(x1,y1,color='blue')
    plt.xlabel("położenie x")
    plt.ylabel("prawdopodobieństwo P(x)")
    plt.show()


def doubleHistoFromFileTresh(file1, file2,N):

    with open(file1) as f1:
        line1=f1.readline()
        hist1 = json.loads(line1)
        x1=toNumber(hist1.keys(), N)
        y1=list(hist1.values())

    with open(file2) as f2:
        line2 = f2.readline()
        hist2=json.loads(line2)
        x2 =toNumber(hist2.keys(), N)
        y2 =list(hist2.values())

    plt.bar(x2,y2, color='blue')
    plt.bar(x1, y1, color='black')
    plt.xlabel("położenie x")
    plt.ylabel("prawdopodobieństwo P(x)")
    plt.show()

def doubleHistoFromFileNoTresh(file1, file2):

    with open(file1) as f1:
        line1=f1.readline()
        hist1 = json.loads(line1)
        x1=toNumberNoTresh(hist1.keys())
        y1=list(hist1.values())

    with open(file2) as f2:
        line2 = f2.readline()
        hist2=json.loads(line2)
        x2 =toNumberNoTresh(hist2.keys())
        y2 =list(hist2.values())

    plt.bar(x2,y2, color='blue')
    plt.bar(x1, y1, color='black')
    plt.xlabel("położenie x")
    plt.ylabel("prawdopodobieństwo P(x)")
    plt.show()


def classicCycleWalk(N,I,iter,sh,col):
    file="classic_cycle_"+str(N)+"_"+str(iter)+"_"+str(sh)
    hist=classicWalkCyclePD(N,I,iter,sh)
    append_record(hist, file)
    plotBar(hist,N,col)

def classicCliqueWalk(N,I,iter,sh,col):
    file="classic_clique_"+str(N)+"_"+str(iter)+"_"+str(sh)
    hist=classicWalkCliquePD(N,I,iter,sh)
    append_record(hist, file)
    plotBarNoTresh(hist,col)

def classicLolliWalk(N, I, iter, sh,col):
    file = "classic_lollipop_" + str(N) + "_" + str(I)+"_"+str(iter) + "_" + str(sh)
    hist = classicWalkLollipopPD(N, I, iter, sh)
    append_record(hist, file)
    plotBarNoTresh(hist,col)

def classicModLolliWalk(N, I,Is, iter, sh,col):
    file = "classic_lollipopMod_" + str(N) + "_" +str(I)+"_"+str(Is)+"_"+ str(iter) + "_" + str(sh)
    hist = classicWalkLollipopModPD(N, I,Is, iter, sh)
    append_record(hist, file)
    plotBarNoTresh(hist,col)
