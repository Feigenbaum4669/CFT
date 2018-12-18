# Checking the version of PYTHON; we only support > 3.5
import sys
import decomposer
import numpy
import math
import os
import json
if sys.version_info < (3, 5):
    raise Exception('Please use Python version 3.5 or greater.')

# useful additional packages
import matplotlib.pyplot as plt
import numpy as np
from math import pi

# importing the QISKit
from qiskit import QuantumProgram
import Qconfig
import classicWalker


# import basic plot tools
#from qiskit.tools.visualization import plot_histogram

def C_MOD_GROVER_COIN(circuit, target,d, control, ancilla):


    ADJ_C_MOD_GROVER_STATE_PREP(circuit, target, d, control, ancilla)
    add_C_GROVER_DIFF_OPER(circuit, target, control, ancilla)
    C_MOD_GROVER_STATE_PREP(circuit, target, d, control, ancilla)

def add_C_GROVER_DIFF_OPER(circuit, target, control, ancilla):
    c=len(target)
    controls=[control]+[target[i] for i in range(c-1)]
    pattern=np.append(np.ones((1), dtype=bool),np.zeros((c-1), dtype=bool))
    circuit.x(target[c-1])
    circuit.h(target[c-1])
    add_GCNOT(circuit, ancilla, controls, target[c-1],pattern)
    circuit.h(target[c-1])
    circuit.x(target[c-1])
    "sign flip"
    circuit.z(target[c-1])
    circuit.x(target[c-1])
    circuit.z(target[c-1])
    circuit.x(target[c-1])

def BINARY_PREP_STATE(circuit,reg, pattern):
    count=0
    for bit in pattern:
        if bit:
            circuit.x(reg[count])
        count=count+1

def C_MOD_GROVER_STATE_PREP(circuit, target,d, control, ancilla):
    c=len(target)
    theta=2.0*numpy.arcsin(1.0/numpy.sqrt(d))
    circuit.cu3(theta, 0, 0, control,  target[c-1])
    circuit.x(target[c - 1])
    circuit.ccx(control, target[c - 1], ancilla)
    for i in range(c-1):
        circuit.ch(ancilla, target[i])
    "uncompute ancilla"
    circuit.ccx(control, target[c - 1], ancilla)
    circuit.x(target[c - 1])

def ADJ_C_MOD_GROVER_STATE_PREP(circuit, target,d, control, ancilla):
    c=len(target)
    theta=-2.0*numpy.arcsin(1.0/numpy.sqrt(d))
    circuit.x(target[c - 1])
    circuit.ccx(control, target[c - 1], ancilla)
    for i in range(c - 1):
        circuit.ch(ancilla, target[i])
    "uncompute ancilla"
    circuit.ccx(control, target[c - 1], ancilla)
    circuit.x(target[c - 1])
    circuit.cu3(theta, 0, 0, control,  target[c-1])

def mapAINCR(no, size, target, ancilla, control):
    if no==0:
        ret=control
    if no<=size and no>0:
        ret=target[no-1]
    if no==size+1:
        ret=ancilla
    return ret

def mapCNOT(no, size, ancilla, controls, target):
    if no<size:
        ret=controls[no]
    if no==size:
        ret=target
    if no>size:
        ret=ancilla
    return ret

def add_CNOT(circuit, ancilla, controls, target):
    N = len(controls)
    controlsDec = list(range(N))
    targetDec = N
    borrows = [N+1]
    decomposed = decomposer.reduce_cnot(controlsDec, targetDec, borrows)
    for c, x in decomposed:
        circuit.ccx(mapCNOT(c[0], N, ancilla, controls, target), mapCNOT(c[1],  N, ancilla, controls, target), mapCNOT(x[0],  N, ancilla, controls, target))


def add_GCNOT(circuit, ancilla, controls, target, cpattern):
    BINARY_PREP_STATE(circuit, controls, np.invert(cpattern))
    add_CNOT(circuit, ancilla, controls, target)
    BINARY_PREP_STATE(circuit, controls, np.invert(cpattern))

def add_AINCREMENT(circuit, ancilla,control, target):
    N=len(target)
    increments=list(range(N+1))
    borrows=[N+1]
    decomposed=decomposer.reduce_increment(increments, borrows)
    for c, x in decomposed:
        if len(c)==0:
            for xx in x:
                circuit.x(mapAINCR(xx,N, target, ancilla, control))
        if len(c)==1:
            circuit.cx(mapAINCR(c[0],N, target, ancilla, control),mapAINCR(x[0],N, target, ancilla, control))
        if len(c)==2:
            circuit.ccx(mapAINCR(c[0], N, target, ancilla, control),mapAINCR(c[1], N, target, ancilla, control), mapAINCR(x[0], N, target, ancilla, control))


def add_C_INCREMENT(circuit, target, control, ancilla, flag):
        if not flag:
            circuit.x(control)

        add_AINCREMENT(circuit, ancilla,control, target)
        circuit.x(control)

        if not flag:
            circuit.x(control)

def add_ADECREMENT(circuit, ancilla,control, target):
    n=len(target)
    for i in range(n):
        circuit.x(target[i])

    add_AINCREMENT(circuit, ancilla,control, target)

    for i in range(n):
        circuit.x(target[i])
    circuit.x(control)


def add_C_DECREMENT(circuit, target, control, ancilla, flag):
    if not flag:
        circuit.x(control)

    add_ADECREMENT(circuit, ancilla,control, target)


    if not flag:
        circuit.x(control)



def build_circuit_cycle(qp, N, iter):
    nodeReg=qp.create_quantum_register('node', N)
    readoutReg=qp.create_classical_register('readout', N)
    subnodeReg=qp.create_quantum_register('subnode',1)
    ancillaReg=qp.create_quantum_register('ancilla',1)
    walk = qp.create_circuit('walk', [nodeReg,subnodeReg,ancillaReg], [readoutReg])

    for i in range(iter):
        walk.h(subnodeReg[0])
        add_C_INCREMENT(walk,nodeReg,subnodeReg[0], ancillaReg[0], True)
        add_C_DECREMENT(walk,nodeReg,subnodeReg[0], ancillaReg[0], False)

    for i in range(N):
        walk.measure(nodeReg[i], readoutReg[i])


def build_circuit_clique(qp, N, iter):
    nodeReg = qp.create_quantum_register('node', N)
    subnodeReg = qp.create_quantum_register('subnode', N)
    readoutReg = qp.create_classical_register('readout', N)
    walk = qp.create_circuit('walk', [nodeReg, subnodeReg], [readoutReg])

    for i in range(iter):
        for i in range(N):
            walk.h(subnodeReg[i])
        for i in range(N):
            walk.swap(nodeReg[i], subnodeReg[i])

    for i in range(N):
        walk.measure(nodeReg[i], readoutReg[i])


def build_circuit_lollipop(qp, N, iter):
    nodeReg = qp.create_quantum_register('node', N+1)
    "readoutReg = qp.create_classical_register('readout', 2*N + 10)"
    readoutReg = qp.create_classical_register('readout', 2*N + 3)
    subnodeReg = qp.create_quantum_register('subnode', N+2)
    ancillaReg = qp.create_quantum_register('ancilla', 7)
    walk = qp.create_circuit('walk', [nodeReg, subnodeReg, ancillaReg], [readoutReg])

    for i in range(iter):
        print("Iteration:" + repr(i+1))
        pattern=np.append(np.ones((N), dtype=bool), np.zeros((1), dtype=bool))

        """compute logic ancillas"""
        add_GCNOT(walk,ancillaReg[5],[nodeReg[i] for i in range(N+1)],ancillaReg[2],pattern)
        add_CNOT(walk, ancillaReg[5], [nodeReg[i] for i in range(N + 1)], ancillaReg[4])

        walk.x(nodeReg[N])
        walk.cx(nodeReg[N], ancillaReg[0])
        walk.x(nodeReg[N])
        walk.x(ancillaReg[2])
        walk.ccx(ancillaReg[2], ancillaReg[0], ancillaReg[1])
        walk.x(ancillaReg[2])
        walk.x(ancillaReg[4])
        walk.x(ancillaReg[0])
        walk.ccx(ancillaReg[4], ancillaReg[0], ancillaReg[3])
        walk.x(ancillaReg[4])
        walk.x(ancillaReg[0])

        """subnode space evolution"""
        for i in range(N):
            walk.ch(ancillaReg[1], subnodeReg[i])

        C_MOD_GROVER_COIN(walk, [subnodeReg[i] for i in range(N + 1)], math.pow(2, N) + 1, ancillaReg[2], ancillaReg[5])
        walk.ch(ancillaReg[3], subnodeReg[N+1])
        walk.cx(ancillaReg[4], subnodeReg[N+1])

        """node space evolution"""
        for i in range(N):
            walk.cswap(ancillaReg[1], nodeReg[i], subnodeReg[i])

        for i in range(N+1):
            walk.cswap(ancillaReg[2], nodeReg[i], subnodeReg[i])

        walk.ccx(ancillaReg[3], subnodeReg[N+1], ancillaReg[6])
        add_C_INCREMENT(walk, [nodeReg[i] for i in range(N+1)], ancillaReg[6], ancillaReg[5], True)
        walk.ccx(ancillaReg[3], subnodeReg[N + 1], ancillaReg[6])

        walk.x(subnodeReg[N+1])
        walk.ccx(ancillaReg[3], subnodeReg[N + 1], ancillaReg[6])
        add_C_DECREMENT(walk, [nodeReg[i] for i in range(N + 1)], ancillaReg[6], ancillaReg[5], True)
        walk.ccx(ancillaReg[3], subnodeReg[N + 1], ancillaReg[6])
        walk.x(subnodeReg[N + 1])
        add_C_DECREMENT(walk, [nodeReg[i] for i in range(N + 1)], ancillaReg[4], ancillaReg[5], True)

        """uncompute logic ancillas"""
        """uncompute ancilla 3"""
        walk.x(ancillaReg[4])
        walk.x(ancillaReg[0])
        walk.ccx(ancillaReg[4],ancillaReg[0], ancillaReg[3])
        walk.x(ancillaReg[4])
        walk.x(ancillaReg[0])
        """uncompute ancilla 0"""
        walk.cx(ancillaReg[1], ancillaReg[0])
        walk.cx(ancillaReg[2], ancillaReg[0])
        """uncompute ancilla 4"""
        pattern=np.append(np.zeros((1), dtype=bool), np.append(np.ones((N), dtype=bool),np.zeros((1), dtype=bool)))
        add_GCNOT(walk, ancillaReg[5], [nodeReg[i] for i in range(N + 1)]+[subnodeReg[N+1]], ancillaReg[4], pattern)
        """uncompute ancilla 2"""
        pattern0 = np.append(np.zeros((N), dtype=bool), np.append(np.ones((1), dtype=bool), np.ones((1), dtype=bool)))
        add_GCNOT(walk, ancillaReg[5], [nodeReg[i] for i in range(N + 1)] + [subnodeReg[N + 1]], ancillaReg[2], pattern0)
        pattern1 = np.append(np.ones((N), dtype=bool), np.zeros((1), dtype=bool))
        add_GCNOT(walk, ancillaReg[5], [nodeReg[i] for i in range(N + 1)] , ancillaReg[6], pattern1)
        pattern2=np.append(np.zeros((1), dtype=bool), np.append(np.ones((N), dtype=bool), np.zeros((2), dtype=bool)))
        add_GCNOT(walk, ancillaReg[5], [nodeReg[N]]+[subnodeReg[i] for i in range(N + 1)]+[ancillaReg[6]], ancillaReg[2], pattern2)
        add_GCNOT(walk, ancillaReg[5], [nodeReg[i] for i in range(N + 1)], ancillaReg[6], pattern1)
        """uncompute ancilla 1"""
        pattern1 = np.append(np.ones((N), dtype=bool),np.zeros((1), dtype=bool))
        add_GCNOT(walk, ancillaReg[5], [subnodeReg[i] for i in range(N + 1)], ancillaReg[6], pattern1)
        pattern2 = np.zeros((3), dtype=bool)
        add_GCNOT(walk, ancillaReg[5], [nodeReg[N]]+[subnodeReg[N]]+[ancillaReg[6]], ancillaReg[1], pattern2)
        add_GCNOT(walk, ancillaReg[5], [subnodeReg[i] for i in range(N + 1)], ancillaReg[6], pattern1)




    for i in range(N+1):
        walk.measure(nodeReg[i], readoutReg[i])
        """
    for i in range(N+1,2*N+3):
        walk.measure(subnodeReg[i-N-1], readoutReg[i])
        """
        """
    for i in range(2*N+3,2*N+10):
        walk.measure(ancillaReg[i-2*N-3], readoutReg[i])
        """


def normalizeCounts(dict,shots):
    keys=dict.keys()

    for key in keys:
        dict[key]=dict[key]/shots

    return dict




def getHittingTimeCycle(N,sh,target,Tmax, pr):
    T=0
    stop=False
    while T<Tmax and not stop:
        T = T + 1
        print("Step " + repr(T))
        Q_program = QuantumProgram()
        build_circuit_cycle(Q_program, N, T)
        result = Q_program.execute(["walk"], backend="local_qasm_simulator", shots=sh, silent=True)
        counts = result.get_counts('walk')
        Ncounts = normalizeCounts(counts, sh)
        pe=Ncounts.get(target, 0)
        print(Ncounts)
        if(pe>0):
            print("Target reached with pe="+repr(pe))
        if pe>=pr:
            stop=True
    if(stop):
        print("Target hit at T="+repr(T))
    else:
        print("Target not hit after Tmax steps")

def append_record(record, file):
    with open(file, 'a') as f:
        json.dump(record, f)
        f.write(os.linesep)

def display_results(file):
    with open(file) as f:
        for line in f:
            plot_histogram(json.loads(line))

def display_resultsBar(file,N):
    with open(file) as f:
        for line in f:
            classicWalker.plotBar(json.loads(line),N)

def display_resultsBarNoTresh(file):
    with open(file) as f:
        for line in f:
            classicWalker.plotBarNoTresh(json.loads(line))


def get_hitting_time(file, target, pr):
    T=0
    stop=False
    with open(file) as f:
        T=T+1
        for line in f:
            Ncounts=json.loads(line)
            pe = Ncounts.get(target, 0)
            if (pe > 0):
                print("Target reached after "+repr(T)+"steps with pe=" + repr(pe))
            if pe >= pr:
                stop=True
                break
        if (stop):
            print("Target hit at T=" + repr(T))
        else:
            print("Target not hit after Tmax steps")

def perform_walks_clique(N, sh, I, T, file):
    for iter in range(I, T):
        print("Step " + repr(iter))
        Q_program = QuantumProgram()
        build_circuit_clique(Q_program, N, iter)
        result = Q_program.execute(["walk"], backend="local_qasm_simulator", shots=sh, silent=True)
        counts = result.get_counts('walk')
        Ncounts = normalizeCounts(counts, sh)
        append_record(Ncounts, file)


def perform_walks_cycle(N, sh, I, T, file):
    for iter in range(I, T):
        print("Step " + repr(iter))
        Q_program = QuantumProgram()
        build_circuit_cycle(Q_program, N, iter)
        result = Q_program.execute(["walk"], backend="local_qasm_simulator", shots=sh, silent=True)
        counts = result.get_counts('walk')
        Ncounts = normalizeCounts(counts, sh)
        append_record(Ncounts, file)

def perform_walks_lollipop(N, sh, I, T, file):
    for iter in range(I, T):
        print("Step " + repr(iter))
        Q_program = QuantumProgram()
        build_circuit_lollipop(Q_program, N, iter)
        result = Q_program.execute(["walk"], backend="local_qasm_simulator", shots=sh, silent=True)
        counts = result.get_counts('walk')
        Ncounts = normalizeCounts(counts, sh)
        append_record(Ncounts, file)


def perform_walk_clique(N, iter, sh,bck,genQASM):
    Q_program = QuantumProgram()
    if(bck=="1"):
        backnd='local_qasm_simulator'
    else:
        backnd = 'ibmqx2'
        Q_program.set_api(Qconfig.APItoken, Qconfig.config['url'])


    print("Trwa generowanie obwodu kwantowego...")
    build_circuit_clique(Q_program, N, iter)
    QASM=None
    if(genQASM):
        qobj= Q_program.compile(['walk'],backend=backnd )
        QASM=Q_program.get_compiled_qasm(qobj,'walk')
    print("Obwód kwantowy wygenerowany. Trwa uruchamianie spaceru...")
    result = Q_program.execute(["walk"], backend=backnd, shots=sh, silent=True)
    print("Spacer zakończony.")
    return result.get_counts('walk'), QASM

def perform_walk_cycle(N, iter, sh,bck,genQASM):
    Q_program = QuantumProgram()
    if (bck == "1"):
        backnd = 'local_qasm_simulator'
    else:
        backnd = 'ibmqx2'
        Q_program.set_api(Qconfig.APItoken, Qconfig.config['url'])


    print("Trwa generowanie obwodu kwantowego...")
    build_circuit_cycle(Q_program, N, iter)
    QASM=None
    if (genQASM):
        qobj = Q_program.compile(['walk'], backend=backnd)
        QASM = Q_program.get_compiled_qasm(qobj, 'walk')
    print("Obwód kwantowy wygenerowany. Trwa uruchamianie spaceru...")
    result = Q_program.execute(["walk"], backend=backnd, shots=sh, silent=True)
    print("Spacer zakończony.")
    return result.get_counts('walk'), QASM

def perform_walk_lollipop(N, iter, sh,bck,genQASM):
    Q_program = QuantumProgram()
    if (bck == "1"):
        backnd = 'local_qasm_simulator'
    else:
        backnd = 'ibmqx2'
        Q_program.set_api(Qconfig.APItoken, Qconfig.config['url'])


    print("Trwa generowanie obwodu kwantowego...")
    build_circuit_lollipop(Q_program, N, iter)
    QASM=None
    if (genQASM):
        qobj = Q_program.compile(['walk'], backend=backnd)
        QASM = Q_program.get_compiled_qasm(qobj, 'walk')
    print("Obwód kwantowy wygenerowany. Trwa uruchamianie spaceru...")
    result = Q_program.execute(["walk"], backend=backnd, shots=sh, silent=True)
    print("Spacer zakończony.")
    return result.get_counts('walk'), QASM

