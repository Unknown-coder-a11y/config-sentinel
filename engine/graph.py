import networkx as nx

class SystemGraphBuilder:
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph(self, raw_data: dict) -> nx.DiGraph:
        services = raw_data.get("services", {})
        sockets = raw_data.get("sockets", [])

        # Add service nodes
        for svc_name, details in services.items():
            self.graph.add_node(svc_name, type="service", status=details.get("status"))

        # Link socket nodes to service processes
        for s in sockets:
            port_node = f"port:{s['port']}"
            proc = s["process"]
            self.graph.add_node(port_node, type="socket")
            
            # Map process aliases (e.g. sshd -> ssh)
            matched_svc = proc
            if proc == "sshd":
                matched_svc = "ssh"

            if matched_svc in services:
                self.graph.add_edge(matched_svc, port_node, relation="listens_on")
            elif proc != "unknown":
                # Create process node if it's not a tracked systemd service
                self.graph.add_node(proc, type="process")
                self.graph.add_edge(proc, port_node, relation="listens_on")

        return self.graph

    def get_subgraph(self, node_name: str) -> set:
        """Extracts direct 1-hop dependencies for testing isolation."""
        if node_name not in self.graph:
            return set()
        deps = {node_name}
        deps.update(self.graph.predecessors(node_name))
        deps.update(self.graph.successors(node_name))
        return deps