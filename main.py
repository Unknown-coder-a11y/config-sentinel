import json
from engine.discovery import SystemDiscoverer
from engine.graph import SystemGraphBuilder
from ai.copilot import ConfigCopilot

def main():
    print("🔍 1. Scanning live system...")
    discoverer = SystemDiscoverer()
    raw_data = {
        "services": discoverer.scan_services(),
        "sockets": discoverer.scan_sockets()
    }

    print("🕸️ 2. Building dependency graph...")
    builder = SystemGraphBuilder()
    graph = builder.build_graph(raw_data)
    print(f"✅ Active Graph: {len(graph.nodes)} nodes, {len(graph.edges)} edges.")

    # Target service to inspect
    target = "nginx"
    isolated_cluster = builder.get_subgraph(target)
    print(f"🎯 3. Isolated cluster for '{target}': {isolated_cluster}")

    print("🤖 4. Dispatching topology payload to local LLM (qwen2.5-coder:1.5b)...")
    copilot = ConfigCopilot()
    ai_analysis = copilot.analyze_subgraph(target, isolated_cluster)

    print("\n--- 🛡️ ConfigSentinel AI Copilot Recommendation ---")
    print(ai_analysis)

if __name__ == "__main__":
    main()