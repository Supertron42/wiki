# Repository structure

## Ownership

| Location | Owns |
| --- | --- |
| site/ | Public HTML, CSS, JavaScript and web assets only |
| site/<registered-slug>/ | One project's documentation and existing local assets |
| site/assets/ | Shared or page-specific stylesheet/script assets |
| site/imagedump/ | Existing image URLs retained for compatibility; place new shared images in assets/images/ |
| projects.json | Project names, stable slugs, descriptions, category colors and optional source URLs |
| tools/ | Standard-library maintenance scripts |
| tests/ | Structural and shared-JavaScript regression tests |
| templates/ | New documentation and source-repository starters |
| docs/ | Maintenance guidance, migration notes and authoring rules |
| .github/ | Validation/deployment workflow and Copilot entry instructions |
| AGENTS.md | Shared instructions for humans and automation |

Only site/ is uploaded by the Pages workflow. All committed repository files can be public on GitHub, including tools, docs and instruction files. File placement is not a confidentiality control.

## Local material outside the checkout

The cleanup uses this sibling layout:

```text
Wiki/
  wiki/                    # The Git checkout
  private/wiki/            # Local tools, addon development, research and paid products
    _apps/
    _wow/
    wowguides/
    restedxpguides/
    onepage website/
    wow_class_guides/
      resources/
      tools/
      _backup_navreorder/
  backups/                 # Verified pre-migration archive and file manifests
```

Paths are local organization choices, not Git submodules or repository dependencies. No private directory is needed to build or validate the documentation site. Research tools may require their original working paths or configuration to be updated before reuse. Do not recreate private folders in the checkout to satisfy an old hard-coded path.

Set WIKI_PRIVATE_DIR to the private/wiki directory and WOW_ADDONS_DIR to the local WoW AddOns directory when using local authoring tools. Never commit machine-specific path values. Local research and original instruction files remain preserved outside the checkout.

## Stable public addresses

The deployment artifact root is site/, so site/collectionsmanager/index.html is served at /wiki/collectionsmanager/. The local site/ name is not part of the public URL. Preserve the repository name, old project slugs, legacy wiki.html redirects and existing anchor IDs. A deliberate URL change requires a redirect and a check of incoming links.

## Generated files

projects.json -> tools/site_tools.py sync -> site/projects.html, marked project-card blocks on site/index.html and site/skyrim.html, site/sitemap.xml and site/robots.txt.

The sitemap is derived from actual HTML pages and excludes redirect stubs and the Search Console verification file. It does not invent modification dates. The generated directory links to all registered projects. The homepage and Skyrim hub use the same registry card component inside PROJECT-CARDS marker pairs; their game chooser, canvas game and other surrounding content remain hand-authored. New project images use the optional registry image path and existing site assets.

Current software guides share site/assets/css/project-guide.css and site/assets/js/site.js. Preserve registered colors with the --accent property; keep page content, headings and legacy anchor aliases inside #content. Historical patch-note anchors remain in their retained archive. Do not copy stylesheet rules into individual pages.

The Collections Manager and ClibDT overview pages add their own scoped stylesheets in site/assets/css/pages/ for their product layouts. Their detailed guides continue to use the shared guide layout. ClibDT's technical.html documents the source-verified behavior and provenance of its offscreen interface images; retain the distinction between development builds, workspace examples and published releases when updating them.

## Preventing drift

The checker rejects unregistered project directories, misplaced root content, private/development paths in site/, unapproved file types, embedded style blocks, duplicate shared utility functions, content appended outside #content, incorrect canonical URLs, broken local links/anchors and stale generated files. The workflow runs checks before uploading site/.

Programs that do not read instruction files still receive the same command-line failures when validation runs. No instruction file can force every external program to comply; use the validation command in any additional editor, publishing tool or automation.

## Existing local writers

The shared project instructions and existing mod project wiki instructions are updated to use site/<slug>/ and the central registry/check command. This also covers the shared template used for future projects. Their original files are backed up with the migration evidence.

GuidePanel is retained under private/wiki/_apps/GuidePanel/. Its public guide root points into site/wow_class_guides/, while research, helper scripts and paid release files stay in the private sibling tree. Its preset variables resolve both locations, and guide-editing prompts reference the current wiki rules. The full GUI and external Claude sessions are not launched as part of the migration; path resolution is checked without sending prompts.
