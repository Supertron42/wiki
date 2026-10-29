# October 23, 2026 repository restructure

## BEFORE (Current Behavior)

The original .github/workflows/static.yml:40 uploaded the repository root. The original .gitignore:30 hid all Python files. Public pages, private tools and research shared a checkout; tracked backup HTML was inside the publishing tree. Public canonical and sitemap URLs frequently omitted /wiki/.

## AFTER (Expected Behavior)

Publish only site/. Keep registered project documentation, stable routes and redirect stubs. Store local private material and verified backups outside the checkout. Keep shared rules, templates and validation commands available to future tools.

## TIER IMPACT

Website maintenance and deployment only. The Collections Manager runtime tiers and other application source are unchanged.

## FILES TO CHANGE

| Original location | Change |
| --- | --- |
| .github/workflows/static.yml:40 | Validate first; upload site/ only |
| .gitignore:30 | Track maintenance scripts; ignore specific generated/editor artifacts |
| Public project folders, index.html, skyrim.html | Move into site/ with original relative routes |
| sitemap.xml, robots.txt | Generate from the actual site and correct /wiki/ base |
| AGENTS.md:1 and CLAUDE.md:1 | Provide shared sustainable structure rules and portable entry instructions |
| wow_class_guides/CLAUDE.md:1 | Preserve detailed authoring guidance in docs/WOW-AUTHORING.md with updated paths |
| Private/research/tooling/backup paths | Preserve outside checkout with original relative layout |

## WIRING UPDATES NEEDED

- Workflow -> tools/site_tools.py check -> site/ deployment.
- projects.json -> project directory and sitemap generation.
- HTML -> linked stylesheets and shared copy/spoiler utilities.
- Appended page sections -> the existing #content container, preserving wording and order.
- Tool-specific entry files -> AGENTS.md -> docs/STRUCTURE.md.
- Existing local project instructions and the shared future-project template -> site/<slug>/ and the registry/check commands.
- Private GuidePanel -> public guide directory plus separate private research/tools/release directory.

## TESTING PLAN

Validate a temporary copy before applying. Snapshot and hash-verify the full original checkout, including ignored files and .git. Preserve page text and all prior public HTML routes except documented backup/scratch pages. Run structural regression tests, shared utility tests and actual-site validation. Inspect representative desktop/mobile pages. Compare original files against their public/private destinations and preserve the Git index/HEAD.

## AI DIRECTORY UPDATES

Maintenance scripts and shared JavaScript identify their registry, workflow and page wiring in file headers. The root shared instructions and tool entry points describe the new layout. The existing WoW reference manifest remains with its guide and points to the linked styles.

The user approved the proposed layout and requested sustainable rules before implementation. No Git commit, push or live deployment is part of this local migration.
