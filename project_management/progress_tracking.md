# Progress tracking

Actual progress compared to the plan. The **Done** dates come from the
merge of each pull request into `main`.

**Status: the project is finished.** Every issue of the 4 epics is done
and merged into `main`.

> TODO: fill the **Planned** column with the dates we set when the
> issues were created on 2026-10-14.

| Issue | Task | Owner | Planned | Done | Status |
| ----- | ---- | ----- | ------- | ---- | ------ |
| #14 | Config parsing with pydantic | dgaillet | | 2026-10-14 | ✅ |
| #14 | Highscore / score management | dgaillet | | 2026-10-14 | ✅ |
| #14 | pygame setup, first window (PR #24) | dgaillet | | 2026-10-14 | ✅ |
| #14 | Maze generator import (PR #25) | mteriier | | 2026-10-14 | ✅ |
| #14 | Ghost AI with BFS (PR #26) | dgaillet | | 2026-10-14 | ✅ |
| #5 | Display the maze with pygame (PR #27) | mteriier | | 2026-10-16 | ✅ |
| #7 | Pac-Man move and display (PR #28) | dgaillet | | 2026-10-16 | ✅ |
| #9 | Pacgums and super pacgums (PR #29) | mteriier | | 2026-10-16 | ✅ |
| #30 | Link between Pac-Man and pacgums (PR #31) | mteriier | | 2026-10-16 | ✅ |
| #10 | In-game scoring (PR #32) | mteriier | | 2026-10-16 | ✅ |
| #8 | Ghosts in game, collisions (PR #33) | dgaillet | | 2026-10-16 | ✅ |
| #12 | Windows: HUD, menu, pause, end screen (PR #34) | mteriier | | 2026-10-19 | ✅ |
| #20 | Cheat mode (PR #35) | dgaillet | | 2026-10-20 | ✅ |
| #11 | Game progression, levels, time limit (PR #37) | dgaillet | | 2026-10-20 | ✅ |
| #38 | Highscore and instructions screens, all buttons routed (PR #39) | dgaillet | | 2026-10-21 | ✅ |
| #13 | Packaging with PyInstaller (PR #40) | dgaillet | | 2026-10-25 | ✅ |
| #23 | Acceptance test plan + config error tests (PR #42) | dgaillet | | 2026-10-27 | ✅ |
| — | README | dgaillet | | 2026-10-27 | ✅ |
| #22 | Project management directory | mteriier | | 2026-10-28 | ✅ |

## Activity

Commits per day, from `git log`:

| Date | Commits | Main work |
| ---- | ------- | --------- |
| 2026-10-07 | 1 | Initial commit |
| 2026-10-14 | 21 | Foundation, planning |
| 2026-10-15 | 3 | Maze display |
| 2026-10-16 | 23 | Gameplay (busiest day) |
| 2026-10-19 | 12 | Windows and menus |
| 2026-10-20 | 13 | Progression, cheat mode, highscore screen, bug fixes |
| 2026-10-21 | 2 | Layouts wiring |
| 2026-10-25 | 3 | Packaging |
| 2026-10-27 | 6 | Tests, README, instructions screen |

## Gap analysis

- **Gameplay went fast**: the whole #15 epic was merged in 3 days
  (Oct 14 → 16) because Foundation (models, config, BFS) was ready and
  unit-tested first.
- **UI took longer than gameplay**: menus, pause, end screen and the
  highscore / instructions screens were spread over Oct 19 → 27, because
  every screen had to be wired to the others (`App` + `Layout` classes).
- **Late deliverables**: packaging, acceptance tests and README were all
  done in the last days. Next time, start the deliverables epic earlier.
