
class Vertex:
    def __init__(self, node, index):
        self.question = node
        self.id = node.id
        self.adjacent = {}
        self.choice = ""
        self.seen = False
        self.seen_as_parent = False
        self.index = index

    def __str__(self):
        return str(self.question.action)

    def add_neighbor(self, neighbor_id, neighbor_vertex, choice=""):  
        self.adjacent[neighbor_id] = neighbor_vertex
        neighbor_vertex.choie = choice

    def get_connections(self):
        return self.adjacent.keys()  

    def get_id(self):
        return self.id

    def get_question(self):
        return self.question

    def get_weight(self, neighbor):
        return self.adjacent[neighbor]

class QuestionGraph:
    def __init__(self):
        self.vert_dict = {}
        self.num_vertices = 0

    def __iter__(self):
        return iter(self.vert_dict.values())

    def add_vertex(self, node):
        new_vertex = Vertex(node, self.num_vertices)
        self.num_vertices = self.num_vertices + 1
        self.vert_dict[node.id] = new_vertex
        return new_vertex

    def get_vertex(self, n):
        if n in self.vert_dict:
            return self.vert_dict[n]
        else:
            return None

    def add_edge(self, frm, to, choice=""):
        if frm.id not in self.vert_dict:
            self.add_vertex(frm)
        if to.id not in self.vert_dict:
            self.add_vertex(to)

        self.vert_dict[frm.id].add_neighbor(to.id, self.vert_dict[to.id], choice)  # Rimosso cost perchè non è importante
        # self.vert_dict[to].add_neighbor(self.vert_dict[frm], cost)  commentata perchè il grafo è orientato

    def get_vertices(self):
        return self.vert_dict.keys()
    
    def reset_seen(self):
        for vert in self.vert_dict.values():
            vert.seen = False

