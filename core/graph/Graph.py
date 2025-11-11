from collections import defaultdict

class classGraph:
    def __init__(self, directed=False):
        self._graph = defaultdict(set)
        self._directed = directed

    def add(self, node1, node2):
        self._graph[node1].add(node2)
        self._graph[node2].add(node1)
    
    def is_connected(self, node1, node2):
        return node1 in self._graph and node2 in self._graph[node1]
    
    def set_color(self, node, color, colors):
        colors[node] = color

    def highest_saturation(self, colors):
        max_sat = -1
        max_degree = -1
        candidate = None

        for node in self._graph:
            if colors.get(node) is not None:
                continue
            neighbor_colors = {
                colors.get(neigh)
                for neigh in self._graph[node]
                if colors.get(neigh) is not None
            }
            saturation = len(neighbor_colors)
            degree = len(self._graph[node])
            if (saturation > max_sat) or (saturation == max_sat and degree > max_degree):
                max_sat = saturation
                max_degree = degree
                candidate = node
        return candidate

    def saturBFS(self, available_colors, preset=None):
        colors = {} if preset is None else preset.copy()

        if preset:
            for node, color in preset.items():
                for neighbor in self._graph[node]:
                    if colors.get(neighbor) == color:
                        return None

        while len(colors) < len(self._graph):
            node = self.highest_saturation(colors)
            if node is None:
                break

            neighbor_colors = {
                colors.get(neigh)
                for neigh in self._graph[node]
                if colors.get(neigh) is not None
            }

            for color in available_colors:
                if color not in neighbor_colors:
                    self.set_color(node, color, colors)
                    break
            else:
                return None

        return colors