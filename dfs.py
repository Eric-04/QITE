from circuit import Circuit

import numpy as np
import networkx as nx
from networkx.classes.graph import Graph

from typing import List, Optional, Union
from qiskit.circuit import QuantumCircuit
from qiskit import *

class DFS():
    def __init__(self,
                graph: Union[Graph, List],
                start_vertex: Optional[int] = 0,
                ):
        self.start_vertex = start_vertex
        self.graph = graph
    
    def _get_opt_edges(self) -> List:
        """Returns the list of edges along the DFS tree"""
        visited = []
        to_opt = []
        
        for edges in list(nx.dfs_edges(self.graph,self.start_vertex)):
            if edges[0] not in visited and edges[1] not in visited:
                to_opt.append(edges)
                visited.append(edges[0])
                visited.append(edges[1])
            if edges[0] in visited and edges[1] not in visited:
                to_opt.append(edges)
                visited.append(edges[1])
        
        return to_opt
    
    def _get_no_opt_edges(self, opt_edges) -> List:
        no_opt_edges = []
        for edge in self.graph.edges:
            if (edge[0],edge[1]) not in opt_edges and (edge[1],edge[0]) not in opt_edges:
                no_opt_edges.append(edge)
        return no_opt_edges
        
    
    def dfs_ansatz(self,optimize=True,undo_gates=True) -> QuantumCircuit:
        """Returns a p=1 QAOA circuit for Max-Cut with the depth first search optimization
        Here, we first create the ansatz, and undo everything. In ideal situation, the
        final result should be all zeros. The deviation from the ideal will give an estimate
        of the noise"""
        
        opt_edges = self._get_opt_edges()
        no_opt_edges = self._get_no_opt_edges(opt_edges)
        
        circ = Circuit(self.graph, opt_edges, no_opt_edges)
        
        self.qc = circ.create_circuit()
        
        return self.qc