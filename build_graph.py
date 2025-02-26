import networkx as nx
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import SparsePauliOp

from dfs import DFS

# Visualization will be performed in the cells below;
def build_ansatz(graph: nx.Graph) -> QuantumCircuit:
    obj = DFS(graph, 1)
    qc = obj.dfs_ansatz(undo_gates=False)

    return qc

def draw_graph(graph: nx.Graph, ansatz: QuantumCircuit):
    ansatz = build_ansatz(graph)
    ansatz.draw("mpl", fold=-1)

def build_maxcut_hamiltonian(graph: nx.Graph) -> SparsePauliOp:
    """
    Build the MaxCut Hamiltonian for the given graph H = (|E|/2)*I - (1/2)*Σ_{(i,j)∈E}(Z_i Z_j)
    """
    num_qubits = len(graph.nodes)
    edges = list(graph.edges())
    num_edges = len(edges)

    pauli_terms = ["I"*num_qubits] # start with identity
    coeffs = [-num_edges / 2]

    for (u, v) in edges: # for each edge, add -(1/2)*Z_i Z_j
        z_term = ["I"] * num_qubits
        z_term[u] = "Z"
        z_term[v] = "Z"
        pauli_terms.append("".join(z_term))
        coeffs.append(0.5)

    return SparsePauliOp.from_list(list(zip(pauli_terms, coeffs)))