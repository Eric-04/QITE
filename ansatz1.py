def build_ansatz(graph: nx.Graph) -> QuantumCircuit:
    def misra_gries_coloring(G):
        edge_colors = {}
        uncolored_edges = list(G.edges())
        
        while uncolored_edges:
            u, v = uncolored_edges.pop()
            fan = [v]
            
            # Find first available colors using incremental search
            used_colors_u = {edge_colors[e] for e in G.edges(u) if e in edge_colors}
            used_colors_v = {edge_colors[e] for e in G.edges(v) if e in edge_colors}
            
            # Find first available color for u
            c = 0
            while c in used_colors_u:
                c += 1
                
            # Find first available color for v
            d = 0
            while d in used_colors_v:
                d += 1

            # Find maximal alternating path with safety checks
            w = v
            while True:
                # Get adjacent colors with default None
                adjacent_colors = (edge_colors.get((w, x)) for x in G.neighbors(w))
                # Find first occurrence of color c
                found = False
                for neighbor in G.neighbors(w):
                    if edge_colors.get((w, neighbor)) == c and neighbor != u:
                        w = neighbor
                        found = True
                        break
                if not found:
                    break
                c, d = d, c  # Swap colors
            
            # Invert path colors with edge existence check
            x = w
            while x != v:
                # Find next node with color c
                next_nodes = [y for y in G.neighbors(x) 
                            if edge_colors.get((x, y)) == c]
                if not next_nodes:
                    break
                y = next_nodes[0]
                edge_colors[(x, y)] = d
                x = y
                c, d = d, c  # Swap colors

            # Apply final coloring
            edge_colors[(u, v)] = c
            
        return edge_colors

    edge_coloring = misra_gries_coloring(graph)
    max_color = max(edge_coloring.values()) + 1

    ansatz = QuantumCircuit(graph.number_of_nodes())
    ansatz.h(range(graph.number_of_nodes()))
    
    theta = ParameterVector(r"θ", max_color)
    
    for color in range(max_color):
        edges = [e for e, c in edge_coloring.items() if c == color]
        param = theta[color]
        for u, v in edges:
            ansatz.cx(u, v)
            ansatz.ry(param, v)
            ansatz.cx(u, v)
    
    return ansatz


# Base score: 0.05591
# Balanced score: 0.05426
# Connected score: 0.14878
