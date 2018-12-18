import numpy as np
import matplotlib.pyplot as plt
import numpy.ma as ma
import quantumWalker
import classicWalker
import math
import random
import os
import json

def start():
    print("----------QUANTUM WALKER----------")
    print("Program do klasycznych i kwantowych spacerów na grafach pełnych, cyklicznych i typu lollipop.")
    print("Wszystkie spacery rozpoczynają się w wierzchołku 0.")
    print("Autor: Oskar Słowik")
    print("Proszę wpisać (exit) aby wyjść z programu.")
    kind()

def kind():
    ans = input("Prosze podać rodzaj symulacji: 1 - klasyczna, 2- kwantowa:")
    if ans == "1":
        classic()
    elif ans=="2":
        quantum()
    elif ans=="exit":
        exit()
    else:
        print("Błędny wybór. Proszę spróbować jeszcze raz lub wpisać (exit) aby wyjść.")
        kind()

def getDataQuantum():
    bck=input("Prosze podać rodzaj backendu: 1 - lokalny symulator unitarny, 2 - procesor 5 - kubitowy IBMQ:")
    N=int(input("Prosze podać rozmiar grafu N:"))
    sh = int(input("Prosze podać ilość uśrednień sh:"))
    k = int(input("Prosze podać ilość kroków spaceru k:"))
    return bck, N, sh, k

def getDataClassic():
    N=int(input("Prosze podać rozmiar grafu N:"))
    sh = int(input("Prosze podać ilość uśrednień sh:"))
    k = int(input("Prosze podać ilość kroków spaceru k:"))
    return  N, sh, k

def classic():
    ans = input("Prosze podać rodzaj grafu do symulacji: 1 - graf pełny, 2 - graf cykliczny, 3 - graf typu lollipop:")
    pdSave = input("Czy zapisać rozkład do pliku? (t/n):")
    if (pdSave == "t"):
        pdFileName = input("Prosze podac nazwę pliku:")
    display = input("Czy wyświetlić rozkład prawdopodobieństwa? (t/n):")
    if ans == "1":
        N, sh, k = getDataClassic()
        pd = classicWalker.classicWalkCliquePD(N,0, k, sh)
        if (display == "t"):
            plotBarNoTresh(pd, "black")
    elif ans == "2":
        N, sh, k = getDataClassic()
        pd= classicWalker.classicWalkCyclePD(N,0, k, sh)
        if (display == "t"):
            plotBar(pd,N, "black")
    elif ans == "3":
         type=getTypeClassic()
         N, sh, k = getDataClassic()
         if(type=="1"):
            pd = classicWalker.classicWalkLolliPD(N, 0, k, sh)
         else:
            pd = classicWalker.classicWalkLollipopModPD(N, 0,0, k, sh)
         if (display == "t"):
             plotBarNoTresh(pd, "black")
    elif ans == "exit":
        exit()
    else:
        print("Błędny wybór. Proszę spróbować jeszcze raz lub wpisać (exit) aby wyjść.")
        quantum()
    if (pdSave == "t"):
        append_record(pd, pdFileName)
        print("Zapisano rozkład prawdopodobieństwa do pliku.")





def getTypeClassic():
    ans = input("Prosze podać typ symulacji klasycznej: 1 - zwykła, 2 - zmodyfikowana.")
    if ans == "1":
        return "1"
    else:
        return "2"

def quantum():
    ans = input("Prosze podać rodzaj grafu do symulacji: 1 - graf pełny, 2 - graf cykliczny, 3 - graf typu lollipop:")
    if ans == "1":
        bck, N, sh, k= getDataQuantum()
        quantumClique(bck,N, sh,k)
    elif ans == "2":
        bck, N, sh, k = getDataQuantum()
        quantumCycle(bck, N, sh, k)
    elif ans=="3":
        bck, N, sh, k = getDataQuantum()
        quantumLolli(bck, N, sh, k)
    elif ans=="exit":
        exit()
    else:
        print("Błędny wybór. Proszę spróbować jeszcze raz lub wpisać (exit) aby wyjść.")
        quantum()

def convTresh(no, tr):
    if(no>tr):
        return no-2*tr
    else:
        return no

def append_record(record, file):
    with open(file, 'a') as f:
        json.dump(record, f)
        f.write(os.linesep)

def toNumber(str, N):
    full=math.pow(2,N-1)
    return [convTresh(int(el,2),full) for el in str]

def toNumberNoTresh(str):
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

def quantumClique(bck,N, sh,iter):
    qasmSave = input("Czy zapisać kod QASM obwodu do pliku? (t/n):")
    if(qasmSave=="t"):
        qasmFileName = input("Prosze podac nazwę pliku:")
    pdSave = input("Czy zapisać rozkład do pliku? (t/n):")

    if (pdSave == "t"):
        pdFileName = input("Prosze podac nazwę pliku:")
    display =input("Czy wyświetlić rozkład prawdopodobieństwa? (t/n):")
    if qasmSave=="t":
        pd, qasm =quantumWalker.perform_walk_clique(N, iter, sh,bck,True)
    elif qasmSave=="n":
        pd, qasm =quantumWalker.perform_walk_clique(N, iter, sh,bck, False)
    elif display=="exit":
        exit()
    else:
        print("Błędny wybór. Proszę spróbować jeszcze raz lub wpisać (exit) aby wyjść.")
        pd, qasm=quantumClique(bck, N, sh, iter)
    if(qasmSave=="t"):
        append_record(qasm,qasmFileName)
        print("Zapisano kod QASM obwodu do pliku.")
    if (pdSave == "t"):
        append_record(pd, pdFileName)
        print("Zapisano rozkład prawdopodobieństwa do pliku.")
    if(display=="t"):
        plotBarNoTresh(pd, "blue")

def quantumCycle(bck,N, sh,iter):
    qasmSave = input("Czy zapisać kod QASM obwodu do pliku? (t/n):")
    if (qasmSave == "t"):
        qasmFileName = input("Prosze podac nazwę pliku:")
    pdSave = input("Czy zapisać rozkład do pliku? (t/n):")

    if (pdSave == "t"):
        pdFileName = input("Prosze podac nazwę pliku:")
    display = input("Czy wyświetlić rozkład prawdopodobieństwa? (t/n):")
    if  qasmSave=="t":
        pd, qasm =quantumWalker.perform_walk_cycle(N, iter, sh,bck,True)
    elif  qasmSave=="n":
        pd, qasm =quantumWalker.perform_walk_cycle(N, iter, sh,bck, False)
    elif display=="exit":
        exit()
    else:
        print("Błędny wybór. Proszę spróbować jeszcze raz lub wpisać (exit) aby wyjść.")
        pd, qasm=quantumCycle(bck, N, sh, iter)
    if(qasmSave=="t"):
         append_record(qasm,qasmFileName)
         print("Zapisano kod QASM obwodu do pliku.")
    if (pdSave == "t"):
        append_record(pd, pdFileName)
        print("Zapisano rozkład prawdopodobieństwa do pliku.")
    if(display=="t"):
         plotBar(pd,N, "blue")

def quantumLolli(bck,N, sh,iter):
    qasmSave = input("Czy zapisać kod QASM obwodu do pliku? (t/n):")
    if(qasmSave=="t"):
        qasmFileName = input("Prosze podac nazwę pliku:")
    pdSave = input("Czy zapisać rozkład do pliku? (t/n):")

    if (pdSave == "t"):
        pdFileName = input("Prosze podac nazwę pliku:")
    display = input("Czy wyświetlić rozkład prawdopodobieństwa? (t/n):")
    if qasmSave=="t":
        pd, qasm =quantumWalker.perform_walk_lollipop(N, iter, sh,bck,True)
    elif qasmSave=="n":
        pd, qasm =quantumWalker.perform_walk_lollipop(N, iter, sh,bck, False)
    elif display=="exit":
        exit()
    else:
        print("Błędny wybór. Proszę spróbować jeszcze raz lub wpisać (exit) aby wyjść.")
        pd, qasm=quantumLolli(bck, N, sh, iter)
    if(qasmSave=="t"):
        append_record(qasm,qasmFileName)
        print("Zapisano kod QASM obwodu do pliku.")
    if (pdSave == "t"):

        append_record(pd, pdFileName)
        print("Zapisano rozkład prawdopodobieństwa do pliku.")
    if(display=="t"):
        plotBarNoTresh(pd, "blue")









start()





