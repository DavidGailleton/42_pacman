# Risk analysis

**Probability** and **Impact**: Low / Medium / High.

| # | Risk | Probability | Impact | Mitigation | Outcome |
| - | ---- | ----------- | ------ | ---------- | ------- |
| R1 | A Python traceback during the defense (= project non-functional) | Medium | High | Config validated with pydantic, faulty values replaced by safe defaults; clear `Error: ...` messages + exit code 1; acceptance test plan and unit tests on broken configs / highscore files | Covered by `tests/test_acceptance_configs.py` |
| R2 | Using a pygame function that has no MLX equivalent | Medium | High | Only basic calls (window, filled shapes, lines, text, key events); each call checked against the MiniLibX docs | One attempt at the graphical maze was reverted (`e3b3ec6`) and redone with allowed calls only |
| R3 | Merge conflicts when both of us edit `game.py` / `maze.py` | High | Medium | Small issues, one branch per issue, pull from `main` often, models separated from renderers | Happened once on `game.py` / `maze.py` (`723fa6c`), fixed by hand |
| R4 | The A-Maze-ing package (`mazegenerator` wheel) fails or is missing | Low | High | Used as-is through a `Maze` wrapper class; `make unzip_maze` to install it; errors caught and reported | No failure seen |
| R5 | Game speed depends on the machine | Medium | Medium | Timers counted in frames, not real `dt` (`cd0702f`) | Same behaviour everywhere |
| R6 | Low FPS from redrawing sprites every frame | Medium | Medium | Pac-Man and ghost sprites cached (`087ec6c`) | Fixed |
| R7 | Corrupt or edited `highscores.json` | Medium | Medium | Invalid file / entries ignored, list capped at 10 | Tested with the `bad_highscores_*.json` fixtures |
| R8 | Packaging: PyInstaller cannot cross-compile | High | Low | Only a Linux build is shipped, documented in the README | Accepted |
| R9 | Late deliverables (README, tests, packaging) before the deadline | Medium | High | Dedicated epic #17 | Done in the last days: tight but delivered |
| R10 | Work not merged before the defense | Medium | High | Open PRs early, check the Kanban board | Everything merged before the defense |
| R11 | Unbalanced workload between the 2 members | Medium | Medium | Issues split by domain (logic vs display / UI), reviewed at each planning point | See [team_organization.md](team_organization.md) |

## Bugs found and fixed

| Bug | Fix |
| --- | --- |
| A pacgum spawned on Pac-Man's start cell, so the game started at 10 points | `ddb9620` |
| Backspace on the end screen when typing a name | `2f1df89` |
| A pacgum draw call was lost during a merge | `84d20ff` |
| Unit tests broken after packaging changes | `28f95ae` |
