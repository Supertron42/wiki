"""Regression checks for failure modes that could republish clutter or break URLs."""
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("site_tools", REPO / "tools/site_tools.py")
tools = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tools)


class StructureTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / "site/example").mkdir(parents=True)
        (self.root / "templates").mkdir()
        (self.root / ".github/workflows").mkdir(parents=True)
        shutil.copyfile(REPO / ".github/workflows/static.yml", self.root / ".github/workflows/static.yml")
        shutil.copyfile(REPO / "templates/project.html", self.root / "templates/project.html")
        (self.root / "projects.json").write_text(json.dumps({"schema_version": 1, "base_url": tools.BASE_URL, "projects": [dict(slug="example", name="Example", description="Example documentation", category="software", color="#4ec9b0", entry="example/index.html", source_url=None)]}), encoding="utf-8")
        registry = json.loads((self.root / "projects.json").read_text())
        registry["projects"].append(dict(slug="wow_class_guides", name="WoW Guides", description="Guide hub", category="wow", color="#C79C6E", entry="wow_class_guides/index.html", source_url=None))
        (self.root / "projects.json").write_text(json.dumps(registry), encoding="utf-8")
        self.write_page("index.html", "<a href='example/index.html#intro'>Example</a>")
        self.write_page("example/index.html", "<h1 id='intro'>Example</h1>")
        self.write_page("skyrim.html")
        self.write_page("wow_class_guides/index.html")
        (self.root / "site/assets/css").mkdir(parents=True)
        (self.root / "site/assets/js").mkdir(parents=True)
        for name in ("assets/css/directory.css", "assets/css/project-guide.css", "assets/js/site.js"):
            shutil.copyfile(REPO / "site" / name, self.root / "site" / name)
        tools.sync(self.root)

    def write_page(self, relative, body=""):
        file = self.root / "site" / relative
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(f'<!doctype html><html><head><title>Example</title><link rel="canonical" href="{tools.public_url(relative)}"></head><body>{body}</body></html>', encoding="utf-8")

    def assert_error(self, contains):
        errors = tools.check(self.root)
        self.assertTrue(any(contains in error for error in errors), errors)

    def test_clean_tree_and_sync_are_repeatable(self):
        self.assertEqual(tools.check(self.root), [])
        before = (self.root / "site/sitemap.xml").read_bytes()
        tools.sync(self.root)
        self.assertEqual(before, (self.root / "site/sitemap.xml").read_bytes())

    def test_backup_page_is_rejected_even_if_locally_ignored(self):
        self.write_page("example/_backup/index.html")
        self.assert_error("Private/development path")

    def test_deployment_cannot_expand_back_to_repository_root(self):
        path = self.root / ".github/workflows/static.yml"
        path.write_text(path.read_text().replace("path: site", "path: '.'"), encoding="utf-8")
        self.assert_error("must upload only site/")

    def test_source_and_archives_cannot_enter_deployment(self):
        for name in ("source.py", "payload.zip", "review.json", "AGENTS.md"):
            with self.subTest(name=name):
                path = self.root / "site/example" / name
                path.write_text("private", encoding="utf-8")
                self.assert_error("Unapproved published file type")
                path.unlink()

    def test_unregistered_project_and_root_page_are_rejected(self):
        self.write_page("unregistered/index.html")
        self.assert_error("Unregistered site directory")
        (self.root / "oops.html").write_text("misplaced", encoding="utf-8")
        self.assert_error("Misplaced repository-root file")

    def test_canonical_without_wiki_is_rejected(self):
        path = self.root / "site/example/index.html"
        path.write_text(path.read_text().replace("github.io/wiki/", "github.io/"), encoding="utf-8")
        self.assert_error("expected one canonical URL")

    def test_missing_file_and_anchor_are_detected(self):
        self.write_page("example/index.html", "<a href='missing.html'>Missing</a><a href='../index.html#no-such-anchor'>Anchor</a>")
        self.assert_error("missing local target")
        self.assert_error("missing anchor")

    def test_css_assets_are_checked(self):
        (self.root / "site/assets/css/broken.css").write_text("body{background:url('../images/missing.png')}", encoding="utf-8")
        self.assert_error("invalid CSS asset")

    def test_urls_cannot_escape_site_or_omit_base(self):
        self.write_page("example/index.html", "<a href='../../projects.json'>Escape</a><a href='/example/'>Bad base</a>")
        self.assert_error("URL escapes site/")
        self.assert_error("same-site URL must include /wiki/")

    def test_filename_case_matches_linux(self):
        self.write_page("example/index.html", "<a href='../INDEX.html'>Wrong case</a>")
        self.assert_error("capitalization")

    def test_generated_outputs_must_be_current(self):
        data = tools.read_registry(self.root)
        data["projects"][0]["description"] = "Updated description"
        (self.root / "projects.json").write_text(json.dumps(data), encoding="utf-8")
        self.assert_error("Generated file is stale")

    def test_duplicate_slug_is_rejected(self):
        data = tools.read_registry(self.root)
        data["projects"].append(data["projects"][0])
        (self.root / "projects.json").write_text(json.dumps(data), encoding="utf-8")
        self.assert_error("duplicate")

    def test_redirect_routes_survive_and_are_not_in_sitemap(self):
        file = self.root / "site/example/wiki.html"
        file.write_text(f'<meta http-equiv="refresh" content="0; url=./"><link rel="canonical" href="{tools.BASE_URL}example/">', encoding="utf-8")
        tools.sync(self.root)
        self.assertNotIn("wiki.html", (self.root / "site/sitemap.xml").read_text())
        self.assertEqual(tools.check(self.root), [])

    def test_inline_shared_code_and_styles_are_rejected(self):
        self.write_page("example/index.html", "<style>body{color:red}</style><script>function copyText(id){}</script>")
        self.assert_error("<style>")
        self.assert_error("shared assets/js/site.js")

    def test_appended_content_cannot_escape_main_container(self):
        self.write_page("example/index.html", "<main id='content'><h1 id='intro'>Example</h1></main><section><h2>Misplaced update</h2></section>")
        self.assert_error("content blocks outside #content")

    def test_comment_tag_examples_do_not_become_real_links(self):
        self.write_page("example/index.html", "<h1 id='intro'>Example</h1><!-- <a href='missing.html'>example</a> -->")
        self.assertEqual(tools.check(self.root), [])

    def test_new_project_registers_and_syncs_without_overwriting(self):
        tools.new_project(self.root, "future-tool", "Future & Tool", "A future program.", "software", None)
        self.assertIn("Future &amp; Tool", (self.root / "site/future-tool/index.html").read_text())
        self.assertEqual(tools.check(self.root), [])
        with self.assertRaises(ValueError):
            tools.new_project(self.root, "future-tool", "Again", "No replacement", "software", None)
        with self.assertRaises(ValueError):
            tools.new_project(self.root, "../escape", "Bad", "Bad slug", "software", None)


if __name__ == "__main__":
    unittest.main()
