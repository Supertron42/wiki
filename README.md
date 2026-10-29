# Supertron's documentation website

Documentation for Skyrim mods, developer tools and World of Warcraft guides.

- Website: https://supertron42.github.io/wiki/
- Project directory: https://supertron42.github.io/wiki/projects.html
- Repository: https://github.com/Supertron42/wiki

## Where things belong

`site/` contains the public website. `projects.json` registers projects and their source links. `tools/` maintains the registry, sitemap and checks. `docs/` explains the structure. Individual applications keep source, builds, tests and developer documentation in separate repositories.

Read [CONTRIBUTING.md](CONTRIBUTING.md) for daily changes, [docs/STRUCTURE.md](docs/STRUCTURE.md) for file placement, and [AGENTS.md](AGENTS.md) for automation rules. Codex, Claude, Cursor, Copilot and Gemini entry files refer to the same rules. Other programs must be configured to read them; the deployment checks enforce the website boundary regardless of editor.

## Check and preview

Use Python 3.11 or newer and Node.js 22 or newer. No package installation is required.

```text
python tools/site_tools.py sync
python -m unittest discover -s tests
node --test tests/site.test.cjs
python tools/site_tools.py check
python -m http.server 8000 --directory site
```

Open http://localhost:8000/ to preview. Relative page links work locally; canonical/share URLs intentionally point to the public `/wiki/` address. Stop the server with Ctrl+C.

## Add a project

```text
python tools/site_tools.py new-project example-tool --name "Example Tool" --description "What the tool does." --category software
```

This creates a registered starter page and refreshes the project directory and sitemap. Replace the starter with verified instructions before publishing. Add `--source-url https://github.com/OWNER/REPOSITORY` only when that repository exists and is intended to be public. The command does not create a source repository or upload source code.

## Publishing

GitHub Actions validates pull requests and pushes, then deploys only `site/` on pushes to `main` or a manual workflow run on `main`. A failed validation blocks that workflow's deployment. Review changes before committing or pushing. Repository branch-protection settings are managed separately; this cleanup does not change them.

Existing project URLs and legacy `wiki.html` redirects are retained. The repository name remains `wiki`, so the site keeps its `/wiki/` prefix.
