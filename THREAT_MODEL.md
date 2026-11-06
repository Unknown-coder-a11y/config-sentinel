# Threat Model

Applies to ConfigSentinel **v0.1** (commit `fae6b85`). This is a living document: update it whenever a control is added or a gap is closed.

## 1. What is being protected

- **The host.** The tool runs commands, some with `sudo`, so a flaw could change or expose the machine it runs on.
- **Configuration and topology data.** Service layout, ports, and (in future) config file contents are sensitive.
- **Integrity of decisions.** Output from the model or from scanned data should not be able to steer the tool into unsafe actions.

## 2. Assumptions and scope

**Assumed:** a single-user development machine (Linux or WSL2), a trusted user, and trusted Ollama binaries and model weights.

**Out of scope (for now):** hostile local users on a shared host, remote network attackers, a compromised root account, and a malicious model supply chain.

## 3. Trust boundaries

| Source | Trust level | Why |
|---|---|---|
| LLM output | **Untrusted** | Small models hallucinate and can be manipulated by their input |
| Scanned data (process names, service states, future config/log text) | **Untrusted** | Any local process can choose its own name; files can contain arbitrary text |
| Local Ollama endpoint | Semi-trusted | Plain HTTP on localhost, no authentication by default |
| The user and their sudo rights | Trusted | The user decides what the tool may do |

## 4. Threats

| ID | Threat | State in v0.1 | Planned mitigation |
|---|---|---|---|
| T1 | Model output gets executed unsafely | **Not wired up.** Model output is printed only. The command that runs is hardcoded in `main.py`. | Model may only return an action ID from a fixed registry; output validated against a schema |
| T2 | Sandbox whitelist bypass | **Open.** Only the binary name is checked. `cat /etc/shadow`, `systemctl stop nginx`, `ip link set ... down`, and `nginx -c <file>` all pass, and with a `sudo` prefix they run as root. | Replace with exact-command registry (no free-form arguments); per-action sudoers rules |
| T3 | Prompt injection through scanned data | **Low exposure.** The prompt contains only node names from the target's 1-hop neighbourhood (service names and port numbers). This grows once config files or logs are added. | Treat all file and log text as data, delimit it in prompts, cap its size, validate model output |
| T4 | Spoofed process names cause misattribution | **Open.** `ss` reports a process name that the process itself controls; the graph trusts it. | Cross-check PID and `/proc/<pid>/exe` against the expected binary path |
| T5 | Over-privileged execution | **Partly open.** `sudo ss` runs from `discovery.py` outside the sandbox and may prompt for a password. | Route all commands through one runner; `sudo -n`; sudoers rules limited to exact commands |
| T6 | Local Ollama endpoint reachable by other processes | **Accepted.** It listens on localhost without authentication. This becomes a real exposure if `OLLAMA_HOST` is set to a non-loopback address. | Document the requirement to keep it bound to `127.0.0.1` |
| T7 | Sensitive data exposure | **Low.** Nothing is persisted; topology is printed to the terminal only. This changes once baselines or snapshots store config copies. | Store them in `0700` directories; avoid logging file contents |
| T8 | Hangs or resource exhaustion | **Partly open.** Sandbox has a 10 s timeout and the LLM call has 60 s, but discovery subprocesses have no timeout. | Add timeouts everywhere; cap captured output size |
| T9 | Dependency supply chain | **Open.** No `requirements.txt` and no version pinning. | Pin versions; add dependency auditing |
| T10 | Unsafe config modification | **Not applicable yet.** v0.1 never writes files. It becomes the central risk once remediation exists (partial writes, race conditions between check and write). | Snapshot before change, atomic writes, post-change verification with automatic rollback, tiered approval (see ROADMAP) |

## 5. Current controls

- No shell is used when running commands (arguments are passed as a list).
- A 10-second timeout on sandbox commands and a 60-second timeout on the model call.
- Model output is never executed.
- Data stays on the machine: no cloud APIs.

## 6. Key gaps, in priority order

1. **T2** is the most serious known weakness. It is safe today only because nothing untrusted reaches the sandbox.
2. **T5** and **T1** both depend on closing T2 first.
3. **T4** and **T3** matter more as the tool starts reading more data.

## 7. Design rule going forward

The model may *suggest*. Deterministic code *decides*. Risk tiers, allowed commands, and approval gates are plain rules in code, never something the model scores or overrides.
