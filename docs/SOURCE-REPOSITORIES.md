# Publishing application source

Keep this wiki as the shared documentation hub. Give each independently built application or mod a separate source repository. Link its public repository from projects.json once it exists; source_url stays null until then.

Use templates/source-repository/ as a starting point, adjusting it to the actual language, build and license. Each source checkout should contain the complete project, its tests, build instructions, dependency locks, license and required third-party notices. Keep installers, compiled output, private credentials, review backups and personal runtime data out of source commits. Publish intended distributable files through that project's release process.

For Collections Manager, the current Python adapter lives in the installed MO2 plugin directory, while Rust, the C++ helper, tests and build tools live in the development project. Consolidate them into a complete source checkout before publishing; deployment should copy matching built files into MO2. Do not treat a DLL-only directory as the complete source or use the installed game/plugin tree as a backup strategy.

Before a first source upload, follow its existing project instructions and verify a fresh checkout can build/test using the documented prerequisites. Preserve original license and third-party notices. Source preparation and GitHub publication are separate actions from maintaining this website.

The website registry supports Skyrim projects, WoW guides and future general software; adding a new category requires updating the tool, documentation and regression checks together.
