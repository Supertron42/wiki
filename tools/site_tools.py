"""Maintain registry cards, project directory and sitemap; validate deployment.

WIRING: projects.json owns directory/home/Skyrim cards; site/ is publish-only.
The Pages workflow calls `check` before upload. Run `sync` after adding pages.
Only Python's standard library is required. Paths resolve from this file.
"""
from __future__ import annotations

import argparse
import html
from html.parser import HTMLParser
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import quote, unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "https://supertron42.github.io/wiki/"
RESERVED_DIRS = {"assets", "imagedump"}
ROOT_FILES = {"index.html", "skyrim.html", "projects.html", "sitemap.xml", "robots.txt",
              ".nojekyll", "google0c75560096bc82d2.html"}
REPO_FILES = {"README.md", "AGENTS.md", "CLAUDE.md", "GEMINI.md", "CONTRIBUTING.md",
              ".gitignore", ".gitattributes", ".editorconfig", "projects.json", "LICENSE", "LICENSE.md"}
EXTENSIONS = {".html", ".css", ".js", ".png", ".webp", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".avif", ".woff", ".woff2"}
FORBIDDEN_PARTS = {"resources", "research", "private", "backups", "backup", "drafts", "node_modules", "__pycache__", ".git", ".claude", "tools", "tests"}
CSS_URL = re.compile(r"url\(\s*['\"]?([^)'\"]+)['\"]?\s*\)", re.I)
VOID_TAGS = {"meta", "link", "br", "hr", "img", "input", "source", "wbr", "area", "base", "embed", "param", "track", "col"}


class Page(HTMLParser):
    """Parse actual HTML tags, ignoring tag-like text in comments/scripts."""
    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.refs: list[str] = []
        self.ids: set[str] = set()
        self.canonicals: list[str] = []
        self.redirect: str | None = None
        self.title = ""
        self.inline_styles = 0
        self.inline_css: list[str] = []
        self.scripts: list[str] = []
        self.stack: list[str] = []
        self.content_layout = False
        self.outside_content: list[str] = []
        self._in_title = self._in_style = self._in_script = False
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id") == "content":
            self.content_layout = True
        if self.stack in (["html", "body"], ["body"]) and tag in {"section", "article", "h1", "h2", "h3", "p", "ul", "ol", "table", "pre"}:
            self.outside_content.append(tag)
        if tag not in VOID_TAGS:
            self.stack.append(tag)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("name"):
            self.ids.add(a["name"])
        for attr in ("href", "src", "poster"):
            if a.get(attr):
                self.refs.append(a[attr])
        if a.get("style"):
            self.inline_css.append(a["style"])
        if tag == "link" and a.get("rel", "").lower() == "canonical":
            self.canonicals.append(a.get("href", ""))
        if tag == "meta" and a.get("http-equiv", "").lower() == "refresh":
            match = re.search(r"url\s*=\s*(.+)", a.get("content", ""), re.I)
            if match:
                self.redirect = match[1].strip(" '\"")
                self.refs.append(self.redirect)
        if tag == "title":
            self._in_title = True
        if tag == "style":
            self.inline_styles += 1
            self._in_style = True
        if tag == "script":
            self._in_script = True

    def handle_endtag(self, tag):
        if tag in self.stack:
            index = len(self.stack) - 1 - self.stack[::-1].index(tag)
            self.stack = self.stack[:index]
        if tag == "title":
            self._in_title = False
        if tag == "style":
            self._in_style = False
        if tag == "script":
            self._in_script = False

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._in_style:
            self.inline_css.append(data)
        if self._in_script:
            self.scripts.append(data)


def read_registry(root: Path):
    data = json.loads((root / "projects.json").read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or data.get("base_url") != BASE_URL:
        raise ValueError("projects.json requires schema_version 1 and the established /wiki/ base_url")
    projects = data.get("projects")
    if not isinstance(projects, list) or not projects:
        raise ValueError("projects.json requires a nonempty projects list")
    seen = set()
    for p in projects:
        if not isinstance(p, dict):
            raise ValueError("Every project must be an object")
        slug = p.get("slug", "")
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", slug) or slug in RESERVED_DIRS or slug in seen:
            raise ValueError(f"Invalid, duplicate or reserved slug: {slug!r}")
        seen.add(slug)
        if p.get("entry") != f"{slug}/index.html":
            raise ValueError(f"{slug}: entry must be {slug}/index.html")
        if not isinstance(p.get("name"), str) or not p["name"].strip():
            raise ValueError(f"{slug}: name is required")
        if not isinstance(p.get("description"), str) or not p["description"].strip():
            raise ValueError(f"{slug}: description is required")
        if p.get("category") not in {"skyrim", "wow", "software"}:
            raise ValueError(f"{slug}: category must be skyrim, wow or software")
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", p.get("color", "")):
            raise ValueError(f"{slug}: color must be a six-digit hex color")
        source = p.get("source_url")
        if source is not None and not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?", source):
            raise ValueError(f"{slug}: source_url must be a GitHub repository URL or null")
    return data


def public_url(relative: str) -> str:
    if relative == "index.html":
        relative = ""
    elif relative.endswith("/index.html"):
        relative = relative[:-len("index.html")]
    return BASE_URL + quote(relative, safe="/-._~")


def page_files(root: Path):
    return sorted((root / "site").rglob("*.html"))


def sitemap_text(root: Path) -> str:
    urls = []
    for path in page_files(root):
        page = Page(path.read_text(encoding="utf-8-sig"))
        if page.redirect is not None or path.name.startswith("google"):
            continue
        urls.append(public_url(path.relative_to(root / "site").as_posix()))
    lines = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    lines.extend(f"  <url><loc>{html.escape(url)}</loc></url>" for url in sorted(urls))
    return "\n".join(lines + ["</urlset>", ""])


def project_cards(data, category=None) -> str:
    """One card component for the directory and marked homepage/hub blocks."""
    cards = []
    for p in sorted(data["projects"], key=lambda p: (p["category"], p["name"].casefold())):
        if category and p["category"] != category:
            continue
        name, description = html.escape(p["name"]), html.escape(p["description"])
        source = f' <a href="{html.escape(p["source_url"], quote=True)}">Source code</a>' if p["source_url"] else ""
        image = f'<img class="project-card-image" src="{html.escape(p["image"], quote=True)}" alt="" loading="lazy">' if p.get("image") else ""
        cards.append(f'<article class="project-card" style="--accent:{p["color"]}">{image}<p class="project-category">{p["category"].title()}</p><h2>{name}</h2><p>{description}</p><p><a href="{p["entry"]}">Open guide</a>{source}</p></article>')
    return "\n".join(cards)


def directory_text(data) -> str:
    return f'''<!DOCTYPE html>
<!-- Generated by tools/site_tools.py sync from projects.json. Edit the registry. -->
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>All Projects | Supertron</title><meta name="description" content="Documentation and available source code for Supertron's mods, tools and guides.">
<link rel="canonical" href="{BASE_URL}projects.html"><link rel="stylesheet" href="assets/css/directory.css">
<script src="assets/js/site.js" defer></script></head><body class="directory"><main>
<nav><a href="index.html">All games</a> · <a href="skyrim.html">Skyrim mods</a> · <a href="wow_class_guides/index.html">WoW guides</a></nav>
<h1>All Projects</h1><p>Documentation, tools and guides by Supertron.</p><div class="project-grid">
{project_cards(data)}
</div><footer><h2>Share this page</h2><button class="spoiler-btn" onclick="toggleSpoiler('bb')">BB Code</button> <button class="spoiler-btn" onclick="toggleSpoiler('md')">Markdown</button>
<div id="bb" class="spoiler-content"><textarea id="bbtext" readonly>[url={BASE_URL}projects.html]Supertron's Projects[/url]</textarea><button class="copy-btn" onclick="copyText('bbtext')">Copy</button></div>
<div id="md" class="spoiler-content"><textarea id="mdtext" readonly>[Supertron's Projects]({BASE_URL}projects.html)</textarea><button class="copy-btn" onclick="copyText('mdtext')">Copy</button></div></footer>
</main></body></html>
'''


def generated_files(root: Path, data):
    files = {
        root / "site/projects.html": directory_text(data),
        root / "site/sitemap.xml": sitemap_text(root),
        root / "site/robots.txt": f"User-agent: *\nAllow: /wiki/\n\nSitemap: {BASE_URL}sitemap.xml\n",
    }
    for name in ("index.html", "skyrim.html"):
        path = root / "site" / name
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        start, end = "<!-- PROJECT-CARDS:START -->", "<!-- PROJECT-CARDS:END -->"
        if start not in text and end not in text:
            continue
        if text.count(start) != 1 or text.count(end) != 1 or text.index(start) >= text.index(end):
            raise ValueError(f"{name}: requires one ordered project-card marker pair")
        before = text[:text.index(start) + len(start)]
        after = text[text.index(end):]
        files[path] = before + "\n<div class=\"project-grid\">\n" + project_cards(data, "skyrim") + "\n</div>\n" + after
    return files


def sync(root: Path):
    data = read_registry(root)
    # Create the directory first so the sitemap includes it on the first run.
    (root / "site/projects.html").write_text(directory_text(data), encoding="utf-8", newline="\n")
    for path, content in generated_files(root, data).items():
        path.write_text(content, encoding="utf-8", newline="\n")


def resolve_local(site: Path, origin: Path, ref: str):
    """Return (target, fragment, error); external/data/mail URLs return no target."""
    try:
        url = urlsplit(ref.strip())
    except ValueError:
        return None, "", "invalid URL"
    if url.scheme and url.scheme not in {"http", "https"}:
        if url.scheme in {"file", "javascript"}:
            return None, "", f"unsupported local URL scheme: {url.scheme}"
        return None, "", None
    if url.netloc and url.netloc.lower() != "supertron42.github.io":
        return None, "", None
    path = unquote(url.path)
    if url.netloc or path.startswith("/"):
        if path == "/wiki":
            path = "/wiki/"
        if not path.startswith("/wiki/"):
            return None, "", "same-site URL must include /wiki/"
        target = site / path[len("/wiki/"):]
    else:
        target = origin.parent / path if path else origin
    lexical = Path(os.path.abspath(target))
    target = target.resolve()
    if not target.is_relative_to(site.resolve()):
        return None, "", "URL escapes site/"
    # Windows accepts wrong case, but GitHub's Linux artifact must use exact names.
    parent = site.resolve()
    for part in lexical.relative_to(site.resolve()).parts:
        if not parent.is_dir():
            break
        names = {entry.name for entry in parent.iterdir()}
        if part not in names and any(name.casefold() == part.casefold() for name in names):
            return None, "", f"filename capitalization does not match: {part}"
        parent = parent / part
    if target.is_dir():
        target = target / "index.html"
    return target, unquote(url.fragment), None


def check(root: Path) -> list[str]:
    errors = []
    try:
        data = read_registry(root)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f"Registry: {exc}"]
    site = root / "site"
    projects = {p["slug"] for p in data["projects"]}
    if not site.is_dir():
        return ["Missing site/ directory"]
    workflow = root / ".github/workflows/static.yml"
    if workflow.is_file():
        text = workflow.read_text(encoding="utf-8")
        uploads = re.findall(r"uses:\s*actions/upload-pages-artifact@[^\n]+\n(.*?)(?=\n\s*- |\Z)", text, re.S)
        if not uploads or any(not re.search(r"^\s*path:\s*['\"]?site['\"]?\s*$", block, re.M) for block in uploads):
            errors.append("Pages workflow must upload only site/")
    else:
        errors.append("Missing .github/workflows/static.yml deployment boundary")
    for p in data["projects"]:
        if not (site / p["entry"]).is_file():
            errors.append(f"Registered entry is missing: {p['entry']}")
    for path in sorted(site.rglob("*")):
        rel = path.relative_to(site)
        parts = rel.parts
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            errors.append(f"Site links/junctions are forbidden: {rel.as_posix()}")
            continue
        if any(part.lower() in FORBIDDEN_PARTS or part.startswith(("_", ".")) and part != ".nojekyll" for part in parts):
            errors.append(f"Private/development path inside site/: {rel.as_posix()}")
        if len(parts) == 1 and path.is_dir() and parts[0] not in projects | RESERVED_DIRS:
            errors.append(f"Unregistered site directory: {parts[0]}")
        if path.is_file():
            if len(parts) == 1 and path.name not in ROOT_FILES:
                errors.append(f"Unexpected root site file: {path.name}")
            if path.name not in ROOT_FILES and path.suffix.lower() not in EXTENSIONS:
                errors.append(f"Unapproved published file type: {rel.as_posix()}")
            if re.search(r"(^|[-_. ])(backup|todo|draft|copy)([-_. ]|$)", path.stem, re.I):
                # backup.html is an existing public ClibDT feature guide.
                if rel.as_posix() not in {"clibdt/backup.html", "assets/css/pages/clibdt/backup.css"}:
                    errors.append(f"Backup/draft/scratch file inside site/: {rel.as_posix()}")
    # Prevent public site content or private working directories returning to root.
    for path in root.iterdir():
        if path.name in {".git", ".github", ".cursor", "site", "tools", "tests", "docs", "templates"}:
            continue
        if path.is_dir() and not path.name.startswith("."):
            errors.append(f"Unexpected repository directory: {path.name}; see docs/STRUCTURE.md")
        if path.suffix.lower() in {".html", ".zip", ".exe", ".dll", ".png", ".webp"}:
            errors.append(f"Misplaced repository-root file: {path.name}")
        elif path.is_file() and path.name not in REPO_FILES:
            errors.append(f"Unexpected repository-root file: {path.name}; put documentation in docs/")
    pages = {}
    for path in page_files(root):
        text = path.read_text(encoding="utf-8-sig")
        pages[path.resolve()] = Page(text)
    for path, page in pages.items():
        rel = path.relative_to(site.resolve()).as_posix()
        if path.name.startswith("google"):
            continue
        if page.inline_styles:
            errors.append(f"{rel}: use assets/css/ rather than a <style> block")
        if page.content_layout and page.outside_content:
            errors.append(f"{rel}: content blocks outside #content: {', '.join(page.outside_content)}")
        if not page.redirect and not page.title.strip():
            errors.append(f"{rel}: missing page title")
        expected = public_url(rel)
        if page.redirect:
            target, _, error = resolve_local(site, path, page.redirect)
            if not error and target:
                expected = public_url(target.relative_to(site.resolve()).as_posix())
        if page.canonicals != [expected]:
            errors.append(f"{rel}: expected one canonical URL: {expected}")
        for script in page.scripts:
            if re.search(r"function\s+(copyText|copyLink|toggleSpoiler)\s*\(", script):
                errors.append(f"{rel}: use shared assets/js/site.js for copy/spoiler functions")
        refs = page.refs + [match.group(1).strip() for css in page.inline_css for match in CSS_URL.finditer(css)]
        for ref in refs:
            target, fragment, error = resolve_local(site, path, ref)
            if error:
                errors.append(f"{rel}: {ref!r}: {error}")
            elif target:
                if not target.is_file():
                    errors.append(f"{rel}: missing local target {ref!r}")
                elif fragment and target in pages and not pages[target].redirect and fragment not in pages[target].ids:
                    errors.append(f"{rel}: missing anchor {ref!r}")
                # A redirect's anchors are resolved in the browser by its script.
    for path in site.rglob("*.css"):
        for match in CSS_URL.finditer(path.read_text(encoding="utf-8")):
            ref = match.group(1).strip()
            target, _, error = resolve_local(site, path, ref)
            if error or target and not target.is_file():
                errors.append(f"{path.relative_to(site).as_posix()}: invalid CSS asset {ref!r}: {error or 'missing file'}")
    for path, expected in generated_files(root, data).items():
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            errors.append(f"Generated file is stale: {path.relative_to(root).as_posix()}; run python tools/site_tools.py sync")
    return sorted(set(errors))


def new_project(root: Path, slug: str, name: str, description: str, category: str, source_url: str | None):
    data = read_registry(root)
    if not re.fullmatch(r"[a-z][a-z0-9-]*", slug) or slug in RESERVED_DIRS or any(p["slug"] == slug for p in data["projects"]):
        raise ValueError("Use a new lowercase hyphenated slug; existing slugs are reserved")
    folder = root / "site" / slug
    if folder.exists():
        raise ValueError(f"Refusing to replace existing folder: {folder}")
    project = dict(slug=slug, name=name, description=description, category=category, color="#4ec9b0", entry=f"{slug}/index.html", source_url=source_url)
    data["projects"].append(project)
    # Validate inputs before writing anything.
    if category not in {"skyrim", "wow", "software"} or not name.strip() or not description.strip():
        raise ValueError("Name, description and a supported category are required")
    if source_url and not re.fullmatch(r"https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/?", source_url):
        raise ValueError("Source URL must identify a GitHub repository")
    template = (root / "templates/project.html").read_text(encoding="utf-8")
    for key, value in {"NAME": name, "DESCRIPTION": description, "URL": public_url(project["entry"])}.items():
        template = template.replace("{{" + key + "}}", html.escape(value, quote=True))
    folder.mkdir()
    (folder / "index.html").write_text(template, encoding="utf-8", newline="\n")
    (root / "projects.json").write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
    sync(root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("check", help="Validate the deployment tree, links, registry and generated files")
    sub.add_parser("sync", help="Regenerate the public project directory, sitemap and robots file")
    new = sub.add_parser("new-project", help="Create a registered documentation page; no source repository is created")
    new.add_argument("slug")
    new.add_argument("--name", required=True)
    new.add_argument("--description", required=True)
    new.add_argument("--category", choices=["skyrim", "wow", "software"], default="software")
    new.add_argument("--source-url")
    args = parser.parse_args()
    try:
        if args.command == "new-project":
            new_project(ROOT, args.slug, args.name, args.description, args.category, args.source_url)
        elif args.command == "sync":
            sync(ROOT)
        errors = check(ROOT)
    except (OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    if errors:
        print("\n".join("ERROR: " + e for e in errors), file=sys.stderr)
        return 1
    print(f"Wiki checks passed: {len(read_registry(ROOT)['projects'])} projects, {len(page_files(ROOT))} HTML files, deployment root site/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
