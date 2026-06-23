# AIFBA Codex Skills

Thin Codex Skills for running AIFBA Amazon operations tasks. The analysis and generation engines remain on AIFBA servers; the public Skill folders validate inputs, call the authenticated API, poll task status, and return results to Codex.

## Current Public Release

- `v0.2.1`
- GitHub install source: `https://github.com/corli-AIFBA/aifba-codex-skills`
- Fallback ZIP: `https://aifba.xyz/assets/downloads/aifba-codex-skills-v0.2.1.zip`
- SHA-256: `fceb5fbc3eb9a1a2592707a3520bbc56c444a2c27da6327ebd149182fe330266`
- Setup guide: `https://aifba.xyz/blog/aifba-codex-amazon-skills.html`

Patch note:

- `v0.2.1` improves helper-script compatibility for stricter Python request and CA-bundle environments.
- The Skills still require only Python 3 standard library. If `certifi` is already installed locally, the scripts use it automatically.

## Included Skills

- `aifba-amazon-title`
- `aifba-amazon-bullets`
- `aifba-amazon-main-image`
- `aifba-amazon-aplus-image`
- `aifba-amazon-ads-diagnosis`
- `aifba-amazon-competitor`
- `aifba-amazon-keywords`
- `aifba-amazon-rufus`

## Install With Codex

Send this repository URL to Codex and ask it to install all AIFBA Skills:

```text
Install all AIFBA Codex Skills from:
https://github.com/corli-AIFBA/aifba-codex-skills
```

Codex can use `$skill-installer` to install Skills from a GitHub repository. Restart Codex after installation if the new Skills are not visible immediately.

## API Key

Create an API key in the AIFBA workspace, then provide it to the Codex process through the `AIFBA_SKILL_API_KEY` environment variable. Never paste the key into a conversation or commit it to a repository.

Full setup guide: https://aifba.xyz/blog/aifba-codex-amazon-skills.html

## Security Boundary

- No AIFBA core analysis logic, model routing, provider configuration, prompts, or credentials are included here.
- Each run uses the user's AIFBA API key, credits, workspace, and existing task history.
- Text results are returned as filtered business fields.
- Image archives and advertising workbooks are downloaded to the user's local workspace by the Skill script.

Copyright 2026 AIFBA. All rights reserved.
