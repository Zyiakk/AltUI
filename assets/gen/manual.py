"""AltUI manual for the Kodex tab: assets/manual/<lang>.md -> Strings keys Man_<id>_T (title) / Man_<id>_B (text).
A chapter starts with '## Title {#id}' (the id is the same in every language, order = en.md); the text runs to the
next '## '. Paragraphs and '- ' lists only ('- ' becomes '• '); anything before the first chapter is ignored."""
import os, re
DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "manual")
HEAD = re.compile(r"^## (.+?)\s*\{#([a-z0-9]+)\}\s*$")


def parse(text):
    out, cur = [], None
    for line in text.splitlines():
        if line.startswith("## "):
            m = HEAD.match(line)
            if not m: raise ValueError("chapter without {#id}: " + line)
            cur = [m.group(2), m.group(1), []]; out.append(cur)
        elif cur is not None:
            cur[2].append("• " + line[2:] if line.startswith("- ") else line)
    return [(i, t, "\n".join(b).strip()) for i, t, b in out]


def load(lang):
    with open(os.path.join(DIR, lang + ".md"), encoding="utf-8") as f: return parse(f.read())


def chapters():
    return [i for i, _, _ in load("en")]


def rows(langs, docs=None):
    """{"Man_<id>_T": (title per lang), "Man_<id>_B": (text per lang)}; braces doubled - strings.rows() runs str.format over every cell."""
    docs = docs or {l: load(l) for l in langs}
    per = {l: {i: (t, b) for i, t, b in docs[l]} for l in langs}
    esc = lambda s: s.replace("{", "{{").replace("}", "}}")
    out = {}
    for i, _, _ in docs[langs[0]]:
        out["Man_%s_T" % i] = tuple(esc(per[l][i][0]) for l in langs)
        out["Man_%s_B" % i] = tuple(esc(per[l][i][1]) for l in langs)
    return out
