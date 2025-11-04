from queue import Queue

class AdjNode:
    def __init__(self, num_vertex):
        self.num_vertex = num_vertex
        self.next = None

class Graph:
    def __init__(self, num):
        self.V = num
        self.graph = [None] * self.V

    def add_edge(self, s, d):
        node = AdjNode(d)
        node.next = self.graph[s]
        self.graph[s] = node

        node = AdjNode(s)
        node.next = self.graph[d]
        self.graph[d] = node


    def highest_saturation_adjacent(self, colors, vertex):
        max_saturation = -1
        max_vertex = None
        temp = self.graph[vertex]
        while temp:
            v = temp.num_vertex
            if colors[v] is not None:
                temp = temp.next
                continue
            neighbor_colors = set()
            temp2 = self.graph[v]
            while temp2:
                if colors[temp2.num_vertex] is not None:
                    neighbor_colors.add(colors[temp2.num_vertex])
                temp2 = temp2.next
            saturation = len(neighbor_colors)
            if saturation > max_saturation:
                max_saturation = saturation
                max_vertex = v
            temp = temp.next
        return max_vertex
    
    def color_vertex(self, colors, vertex):
        neighbor_colors = set()
        temp = self.graph[vertex]
        while temp:
            if colors[temp.num_vertex] is not None:
                neighbor_colors.add(colors[temp.num_vertex])
            temp = temp.next
        for color in range(self.V):
            if color not in neighbor_colors:
                colors[vertex] = color
                return color
        return None

    def colorir(self):
        fila = Queue()
        colors = [None] * self.V
        begin = self.highest_saturation_vertex(colors)
        fila.put(begin)
        while not fila.empty():
            vertice = fila.get()
            adjacentVertex = self.highest_saturation_vertex(vertice)
            while adjacentVertex is not None:
                color = self.colorVertex(adjacentVertex)
                if color is None:
                    return False
                fila.put(adjacentVertex)
                adjacentVertex = self.highest_saturation_vertex(vertice)
        return true

        