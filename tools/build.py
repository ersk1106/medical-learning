"""Build the static learning site from content/*.md into site/.

Usage: python3 tools/build.py
"""
import os, re, shutil, html
import markdown

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "content")
OUT = os.path.join(ROOT, "site")

CSS = """
:root{--ink:#1f2328;--sub:#5d6670;--line:#e3e6ea;--bg:#ffffff;--soft:#f6f7f9;--accent:#2f5d9e;--warn:#9a3b2f}
*{box-sizing:border-box}
body{margin:0;font-family:'Hiragino Sans','Noto Sans JP','Noto Sans CJK JP',system-ui,sans-serif;color:var(--ink);background:var(--bg);line-height:1.8;font-size:16px}
header{position:sticky;top:0;z-index:5;background:#fff;border-bottom:1px solid var(--line)}
.bar{display:flex;align-items:center;gap:12px;max-width:860px;margin:0 auto;padding:10px 16px}
.brand{font-weight:700;color:var(--ink);text-decoration:none;font-size:15px}
details.nav{margin-left:auto}
details.nav summary{cursor:pointer;list-style:none;padding:6px 12px;border:1px solid var(--line);border-radius:999px;font-size:14px}
details.nav summary::-webkit-details-marker{display:none}
details.nav[open] .menu{display:block}
.menu{display:none;position:absolute;right:16px;top:52px;background:#fff;border:1px solid var(--line);border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,.08);padding:8px;max-height:70vh;overflow:auto;width:min(320px,90vw)}
.menu a{display:block;padding:8px 10px;border-radius:8px;color:var(--ink);text-decoration:none;font-size:14px}
.menu a:hover,.menu a.cur{background:var(--soft)}
.menu .grp{font-size:12px;color:var(--sub);padding:8px 10px 2px}
main{max-width:860px;margin:0 auto;padding:20px 16px 64px}
h1{font-size:26px;line-height:1.4;margin:8px 0 4px}
h2{font-size:21px;margin:36px 0 10px;padding-top:12px;border-top:1px solid var(--line)}
h3{font-size:17px;margin:22px 0 6px}
p,li{font-size:16px}
a{color:var(--accent)}
img{max-width:100%;height:auto;border:1px solid var(--line);border-radius:10px;margin:8px 0}
table{border-collapse:collapse;width:100%;margin:10px 0;font-size:14px;display:block;overflow-x:auto}
th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{background:var(--soft);white-space:nowrap}
blockquote{margin:12px 0;padding:8px 14px;background:var(--soft);border-left:4px solid var(--accent);border-radius:6px;color:var(--sub)}
.meta{color:var(--sub);font-size:13px;margin-bottom:8px}
.pager{display:flex;justify-content:space-between;gap:12px;margin-top:40px;font-size:14px}
.pager a{flex:1;padding:10px 12px;border:1px solid var(--line);border-radius:10px;text-decoration:none;color:var(--ink)}
.pager a.next{text-align:right}
#qa{margin-top:40px;padding:16px;border:1px solid var(--line);border-radius:14px;background:var(--soft)}
#qa h2{border:0;margin:0 0 4px;padding:0;font-size:19px}
.qa-lead{color:var(--sub);font-size:13px;margin:0 0 10px}
.qa-chips{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:10px}
.qa-chip{font:inherit;font-size:13px;padding:6px 10px;border:1px solid var(--line);border-radius:999px;background:#fff;color:var(--ink);cursor:pointer}
.qa-log{display:flex;flex-direction:column;gap:8px;margin-bottom:10px}
.qa-msg{padding:10px 12px;border-radius:12px;font-size:15px;line-height:1.7;max-width:100%}
.qa-msg p{margin:0 0 6px;font-size:15px}.qa-msg p:last-child{margin:0}
.qa-msg ul{margin:4px 0 6px;padding-left:20px}.qa-msg li{font-size:15px}
.qa-user{align-self:flex-end;background:var(--accent);color:#fff;max-width:85%}
.qa-bot{align-self:flex-start;background:#fff;border:1px solid var(--line)}
.qa-note{color:var(--sub);font-size:12px}
#qa textarea{width:100%;min-height:72px;font:inherit;font-size:16px;padding:10px;border:1px solid var(--line);border-radius:10px;resize:vertical}
.qa-row{display:flex;gap:8px;align-items:center;margin-top:8px;flex-wrap:wrap}
.qa-send{font:inherit;padding:8px 18px;border:0;border-radius:999px;background:var(--accent);color:#fff;cursor:pointer}
.qa-send:disabled{opacity:.5}
.qa-stop,.qa-clear{font:inherit;font-size:13px;padding:6px 12px;border:1px solid var(--line);border-radius:999px;background:#fff;cursor:pointer}
.qa-status{color:var(--sub);font-size:13px}
.qa-fab{position:fixed;right:16px;bottom:16px;z-index:6;background:var(--accent);color:#fff;text-decoration:none;padding:10px 16px;border-radius:999px;box-shadow:0 6px 18px rgba(0,0,0,.18);font-size:14px}
footer{color:var(--sub);font-size:12px;text-align:center;padding:24px 16px;border-top:1px solid var(--line)}
"""


def read_md(path):
    text = open(path, encoding="utf-8").read()
    meta = {}
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if m:
        for line in m.group(1).splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
        text = text[m.end():]
    return meta, text


def render(md_text, depth):
    body = markdown.markdown(md_text, extensions=["tables", "sane_lists"])
    # figures: content/lessons uses ../../figures/ -> site path
    prefix = "../" * depth
    body = body.replace('src="../../figures/', f'src="{prefix}figures/')
    # tap a figure to open it full size
    body = re.sub(r'(<img [^>]*src="([^"]+)"[^>]*>)', r'<a href="\2" target="_blank">\1</a>', body)
    # links to other content pages: .md -> .html (already html in sources)
    body = re.sub(r'href="(?!https?:)([^"]+)\.md"', r'href="\1.html"', body)
    # external links open in new tab
    body = re.sub(r'<a href="(https?://[^"]+)"', r'<a href="\1" target="_blank" rel="noopener"', body)
    return body


QA = """<section id="qa"><h2>この教材について質問する</h2>
<p class="qa-lead">このページの内容をもとに Claude が答えます。医学的な判断は必ず専門家に確認してください。</p>
<div class="qa-chips">
<button class="qa-chip" type="button" data-q="この回の内容を3行でまとめて">3行でまとめて</button>
<button class="qa-chip" type="button" data-q="中学生にもわかるように、たとえ話を使って説明して">もっとやさしく</button>
<button class="qa-chip" type="button" data-q="この回の内容で、一般向け解説動画の冒頭30秒のナレーション案を書いて。誤解を招く表現は避けて">動画の台本案</button>
<button class="qa-chip" type="button" data-q="この手技について医師や看護師に取材するとき、聞くとよい質問を5つ挙げて">取材で聞くこと</button>
<button class="qa-chip" type="button" data-q="この回の内容から理解度を確かめる問題を3問出して。答えは最後にまとめて">問題を出して</button>
</div>
<div class="qa-log" aria-live="polite"></div>
<form><textarea placeholder="例：ドレーンはいつ抜くの？　この用語の意味は？" aria-label="質問"></textarea>
<div class="qa-row"><button class="qa-send" type="submit">送信</button><button class="qa-stop" type="button" hidden>停止</button><button class="qa-clear" type="button" hidden>履歴を消す</button><span class="qa-status"></span></div></form>
</section>"""


def page(title, body, nav_html, depth, meta_line="", pager=""):
    p = "../" * depth
    return f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}｜医療知識 学習ロードマップ</title>
<style>{CSS}</style></head>
<body>
<header><div class="bar"><a class="brand" href="{p}index.html">医療知識 学習ロードマップ</a>
<details class="nav"><summary>目次</summary><div class="menu">{nav_html}</div></details></div></header>
<main>{meta_line}<article>{body}</article>{pager}{QA}</main>
<a class="qa-fab" href="#qa">質問する</a>
<script src="{p}qa.js"></script>
<footer>医療系動画制作者のための学習教材。医学的判断の根拠にはせず、必ず専門家の監修を受けてください。</footer>
</body></html>"""


def main():
    if os.path.isdir(OUT):
        shutil.rmtree(OUT)
    os.makedirs(os.path.join(OUT, "lessons"))
    shutil.copy(os.path.join(ROOT, "tools", "qa.js"), os.path.join(OUT, "qa.js"))
    # figures (PNG only)
    for sub in sorted(os.listdir(os.path.join(ROOT, "figures"))):
        d = os.path.join(ROOT, "figures", sub)
        if not os.path.isdir(d):
            continue
        os.makedirs(os.path.join(OUT, "figures", sub), exist_ok=True)
        for f in os.listdir(d):
            if f.endswith(".png"):
                shutil.copy(os.path.join(d, f), os.path.join(OUT, "figures", sub, f))

    top = [("index", *read_md(os.path.join(SRC, "index.md"))), ("basics", *read_md(os.path.join(SRC, "basics.md")))]
    lessons = []
    for f in os.listdir(os.path.join(SRC, "lessons")):
        if f.endswith(".md"):
            meta, text = read_md(os.path.join(SRC, "lessons", f))
            lessons.append((f[:-3], meta, text))
    lessons.sort(key=lambda x: (x[1].get("date", ""), int(x[1].get("no", "0") or 0) if x[1].get("no", "0") != "0" else 0.5))

    def nav(depth, cur):
        p = "../" * depth
        items = [f'<a href="{p}index.html" class="{"cur" if cur=="index" else ""}">トップ（ロードマップ・学習ログ）</a>',
                 f'<a href="{p}basics.html" class="{"cur" if cur=="basics" else ""}">総論：病院の全体像</a>',
                 '<div class="grp">レッスン</div>']
        for slug, meta, _ in lessons:
            items.append(f'<a href="{p}lessons/{slug}.html" class="{"cur" if cur==slug else ""}">{html.escape(meta.get("short", meta.get("title", slug)))}</a>')
        return "".join(items)

    for slug, meta, text in top:
        open(os.path.join(OUT, f"{slug}.html"), "w", encoding="utf-8").write(
            page(meta.get("title", slug), render(text, 0), nav(0, slug), 0))

    for i, (slug, meta, text) in enumerate(lessons):
        prev_ = lessons[i - 1] if i > 0 else None
        next_ = lessons[i + 1] if i + 1 < len(lessons) else None
        pg = '<div class="pager">'
        pg += f'<a href="{prev_[0]}.html">← {html.escape(prev_[1].get("short",""))}</a>' if prev_ else "<span></span>"
        pg += f'<a class="next" href="{next_[0]}.html">{html.escape(next_[1].get("short",""))} →</a>' if next_ else "<span></span>"
        pg += "</div>"
        ml = f'<div class="meta">配信日：{meta.get("date","")}　分野：{html.escape(meta.get("group",""))}</div>'
        open(os.path.join(OUT, "lessons", f"{slug}.html"), "w", encoding="utf-8").write(
            page(meta.get("title", slug), render(text, 1), nav(1, slug), 1, ml, pg))
    print(f"built {len(top)} pages + {len(lessons)} lessons -> {OUT}")


if __name__ == "__main__":
    main()
