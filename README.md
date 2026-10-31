# Deep Science Founder Radar

A directory of Indian deep science companies from pre-seed to listed. Each profile covers what the company builds (with a plain-English explainer), the founders, the latest round with its lead investor and partner, parallel companies abroad, what to judge it on next, and its fit with India's RDI scheme.

The site is static: `index.html` reads three JSON files in `data/`. A daily scheduled Claude run searches for new signals, updates those files, and emails a digest.

## Deploy on GitHub Pages

1. Create a new public repository, for example `deeptech-radar`.
2. Upload everything in this folder to the root of the repo: `index.html`, `README.md`, `.nojekyll` and the `data/` folder.
3. In the repo, go to **Settings → Pages**, set **Source** to "Deploy from a branch", pick `main` and `/ (root)`, then save.
4. After a minute the site is live at `https://<your-username>.github.io/deeptech-radar/`.

To put it beside your existing site instead, copy the folder into your `<username>.github.io` repo as `radar/`; it will be at `https://<username>.github.io/radar/`.

## Keeping it live

The data updates when new versions of `data/leads.json`, `data/excluded.json` and `data/runs.json` are committed. The daily run can commit them for you once GitHub is connected to Claude and the repo name is added to the scheduled task. Until then, you can download fresh files from the Claude dashboard's Sources panel and upload them here.

## Network page

The Network tab draws companies, investors, institutions, sectors and (optionally) founders as a force-directed graph with d3, built from the `investors` and `institution_tags` fields in `leads.json`.

## Files

- `data/leads.json`: one object per company, with source URL, scores (fit, team, market, IP, each 1–5), de-risking stage, explainer and RDI fields.
- `data/firms.json`: investor firm websites used for links (only sites that were checked).
- `data/excluded.json`: kept for compatibility; the directory now covers every stage.
- `data/runs.json`: run log, newest first.

The radar score (out of 100) is computed in the page: fit 30%, team 25%, market 25%, IP 20%. Each company is filed under the stage of its latest known round (`round_tab`).

## Preview locally

Opening `index.html` straight from disk blocks the data files. Serve the folder instead:

```
python3 -m http.server 8000
```

then open http://localhost:8000.

Scores are judgement calls based on public reporting. Not investment advice.
