# Team organization

## Members and roles

| Member | Domain | Main tasks |
| ------ | ------ | ---------- |
| **dgaillet** | Game logic, tooling | config parsing, highscore system, pygame setup, ghost AI (BFS), Pac-Man movement, ghosts in game and collisions, game progression, cheat mode, highscore and instructions screens, layouts wiring, packaging, acceptance test plan, README |
| **mteriier** | Display, UI | maze generator import, maze display, pacgums and super pacgums, Pac-Man / pacgum link, in-game scoring, HUD, menus, pause / resume, end screen |

## Workflow

1. Each task is a GitHub issue, attached to one of the 4 epics.
2. The owner creates a branch `<issue number>-<short-name>`
   (e.g. `13-project-packaging`).
3. Before merging: `make lint` (flake8 + mypy) and `make test` must pass.
4. A pull request is opened and merged into `main` by its author.
5. The issue is moved to **Done** on the Kanban board.

## How decisions were made

> TODO: describe how you decided things together (meetings at 42,
> Discord, discussion in the issue / PR, ...).

Main technical decisions:

| Decision | Why |
| -------- | --- |
| Models (`Maze`, `Pacgum`, `Ghost`, `Config`) know nothing about pygame; renderers draw them | Logic is unit-testable and the graphics can be swapped for MLX |
| pydantic for the config | Type and value checks for free, faulty values replaced by defaults |
| BFS for the ghosts' path finding | Simple, always finds the shortest path in a maze |
| `App` + `Layout` classes for the screens | One place to switch between menu, game, pause, end and highscore screens |
| Timers counted in frames | Same game speed on every machine |
| PyInstaller for packaging | Standalone executable, no Python needed |

## Blocking points and conflicts

| Problem | How it was handled |
| ------- | ------------------ |
| Not sure which pygame functions are allowed (MLX equivalence) | Checked each call against the MiniLibX docs; reverted the first graphical maze attempt |
| Merge conflict on `game.py` and `maze.py` | Solved by hand (`723fa6c`); after that, smaller branches and more frequent pulls from `main` |
| A draw call lost during a merge | Found while testing, re-added (`84d20ff`) |
| Unit tests broken after the packaging change | Fixed before merging PR #40 (`28f95ae`) |
| Duplicated work: both of us implemented the highscore and instructions screens (dgaillet in PR #39, mteriier on branch `36-layout-viewscore-instructions`) | dgaillet's version was merged first and kept; branch #36 was dropped. Lesson: move the issue to **In progress** on the Kanban and assign it before starting, so the other member knows |
