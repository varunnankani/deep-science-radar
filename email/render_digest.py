#!/usr/bin/env python3
"""Deep Science Radar weekly digest: the fixed email design.

Usage:  python3 email/render_digest.py content.json out.html [out.txt]

Content goes in a JSON file; this script owns all the design, so every
issue looks the same. Light design only: it reads correctly in Gmail light
mode, Gmail/iOS dark mode (which inverts light emails cleanly) and print.
Every background is set with BOTH the bgcolor attribute and an inline
style, because Gmail drops some CSS backgrounds.

content.json shape (every key except the ones marked optional is required):
{
  "week_ending": "31 Oct 2026",
  "headline": "Pixxel closes $100M, Skyroot reaches orbit, ...",
  "headline_accent": "$100M",            # optional: substring shown in the accent colour
  "dek": "One or two sentences.",
  "stats": [{"value": "52", "label": "companies tracked", "tone": "ink"}, ...],   # 2-4 items; tone: ink|funding|milestone|ip|correction|watch
  "sections": [
    {"kind": "funding",                  # new|funding|milestone|ip|correction|watch|method (fixed colour + label per kind)
     "title": "Money moved",
     "note": "Closed rounds only. Reported talks never count.",   # optional
     "items": [
       {"name": "Pixxel", "id": "pixxel",             # id optional: links the name to #company/<id>
        "chip": "Series C · $100M", "chip_from": null, # chip_from optional: struck-through old value (e.g. "TRL 7–8")
        "chip_tone": null,                             # optional override, e.g. "watch" for a setback
        "meta": "Co-led by Temasek and Seraphim · 7 Sep 2026",   # optional
        "body": "Plain-English explainer."},           # optional
       {"lead": "Omspace", "text": "flew a sounding rocket ...", "chip": "TRL 4"}   # compact row form
     ]}
  ],
  "coverage": "52 companies tracked: 45 core, 7 benchmarks. 4 core companies still lack team evidence."   # optional
}
"""
import html, json, re, sys

SITE = "https://varunnankani.github.io/deep-science-radar/"

# Light palette derived from the site's tokens (cyan/amber/violet/green/coral),
# darkened so text on white passes WCAG AA.
PAGE, CARD, LINE = "#F2F4F8", "#FFFFFF", "#DFE4EC"
INK, INK2, INK3 = "#0B1424", "#45526A", "#6B778A"
TONES = {
    #  key          text       wash       border
    "ink":        ("#0B1424", "#F2F4F8", "#DFE4EC"),
    "funding":    ("#087482", "#E2F5F7", "#A6DCE2"),   # site cyan  #6DE4EE
    "milestone":  ("#9A5208", "#FDF1E2", "#EFC48F"),   # site warn  #F2B266
    "ip":         ("#5541C4", "#EFECFE", "#CEC5F6"),   # site violet #B3A0FF
    "correction": ("#1D7347", "#E4F4EA", "#A8D9BE"),   # site green #7FD6A8
    "watch":      ("#B02A1F", "#FDECEA", "#F1B7B1"),   # site danger #F28B82
    "new":        ("#087482", "#E2F5F7", "#A6DCE2"),
    "method":     ("#45526A", "#EEF1F6", "#D3DAE5"),
}
LABEL = {"new": "New company", "funding": "Funding", "milestone": "Technical milestone", "ip": "Patents",
         "correction": "Correction", "watch": "Open question", "method": "Method change"}
ORDER = ["new", "funding", "milestone", "ip", "correction", "watch", "method"]

HEAD = "font-family:'Space Grotesk','Helvetica Neue',Helvetica,Arial,sans-serif;"
SANS = "font-family:'IBM Plex Sans','Helvetica Neue',Helvetica,Arial,sans-serif;"
MONO = "font-family:'IBM Plex Mono',Menlo,Consolas,'Courier New',monospace;"

e = lambda s: html.escape(str(s), quote=True)

def chip(text, tone, frm=None):
    t, w, b = TONES[tone]
    old = (f'<span style="{MONO}font-size:11px;color:{INK3};text-decoration:line-through">{e(frm)}</span>'
           f'<span style="{SANS}font-size:11px;color:{INK3}">&nbsp;&rarr;&nbsp;</span>') if frm else ""
    return (old + f'<span style="display:inline-block;{MONO}font-size:11px;line-height:18px;font-weight:600;letter-spacing:.03em;'
            f'text-transform:uppercase;white-space:nowrap;color:{t};background-color:{w};border:1px solid {b};'
            f'border-radius:4px;padding:0 7px">{e(text)}</span>')

def name_html(item, size):
    n = e(item.get("name") or item.get("lead"))
    style = f"{HEAD}font-size:{size}px;line-height:1.3;font-weight:700;color:{INK};text-decoration:none"
    if item.get("id"):
        return f'<a href="{SITE}#company/{e(item["id"])}" style="{style}">{n}</a>'
    return f'<span style="{style}">{n}</span>'

def card_row(item, tone, last):
    sep = "" if last else f"border-bottom:1px solid {LINE};"
    ct = item.get("chip_tone") or tone
    c = chip(item["chip"], ct, item.get("chip_from")) if item.get("chip") else ""
    if "lead" in item:  # compact row
        return (f'<tr><td style="padding:12px 20px;{sep}{SANS}font-size:14px;line-height:1.55;color:{INK2}">'
                f'{name_html(item, 14)} {e(item.get("text", ""))}{"&nbsp; " + c if c else ""}</td></tr>')
    meta = f'<div style="{SANS}font-size:13px;line-height:1.45;color:{INK3};margin-top:3px">{e(item["meta"])}</div>' if item.get("meta") else ""
    body = f'<div style="{SANS}font-size:14.5px;line-height:1.6;color:{INK2};margin-top:8px">{e(item["body"])}</div>' if item.get("body") else ""
    return (f'<tr><td style="padding:16px 20px;{sep}">'
            f'<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>'
            f'<td valign="top">{name_html(item, 16)}</td>'
            f'<td valign="top" align="right" style="padding-left:10px;white-space:nowrap">{c}</td></tr></table>'
            f'{meta}{body}</td></tr>')

def section(sec):
    kind = sec["kind"]
    t, w, b = TONES[kind]
    items = sec["items"]
    rows = "".join(card_row(it, kind, i == len(items) - 1) for i, it in enumerate(items))
    note = f'<div style="{SANS}font-size:14px;line-height:1.5;color:{INK3};margin-top:4px">{e(sec["note"])}</div>' if sec.get("note") else ""
    return f'''
<tr><td style="padding:30px 28px 12px">
 <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
  <td width="8" height="8" bgcolor="{t}" style="width:8px;height:8px;background-color:{t};border-radius:4px;font-size:1px;line-height:1px">&nbsp;</td>
  <td style="padding-left:8px;{MONO}font-size:11px;line-height:1;letter-spacing:.12em;text-transform:uppercase;color:{t};font-weight:600">{e(LABEL[kind])}</td>
 </tr></table>
 <div style="{HEAD}font-size:21px;line-height:1.25;font-weight:700;letter-spacing:-.01em;color:{INK};margin-top:9px">{e(sec["title"])}</div>{note}
</td></tr>
<tr><td style="padding:0 28px">
 <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{CARD}"
  style="background-color:{CARD};border:1px solid {LINE};border-top:3px solid {t};border-radius:10px">{rows}</table>
</td></tr>'''

def stat(s):
    t = TONES.get(s.get("tone", "ink"), TONES["ink"])[0]
    return (f'<td valign="top" style="padding:0 4px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{CARD}" '
            f'style="background-color:{CARD};border:1px solid {LINE};border-radius:10px"><tr><td style="padding:14px 12px">'
            f'<div style="{MONO}font-size:24px;line-height:1;font-weight:600;color:{t}">{e(s["value"])}</div>'
            f'<div style="{SANS}font-size:12px;line-height:1.35;color:{INK3};margin-top:7px">{e(s["label"])}</div></td></tr></table></td>')

def render(c):
    for k in ("week_ending", "headline", "dek", "stats", "sections"):
        if k not in c: raise SystemExit(f"content.json missing '{k}'")
    secs = sorted(c["sections"], key=lambda s: ORDER.index(s["kind"]))
    h = e(c["headline"])
    if c.get("headline_accent") and e(c["headline_accent"]) in h:
        a = e(c["headline_accent"])
        h = h.replace(a, f'<span style="color:{TONES["funding"][0]}">{a}</span>', 1)
    stats = "".join(stat(s) for s in c["stats"][:4])
    cov = (f'<div style="{SANS}font-size:13px;line-height:1.55;color:{INK2};margin-bottom:10px">{e(c["coverage"])}</div>'
           if c.get("coverage") else "")
    return f'''<meta name="color-scheme" content="light only"><meta name="supported-color-schemes" content="light">
<div style="display:none;max-height:0;overflow:hidden;opacity:0;color:{PAGE}">{e(c["dek"])}</div>
<table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0" bgcolor="{PAGE}" style="background-color:{PAGE}">
<tr><td align="center" style="padding:20px 10px">
<table role="presentation" width="640" cellpadding="0" cellspacing="0" border="0" bgcolor="{PAGE}" style="width:100%;max-width:640px;background-color:{PAGE}">

<tr><td bgcolor="{CARD}" style="background-color:{CARD};border:1px solid {LINE};border-top:3px solid {TONES["funding"][0]};border-radius:12px;padding:0">
 <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0">
  <tr><td style="padding:16px 24px;border-bottom:1px solid {LINE}">
   <table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>
    <td style="{HEAD}font-size:16px;font-weight:700;color:{INK}"><span style="color:{TONES["funding"][0]}">&#9673;</span>&nbsp; Deep Science Radar</td>
    <td align="right" style="{MONO}font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:{INK3}">Weekly digest</td>
   </tr></table></td></tr>
  <tr><td style="padding:26px 24px 8px">
   <div style="{MONO}font-size:11px;line-height:1.4;letter-spacing:.12em;text-transform:uppercase;color:{INK3}">India &middot; week ending {e(c["week_ending"])}</div>
   <div style="{HEAD}font-size:30px;line-height:1.15;font-weight:700;letter-spacing:-.02em;color:{INK};margin-top:12px">{h}</div>
   <div style="{SANS}font-size:15.5px;line-height:1.6;color:{INK2};margin-top:12px">{e(c["dek"])}</div>
  </td></tr>
  <tr><td style="padding:16px 20px 22px"><table role="presentation" width="100%" cellpadding="0" cellspacing="0" border="0"><tr>{stats}</tr></table></td></tr>
 </table>
</td></tr>
{"".join(section(s) for s in secs)}
<tr><td style="padding:32px 28px 6px">
 {cov}
 <table role="presentation" cellpadding="0" cellspacing="0" border="0"><tr>
  <td bgcolor="{TONES["funding"][0]}" style="background-color:{TONES["funding"][0]};border-radius:8px">
   <a href="{SITE}" style="display:inline-block;{SANS}font-size:14px;font-weight:600;color:#FFFFFF;text-decoration:none;padding:11px 18px">Open the radar &rarr;</a></td>
  <td width="10">&nbsp;</td>
  <td bgcolor="{CARD}" style="background-color:{CARD};border:1px solid {LINE};border-radius:8px">
   <a href="{SITE}#updates" style="display:inline-block;{SANS}font-size:14px;font-weight:600;color:{INK};text-decoration:none;padding:10px 18px">All updates</a></td>
 </tr></table>
</td></tr>
<tr><td style="padding:24px 28px 30px">
 <div style="border-top:1px solid {LINE};padding-top:14px;{SANS}font-size:12px;line-height:1.65;color:{INK3}">
 <b style="color:{INK2}">TRL</b> (technology readiness level) runs from 1, an idea on paper, to 9, proven in real use.<br>
 Built and maintained by Varun Nankani. Every company links to its sources. Assessments are judgement calls from public information, not investment advice.</div>
</td></tr>
</table></td></tr></table>'''

def plain(c):
    out = [f"DEEP SCIENCE RADAR · WEEKLY DIGEST · week ending {c['week_ending']}", "", c["headline"], "", c["dek"], ""]
    out.append("  ·  ".join(f"{s['value']} {s['label']}" for s in c["stats"]))
    for s in sorted(c["sections"], key=lambda s: ORDER.index(s["kind"])):
        out += ["", s["title"].upper()]
        for it in s["items"]:
            n = (it.get("name") or it.get("lead")).rstrip(":")
            ch = f" [{it['chip_from'] + ' -> ' if it.get('chip_from') else ''}{it['chip']}]" if it.get("chip") else ""
            out.append(f"- {n}{ch}: " + " ".join(x for x in (it.get("meta"), it.get("body"), it.get("text")) if x))
    if c.get("coverage"): out += ["", c["coverage"]]
    out += ["", SITE, "Assessments are judgement calls from public information, not investment advice."]
    return "\n".join(out)

if __name__ == "__main__":
    if len(sys.argv) < 3: raise SystemExit(__doc__)
    content = json.load(open(sys.argv[1], encoding="utf-8"))
    doc = render(content)
    if "—" in doc: raise SystemExit("No em dashes in the digest.")
    open(sys.argv[2], "w", encoding="utf-8").write(re.sub(r"\s*\n\s*", " ", doc))
    if len(sys.argv) > 3: open(sys.argv[3], "w", encoding="utf-8").write(plain(content))
    print("ok", len(doc))
