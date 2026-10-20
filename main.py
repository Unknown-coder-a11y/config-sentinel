from engine.discovery import SystemDiscoverer
from engine.graph import SystemGraphBuilder

def main():
    print("🔍 Scanning live system...")
    discoverer = SystemDiscoverer()
    raw_data = {
        "services": discoverer.scan_services(),
        "sockets": discoverer.scan_sockets()
    }

    print("🕸️ Building dependency graph...")
    builder = SystemGraphBuilder()
    graph = builder.build_graph(raw_data)

    print(f"✅ Discovered {len(graph.nodes)} nodes and {len(graph.edges)} connections!")
    print("Nodes:", list(graph.nodes))

    # Test isolated subgraph extraction
    isolated = builder.get_subgraph("nginx")
    print("Isolated Nginx cluster:", isolated)

if __name__ == "__main__":
    main()