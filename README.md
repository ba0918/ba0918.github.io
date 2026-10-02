# ba0918.github.io

Portfolio top page for https://ba0918.github.io/.

- `site/products.json` — featured products and their EN/JA descriptions. Add an entry here to feature a new product; set `site` when it has its own website.
- `site/build.py` — renders `site/template.html`. The six most recently pushed public, non-fork, non-archived repositories are listed from the GitHub API, excluding featured products and the configured exclusions. Older entries remain available via the all-repositories link. A repository that publishes GitHub Pages gets a "Website" link automatically.
- `.github/workflows/pages.yml` — builds and deploys on every push to `master`, and once a day so the repository list stays current. Pages source must be set to "GitHub Actions".

Each product publishes its own site from its own repository at `https://ba0918.github.io/<repo>/`.

Preview locally:

```sh
python3 site/build.py --out _site && python3 -m http.server -d _site
```
