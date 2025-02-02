from typing import Optional, List
from qiskit import QuantumCircuit
from qiskit.circuit import ParameterVector
import networkx as nx


class Circuit():
    
    def __init__(self,
                opt_edges: List,
                no_opt_edges: dict,
                gamma: float,
                ):
        
        self.opt_edges = opt_edges
        # TODO: change
        # self.no_opt_edges = no_opt_edges
        self.no_opt_edges = [v for k, vs in no_opt_edges.items() for v in vs]
        # self.gamma = gamma
        self.gamma = ParameterVector(r"$\theta$", len(self.opt_edges) + len(self.no_opt_edges))
        self.graph = nx.Graph()
        edges = list(self.opt_edges)
        # TODO: change
        # for color, edge_list in self.no_opt_edges.items():
        #     edges = edges + edge_list
        for edge in self.no_opt_edges:
            edges.append(edge)
        self.graph.add_edges_from(edges)
        self.qc = QuantumCircuit(len(self.graph.nodes))
            
        
    def _add_unoptimized_edges(self, undo_gates:bool):
        """Appends the circuit corresponding to the unoptimized edges"""
        # TODO: change
        # for color in list(self.no_opt_edges.keys()):
            
            # for edge in self.no_opt_edges[color]:
            #     self.qc.cx(edge[0],edge[1])
            #     self.qc.rz(self.gamma,edge[1])
            #     self.qc.cx(edge[0],edge[1])
        for t, edge in zip(self.gamma[-len(self.no_opt_edges):], self.no_opt_edges):
            self.qc.cx(edge[0],edge[1])
            self.qc.rz(t,edge[1])
            self.qc.cx(edge[0],edge[1])
        
        if undo_gates:
            self.qc.barrier()
            
            for color in reversed(list(self.no_opt_edges.keys())):
                for edge in self.no_opt_edges[color]:
                    self.qc.cx(edge[0],edge[1])
                    self.qc.rz(-1*self.gamma,edge[1])
                    self.qc.cx(edge[0],edge[1])
    
        
    def create_circuit(self,optimize=True,undo_gates=True) -> QuantumCircuit:
        """Given the set of optimized and unoptimized edges, creates the quantum circuit"""
        self.qc.h(range(self.qc.num_qubits))
        
        if not optimize:
            for edge in self.opt_edges:
                self.qc.cx(edge[0],edge[1])
                self.qc.rz(self.gamma,edge[1])
                self.qc.cx(edge[0],edge[1])
        
        else:
            # TODO: change
            # for edge in self.opt_edges:
            #     self.qc.rz(self.gamma,edge[1])
            #     self.qc.cx(edge[0],edge[1])
            for t, edge in zip(self.gamma[:len(self.no_opt_edges)], self.opt_edges):
                self.qc.rz(t,edge[1])
                self.qc.cx(edge[0],edge[1])
        
        self._add_unoptimized_edges(undo_gates=undo_gates)
        
        if undo_gates:
            if not optimize:
                for edge in reversed(self.opt_edges):
                    self.qc.cx(edge[0],edge[1])
                    self.qc.rz(-1*self.gamma,edge[1])
                    self.qc.cx(edge[0],edge[1])
            else:
                for edge in reversed(self.opt_edges):
                    self.qc.cx(edge[0],edge[1])
                    self.qc.rz(-1*self.gamma,edge[1])
            
            self.qc.h(range(self.qc.num_qubits))
        
        self.qc.measure_all()
        
        return self.qc