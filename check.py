import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import time

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

from utils import compute_cut_size

def build_solution(qit_evolver, ansatz, graph):
    shots = 100_000

    # Sample your optimized quantum state using Aer
    backend = AerSimulator()
    optimized_state = ansatz.assign_parameters(qit_evolver.param_vals[-1])
    optimized_state.measure_all()
    counts = backend.run(optimized_state, shots=shots).result().get_counts()

    # Find the sampled bitstring with the largest cut value
    cut_vals = sorted(((bs, compute_cut_size(graph, bs)) for bs in counts), key=lambda t: t[1])
    best_bs = cut_vals[-1][0]

    # Now find the most likely MaxCut solution as sampled from your optimized state
    # We'll leave this part up to you!!!
    most_likely_soln, _ = max(counts.items(), key=lambda x: x[1])

    print(counts)

    interpret_solution(graph, best_bs)
    print("Cut value: "+str(compute_cut_size(graph, best_bs)))
    
    
    XS_brut, XS_balanced, XS_connected = get_challenge_solutions(graph)
    print_shots(counts, shots, XS_brut, XS_balanced, XS_connected)

    print("Base score: " + str(final_score(graph,XS_brut,counts,shots,ansatz,'base')))
    print("Balanced score: " + str(final_score(graph,XS_brut,counts,shots,ansatz,'balanced')))
    print("Connected score: " + str(final_score(graph,XS_brut,counts,shots,ansatz,'connected')))
    return most_likely_soln

def interpret_solution(graph, bitstring):
    """
    Visualize the given ``bitstring`` as a partition of the given ``graph``.
    """
    pos = nx.spring_layout(graph, seed=42)
    set_0 = [i for i, b in enumerate(bitstring) if b == '0']
    set_1 = [i for i, b in enumerate(bitstring) if b == '1']

    plt.figure(figsize=(4, 4))
    nx.draw_networkx_nodes(graph, pos=pos, nodelist=set_0, node_color='blue', node_size=700)
    nx.draw_networkx_nodes(graph, pos=pos, nodelist=set_1, node_color='red', node_size=700)

    cut_edges = []
    non_cut_edges = []
    for (u, v) in graph.edges:
        if bitstring[u] != bitstring[v]:
            cut_edges.append((u, v))
        else:
            non_cut_edges.append((u, v))

    nx.draw_networkx_edges(graph, pos=pos, edgelist=non_cut_edges, edge_color='gray', width=2)
    nx.draw_networkx_edges(graph, pos=pos, edgelist=cut_edges, edge_color='green', width=2, style='dashed')

    nx.draw_networkx_labels(graph, pos=pos, font_color='white', font_weight='bold')
    plt.axis('off')
    plt.show()

def get_challenge_solutions(graph):
    start_time = time.time()
    # Brute-force approach with conditional checks

    verbose = False

    G = graph
    n = len(G.nodes())
    w = np.zeros([n, n])
    for i in range(n):
        for j in range(n):
            temp = G.get_edge_data(i, j, default=0)
            if temp != 0:
                w[i, j] = 1.0
    if verbose:
        print(w)

    best_cost_brute = 0
    best_cost_balanced = 0
    best_cost_connected = 0

    for b in range(2**n):
        x = [int(t) for t in reversed(list(bin(b)[2:].zfill(n)))]

        # Create subgraphs based on the partition
        subgraph0 = G.subgraph([i for i, val in enumerate(x) if val == 0])
        subgraph1 = G.subgraph([i for i, val in enumerate(x) if val == 1])

        bs = "".join(str(i) for i in x)
        
        # Check if subgraphs are not empty
        if len(subgraph0.nodes) > 0 and len(subgraph1.nodes) > 0:
            cost = 0
            for i in range(n):
                for j in range(n):
                    cost = cost + w[i, j] * x[i] * (1 - x[j])
            if best_cost_brute < cost:
                best_cost_brute = cost
                xbest_brute = x
                XS_brut = []
            if best_cost_brute == cost:
                XS_brut.append(bs)

            outstr = "case = " + str(x) + " cost = " + str(cost)

            if (len(subgraph1.nodes)-len(subgraph0.nodes))**2 <= 1:
                outstr += " balanced"
                if best_cost_balanced < cost:
                    best_cost_balanced = cost
                    xbest_balanced = x
                    XS_balanced = []
                if best_cost_balanced == cost:
                    XS_balanced.append(bs)

            if nx.is_connected(subgraph0) and nx.is_connected(subgraph1):
                outstr += " connected"
                if best_cost_connected < cost:
                    best_cost_connected = cost
                    xbest_connected = x
                    XS_connected = []
                if best_cost_connected == cost:
                    XS_connected.append(bs)
            if verbose:
                print(outstr)
    
    end_time = time.time()
    print(end_time - start_time)

    # This is classical brute force solver results:
    interpret_solution(graph, xbest_brute)
    print(graph, xbest_brute)
    print("\nBest solution = " + str(xbest_brute) + " cost = " + str(best_cost_brute))
    print(XS_brut)

    interpret_solution(graph, xbest_balanced)
    print(graph, xbest_balanced)
    print("\nBest balanced = " + str(xbest_balanced) + " cost = " + str(best_cost_balanced))
    print(XS_balanced)

    interpret_solution(graph, xbest_connected)
    print(graph, xbest_connected)
    print("\nBest connected = " + str(xbest_connected) + " cost = " + str(best_cost_connected))
    print(XS_connected)
    plt.show()

    return XS_brut, XS_balanced, XS_connected

def print_shots(counts, shots, XS_brut, XS_balanced, XS_connected):
    # And this is how we calculate the shots counted toward scores for each class of the problems

    sum_counts = 0
    for bs in counts:
        if bs in XS_brut:
            sum_counts += counts[bs]

    print(f"Pure max-cut: {sum_counts} out of {shots}")

    sum_balanced_counts = 0
    for bs in counts:
        if bs in XS_balanced:
            sum_balanced_counts += counts[bs]

    print(f"Balanced max-cut: {sum_balanced_counts} out of {shots}")

    sum_connected_counts = 0
    for bs in counts:
        if bs in XS_connected:
            sum_connected_counts += counts[bs]

    print(f"Connected max-cut: {sum_connected_counts} out of {shots}")

def final_score(graph, XS_brut, XS_balanced, XS_connected, counts, shots, ansatz, challenge):

    if(challenge=='base'):
        sum_counts = 0
        for bs in counts:
            if bs in XS_brut:
                sum_counts += counts[bs]
    elif(challenge=='balanced'):
        sum_balanced_counts = 0
        for bs in counts:
            if bs in XS_balanced:
                sum_balanced_counts += counts[bs]        
        sum_counts = sum_balanced_counts
    elif(challenge=='connected'):
        sum_connected_counts = 0
        for bs in counts:
            if bs in XS_connected:
                sum_connected_counts += counts[bs]
        sum_counts = sum_connected_counts

    
    transpiled_ansatz = transpile(ansatz, basis_gates = ['cx','rz','sx','x'])
    cx_count = transpiled_ansatz.count_ops()['cx']
    score = (4*2*graph.number_of_edges())/(4*2*graph.number_of_edges() + cx_count) * sum_counts/shots

    return np.round(score,5)