# WoW guide authoring and verification

Read AGENTS.md and docs/STRUCTURE.md first. Public guides now live under site/wow_class_guides/.
All paths below for guide pages are relative to that directory unless explicitly qualified.
Original detailed rules are preserved below. Their local research/tools directories were moved to
the sibling private/wiki/wow_class_guides/ tree; use WIKI_PRIVATE_DIR and WOW_ADDONS_DIR for local paths.
Never save downloaded research or addon source in site/. The site builds without these private inputs.
CSS formerly embedded in the reference page is now linked under site/assets/css/; follow the link
before changing it. Shared copy/spoiler functions live in site/assets/js/site.js; do not copy them back.
Generate the sitemap with python tools/site_tools.py sync rather than adding XML entries manually.
Keep research copies outside the checkout even where the historical instructions below say resources/.

# WoW Classic TBC Class Guides

## Reference Template & Required Page Features
**`warrior/prot/classguide-warrior-prot.html` is the canonical reference template.** When building or updating any guide, open it first and copy its structure, CSS, and scripts verbatim, change only the data and the accent color. The top of that file contains an `AI-MANIFEST` HTML comment (invisible to users, greppable) that indexes every feature with a GREP anchor. Grep for `AI-MANIFEST` to read it, then grep the listed anchors to find each feature's code.

**Every guide MUST include all of these features** (this list is the build checklist):

| # | Feature | Grep anchor | Notes |
|---|---|---|---|
| 1 | Wowhead tooltips | `whTooltips` | `<head>` script + `tooltips.js` |
| 2 | Fixed left nav | `id="nav"` | 200px, `position:fixed` |
| 3 | Collapsible nav sections | `nav-section` | h3 click toggles `.open`. Nested links (e.g. per-slot under a raid phase) use `class="nav-sub"` (deeper indent, dimmer/smaller text, vertical guide line), never inline `padding-left`. **Per-phase sub-collapse (required):** the nav-collapse IIFE auto-wraps each run of `nav-sub` links under its parent link into a `.nav-subsection`; only the phase/section currently in view shows its slot list (scrollspy opens the active sub-group, collapses the rest) so phases never blend into one long list. CSS: `#nav .nav-subsection{display:none}` / `.open{display:block}`. |
| 4 | **Scrollspy nav highlight** | `Scrollspy` | Highlights the section in view, expands it, collapses others, scrolls active link into view. CSS: `#nav h3.active-section` + `a.active`. JS: the `Scrollspy:` IIFE near `</body>`. |
| 5 | Mobile nav hamburger | `nav-toggle` | `.nav-backdrop`, `toggleNav()` |
| 6 | Source filter bar | `filter-bar` | buttons call `filterGear()`; rows need `data-source` |
| 7 | Gear tables | `gear-table` | cols: Rank / Item / Source / Notes. **Shrink-to-fit** (`table-layout`/`width: auto`), `td:last-child` capped at `max-width: 360px` so long notes wrap. Do NOT add a JS column-width sync, it was removed for bloating cells. |
| 8 | Horizontal table-wrap | `table-wrap` | JS auto-wraps every table; `overflow-x: visible` on desktop (lets sticky headers pin to the page), `auto` on phones for horizontal scroll |
| 9 | Sticky table headers | `Sticky headers` | `thead th { position: sticky; top: 0 }` on desktop; reverts to `static` on phones |
| 10 | Source type icons | `boss-icon` | see icon table in main CLAUDE.md |
| 11 | Heroic span | `class="heroic"` | never `(H)` |
| 12 | Info / Tip / Warn boxes | `info-box` / `tip-box` / `warn-box` | |
| 13 | Gem/enchant per-slot blocks | `gem-enchant-info` | + `socket-red/yellow/blue/meta` |
| 14 | Copy-link buttons | `spoiler-btn` | BB Code + Markdown, `copyText()` |
| 15 | "My Other Projects" footer button | `My Other Projects` | absolute-positioned in nav |
| 16 | **Per-slot phase layout** | `id="phase1-` | EVERY raid phase, once its data exists, is broken out per gear slot exactly like Phase 1/Phase 2: intro `<p>` (+ `tip-box` for set bonuses), then per slot an `<h2 id="phaseN-<slot>">` + a `<p class="gem-enchant-info">` line + a ranked `gear-table` (BiS / Alt BiS / Good rows, `data-source`). Nav gets matching `nav-sub` sub-links per slot. A phase with no data yet keeps the single "Awaiting data" placeholder table until filled. **Do NOT leave a filled phase as a flat one-table list.** |
| 17 | **Hub back-link** | `All Guides` | An ALWAYS-VISIBLE single link at the very top of `#nav` (before the first `<h3>`, so the collapse/scrollspy JS never hides it): `<a href="../../index.html">&#8592; All Guides</a>` and NOTHING else. The old per-guide switcher list (every class/spec linked in every guide, `nav-grouplabel` label) was **removed by user request**, do NOT re-add it; cross-guide navigation goes through the hub. **When a new guide ships, do BOTH of: (a) add/activate a card on the hub (`site/wow_class_guides/index.html`), and (b) add a `<url>` entry to the generated `site/sitemap.xml`** (run `python tools/site_tools.py sync`; loc `https://supertron42.github.io/wiki/wow_class_guides/<class>/<spec>/classguide-<class>-<spec>.html`, `changefreq monthly`, `priority 0.8`). |
| 19 | **Talents: build grid + leveling order** | `talent-trees` | The Talents section (`<h1 id="talents">`) has, after the build summary + key-talents box: (a) an `<h2 id="talent-build">` with a Wowhead-style CSS **talent-tree grid** (`.talent-trees` > `.talent-tree` > `.talent-grid` of `.talent-cell` placed by inline `grid-row`/`grid-column`; spent talents `.on`, maxed `.max`, rank badge `.talent-rank`), and (b) an `<h2 id="talent-leveling">` **Leveling Order (1-70)** table (Order / Talent / Points / Tree, main tree first). Nav gets `talent-build` + `talent-leveling` sub-links. **Data source = wowtbc.gg class-guide `page-data.json` `bisTalentOne`** (exact ranks/totals; correct wowtbc's mislabeled warrior trees: Death Wish->Fury, Sweeping Strikes->Arms, Endless Rage->Fury, Tactical Mastery->Arms; verify per-tree totals). CSS GREP: `.talent-trees` (shared teal `#4ec9b0`, class-agnostic). Tank guides get this too. |
| 18 | **Export to AtlasLoot** | `export-atlasloot` | Two entry points: (a) a per-table **Export to AtlasLoot** button (`.al-table-btn`) injected above EVERY gear table, and (b) an `<h1 id="export-atlasloot">` Resources section (before "Link to This Page") + nav link. The scan IIFE walks `table.gear-table` under the `#pre-raid-bis`/`#phaseN` `<h1>`s (gems/enchants/consumables/quests under other `<h1>`s are skipped), groups rows by phase, and injects each button between a slot's `<h2>` and its table. `alStringFromRows()` is the shared builder of AtlasLoot's **native** favourite-import string `i:<id>:<note>,i:<id>,...` (Favourites `IMPORT_PATTERN`); the note is the rank cell, so a "BiS" note makes AtlasLoot auto-flag the slot's main item. The per-table button opens a modal (`alOpenTableModal`, `.al-modal-*`) asking **this slot only** vs **entire `<phase>`**, auto-copies, and points to Resources for the whole guide. The Resources `buildAtlasLootExport()` has a "Choose Phases" checkbox spoiler (empty phases auto-dropped), a "BiS rows only" toggle, a readonly `#atlasloot-export` textarea + Copy button. **In-game side = the `AtlasLootWishlist` addon (v1.3+)**: `/alimport` (or the Wishlist tab's Import button) opens a paste box that creates a named profile list via `fav:ImportItemList`. CSS GREP: `.al-table-btn` / `.al-modal` / `.al-opt`. All `al-*` styling uses shared teal `#4ec9b0` (class-agnostic, identical across guides). |

**When you add a new feature to one guide, you MUST:** (a) add it to the reference template's `AI-MANIFEST`, (b) add a row to this table, and (c) back-port it to every other existing guide so all guides stay in sync.

**Standard content sections (every guide should have ALL of these, in this order):** Overview, Talents (build grid + leveling order, see feature 19), Rotation, Quest Strategy, Reputation, Pre-Raid BiS, Badge Priority, Raid Phases (1-5), Gems, Enchants, Consumables, Raid Buffs & Debuffs, Useful Links, Link to This Page.

This order follows the player's journey: build the character (talents, then the rotation those talents enable), gear a fresh 70 (quest rewards and rep feed the pre-raid set, so they come first), then raid progression, then optimization. **The nav order is not cosmetic:** the Scrollspy IIFE pairs nav links to targets in nav DOM order and `break`s at the first target below the reading line, so **the nav link order MUST match `<h1>`/`<h2>` document order exactly** or the highlight desyncs. Reordering the nav always means reordering the matching content blocks too. PvP guides use the same principle with their own spine (Overview, Talents, Rotation, Macros, Starter Gear, Seasons 1-4, Gems, Enchants, Arena Comps, Races, Consumables, Resources). (The Talents section is now required for ALL specs including tanks, not just DPS.) Match the prot guide's structure for each; a new guide is not "complete" until every one of these exists (Phases 3-5 may stay "Awaiting data" placeholders).

- **Overview** (`<h1 id="overview">`): value-forward. A one-line lead that sells the guide (consensus-ranked + stat-verified + hover tooltips), then the spec's identity in a sentence, then the **"caps first" framing**: a `tip-box` for the cap(s) to hit before anything else and an `info-box` with the stat priority. Caps differ by class, e.g. tank = 490 Defense; melee DPS = hit/expertise caps; **caster = spell hit cap (~76 hit with talents / 202 hard cap vs raid bosses, then spell crit/haste/spellpower)**.
- **Rotation** (`<h1 id="rotation">`, right after Overview): `<h2>` sub-sections + matching `nav-sub` links. Sub-sections vary by class: tank = priority/pull/aoe/cooldowns/rage/buffs; melee DPS = priority/aoe/cooldowns/rage/buffs; **caster = priority/aoe/cooldowns/mana/buffs (no rage/pull)**. Abilities use spell tooltips (`https://www.wowhead.com/tbc/spell=<id>`); pull the ability priority + spell IDs from the spec's rotation guides (Icy Veins rotation pages embed spell IDs in `data-wowhead` attrs; cross-ref Warcraft Tavern).
- **Badge Priority / Raid Buffs / Quest Strategy** follow the prot section shapes (a priority table; class-buffs + boss-debuffs + ideal-party; a "fresh 70 gearing" table). Adapt content to the class (a caster's ideal party wants spellpower/spell-crit/spell-haste buffs and the spell-hit-reducing boss debuffs, not the melee set).

**Scrollspy is mandatory.** Users must always be able to tell which section they are reading from the left nav. The active section header turns teal (`active-section`) and auto-expands; the active sub-link gets the `.active` left-border.

## File Structure & Naming
Each class/spec guide lives in its own folder, with raw source HTML kept outside the repository in `WIKI_PRIVATE_DIR/wow_class_guides/resources/`.

**Naming convention:** `classguide-<class>-<spec>.html` (all lowercase, hyphenated).

**Output guide HTML** (the published wiki pages):
- `warrior/fury/classguide-warrior-fury.html`
- `warrior/prot/classguide-warrior-prot.html`
- Future: `warrior/arms/`, `paladin/prot/`, `paladin/holy/`, `paladin/ret/`, `druid/feral/`, `druid/balance/`, `druid/resto/`, `shaman/enh/`, `shaman/ele/`, `shaman/resto/`, `priest/holy/`, `priest/disc/`, `priest/shadow/`, `mage/`, `warlock/`, `rogue/`, `hunter/bm/`, `hunter/mm/`, `hunter/surv/`, same `classguide-<class>-<spec>.html` pattern.

**Resource folders** (raw saved web pages, Wowhead, Icy Veins, Warcraft Tavern, wowtbc.gg, etc.):
- `WIKI_PRIVATE_DIR/wow_class_guides/resources/warrior/fury/`, Fury Warrior source materials
- `WIKI_PRIVATE_DIR/wow_class_guides/resources/warrior/prot/`, Protection Warrior source materials (Wowhead P1 + P2, Warcraft Tavern P1, Icy Veins raid + pre-raid, wowtbc.gg page + JSON). See its `SOURCES.md`.
- Add a sibling folder under `WIKI_PRIVATE_DIR/wow_class_guides/resources/<class>/<spec>/` whenever starting a new guide. **Update this list when you add resources for a new class/spec.**

### RULE: Save every source you fetch (REQUIRED)
**Any time you pull a page/data to build or update a guide, save the raw copy into that spec's `WIKI_PRIVATE_DIR/wow_class_guides/resources/<class>/<spec>/` folder**, do not leave it in a temp dir. This keeps every claim in the guide traceable and re-checkable offline.
- Most guide sites are JS-rendered and block plain WebFetch, so fetch with curl + a browser UA and write the response to the folder (see the curl recipes under "Sources Integrated So Far"). Save the structured payload when there is one (e.g. wowtbc.gg's `page-data.json`), not just the SPA shell.
- **Naming:** `<Page Title> - <Source>.html` (or `.json`), e.g. `Protection Warrior Tank Phase 1 Best in Slot (BiS) - TBC Classic - Warcraft Tavern.html`. One file per source per phase/page.
- **Maintain a `SOURCES.md`** in each spec folder: one line per file mapping `filename → URL → what it covers → date fetched`. Update it whenever you add a source.
- Tertiary sources you only spot-checked (and did not use for rankings) do not need saving; anything that informed the tables does.

**Canonical URL format** (for `<link rel="canonical">` and copy-link buttons):
`https://supertron42.github.io/wiki/wow_class_guides/<class>/<spec>/classguide-<class>-<spec>.html`

**Cross-spec navigation:** Use relative paths between sibling specs, e.g. from prot to fury: `../fury/classguide-warrior-fury.html`.

## Workflow (build/update in PASSES, do not write a row end-to-end from memory)
Build and edit guides in discrete passes. The point is to **separate generating content from verifying it**, and to **batch same-type work** so each ground-truth tool runs once per section instead of per item. Most past errors came from writing a row's rankings + source + notes in one breath, half of it from memory. Do not do that. Run the passes in order; for a big guide do them per-section so the file is never broken for long.

**Pass 0 - Gather sources (REQUIRED, do this first, do NOT wait for the user to hand you HTML):**
When asked to build or refresh a guide, go research and download the sources yourself before anything else. Do not build from memory and do not assume `WIKI_PRIVATE_DIR/wow_class_guides/resources/` is already complete.
- Identify the spec's authoritative pages (the set that has served well: **Wowhead** BiS + pre-raid + phase guides, **wowtbc.gg** BiS list (Gatsby `page-data.json`), **Icy Veins** gear + rotation + talents, **Warcraft Tavern** per-phase BiS). Use WebSearch to find current URLs if you do not know them; spec/phase guide URLs change.
- **Download each with curl + a browser UA** (plain WebFetch returns only the SPA shell on these sites, see the curl recipes under "Sources Integrated So Far"). Save the raw response, and the structured payload when there is one (wowtbc.gg `page-data.json`), into `WIKI_PRIVATE_DIR/wow_class_guides/resources/<class>/<spec>/`. Naming + `SOURCES.md` per the "Save every source you fetch" RULE below.
- **Minimum bar before Pass 1:** pre-raid BiS, every currently-live raid phase, gems, enchants, consumables, and (for non-tank specs) talents + rotation, each backed by at least one saved source. For a DPS guide pull a rotation/talents source explicitly. If a fetch is blocked (CloudFront 403, etc.), note it in `SOURCES.md` and find an alternate source; never silently skip a section.
- WebFetch/WebSearch are allowed and expected here. Use Questie / AtlasLoot (authoritative game DBs) for item/NPC IDs, coords, and drop sources; the BIS-TBC / TBCA ranking addons are a **last-resort fallback only** (see "TBC BIS Anniversary Addons" below), never a replacement for pulling the written guides (the guides carry the rankings + reasoning the addons do not, and have proven more reliable).

**Pass 1 - Extract & rank** (from the saved `WIKI_PRIVATE_DIR/wow_class_guides/resources/<class>/<spec>/` sources ONLY, never memory):
- Parse the saved HTML/JSON, pull the useful gear/talent/consumable data, and decide which section each piece belongs to (Pre-Raid BiS, each Phase, Gems, Enchants, Talents, Consumables, ...).
- Sort/rank by slot using the source's ordering (first listed = best). When sources conflict, keep both and note the discrepancy. Cross-reference against what's already in the guide before adding.
- Output of this pass is item IDs + ranking + which slot/phase. Leave Source and Notes rough.

**Pass 2 - Sources** (ground truth = `WIKI_PRIVATE_DIR/wow_class_guides/tools/al_item_source.py`, see the Source-column RULE):
- Run it on every item ID in the section, then fill each Source cell + icon + `data-source` from its output. Nothing from memory. Tier pieces: name the token-drop boss (token table in the Source section).

**Pass 3 - Notes** (ground truth = `WIKI_PRIVATE_DIR/wow_class_guides/tools/wh_item_stats.py`, see the Notes RULE):
- Run it on every item ID to VERIFY the item, then write each note as **judgment, not a stat list** (why-this-rank / trade-off / when-to-swap / how-to-get). Never dump the stats the tooltip already shows, and never claim a stat from memory. See "RULE: Notes are JUDGMENT, NOT a stat list".

**Pass 4 - Structure & features:**
- Work the `AI-MANIFEST` checklist in `warrior/prot/classguide-warrior-prot.html` (grep it): per-slot phase layout, nav + scrollspy + class switcher, AtlasLoot export, copy-link buttons, tooltips on every item/boss/zone/quest. New guide is not "complete" until every Standard Content Section exists.

**Pass 5 - Automated audit gate** (`WIKI_PRIVATE_DIR/wow_class_guides/tools/audit_guide.py`, run before declaring done / before any commit):
```
python tools/audit_guide.py                  # all guides
python tools/audit_guide.py <path/to/guide>  # one guide; exit code != 0 if any hard error
```
It checks: Source cells vs AtlasLoot loot tables, icon/`data-source`/cell agreement, em-dash, `<td>` balance, and Wowhead-link coverage. **Hard ERRORs must be zero before finishing.** WARNs are for a human to confirm (legit tier tokens, plain-text bosses, classic carryovers); read each and either fix it or confirm it is intentional. This is a script gate, not a re-read, it is the highest-value pass and catches what self-review misses.

## Wowhead Tooltips (Required on ALL items, bosses, quests, zones)
- Every item MUST be a Wowhead link: `<a href="https://www.wowhead.com/tbc/item=XXXXX" data-wh-icon-size="small">Item Name</a>`
- Every boss MUST be a Wowhead NPC link: `<a href="https://www.wowhead.com/tbc/npc=XXXXX">Boss Name</a>`
- Every dungeon/raid MUST be a Wowhead zone link: `<a href="https://www.wowhead.com/tbc/zone=XXXXX">Zone Name</a>`
- Every quest MUST be a Wowhead quest link: `<a href="https://www.wowhead.com/tbc/quest=XXXXX">Quest Name</a>`
- Enchants use spell links: `<a href="https://www.wowhead.com/tbc/spell=XXXXX">Enchant Name</a>` or item links for leg armor/scopes.
- The tooltip script is loaded in `<head>`: `const whTooltips = {colorLinks: true, iconizeLinks: true, iconSize: 'small'};`

## Source Column Format
Sources MUST follow this format: **Region - Heroic (if applicable) - Dungeon/Raid - Boss (drop%)**

Examples:
- `Deadwind Pass - Karazhan - Prince Malchezaar (33%)`
- `Caverns of Time - <span class="heroic">Heroic</span> - Old Hillsbrad - Epoch Hunter (16%)`
- `Hellfire Peninsula - World Boss - Doom Lord Kazzak (19%)`
- `Shadowmoon Valley - World Boss - Doomwalker (19%)`

Region mapping for TBC dungeons/raids:
- **Hellfire Peninsula**: Blood Furnace, Shattered Halls, Ramparts, Magtheridon's Lair
- **Zangarmarsh**: Slave Pens, Underbog, Steamvault, **Serpentshrine Cavern (SSC)** (all Coilfang)
- **Terokkar Forest**: Auchenai Crypts, Sethekk Halls, Shadow Labyrinth, Mana-Tombs
- **Netherstorm**: Mechanar, Botanica, Arcatraz, **Tempest Keep / The Eye (TK)**
- **Caverns of Time**: Old Hillsbrad, Black Morass
- **Deadwind Pass**: Karazhan
- **Blade's Edge Mtns**: Gruul's Lair
- **Ghostlands / Eversong**: Zul'Aman (ZA)
- **Isle of Quel'Danas**: Sunwell Plateau (SWP), Magisters' Terrace
- **Shadowmoon Valley**: Black Temple

The two that bite most often: **SSC is in Zangarmarsh** (not its own region) and **Tempest Keep is in Netherstorm**. Most Phase 2 source errors were SSC/TK bosses swapped with each other or with Karazhan.

Non-dungeon sources:
- Quests: `Zone Name - Quest: Quest Name`
- Crafted: `Crafted - Profession (BoE/BoP)`
- Badge vendor: `Shattrath - XX Badge of Justice`
- Reputation: `Faction - Exalted/Revered`
- PvP: `PvP - Arena Season X` or `PvP - Honor`
- World Drop: `World Drop - BoE`

### RULE: Source column must be VERIFIED against the loot tables (REQUIRED)
The Source column (which boss / zone / faction an item comes from) was the single biggest source of errors, a whole guide had ~37 wrong attributions because bosses were written from memory. **Never write a Source cell from memory.** Verify every item against the local AtlasLootClassic loot tables, the same way Notes are verified against `wh_item_stats.py`.

**Source-of-truth = `WIKI_PRIVATE_DIR/wow_class_guides/tools/al_item_source.py`** (reverse-maps itemID -> boss/zone from `AtlasLootClassic_DungeonsAndRaids/data-tbc.lua` + Factions; read-only, ships with the live game, no network):
```
python tools/al_item_source.py 28825 28439 30115 ...   # prints id -> "Zone / Boss" or "REP: Faction" or "<not in loot tables>"
```
Workflow: extract a section's item IDs -> run the tool -> set each Source cell from its output -> the icon/`data-source` must match the source type (a 🐉/💀 boss cell must name a real boss the tool returns; a `<not in loot tables>` item is crafted/quest/world-drop/PvP/tier-token, NOT a boss drop).

Gotchas that caused the errors (check these explicitly):
- **`data-source` attr, icon, and cell text must agree.** A Karazhan item is `data-source="raid"` + 🐉; a heroic dungeon item is `data-source="heroic"` + 💀; a world-drop BoE is `data-source="drop"` + 🌍, never a boss. (Blinkstrike, Dragonstrike, Dragonmaw were all wrongly listed as raid boss drops, they are world-drop / crafted.)
- **Crafted gear is not a drop.** If the tool says `<not in loot tables>` and the item is a profession recipe (e.g. Dragonstrike/Dragonmaw = Blacksmithing), use 🔨 `Crafted - <Profession>`.
- **Rep rewards are not drops.** The tool prints `REP: <Faction> - <Level>`; use that exact rep LEVEL (Honored/Revered/Exalted). Violet Badge was listed Exalted but is Honored.
- **Raid trash is not a boss.** SSC/TK trinkets like Spyglass of the Hidden Fleet drop off trash; write `<Region> - <Raid> - Trash drop`, not a boss or a quest.

### Tier set tokens (T4/T5) -> boss (verify, these were ALL wrong once)
A tier-set REDEEMED piece (Warbringer/Destroyer/Tirisfal/Aldor/...) is **not** in the loot tables; the **token** drops and is turned in at Shattrath. Name the boss the TOKEN drops from. Token class groups: **Defender** = Warrior/Priest/Druid, **Champion** = Paladin/Rogue/Shaman, **Hero** = Hunter/Mage/Warlock (confirm via the token's Wowhead tooltip "Classes:" line).

| Slot | T4 token boss (Kara/Gruul/Mag) | T5 token boss (SSC/TK) |
|---|---|---|
| Head | Prince Malchezaar (Karazhan) | Lady Vashj (SSC) |
| Shoulders | High King Maulgar (Gruul's Lair) | Void Reaver (Tempest Keep) |
| Chest | Magtheridon (Magtheridon's Lair) | Kael'thas Sunstrider (Tempest Keep) |
| Hands | The Curator (Karazhan) | Leotheras the Blind (SSC) |
| Legs | Gruul the Dragonkiller (Gruul's Lair) | Fathom-Lord Karathress (SSC) |

To confirm any token slot, pass the token id to `al_item_source.py` (e.g. `30243` Helm of the Vanquished Defender -> Lady Vashj).

## Source Type Icons (Required)
Every item's source cell must be prefixed with an icon indicating the source type:

| Source Type | Icon | CSS Class | HTML |
|---|---|---|---|
| Raid Boss | 🐉 | `.boss-icon` | `<span class="boss-icon">🐉</span>` |
| Dungeon Boss | 💀 | `.boss-icon` | `<span class="boss-icon">💀</span>` |
| Quest Reward | ❗(yellow !) | `.quest-icon` | `<span class="quest-icon">!</span>` |
| Badge of Justice | 🎖️ | `.badge-icon` | `<span class="badge-icon">🎖️</span>` |
| Reputation | 📜 | `.rep-icon` | `<span class="rep-icon">📜</span>` |
| Crafted | 🔨 | `.craft-icon` | `<span class="craft-icon">🔨</span>` |
| PvP | ⚔️ | `.pvp-icon` | `<span class="pvp-icon">⚔️</span>` |
| World Drop | 🌍 | `.drop-icon` | `<span class="drop-icon">🌍</span>` |

CSS for all icons: `margin-right: 3px; font-size: 12px;`
Quest icon additionally: `color: #FFD100; font-weight: bold; font-size: 14px;`

## Heroic Tag
Never use `(H)`. Always use the styled span: `<span class="heroic">Heroic</span>`
- CSS: neon orange `#ff6600`, bold, with subtle glow via text-shadow.

## Notes Column

### RULE: Notes must be VERIFIED against real item stats (REQUIRED)
Notes were historically hit-and-miss because they were written from memory (threat items got called "avoidance", etc.). **Never write a stat-based claim from memory.** Ground every note in the item's actual stats.

**Stat source = `WIKI_PRIVATE_DIR/wow_class_guides/tools/wh_item_stats.py`** (fetches Wowhead's tooltip endpoint `nether.wowhead.com/tbc/tooltip/item/<id>`, the only reliable stat source; plain WebFetch fails). Run it on every item ID in a section before writing notes; it caches to `WIKI_PRIVATE_DIR/wow_class_guides/tools/.wh_cache/` so it is fast/offline on re-run:
```
python tools/wh_item_stats.py 29011,28825,28516,...     # prints id, ilvl, attrs, equip/use/proc, sockets
```
Workflow: extract the section's item IDs → run the tool → write each note from the digest → spot-check that the note's claim matches the real stats. Stat-to-role by archetype:
- **Tank:** `+def/+dodge/+parry/+block` = survival; `+hit/+exp/+AP/+crit` = threat. (`WIKI_PRIVATE_DIR/wow_class_guides/tools/wh_item_stats.py` also resolves spells via `nether.wowhead.com/tbc/tooltip/spell/<id>`.)
- **Melee DPS:** `+hit/+exp/+crit/+AP/+str/+agi/+haste` = the good stats; `+def/+dodge/+block` on a piece means it's a tank item, not for you.
- **Caster DPS/healer:** `+spell damage/+spell hit/+spell crit/+spell haste/+int/+spirit/+mp5` = caster stats; `+AP/+str/+agi` means it's a melee item. Do NOT call a +spellpower piece "threat" or mix it with melee stats.

### RULE: Notes are JUDGMENT, NOT a stat list (REQUIRED, user-mandated)
**A note that just restates the item's stats is banned.** The hover tooltip already shows every number; repeating "Str + crit + resilience" or "agi + hit + AP, no avoidance" in the Notes column is dead weight the user explicitly hates. You still **verify** the item against `wh_item_stats.py` (above) so your judgment is correct, but the note **text** must tell the reader something the tooltip cannot:
- **Why it's ranked here / the trade-off:** "more threat but no Resilience, wear it only once you're already tanky", "the rare crafted ring that carries Resilience", "set piece, prioritise for the 2-set bonus".
- **When to use / swap it:** "fire it inside a Death Wish window, not on cooldown", "run survival until crit-immune (490 Defense), then swap", "save the active for the CC that would kill you".
- **How to get it / acquisition friction:** "Honor purchase, no rating needed", "craft it early", "badge cloak, buy it and forget the slot".
- **Role in the kit / set-bonus dependency:** "your main gem home (three sockets)", "the whole point of the Mace-spec build".

Contrast:
- ❌ BANNED (stat dump): `Str + crit + resilience, meta socket` / `Crit + AP threat cloak` / `+45 resilience, on-use CC break`.
- ✅ GOOD (judgment): `Set piece and your only meta slot, buy toward the 5-set bonus` / `Raid cloak: pure damage, no Resilience, take it early when kills beat mitigation` / `Your CC break, never unequip it, save the active for the stun that kills you`.

Keep it to ~1 line. If a slot's pick is so obvious you can't say anything the tooltip doesn't, write the shortest purposeful pointer ("set piece, buy toward the 4-set") rather than padding with stats.
- **No website names in notes** (user preference): describe by role/judgment, not "Wowhead #1". Consensus framing only ("Unanimous BiS", "consensus pick").

### General
- Every pre-raid item should have a note. No empty note cells in the pre-raid section.
- Weapon entries: note what's relevant to the class. Melee = weapon type for racials ("Axe - Orc racial", "Mace/Sword - Human racial"). Casters = weapon type + whether it carries a spell-damage stat-stick role (staff vs main-hand+off-hand vs dagger+wand), and note the wand slot separately.
- Where survival and threat picks genuinely split a slot, list both and label `BiS (Survival)` / `BiS (Threat)`; tell the reader to run survival until crit-immune (490 Defense), then threat.

## Accent Color
Each class uses its **official WoW class color** as the primary accent. When starting a new class, swap the Warrior hex (`#C79C6E`) for the class color everywhere it appears (`#nav h3`, `h1`, borders, `.copy-btn`, the "My Other Projects" button can stay). Keep the shared secondary colors: **active/teal `#4ec9b0`** and **h2 headings `#dcdcaa`**.

| Class | Hex | Class | Hex |
|---|---|---|---|
| Warrior | `#C79C6E` | Mage | `#69CCF0` |
| Paladin | `#F58CBA` | Warlock | `#9482C9` |
| Hunter | `#ABD473` | Priest | `#FFFFFF` |
| Rogue | `#FFF569` | Shaman | `#0070DE` |
| Druid | `#FF7D0A` | Death Knight | `#C41F3B` |

For light colors on the dark theme (Priest white, Rogue yellow), keep body text the default `#d4d4d4`; only headers/accents use the class color.

## Style
- Match the existing wiki dark theme (VS Code style, dark backgrounds, left nav).
- Table format: Rank / Item / Source / Notes columns.
- Mark world boss / extremely rare drops so the user knows what's realistic vs aspirational.
- Gem tables organized by socket color with separate sub-tables. (Caster gems = spell damage / Runed/Glowing/etc.; melee = the Bold/Solid/Inscribed lines. Use the class-correct gems.)
- Enchant table includes Wowhead links (spell or item) for every enchant.
- **No em dashes anywhere** (files or chat): use a comma, colon, period, or rephrase. Never the em-dash character (U+2014) or `&mdash;`. Sweep new content before finishing.

## TBC BIS Anniversary Addons (LAST-RESORT FALLBACK ONLY)
**The written guides are the source of truth for rankings: wowtbc.gg, Wowhead, Icy Veins, Warcraft Tavern (Pass 0/1).** The TBCA_BIS and BIS-TBC addons have proven LESS reliable than the actual guides (their EPV/threat scoring disagrees with consensus and their talent builds are not always current, e.g. TBCA's Fury build does not even reach Bloodthirst). So treat them as a **fallback only**, consult them only when:
1. The written guides genuinely disagree and you need a tie-breaker, OR
2. No written guide covers a slot/spec at all and you have nothing else.

When an addon conflicts with the written guides, **the guides win.** Never let an addon override a sourced guide ranking. (For drop SOURCES, AtlasLoot loot tables remain authoritative, that is a separate game-data DB, not a ranking addon, see `WIKI_PRIVATE_DIR/wow_class_guides/tools/al_item_source.py`. For talent data, prefer the guides / wowtbc.gg `bisTalentOne`, not TBCA's `TalentData.lua`.)

Note: addon rankings are used only behind the scenes to inform ordering, do NOT add a visible "TBC BIS Rank" column to gear tables (this column was removed; tables are Rank / Item / Source / Notes).

**BIS-TBC** (v1.15), `<WOW_ADDONS_DIR>/BIS-TBC/`
- Key data file: `BIS-TBC_bislists.lua`, contains ranked item lists per class/spec/phase
  - Format: `BISTBC_bislists["Class"]["Spec"]["Phase"][slotIndex] = { ["slot_name"] = "Slot", [1] = itemID, [2] = itemID, ... }`
  - Phases: `PR` (pre-raid), `T4`, `T5`, `T6`, `ZA`, `SWP`
  - Example: `BISTBC_bislists["Warrior"]["Fury"]["PR"][1]` = Head slot pre-raid Fury Warrior rankings
- Other data files: `BIS-TBC_items.lua` (item metadata), `BIS-TBC_sources.lua` (drop sources), `BIS-TBC_gems.lua`, `BIS-TBC_enchants.lua`

**TBCA_BIS** (v4.3), `<WOW_ADDONS_DIR>/TBCA_BIS/`
- Fallback only. EPV-based gear scoring that often disagrees with the guides; `Data/TalentData.lua` builds are not always current. Use only as a tie-breaker when guides conflict.
- Key data files: `Data/BiSData.lua`, `Data/TalentData.lua`

**Specs covered:** Warrior Fury, Warrior Protection. Both specs' data is in the addon under `["Warrior"]["Fury"]` and `["Warrior"]["Protection"]`.

## Sources Integrated So Far
1. **Icy Veins** - Fury Warrior Pre-Raid Gear (pre-raid BiS, gem IDs)
2. **wowtbc.gg** - Fury Warrior BiS List (Phase 1 raid gear, enchants, gems per slot, drop rates)
3. **Wowhead** - Warrior DPS Gems & Enchants Guide (full enchant list, gem strategy, meta requirements)
4. **Wowhead** - Warrior DPS Pre-Raid BiS (alternative rankings, new items like Badge of Swarmguard, Blinkstrike)
5. **Warcraft Tavern** - Fury Warrior Pre-Raid BiS (additional items, Ragesteel Shoulders ranking)
6. **Wowhead** - Protection Warrior Phase 2 BiS Guide (SSC/TK gear, T5 set, Spyglass of the Hidden Fleet trinket)
   - Saved at: `WIKI_PRIVATE_DIR/wow_class_guides/resources/warrior/prot/Protection Warrior Tank Best in Slot (BiS) Phase 2 Gear Guide - TBC Classic - Wowhead.html`
7. **wowtbc.gg** - Protection Warrior BiS List (per-slot gem socket patterns + enchant picks, drop %)
   - Saved at: `WIKI_PRIVATE_DIR/wow_class_guides/resources/warrior/prot/Protection Warrior Best in Slot (BiS) List - TBC Classic · wowtbc.gg.html`
   - Note: wowtbc.gg enchant picks lean DPS/threat (Glyph of Ferocity, Greater Inscription of Vengeance, Chest - Exceptional Stats). Cross-reference with Wowhead's tank-flavored picks (Arcanum of Defense, Greater Inscription of the Knight/Warding, Major Resilience) and surface both as options.
8. **Wowhead + wowtbc.gg** - Protection Warrior **Phase 1** BiS (the live per-slot tables in the prot guide).
   - Wowhead drives the primary tank/survival ranking; wowtbc.gg folds in threat/PvP picks. They genuinely disagree at several slots (neck, back, wrist, hands, waist, feet lean PvP on wowtbc.gg; both rank Warbringer **Shoulderplates** 29023 and **Wrynn Dynasty Greaves** over the tier survival pieces). Each row notes which guide it came from.
   - **HOW TO GET THE REAL DATA (the guide sites are JS-rendered, WebFetch returns only nav):**
     - **wowtbc.gg** is Gatsby: `curl -sA "Mozilla/5.0" https://wowtbc.gg/page-data/bis-list/<spec>/page-data.json` → `result.pageContext.bisList[]`. Each entry has `name`, `slot` (head/neck/.../finger 1/trinket 1/weapon/off hand/ranged), `phase` (`Pre-Bis`/`T4`/`T5`/`T6`/`ZA`/`SWP`), `final_value`, and per-tier objects (`t4`,`t5`,...) with `bis`/`solo`/`group` flags + recommended `enchant`/`gems`. **NB its `source` field is the zone and `source_type` is the boss (swapped from the column name).**
     - **Wowhead** guides DO render server-side to `curl -sL -A "Mozilla/5.0 (Windows NT 10.0; Win64; x64)" <guide-url>` (browser UA required). Item links `href="/tbc/item=<id>/<slug>">Name<` appear in ranked order per slot, with item IDs.
     - **Warcraft Tavern** (curl + browser UA works; plain WebFetch 403s). Each phase has its own page, e.g. `https://www.warcrafttavern.com/tbc/guides/pve-protection-warrior-tank-gear-bis/` (= Phase 1). The clean "Ideal Set" table per slot is keyed by `<img alt="<slot> slot equipment icon">` headers; items link as `wowclassicdb.com/tbc/item/<id>">Name<` (NOT `item=`). The inline-prose `tbcdb.com/?item=<id>` links are discussion, not the ranked list. Balanced/tank lean; surfaces extra items (Bulwark of Kings, Black Planar Edge, Strength of the Untamed).
     - **Icy Veins** (curl + browser UA): `https://www.icy-veins.com/tbc-classic/protection-warrior-tank-pve-gear-best-in-slot` (raid/endgame BiS, light on mid-phases) and `.../protection-warrior-tank-pve-pre-raid-gear` (strong pre-raid). Tank lean. Correct URL stem is `protection-warrior-tank-pve-*`.
     - Secondary/tertiary (fetchable, lower quality): **overgear.com** (general all-class phase lists), **lootxphub.com** (names only, no item links).
     - Plain WebFetch fails on all of these; always curl with a browser UA.
   - **Blend the sources:** wowtbc.gg leans threat/PvP, Wowhead/Warcraft Tavern/Icy Veins lean tank. They disagree at many slots, so cite which guide(s) back each row and note splits. Always verify item IDs/names against the local Questie `tbcItemDB.lua`/`tbcNpcDB.lua` (the addon `BIS-TBC` ranks by threat and can differ from a tank guide).
