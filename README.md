<h1 align="center">
  <img src="https://avatars.githubusercontent.com/u/58616955?v=4" width="120" alt="Jordan Newell" />
  <br>Jordan Newell
</h1>

<p align="center"><em>Self-hosted infra, agent fleets, small tools that ship.</em></p>

<p align="center">
  <a href="https://jordannewell.com">site</a> ·
  <a href="https://status.jordannewell.com">status</a> ·
  <a href="mailto:jordan@jordannewell.com">mail</a>
</p>

---

### What I'm doing right now

Running a homelab like it's a small company.

- **16-agent OpenClaw fleet** across 7 Linux machines on a Tailscale tailnet (11 nodes)
- **Self-hosted stack:** `*arr` → Jellyfin, SearXNG + YaCy, Synapse, Mailcow, Vaultwarden
- **Observability:** Prometheus + Grafana + Alloy · fail2ban → Discord + Matrix
- **Reusable pattern I'd bring to a team:** sentinel-file nginx fallback — 170ms vs 1.2s failover for known outages. Shipped to prod on `status.jordannewell.com` (2026-07-16). Beats `proxy_connect_timeout` whack-a-mole by 7×.

### Shipped

| Repo | What it does |
|---|---|
| [`crypto-key-classifier`](https://github.com/JordanNewell/crypto-key-classifier) | Identify any crypto key — BTC/ETH/SOL/Cosmos + ~50 chains, BIP-39/Electrum mnemonics. Headline feature: Cosmos HRP swap (one decode → 19 re-encodings). 17 validators, 229 tests, tagged `v0.4.0-hardened`. |
| [`jordannewell-com`](https://github.com/JordanNewell/jordannewell-com) | Source for [`jordannewell.com`](https://jordannewell.com) — Astro SSG, deployed via tar-over-ssh to a Hetzner host behind Cloudflare. CSP + MTA-STS + TLS-RPT + OG tags. |
| [`dotfiles`](https://github.com/JordanNewell/dotfiles) | Personal dev env — PowerShell + Bash profiles, editor config, portable env-var-driven paths across Windows + Linux fleet. |

### Verified OSS contributions

I file bugs with repros. They get fixed.

- [OpenClaw #81172](https://github.com/openclaw/openclaw/issues/81172) — `memory-core: memory_search blocks event loop for 60+ seconds` · filed 2026-05-18 under `dev23xyz-oss`, closed same day

### Notes on style

- **Don't over-engineer.** Three lines beats a premature abstraction.
- **Ship, then maintain.** v0.1 in the wild beats v1.0 in your head.
- **Read source before shipping "gap-fillers."** Hard-learned.

---

<p align="center">
  <img src="https://github-readme-stats.vercel.app/api?username=JordanNewell&show_icons=true&hide_title=true&include_all_commits=true&card_width=320" height="160" alt="stats" />
  <img src="https://github-readme-stats.vercel.app/api/top-langs/?username=JordanNewell&layout=compact&hide_title=true&card_width=320" height="160" alt="top langs" />
</p>
