# Maintaining the wiki

## Update an existing project

1. Read AGENTS.md. Find the project in projects.json and edit its pages under site/<slug>/.
2. Verify product behavior against its actual source or release. Keep existing anchors and public filenames.
3. Edit linked styles in site/assets/css/. Use site/assets/js/site.js for copy and spoiler controls.
4. If a new page needs navigation, link it from its project hub. For WoW guides, follow docs/WOW-AUTHORING.md.
5. Run the commands below and preview the affected pages at desktop and mobile widths.

```text
python tools/site_tools.py sync
python -m unittest discover -s tests
node --test tests/site.test.cjs
python tools/site_tools.py check
```

`sync` updates the generated project directory, sitemap, robots file and PROJECT-CARDS blocks on the homepage and Skyrim hub. Do not hand-edit those generated areas. All Skyrim registry entries use the same card renderer in each hub; surrounding game/hero content stays curated. Edit a factual registry description and optional existing image path rather than adding duplicate cards.

Software guides use assets/css/project-guide.css for shared navigation, heading hierarchy, spacing, tables and share controls. Preserve their accent colors, public filenames and anchors. Keep current instructions concise and source-verified; retain historical notes as an archive rather than presenting old steps as current. Preview desktop and mobile layouts.

## Add future software

Use the README's `new-project` command and supply a short factual description. New slugs use lowercase words separated by hyphens; old slugs stay unchanged. The command refuses existing folders and reserved names. It generates an entry page with navigation, canonical metadata and share buttons. Add actual documentation before publishing.

Put source in a separate repository following docs/SOURCE-REPOSITORIES.md. Update that project's source_url in projects.json when ready. Leave it null until then; do not link to a guessed repository.

## File and URL conventions

- Canonical and share links start with https://supertron42.github.io/wiki/.
- Use relative links for local navigation and assets. Match exact filename capitalization for Linux hosting.
- Keep shared images under site/assets/images/ when new; existing image paths stay stable.
- Use UTF-8 and LF for new text files; .editorconfig and .gitattributes declare this.
- Keep backups and original research outside the repository. See docs/STRUCTURE.md.
- Add new approved website file types deliberately in tools/site_tools.py with a regression check.

## Validation limits

The checker validates the local deployment tree, HTML links/anchors, CSS assets, canonical URLs, registry and generated files. It does not crawl external sites, verify gameplay claims, execute every page interaction or certify private-data absence. Preview behavior after editing HTML/JavaScript. Tests exercise structural failures and shared utility behavior.
