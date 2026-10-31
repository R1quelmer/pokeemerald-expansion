# Codex instructions — FireRed hack project

## Project target

This fork is being used as the source project for a Pokémon FireRed ROM hack.

- Primary game target: **Pokémon FireRed (FRLG/Kanto build)**.
- Primary build command: `make firered -j$(nproc)`.
- Work on the current feature branch unless the user explicitly requests another branch.
- Do not make project changes directly on `master` unless explicitly requested.

## Build and validation

- After code or data changes, build the FireRed target with `make firered -j$(nproc)` whenever the environment supports the toolchain.
- If switching between Emerald and FRLG builds, run `make clean` first.
- Treat FireRed build failures as blockers: inspect and fix the actual compiler/map/script error rather than bypassing validation.
- For shared battle-engine changes, run relevant automated tests when practical.

## FireRed-specific rules

- Prefer FRLG/Kanto-specific maps, data tables, scripts and constants where the project has separate Emerald and FRLG variants.
- New Kanto maps should use `REGION_KANTO` when a region attribute is needed.
- FRLG layouts should use the appropriate FireRed layout/version settings expected by the project.
- Avoid unintentionally changing Emerald-only content when implementing a FireRed feature, except when the implementation lives in shared engine code.

## Repository safety

- Never commit generated ROM binaries, save files, build directories or copyrighted base-game ROM files.
- `.gba` outputs are build artifacts and must remain outside version control.
- Keep changes focused and easy to review; prefer separate commits for unrelated features.
- Do not rewrite or force-update `master`.

## Working style

When implementing a requested feature:

1. Locate the relevant FireRed/FRLG data, scripts, graphics, map, or engine code.
2. Explain briefly which files will be changed when the change is substantial.
3. Implement the smallest complete version of the feature.
4. Build the FireRed target and fix build errors.
5. Summarize changed files, behavior, and any testing still requiring an emulator.

The project owner may be working from a phone and may not be familiar with the decompilation codebase, so keep instructions concrete and avoid requiring manual source edits when the change can be implemented directly in the repository.
