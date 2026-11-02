import json
from engine.discovery import SystemDiscoverer
from engine.graph import SystemGraphBuilder
from ai.copilot import ConfigCopilot
from engine.sandbox import VerificationSandbox

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

    target = "nginx"
    isolated_cluster = builder.get_subgraph(target)
    print(f"🎯 3. Isolated cluster for '{target}': {isolated_cluster}")

    print("🤖 4. Dispatching topology payload to local LLM...")
    copilot = ConfigCopilot()
    ai_analysis = copilot.analyze_subgraph(target, isolated_cluster)

    print("\n--- 🛡️ ConfigSentinel AI Copilot Recommendation ---")
    print(ai_analysis)

    print("\n⚡ 5. Executing Automated Verification Sandbox...")
    sandbox = VerificationSandbox()
    
    cmd = "sudo nginx -t"
    print(f"Executing: `{cmd}`")
    res = sandbox.execute_verification(cmd)

    if res.get("success"):
        print("\n✅ [VERIFICATION EXECUTED]")
        if res.get('stdout'):
            print(f"STDOUT:\n{res['stdout']}")
        if res.get('stderr'):
            print(f"STDERR:\n{res['stderr']}")
    else:
        print("\n❌ [VERIFICATION FAILED / BLOCKED]")
        error_msg = res.get('error') or res.get('stderr') or "Unknown execution failure"
        print(f"Reason/Error:\n{error_msg}")

if __name__ == "__main__":
    main()
