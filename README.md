# ConfigSentinel

A local-first configuration scanner and SRE copilot for Linux and WSL2. It maps what is running on a host, asks a small local LLM to interpret it, and checks configuration through a restricted command runner. Nothing leaves the machine.

> **Status: v0.1 prototype.** Read-only scanning and analysis work. Automated remediation is **not implemented**. Read [Known limitations](#known-limitations) before running it anywhere that matters.

## What works today

- **Discovery** (`engine/discovery.py`): lists listening sockets with `ss -tulpn` and checks the state of `nginx` and `ssh` with `systemctl is-active`.
- **Topology graph** (`engine/graph.py`): builds a NetworkX directed graph (service or process → port) and can extract one target's 1-hop neighbourhood, so the model receives a small, focused payload instead of the whole host.
- **Local AI copilot** (`ai/copilot.py`): sends that payload to a local Ollama server (default model `qwen2.5-coder:1.5b`) and prints a short diagnosis. The output is advisory text only and is never executed.
- **Verification sandbox** (`engine/sandbox.py`): runs a command only if its binary is on a whitelist (`nginx`, `systemctl`, `ss`, `netstat`, `ip`, `cat`, `tail`), with a 10-second timeout and no shell. `main.py` uses it to run `sudo nginx -t`.

## Quick start

Requirements: Linux or WSL2, Python 3.10+, [Ollama](https://ollama.com), and `sudo` access. nginx is optional but needed for the syntax check to succeed.

```bash
git clone https://github.com/Unknown-coder-a11y/config-sentinel.git
cd config-sentinel
python -m venv venv && source venv/bin/activate
pip install networkx requests
ollama pull qwen2.5-coder:1.5b
python main.py
```

You will be prompted for your sudo password: socket scanning (`sudo ss`) and the nginx syntax check (`sudo nginx -t`) need root. The target service is currently hardcoded to `nginx` in `main.py`.

## How a run works

1. **Scan** the live system (sockets and services).
2. **Build** the dependency graph.
3. **Isolate** the target service and its direct neighbours.
4. **Ask** the local model for a short diagnosis of that cluster.
5. **Verify** with a whitelisted command (`sudo nginx -t`) and report pass or fail.

## Design principles

- **Local-first.** Inference runs through Ollama on your own machine. No configuration or topology data goes to a third-party API.
- **Small context.** Only the target's neighbourhood is sent to the model. This keeps prompts fast on modest hardware and limits what the model sees.
- **Advisory AI.** The model's output is displayed, never executed. Anything that runs goes through the sandbox.

## Project layout

```
main.py              pipeline entry point
engine/discovery.py  socket and service scanning
engine/graph.py      NetworkX topology graph and subgraph extraction
engine/sandbox.py    whitelisted command runner
ai/copilot.py        Ollama client and prompt
config/quirks.yaml   reserved for per-service settings (currently empty)
```

## Known limitations

This is an early prototype, and these are the gaps I know about:

- **The sandbox whitelist is binary-level only.** It does not restrict arguments. `cat` and `tail` can read any file the process can read, `systemctl` and `ip` allow state-changing subcommands, and a `sudo` prefix runs the command as root. **Do not feed model output into the sandbox.** Today `main.py` only runs a hardcoded command. Replacing the whitelist with an exact-command registry is the first roadmap item.
- **Discovery calls `sudo ss` directly**, outside the sandbox and without a timeout.
- **The prompt's system status is hardcoded** to `"degraded"` rather than measured, and the model's reply is free text from a 1.5B model, so it can be wrong or invent commands.
- **Process names are self-reported** by the processes, so a socket can be attributed to the wrong service.
- Only `nginx` and `ssh` are scanned, and there are no tests, no rollback, and no remediation yet.

## Documents

- [ROADMAP.md](ROADMAP.md): what is planned, in order
- [THREAT_MODEL.md](THREAT_MODEL.md): what this tool defends against and where it falls short

## License

Not yet chosen.
