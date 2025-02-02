from typing import Optional, List
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
import networkx as nx

class Circuit():
    
    def __init__(self,
                graph: nx.Graph,
                opt_edges: List,
                no_opt_edges: List,
                ):
        
        self.opt_edges = opt_edges
        self.no_opt_edges = no_opt_edges
        self.gamma = ParameterVector(r"$\theta$", graph.number_of_edges())
        self.graph = graph
        self.qc = QuantumCircuit(self.graph.number_of_nodes())
    
    def _add_unoptimized_edges(self):
        """Appends the circuit corresponding to the unoptimized edges"""
        for t, edge in zip(self.gamma[len(self.opt_edges):], self.no_opt_edges):
            self.qc.cx(edge[0],edge[1])
            self.qc.ry(t,edge[1])
            self.qc.cx(edge[0],edge[1])
    
        
    def create_circuit(self) -> QuantumCircuit:
        """Given the set of optimized and unoptimized edges, creates the quantum circuit"""
        self.qc.h(range(self.qc.num_qubits))

        for t, edge in zip(self.gamma[:len(self.opt_edges)], self.opt_edges):
            self.qc.ry(t,edge[1])
            self.qc.cx(edge[0],edge[1])
        
        self._add_unoptimized_edges()
        
        return self.qc