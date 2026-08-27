#!/usr/bin/env python3
"""
LAB53 site builder — turns posts-src/<slug>/post.md into journal/<slug>/index.html
and regenerates the post list in blog.html.

Usage:
    python3 build.py

No dependencies beyond the Python standard library — nothing to install.

--------------------------------------------------------------------------
HOW TO WRITE A POST
--------------------------------------------------------------------------
1. Make a new folder: posts-src/your-post-slug/
2. Inside it, create post.md:

       title: Your Post Title
       date: 2026-09-01
       category: Exhibitions
       image: cover.jpg
       excerpt: One or two sentences for the blog listing card.
       ---
       Your first paragraph.

       Your second paragraph. **Bold** and *italic* both work inline.

       ^A short caption line, e.g. an image credit or artwork title.

       > A pulled quote, styled as a block quote.

       Q: A question, for interview-style posts.
       An answer paragraph right after a Q: line is treated as normal text.

       NOTE: An editorial note, e.g. "This interview originally appeared in..."

3. If your image is a file (not a URL), put it in the same folder
   (posts-src/your-post-slug/cover.jpg) and set `image: cover.jpg` in the
   front matter — the build copies it into the post's own journal folder.
   If `image:` starts with http:// or https://, it's used as-is (hotlinked).
4. Run:  python3 build.py
5. Check the result, then:  git add -A && git commit -m "New post: ..." && git push

The "slug" (folder name) becomes the URL: /journal/your-post-slug/
--------------------------------------------------------------------------
"""
import os
import re
import glob
import shutil
import sys
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC_DIR = os.path.join(ROOT, "posts-src")
OUT_DIR = os.path.join(ROOT, "journal")
BLOG_PATH = os.path.join(ROOT, "blog.html")

CATEGORY_CLASS = {
    "Exhibitions": "on-teal",
    "Interview": "on-gold",
    "Essay": "on-coral",
}
DEFAULT_CLASS = "on-paper"

PAGE_TEMPLATE = """<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="UTF-8">
<title>{title} — LAB53 Journal</title>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{desc}">
<link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' fill='%2300A99D'/%3E%3Ctext x='32' y='44' font-family='Poppins, sans-serif' font-weight='700' font-size='32' fill='white' text-anchor='middle'%3E53%3C/text%3E%3C/svg%3E">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,340;0,9..144,440;0,9..144,560;1,9..144,340;1,9..144,440&family=Poppins:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500;600&display=swap">
<link rel="stylesheet" href="/style.css">
</head>
<body>

<nav class="topnav">
  <div class="wrap topnav-inner">
    <a href="/index.html" class="topnav-mark"><img src="/assets/logo-teal.png" alt="LAB53"></a>
    <div class="topnav-links">
      <a href="/index.html">Mission</a>
      <a href="/blog.html" class="current">Blog</a>
      <a href="/contact.html">Contact</a>
    </div>
  </div>
</nav>

<main>
  <section class="band" style="border-bottom:none;">
    <div class="post-single-wrap">
      <p class="post-back"><a href="/blog.html">&larr; Journal</a></p>
      <div class="post-single-thumb"><img src="{image}" alt="{title}" loading="lazy"></div>
      <span class="post-single-meta">{date_disp} — {category}</span>
      <h1 class="post-single-title">{title}</h1>
      <div class="post-body">
{body}
      </div>
      <p class="post-single-foot">No. {num} — LAB53 Journal — originally published {orig_date}</p>
    </div>
  </section>
</main>

<footer>
  <div class="wrap foot-inner">
    <div class="foot-mark"><span class="dot"></span> LAB53 — Contemporary art, Caribbean, Latin America &amp; diasporas</div>
    <div class="foot-links">
      <a href="mailto:hello@projectlab53.com">Email</a>
      <a href="https://instagram.com/project_lab53" target="_blank" rel="noopener">Instagram</a>
      <a href="/contact.html">Contact</a>
    </div>
    <div class="foot-meta">Est. 2015</div>
  </div>
</footer>

</body>
</html>
"""

CARD_TEMPLATE = """        <a class="post-card" href="/journal/{slug}/">
          <div class="post-thumb"><img src="{image}" alt="Cover image for {title_attr}" loading="lazy"><span class="stamp {tagclass}">{num}</span></div>
          <div>
            <span class="post-cap">{date_disp} — {category}</span>
            <h3 class="post-title">{title}</h3>
            <p class="post-excerpt">{excerpt}</p>
          </div>
        </a>"""


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def inline_md(text):
    text = esc(text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", text)
    return text


def render_body(raw):
    blocks = [b.strip() for b in re.split(r"\n\s*\n", raw.strip()) if b.strip()]
    out = []
    for b in blocks:
        b = " ".join(line.strip() for line in b.splitlines())
        if b.startswith("^"):
            out.append(f'        <p class="cap-line">{inline_md(b[1:].strip())}</p>')
        elif b.startswith("> "):
            out.append(f"        <blockquote>{inline_md(b[2:].strip())}</blockquote>")
        elif b.startswith("Q: "):
            out.append(f'        <p class="q"><strong>{inline_md(b[3:].strip())}</strong></p>')
        elif b.startswith("NOTE: "):
            out.append(f'        <p class="note">{inline_md(b[6:].strip())}</p>')
        else:
            out.append(f"        <p>{inline_md(b)}</p>")
    return "\n".join(out)


def parse_post(path):
    with open(path, encoding="utf-8") as f:
        raw = f.read()
    if "\n---\n" not in raw:
        raise ValueError(f"{path}: missing '---' separator between front matter and body")
    fm_raw, body_raw = raw.split("\n---\n", 1)
    fm = {}
    for line in fm_raw.strip().splitlines():
        if not line.strip() or ":" not in line:
            continue
        k, v = line.split(":", 1)
        fm[k.strip().lower()] = v.strip()
    for required in ("title", "date", "category", "image", "excerpt"):
        if required not in fm:
            raise ValueError(f"{path}: missing required front matter field '{required}'")
    return fm, body_raw


def main():
    if not os.path.isdir(SRC_DIR):
        print(f"No {SRC_DIR} found — nothing to build.")
        return 1

    posts = []
    for post_dir in sorted(glob.glob(os.path.join(SRC_DIR, "*"))):
        if not os.path.isdir(post_dir):
            continue
        slug = os.path.basename(post_dir)
        md_path = os.path.join(post_dir, "post.md")
        if not os.path.isfile(md_path):
            print(f"skip {slug}: no post.md")
            continue
        fm, body_raw = parse_post(md_path)
        try:
            date_obj = datetime.strptime(fm["date"], "%Y-%m-%d")
        except ValueError:
            print(f"error in {slug}: date must be YYYY-MM-DD, got {fm['date']!r}")
            return 1

        image = fm["image"]
        if not image.startswith(("http://", "https://")):
            src_img = os.path.join(post_dir, image)
            if not os.path.isfile(src_img):
                print(f"error in {slug}: image file '{image}' not found next to post.md")
                return 1
            out_post_dir = os.path.join(OUT_DIR, slug)
            os.makedirs(out_post_dir, exist_ok=True)
            shutil.copyfile(src_img, os.path.join(out_post_dir, image))
            image_ref = f"/journal/{slug}/{image}"
        else:
            image_ref = image

        posts.append(dict(
            slug=slug,
            title=fm["title"],
            date_obj=date_obj,
            category=fm["category"],
            image=image_ref,
            excerpt=fm["excerpt"],
            body_raw=body_raw,
            lang=fm.get("lang", "en"),
        ))

    if not posts:
        print("No posts found in posts-src/.")
        return 1

    posts.sort(key=lambda p: p["date_obj"], reverse=True)

    cards = []
    for i, p in enumerate(posts, start=1):
        num = f"{i:02d}"
        date_disp = p["date_obj"].strftime("%Y.%m.%d")
        orig_date = p["date_obj"].strftime("%B %-d, %Y") if sys.platform != "win32" else p["date_obj"].strftime("%B %d, %Y")
        tagclass = CATEGORY_CLASS.get(p["category"], DEFAULT_CLASS)

        page_html = PAGE_TEMPLATE.format(
            lang=p["lang"],
            title=esc(p["title"]),
            desc=esc(p["excerpt"]),
            image=p["image"],
            date_disp=date_disp,
            category=esc(p["category"]),
            num=num,
            orig_date=orig_date,
            body=render_body(p["body_raw"]),
        )
        out_post_dir = os.path.join(OUT_DIR, p["slug"])
        os.makedirs(out_post_dir, exist_ok=True)
        with open(os.path.join(out_post_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(page_html)

        cards.append(CARD_TEMPLATE.format(
            slug=p["slug"],
            image=p["image"],
            title_attr=esc(p["title"]),
            title=inline_md(p["title"]),
            date_disp=date_disp,
            category=esc(p["category"]),
            excerpt=inline_md(p["excerpt"]),
            tagclass=tagclass,
            num=num,
        ))
        print(f"built  {num}  {p['slug']}")

    # splice the generated cards into blog.html between markers
    with open(BLOG_PATH, encoding="utf-8") as f:
        blog_html = f.read()

    start_marker = '<div class="post-list">'
    end_marker = "</div>\n    </div>\n  </section>\n</main>"
    start_i = blog_html.index(start_marker) + len(start_marker)
    end_i = blog_html.index(end_marker, start_i)

    new_blog_html = (
        blog_html[:start_i]
        + "\n\n"
        + "\n\n".join(cards)
        + "\n\n      "
        + blog_html[end_i:]
    )
    with open(BLOG_PATH, "w", encoding="utf-8") as f:
        f.write(new_blog_html)

    print(f"\nbuilt {len(posts)} posts, updated blog.html")
    return 0


if __name__ == "__main__":
    sys.exit(main())
