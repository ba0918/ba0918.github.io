# ba0918.github.io

Portfolio top page for https://ba0918.github.io/.

- `site/products.json` — ordered categories, featured products and their EN/JA descriptions. Add an entry to a category's `items`; set `site` for a website or `store` for a Chrome Web Store listing. `title` optionally overrides the repository name. All category items are excluded from Recent work.
- `site/build.py` — renders `site/template.html`. The six most recently pushed public, non-fork, non-archived repositories are listed from the GitHub API, excluding featured products and the configured exclusions. Older entries remain available via the all-repositories link. A repository that publishes GitHub Pages gets a "Website" link automatically.
- `.github/workflows/pages.yml` — builds and deploys on every push to `master`, and once a day so the repository list stays current. Pages source must be set to "GitHub Actions".

Each product publishes its own site from its own repository at `https://ba0918.github.io/<repo>/`.

Preview locally:

```sh
python3 site/build.py --out _site && python3 -m http.server -d _site
```

Run `python3 site/check.py --out _site` before previewing or publishing (Python 3.11+
and Node.js 18+). Pages uses the same check for JavaScript, the language contract,
local assets and fragment links. Use `--repos repos.json` with the builder to reuse a
saved GitHub API response for offline or before/after comparisons.

Language selection reads a valid `ba0918-language` (`en`/`ja`) first, then the legacy
`portfolio-lang`, otherwise English. Browser language no longer determines the initial
page language. Reading never writes or promotes a legacy value. Only an explicit
switch saves the shared key; storage denial still allows in-page switching. Other
ba0918 pages inherit the choice on navigation/reload, without live tab synchronization.
