# Deep Science Founder Radar

Early-stage Indian deep science companies, found from public signals (grants, incubators, patents, papers, small funding rounds) and scored the way an early investor would. Each lead has a plain-English explainer and a mapping to India's RDI scheme.

The site is static: `index.html` reads three JSON files in `data/`. A daily scheduled Claude run searches for new signals, updates those files, and emails a digest.

## Deploy on GitHub Pages

1. Create a new public repository, for example `deeptech-radar`.
2. Upload everything in this folder to the root of the repo: `index.html`, `README.md`, `.nojekyll` and the `data/` folder.
3. In the repo, go to **Settings → Pages**, set **Source** to "Deploy from a branch", pick `main` and `/ (root)`, then save.
4. After a minute the site is live at `https://<your-username>.github.io/deeptech-radar/`.

To put it beside your existing site instead, copy the folder into your `<username>.github.io` repo as `radar/`; it will be at `https://<username>.github.io/radar/`.

## Keeping it live

The data updates when new versions of `data/leads.json`, `data/excluded.json` and `data/runs.json` are committed. The daily run can commit them for you once GitHub is connected to Claude and the repo name is added to the scheduled task. Until then, you can download fresh files from the Claude dashboard's Sources panel and upload them here.

## Files

- `data/leads.json`: one object per company, with source URL, scores (fit, team, market, IP, each 1–5), de-risking stage, explainer and RDI fields.
- `data/excluded.json`: companies seen but left out, with the reason.
- `data/runs.json`: run log, newest first.

The combined score (out of 100) is computed in the page: fit 30%, team 25%, market 25%, IP 20%. Stage is a gate for the shortlist (stages 1–3), not a weight.

## Preview locally

Opening `index.html` straight from disk blocks the data files. Serve the folder instead:

```
python3 -m http.server 8000
```

then open http://localhost:8000.

Scores are judgement calls based on public reporting. Not investment advice.
