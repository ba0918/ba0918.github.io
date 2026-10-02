#!/usr/bin/env python3
"""Build the portfolio top page for https://ba0918.github.io/.

Featured products and their EN/JA blurbs come from site/products.json. Every
other public, non-fork, non-archived repository is listed from the GitHub API,
so a new repository (or a new project site under /<repo>/) shows up on the next
build without editing this repository.

Usage:
  python3 site/build.py --out _site [--repos repos.json]

--repos reads a saved `GET /users/<user>/repos` response instead of calling the
API (for offline previews). GITHUB_TOKEN, when set, is sent with API requests.
"""

import argparse
import datetime
import html
import json
import os
import shutil
import sys
import urllib.request
from pathlib import Path

USER = "ba0918"
ROOT = Path(__file__).resolve().parent


def esc(text):
    return html.escape(text or "", quote=True)


def fetch_repos():
    repos, page = [], 1
    headers = {"Accept": "application/vnd.github+json", "User-Agent": f"{USER}-portfolio-build"}
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"
    while True:
        url = f"https://api.github.com/users/{USER}/repos?type=owner&sort=pushed&per_page=100&page={page}"
        with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as res:
            batch = json.load(res)
        if not isinstance(batch, list):
            raise RuntimeError(f"unexpected API response: {batch!r}")
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1


def site_url(repo):
    """The project site URL for a repository, if it publishes one."""
    homepage = (repo.get("homepage") or "").strip()
    if homepage.startswith("https://"):
        return homepage
    if repo.get("has_pages"):
        return f"https://{USER}.github.io/{repo['name']}/"
    return None


def lang_badge(repo):
    lang = repo.get("language")
    return f'<span class="lang">{esc(lang)}</span>' if lang else ""


def updated(repo):
    pushed = (repo.get("pushed_at") or "")[:10]
    if not pushed:
        return ""
    return (
        f'<time datetime="{pushed}"><span class="en">Updated {pushed}</span>'
        f'<span class="ja">{pushed} 更新</span></time>'
    )


def links(repo_url, site):
    out = []
    if site:
        out.append(
            f'<a class="button primary" href="{esc(site)}">'
            '<span class="en">Website</span><span class="ja">サイトを見る</span></a>'
        )
    out.append(f'<a class="button" href="{esc(repo_url)}">GitHub</a>')
    return "".join(out)


def featured_card(item, repo):
    name = item["repo"]
    repo_url = repo.get("html_url") or f"https://github.com/{USER}/{name}"
    site = item.get("site") or site_url(repo)
    meta = " ".join(x for x in (lang_badge(repo), updated(repo)) if x)
    return f"""<article class="card">
  <h3><a href="{esc(site or repo_url)}">{esc(name)}</a></h3>
  <p class="en">{esc(item["en"])}</p>
  <p class="ja">{esc(item["ja"])}</p>
  <p class="meta">{meta}</p>
  <div class="card-links">{links(repo_url, site)}</div>
</article>"""


def repo_row(repo):
    site = site_url(repo)
    site_link = (
        f' <a class="site-link" href="{esc(site)}"><span class="en">Website</span><span class="ja">サイト</span></a>'
        if site
        else ""
    )
    desc = repo.get("description") or ""
    meta = " ".join(x for x in (lang_badge(repo), updated(repo)) if x)
    return f"""<li>
  <div class="repo-head"><a href="{esc(repo["html_url"])}">{esc(repo["name"])}</a>{site_link}</div>
  {f'<p>{esc(desc)}</p>' if desc else ''}
  <p class="meta">{meta}</p>
</li>"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", required=True)
    parser.add_argument("--repos", help="saved /users/<user>/repos JSON instead of calling the API")
    args = parser.parse_args()

    config = json.loads((ROOT / "products.json").read_text(encoding="utf-8"))
    if args.repos:
        repos = json.loads(Path(args.repos).read_text(encoding="utf-8"))
    else:
        try:
            repos = fetch_repos()
        except Exception as error:  # still publish the featured products
            print(f"warning: could not list repositories: {error}", file=sys.stderr)
            repos = []

    public = [r for r in repos if not r.get("private")]
    by_name = {r["name"]: r for r in public}
    featured_names = {item["repo"] for item in config["featured"]}
    skip = featured_names | set(config.get("exclude", []))

    featured = "\n".join(featured_card(item, by_name.get(item["repo"], {})) for item in config["featured"])
    others = [r for r in public if not r.get("fork") and not r.get("archived") and r["name"] not in skip]
    others.sort(key=lambda r: r.get("pushed_at") or "", reverse=True)
    other_rows = "\n".join(repo_row(r) for r in others)

    page = (ROOT / "template.html").read_text(encoding="utf-8")
    page = page.replace("{{featured}}", featured)
    page = page.replace("{{others}}", other_rows)
    page = page.replace("{{others_hidden}}", "" if others else " hidden")
    page = page.replace("{{built}}", datetime.date.today().isoformat())

    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    (out / "index.html").write_text(page, encoding="utf-8")
    for asset in ("style.css", "favicon.svg"):
        shutil.copy(ROOT / asset, out / asset)
    (out / ".nojekyll").write_text("")
    print(f"built {out / 'index.html'}: {len(config['featured'])} featured, {len(others)} other repositories")


if __name__ == "__main__":
    main()
