import matplotlib.pyplot as plt
from IPython import display

import networkx as nx
import numpy as np
import pandas as pd
import time

from typing import List
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import ParameterVector
from qiskit.quantum_info import SparsePauliOp
from qiskit_aer import AerSimulator

from build_graph import build_ansatz, build_maxcut_hamiltonian
from varQITE import QITEvolver

from generate_graph import cycle_graph_c8, complete_bipartite_graph_k88, complete_bipartite_graph_k_nn, regular_graph_4_8, cubic_graph_3_16, random_connected_graph_16, expander_graph_n

def main():
    # show graph
    graph1 = cycle_graph_c8() 
    graph2 = complete_bipartite_graph_k88() 
    graph3 = complete_bipartite_graph_k_nn(5) 
    graph4 = regular_graph_4_8() 
    graph5 = cubic_graph_3_16() 
    graph6 = random_connected_graph_16(p=0.18)
    graph7 = expander_graph_n(16) 
    #graph8 = -> make your own cool graph

    # input graph
    graph = graph4
    ham = build_maxcut_hamiltonian(graph)
    ansatz = build_ansatz(graph)

    # Set up your QITEvolver and evolve!
    qit_evolver = QITEvolver(ham, ansatz)
    qit_evolver.evolve(num_steps=40, lr=0.1, verbose=True) # lr was 0.5

    # Visualize your results!
    qit_evolver.plot_convergence()



if __name__ == "__main__":
    main()