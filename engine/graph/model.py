import json
import uuid


class Node:
    def __init__(self, labels, properties=None, node_id=None):
        self.id = node_id or str(uuid.uuid4())
        self.labels = labels if isinstance(labels, list) else [labels]
        self.properties = properties or {}

    def to_dict(self):
        return {
            "id": self.id,
            "labels": self.labels,
            "properties": self.properties
        }


class Edge:
    def __init__(self, edge_type, from_id, to_id, properties=None, edge_id=None):
        self.id = edge_id or str(uuid.uuid4())
        self.type = edge_type
        self.from_id = from_id
        self.to_id = to_id
        self.properties = properties or {}

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type,
            "from": self.from_id,
            "to": self.to_id,
            "properties": self.properties
        }


class Graph:
    def __init__(self):
        self.nodes = {}   # id -> Node
        self.edges = []   # list of Edge

    def add_node(self, node):
        self.nodes[node.id] = node
        return node

    def add_edge(self, edge):
        self.edges.append(edge)
        return edge

    def create_node(self, labels, properties=None):
        node = Node(labels, properties)
        return self.add_node(node)

    def create_edge(self, edge_type, from_id, to_id, properties=None):
        edge = Edge(edge_type, from_id, to_id, properties)
        return self.add_edge(edge)

    def get_nodes_by_label(self, label):
        return [n for n in self.nodes.values() if label in n.labels]

    def get_edges_by_type(self, edge_type):
        return [e for e in self.edges if e.type == edge_type]

    def get_edges_from(self, node_id):
        return [e for e in self.edges if e.from_id == node_id]

    def get_edges_to(self, node_id):
        return [e for e in self.edges if e.to_id == node_id]

    def to_dict(self):
        return {
            "nodes": [n.to_dict() for n in self.nodes.values()],
            "edges": [e.to_dict() for e in self.edges]
        }

    def save(self, path):
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"Graph saved: {len(self.nodes)} nodes, {len(self.edges)} edges -> {path}")

    @classmethod
    def load(cls, path):
        with open(path) as f:
            data = json.load(f)
        g = cls()
        for nd in data["nodes"]:
            node = Node(nd["labels"], nd["properties"], nd["id"])
            g.nodes[node.id] = node
        for ed in data["edges"]:
            edge = Edge(ed["type"], ed["from"], ed["to"], ed["properties"], ed["id"])
            g.edges.append(edge)
        return g
