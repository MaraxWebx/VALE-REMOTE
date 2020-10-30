from app.models import *
import networkx as nx
import matplotlib.pyplot as plt
import io
import urllib, base64

class Vertex:
    def __init__(self, node, index):
        self.question = node
        self.id = node.id
        self.adjacent = {}
        self.choice = ""
        self.seen = False
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

    def print_graph(self):
        g = nx.Graph()

        for key in self.get_vertices():
            vert = self.get_vertex(key)
            if vert is not None:
                for adj in vert.adjacent:
                    g.add_edges_from([(vert, vert.adjacent[adj], {'choice' : vert.adjacent[adj].choice})])

        plt.figure(dpi=120)
        pos = nx.spring_layout(g, scale=0.2)
        nx.draw_networkx_nodes(g,pos)
        nx.draw_networkx_edges(g,pos)
        y_off = 0.02
        nx.draw_networkx_labels(g, pos = {k:([v[0], v[1]+y_off]) for k,v in pos.items()})
        nx.draw(g, with_labels=True, arrows=True)
        buf = io.BytesIO()
        plt.savefig(buf, format='jpg')
        buf.seek(0)
        string = base64.b64encode(buf.read())
        uri = 'data:image/png;base64,' + urllib.parse.quote(string)
        html = '<img src = "%s"/>' % uri
        return html

