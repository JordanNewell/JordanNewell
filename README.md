<h1 align="center">Jordan Newell</h1>
<p align="center"><em>Self-hosted infra. Small tools that ship. Files bugs with repros.</em></p>

<p align="center">
  <a href="https://jordannewell.com">site</a> ·
  <a href="https://status.jordannewell.com">status</a> ·
  <a href="mailto:jordan@jordannewell.com">mail</a>
</p>

---

### Code

| Repo | What it is |
|---|---|
| [`crypto-key-classifier`](https://github.com/JordanNewell/crypto-key-classifier) | Decode a crypto key once, re-encode across ~50 chains. Headline: Cosmos HRP swap — one decode → 19 re-encodings. 17 validators, 229 tests. |
| [`jordannewell-com`](https://github.com/JordanNewell/jordannewell-com) | Source for [`jordannewell.com`](https://jordannewell.com) — shipping-in-public field notes on AI agents, self-hosted infra, crypto tooling, venture research. Astro SSG, tar-over-ssh to Hetzner behind Cloudflare. LLM-discoverable by design (`/llms.txt`, schema.org JSON-LD, AI feed, AI-crawler allowlist). |
| [`git-hygiene`](https://github.com/JordanNewell/git-hygiene) | *Tools don't get co-author credit.* `commit-msg` + `pre-commit` hooks that strip AI-attribution trailers (Co-Authored-By: Claude, etc.) and catch credential patterns pre-staging. Zero deps beyond bash/grep/awk. PGP-signed. |

### Outside GitHub

- One verified OSS bug: [`openclaw/openclaw#81172`](https://github.com/openclaw/openclaw/issues/81172) — `memory_search` event-loop blocking (closed same day).
- Homelab: 7 Linux boxes on Tailscale running `*arr` → Jellyfin, SearXNG + YaCy, Synapse, Mailcow, Vaultwarden. Not a portfolio item — what I actually run every day.
