# Roadmap

Work is split into small, independent milestones. Each one ends with passing tests and its own commit. Checked items are done in the repository; unchecked items are planned.

## v0.1: Prototype (current)

- [x] System discovery (sockets, `nginx` and `ssh` service state)
- [x] NetworkX topology graph with 1-hop subgraph isolation
- [x] Local LLM integration through Ollama
- [x] Whitelisted command runner with timeout
- [x] End-to-end pipeline in `main.py`

## Housekeeping

- [ ] Fix `.gitignore` (misnamed), remove committed `.pyc` and swap files
- [ ] Add `requirements.txt` and pin versions
- [ ] Choose a license
- [ ] Fill in or remove `config/quirks.yaml`

## v0.2: Safety core

*The first priority, because it closes the biggest known gap (THREAT_MODEL T2).*

- [ ] Replace the binary whitelist with an exact-command action registry
- [ ] Constrain model output to a JSON schema; the model can only pick registered action IDs
- [ ] Pass measured service status to the model instead of a hardcoded value
- [ ] Discovery: `sudo -n`, timeouts, record bind addresses, detect missing systemd (WSL2)
- [ ] Governance: risk tiers as plain code, default deny for unknown paths and actions
- [ ] Drift detection: baseline hashes and diffs of watched config files
- [ ] Unit tests for the safety logic (path traversal and symlink cases included)

## v0.3: Configuration and plugins

- [ ] Move hardcoded settings (target, paths, model name) into a config file
- [ ] Service definitions as small plugins, so adding a service means adding one file

## v0.4: Transactional remediation

- [ ] Snapshot with SHA-256 manifest before any change
- [ ] Atomic writes, then verify (syntax check, reload, health check)
- [ ] Automatic rollback when any verification step fails
- [ ] `--apply` flow for hand-written patches, with dry-run by default

## v0.5: Audit log

- [ ] Append-only JSONL record of every decision, action, approval, and result

## v0.6: More scanners

Each is a standalone function that returns findings:

- [ ] SSH configuration risks (for example root login enabled)
- [ ] Services bound to all interfaces
- [ ] Permissions on sensitive files and world-writable configs

## v0.7: Model-proposed patches

*Only after v0.4 and v0.5 are trustworthy.*

- [ ] The model proposes a diff, which goes through the same governance, snapshot, and verification path as a hand-written one

## v1.0: Polish

- [ ] CLI subcommands (`scan`, `baseline`, `apply`, `rollback`)
- [ ] Packaging and installation docs
- [ ] Updated threat model

## Working agreements

- One branch per milestone, merged only when its tests pass.
- Safety-related behavior gets a test first.
- Modules talk to each other through plain data (dicts), not each other's internals.
- Every new capability updates `THREAT_MODEL.md`.
