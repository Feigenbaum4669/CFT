# Checking the version of PYTHON; we only support > 3.5
import sys
import numpy
import decomposer
import walker
if sys.version_info < (3, 5):
    raise Exception('Please use Python version 3.5 or greater.')

# useful additional packages
import matplotlib.pyplot as plt
import numpy as np
from math import pi

# importing the QISKit
from qiskit import QuantumProgram


# import basic plot tools
from qiskit.tools.visualization import plot_histogram

def build_circuit_GCNOT(qp, N, cpattern, initpattern):
    nodeReg = qp.create_quantum_register('node', N + 1)
    readoutReg = qp.create_classical_register('readout', N + 1)
    ancillaReg = qp.create_quantum_register('ancilla', 1)
    walk = qp.create_circuit('test', [nodeReg, ancillaReg], [readoutReg])
    walker.BINARY_PREP_STATE(walk, nodeReg, initpattern)
    walker.add_GCNOT(walk, ancillaReg[0], [nodeReg[i] for i in range(N)], nodeReg[N],cpattern)

    for i in range(N + 1):
        walk.measure(nodeReg[i], readoutReg[i])


def build_circuit_CNOT(qp, N, initpattern):
    nodeReg = qp.create_quantum_register('node', N+1)
    readoutReg = qp.create_classical_register('readout', N+1)
    ancillaReg = qp.create_quantum_register('ancilla', 1)
    walk = qp.create_circuit('test', [nodeReg, ancillaReg], [readoutReg])
    walker.BINARY_PREP_STATE(walk, nodeReg, initpattern)
    walker.add_CNOT(walk, ancillaReg[0],  [nodeReg[i] for i in range(N)], nodeReg[N])


    for i in range(N+1):
        walk.measure(nodeReg[i], readoutReg[i])


def build_circuit_C_INCR(qp, N,flag, initpattern, iter):
    nodeReg = qp.create_quantum_register('node', N+1)
    readoutReg = qp.create_classical_register('readout', N+2)
    ancillaReg = qp.create_quantum_register('ancilla', 1)
    walk = qp.create_circuit('test', [nodeReg, ancillaReg], [readoutReg])
    walker.BINARY_PREP_STATE(walk, nodeReg, initpattern)
    for i in range(iter):
        walker.add_C_INCREMENT(walk, [nodeReg[i] for i in range(N)], nodeReg[N], ancillaReg[0], flag)

    for i in range(N+1):
        walk.measure(nodeReg[i], readoutReg[i])

    walk.measure(ancillaReg[0], readoutReg[N+1])

def build_circuit_C_DECR(qp, N,flag, initpattern, iter):
    nodeReg = qp.create_quantum_register('node', N+1)
    readoutReg = qp.create_classical_register('readout', N+2)
    ancillaReg = qp.create_quantum_register('ancilla', 1)
    walk = qp.create_circuit('test', [nodeReg, ancillaReg], [readoutReg])
    walker.BINARY_PREP_STATE(walk, nodeReg, initpattern)
    for i in range(iter):
        walker.add_C_DECREMENT(walk, [nodeReg[i] for i in range(N)], nodeReg[N], ancillaReg[0], flag)

    for i in range(N+1):
        walk.measure(nodeReg[i], readoutReg[i])

    walk.measure(ancillaReg[0], readoutReg[N+1])

def  build_circuit_C_MOD_GROVER_STATE_PREP(qp, d, c):
    nodeReg = qp.create_quantum_register('node', c+1)
    ancillaReg = qp.create_quantum_register('ancilla', 1)
    readoutReg = qp.create_classical_register('readout', c)
    walk = qp.create_circuit('test', [nodeReg, ancillaReg], [readoutReg])
    walk.x(nodeReg[0])
    walker.C_MOD_GROVER_STATE_PREP(walk,[nodeReg[i] for i in range(1,c+1)], d, nodeReg[0], ancillaReg[0])
    "modyfikacja- pierwotnie: patrz przypadek ADJ"
    for i in range(c):
        walk.measure(nodeReg[i+1], readoutReg[i])

    "walk.measure(ancillaReg[0], readoutReg[c+1])"

def build_circuit_C_MOD_GROVER_COIN(qp, d, c):

    nodeReg = qp.create_quantum_register('node', c)
    controlReg=qp.create_quantum_register('control', 1)
    ancillaReg = qp.create_quantum_register('ancilla', 1)
    readoutReg = qp.create_classical_register('readout', c )
    walk = qp.create_circuit('test', [nodeReg, controlReg, ancillaReg], [readoutReg])
    walk.x(controlReg[0])
    walker.C_MOD_GROVER_COIN(walk, nodeReg, d, controlReg[0], ancillaReg[0])

    """
    modyfikacja
    walk.measure(controlReg[0], readoutReg[0])
    """
    for i in range(c):
        walk.measure(nodeReg[i], readoutReg[i])
    """
    walk.measure(ancillaReg[0], readoutReg[c + 1])
    """

def  build_circuit_ADJ_C_MOD_GROVER_STATE_PREP(qp, d, c):
    nodeReg = qp.create_quantum_register('node', c + 1)
    ancillaReg = qp.create_quantum_register('ancilla', 1)
    readoutReg = qp.create_classical_register('readout', c + 2)
    walk = qp.create_circuit('test', [nodeReg, ancillaReg], [readoutReg])
    walk.x(nodeReg[0])
    walker.ADJ_C_MOD_GROVER_STATE_PREP(walk, [nodeReg[i] for i in range(1, c + 1)], d, nodeReg[0], ancillaReg[0])
    walker.C_MOD_GROVER_STATE_PREP(walk, [nodeReg[i] for i in range(1, c + 1)], d, nodeReg[0], ancillaReg[0])

    for i in range(c + 1):
        walk.measure(nodeReg[i], readoutReg[i])

    walk.measure(ancillaReg[0], readoutReg[c + 1])

def build_circuit_C_GROVER_DIFF_OPER(qp,c, initpattern):
    nodeReg = qp.create_quantum_register('node', c+1)
    readoutReg = qp.create_classical_register('readout', c+2)
    ancillaReg = qp.create_quantum_register('ancilla', 1)
    walk = qp.create_circuit('test', [nodeReg, ancillaReg], [readoutReg])
    walker.BINARY_PREP_STATE(walk, nodeReg, initpattern)

    for i in range(1,c+1):
        walk.h(nodeReg[i])


    walker.add_C_GROVER_DIFF_OPER(walk, [nodeReg[i] for i in range(1,c+1)], nodeReg[0], ancillaReg[0])

    for i in range(1,c+1):
        walk.h(nodeReg[i])


    for i in range(c+1):
        walk.measure(nodeReg[i], readoutReg[i])

    walk.measure(ancillaReg[0], readoutReg[c + 1])


def test_circuit_CNOT(N, sh):
    Q_program = QuantumProgram()
    pattern = numpy.ones((N + 1), dtype=bool)
    pattern[0] = False
    pattern[1] = False
    pattern[2] = False
    pattern[3] = True
    build_circuit_CNOT(Q_program, N, pattern)
    result = Q_program.execute(["test"], backend="local_qasm_simulator",shots=sh, silent = True)
    plot_histogram(result.get_counts('test'))


def test_circuit_GCNOT(N, sh):
    Q_program = QuantumProgram()
    initpattern = numpy.zeros((N + 1), dtype=bool)
    cpattern = numpy.zeros((N), dtype=bool)
    cpattern[0]=True
    cpattern[1] = True
    cpattern[2] = False
    initpattern[0] = True
    initpattern[1] = True
    initpattern[2] = False
    initpattern[3] = True
    build_circuit_GCNOT(Q_program, N, cpattern, initpattern)
    result = Q_program.execute(["test"], backend="local_qasm_simulator",shots=sh, silent = True)
    plot_histogram(result.get_counts('test'))
"""
test_circuit_GCNOT(3, 10)
"""

def test_circuit_C_INCR(N,flag, sh, iter):
    Q_program = QuantumProgram()
    initpattern = numpy.zeros((N + 1), dtype=bool)
    cpattern = numpy.zeros((N), dtype=bool)
    initpattern[0] = False
    initpattern[1] = False
    initpattern[2] = False
    initpattern[3] = True
    build_circuit_C_INCR(Q_program, N,flag, initpattern, iter)
    result = Q_program.execute(["test"], backend="local_qasm_simulator",shots=sh, silent = True)
    plot_histogram(result.get_counts('test'))

def test_circuit_C_DECR(N,flag, sh, iter):
    Q_program = QuantumProgram()
    initpattern = numpy.zeros((N + 1), dtype=bool)
    cpattern = numpy.zeros((N), dtype=bool)
    initpattern[0] = False
    initpattern[1] = False
    initpattern[2] = False
    initpattern[3] = True
    build_circuit_C_DECR(Q_program, N,flag, initpattern, iter)
    result = Q_program.execute(["test"], backend="local_qasm_simulator",shots=sh, silent = True)
    plot_histogram(result.get_counts('test'))

def test_circuit_C_MOD_GROVER_STATE_PREP(d,c,sh):
    Q_program = QuantumProgram()

    build_circuit_C_MOD_GROVER_STATE_PREP(Q_program,d,c)
    result = Q_program.execute(["test"], backend="local_qasm_simulator",shots=sh, silent = True)
    plot_histogram(result.get_counts('test'))

def test_circuit_ADJ_C_MOD_GROVER_STATE_PREP(d,c,sh):
    Q_program = QuantumProgram()

    build_circuit_ADJ_C_MOD_GROVER_STATE_PREP(Q_program, d, c)
    result = Q_program.execute(["test"], backend="local_qasm_simulator",shots=sh, silent = True)
    plot_histogram(result.get_counts('test'))

"""
test_circuit_ADJ_C_MOD_GROVER_STATE_PREP(5,3,1000)
"""

def test_circuit_C_GROVER_DIFF_OPER(c,sh):
    Q_program = QuantumProgram()
    initpattern = numpy.zeros((c+1), dtype=bool)
    initpattern[0]=True
    build_circuit_C_GROVER_DIFF_OPER(Q_program,c, initpattern)
    result = Q_program.execute(["test"], backend="local_qasm_simulator", shots=sh, silent=True)
    plot_histogram(result.get_counts('test'))

"""
test_circuit_C_GROVER_DIFF_OPER(3, 1000)
"""

def test_circuit_C_MOD_GROVER_COIN(d,c,sh):
    Q_program = QuantumProgram()

    build_circuit_C_MOD_GROVER_COIN(Q_program, d, c)
    result = Q_program.execute(["test"], backend="local_qasm_simulator",shots=sh, silent = True)
    plot_histogram(result.get_counts('test'))
"""
test_circuit_C_MOD_GROVER_COIN(5,3,1000)
"""
"""
plot_histogram({"000":0.439, "001": 0.137, "010":0.115 ,"011":0.199, "100":0.051,"101":0.014, "110":0.01 ,"111":0})

"""
"""
test_circuit_C_MOD_GROVER_COIN(5,3,100000)
"""


