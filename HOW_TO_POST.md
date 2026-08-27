# Writing & publishing a new LAB53 journal post

No Jekyll, no plugins, nothing to install — just a folder, a text file, and one command. This lives entirely inside your `Website/` folder (and its mirror in `projectlab53-repo/`).

## 1. Make a new post folder

Inside `posts-src/`, create a folder named after your post's URL slug (lowercase, hyphens, no spaces), e.g.:

```
posts-src/new-exhibition-2026/
```

## 2. Write `post.md` inside it

```
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
```

Front matter fields:
- `title`, `date` (YYYY-MM-DD), `category` — use `Exhibitions`, `Interview`, or `Essay` to match the site's color-coding (anything else falls back to a neutral stamp), `image`, `excerpt` — all required.
- `lang` — optional, `en` or `es` (defaults to `en`), sets the page's language attribute.

Body syntax — separate every block (paragraph, caption, quote, etc.) with a **blank line**:
- Plain line → normal paragraph.
- `^text` → small italic caption (image credits, artwork titles).
- `> text` → pulled quote / blockquote.
- `Q: text` → bold interview question.
- `NOTE: text` → small editorial note at the end.
- `**bold**` and `*italic*` work inline anywhere.

## 3. Add your image

- **Local file** (recommended): drop it in the same folder — `posts-src/new-exhibition-2026/cover.jpg` — and set `image: cover.jpg`. The build step copies it into the live site automatically.
- **Hotlinked URL**: set `image: https://...` directly and it's used as-is.

## 4. Build the site

From the `Website/` folder (or `projectlab53-repo/`, wherever you're working):

```
python3 build.py
```

This reads every `posts-src/*/post.md`, regenerates that post's page at `journal/<slug>/index.html`, and rebuilds the post list on `blog.html` — newest post first, auto-numbered. Existing posts are untouched unless you edit their `post.md`.

## 5. Preview it (optional but recommended)

```
python3 -m http.server 8000
```

then open `http://localhost:8000/blog.html` in your browser and click through to the new post.

## 6. Publish

Do this inside `projectlab53-repo/` (the folder connected to GitHub):

```
git add -A
git commit -m "New post: Your Post Title"
git push
```

GitHub Pages picks it up automatically — the live site updates within a minute or two.

## To edit or remove a post later

- **Edit**: change its `post.md`, run `python3 build.py` again, commit, push.
- **Remove**: delete its folder from `posts-src/`, run `python3 build.py`, then also delete the now-orphaned `journal/<slug>/` folder by hand before committing (the builder doesn't delete old pages on its own — do a quick sanity check of `blog.html` and `journal/` before pushing).

## Keeping the two folders in sync

`Website/` is your working copy; `projectlab53-repo/` is what's connected to GitHub. Whichever one you write new posts in, copy the same `posts-src/<slug>/` folder into the other before running `build.py` there too, so both stay identical. (Simplest habit: always work directly inside `projectlab53-repo/`, since that's the one you push from.)
