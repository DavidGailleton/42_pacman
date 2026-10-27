# Acceptance test plan

This is the test plan to run before the defense, and again during it. It
covers every way a grader can try to break the game: command-line
arguments, config files, highscore files, the maze generator, and a full
playthrough.

## Pass rule

A test **passes** only if all of these are true:

- No Python traceback is printed, at any moment.
- The game either keeps running or stops with a clear `Error: ...` message.
- The message or behaviour matches the **Expected** column.

One traceback anywhere means the project is non-functional, so a failing
test here blocks the release.

## Setup

```bash
make install
# Each test is launched from the repository root:
uv run python3 pac-man.py <config>
echo $?          # exit code, when the table asks for it
```

The fixture files live in [`test_configs/`](test_configs/). In the tables
below, `T=project_management/test_configs`.

For the highscore tests (section D), the config `$T/highscore_test.json`
reads and writes `$T/test_highscores.json` (gitignored). Copy one of the
`bad_highscores_*.json` files onto it before launching, so the real
`highscores.json` is never touched:

```bash
cp $T/bad_highscores_broken.json $T/test_highscores.json
uv run python3 pac-man.py $T/highscore_test.json
```

Fill the **Result** column with ✅ or ❌, and write what you saw in
**Notes** when it fails.

---

## A. Command line

| ID | Steps | Expected | Result | Notes |
|----|-------|----------|--------|-------|
| A1 | `uv run python3 pac-man.py` | `Error: expected exactly one argument (got 0)` + usage line, exit code 1 | | |
| A2 | `uv run python3 pac-man.py a.json b.json` | Same message with `(got 2)`, exit code 1 | | |
| A3 | Start the game, press Ctrl+C in the terminal | Game stops, no traceback | | |
| A4 | Start the game, close the window with the ✕ button | Game stops, exit code 0 | | |

## B. Config file cannot be read

All cases print one `Error: ...` line and exit with code 1, before any
window opens.

| ID | Steps | Expected | Result | Notes |
|----|-------|----------|--------|-------|
| B1 | `pac-man.py nope.json` | `Error: config file 'nope.json' not found` | | |
| B2 | `pac-man.py $T` (a directory) | `Error: '...' is a directory, not a config file` | | |
| B3 | `cp config.json /tmp/p.json && chmod 000 /tmp/p.json`, then run with it | `Error: permission denied when reading '/tmp/p.json'` | | |
| B4 | `printf '\xff\xfe{' > /tmp/bin.json`, then run with it | `Error: '/tmp/bin.json' is not a UTF-8 text file` | | |
| B5 | `pac-man.py $T/invalid_json.json` (trailing comma) | `Error: '...' is not valid JSON: Expecting property name enclosed in double quotes (line 4, column 1)` | | |
| B6 | `pac-man.py $T/empty.json` | `Error: '...' is not valid JSON: Expecting value (line 1, column 1)` | | |
| B7 | `pac-man.py $T/comments.json` (`#` lines, some indented, inside objects and arrays) | No message, game starts normally | | |

## C. Faulty config values

The game must **start anyway**. Each bad value prints
`Warning: invalid value X for 'key' (reason), using default Y`.

| ID | Steps | Expected | Result | Notes |
|----|-------|----------|--------|-------|
| C1 | `pac-man.py $T/not_object.json` (root is `[1, 2, 3]`) | `Warning: config root must be a JSON object, using default values for everything`, game starts | | |
| C2 | `pac-man.py $T/empty_levels.json` (only `levels` key) | One `Warning: missing key '...'` per missing key | | |
| C3 | `pac-man.py $T/wrong_types.json` (`"lives": "3"`, `"seed": true`, `levels` is an object, float, null...) | One warning per key (8), all defaults used | | |
| C4 | `pac-man.py $T/out_of_range.json` (`lives: 0`, negative points, `level_max_time: 0`, width 5, height 500) | One warning per bad key; `levels` falls back to the 10 default levels | | |
| C5 | `pac-man.py $T/empty_levels.json` (`"levels": []`) | Warning on `levels`, game has 10 levels of 21×21 | | |
| C6 | `pac-man.py $T/unknown_keys.json` (extra keys at top level and in a level) | No warning, game starts | | |
| C7 | `pac-man.py $T/out_of_range.json` (`"highscore_filename": ""`) | Warning, `highscores.json` is used | | |
| C8 | Grader edits `config.json` live (e.g. `lives: 1`, `level_max_time: 5`, `point_per_pacgum: 1000`) | New values visible in the HUD and in the score | | |

## D. Highscores

Use `$T/highscore_test.json` (see Setup).

| ID | Steps | Expected | Result | Notes |
|----|-------|----------|--------|-------|
| D1 | `rm -f $T/test_highscores.json`, open Highscores, then finish a game and save a name | Empty table, no warning; the file is created after saving | | |
| D2 | Copy `bad_highscores_broken.json` (cut-off JSON), open Highscores | `Warning: cannot read highscores (...), ignoring file`, empty table | | |
| D3 | Copy `bad_highscores_not_list.json` (root is an object) | `Warning: highscore file must contain a list, ignoring file`, empty table | | |
| D4 | Copy `bad_highscores_entries.json` (name too long, symbols, empty, negative, float, bool, string score, missing name) | Only `VALID ONE 900` and `VALID TWO 300` are shown | | |
| D5 | Copy `bad_highscores_too_many.json` (15 entries) | Only the 10 best (`PLAYER 15` to `PLAYER 6`) are shown | | |
| D6 | Set `"highscore_filename": "/proc/nope/x.json"` or a directory, finish a game, save | `Warning: cannot save highscores (...)`, back to main menu, no crash | | |
| D7 | On the end screen: type letters, digits, spaces, symbols, more than 10 chars, then Backspace | Only letters/digits/spaces accepted, stops at 10 chars, Backspace removes the last char | | ❌ **Known bug:** Backspace keeps only the last character (`self.name[-1:]` in `src/layouts/end_screen.py`) |
| D8 | On the end screen, press Enter with an empty name | Score is not saved, a warning is printed, back to main menu | | |
| D9 | Save a score, quit, relaunch, open Highscores | The score is still there | | |

## E. Maze generator

| ID | Steps | Expected | Result | Notes |
|----|-------|----------|--------|-------|
| E1 | Uninstall the A-Maze-ing package (`uv pip uninstall mazegenerator`), launch the game. Run `make install` afterwards to reinstall it. | Clean `Error: ...` message, exit code 1 | | ❌ **Known bug:** `ModuleNotFoundError` traceback, because `src/__main__.py` imports `App` before its `try` block |
| E2 | Generator raises during level loading (simulated by replacing `MazeGenerator` with a class that raises) | `Error: Maze Generation Failed: ...`, exit code 1, no traceback | | |
| E3 | Levels at the size limits: `{"width": 10, "height": 10}`, `{"width": 100, "height": 100}`, `{"width": 10, "height": 100}` | Mazes are generated (the generator may print that the "42" pattern does not fit), game playable | | |
| E4 | Launch twice with the same `seed` | Level 1 is the same maze both times; level 2 is different from level 1 | | |
| E5 | Look at a maze | It has loops (not a perfect maze), and the 4 corners can be reached | | |

## F. Gameplay and UI flow

Use `config.json` unless stated otherwise.

| ID | Steps | Expected | Result | Notes |
|----|-------|----------|--------|-------|
| F1 | Main menu: try Start, Highscores, Instructions, Exit, using arrows and W/S | Each entry opens the right screen; Esc/Enter goes back; Exit closes the game | | |
| F2 | Move with arrow keys, then WASD | Pac-Man moves in corridors only, walls block him | | |
| F3 | Eat a pacgum, a super-pacgum, a frightened ghost | Score goes up by `point_per_pacgum`, `point_per_super_pacgum`, `point_per_ghost`; it never goes down | | |
| F4 | Eat a super-pacgum | Ghosts turn blue for about 7 s and run away; an eaten ghost comes back in its corner after about 5 s | | |
| F5 | Touch a ghost in chase mode | One life lost, Pac-Man respawns at the center | | |
| F6 | Lose every life | Game Over screen with the final score and name entry | | |
| F7 | Eat every pacgum of a level | Next level starts; score and lives are kept | | |
| F8 | Wait for the timer to reach 0 | Next level starts; score and lives are kept | | |
| F9 | Press Esc during play | Pause menu; Resume continues where it stopped (timer did not run); Main menu goes back | | |
| F10 | Press C during play | `CHEAT MODE` shown in the HUD, ghosts do not kill Pac-Man; press C again to turn it off | | |
| F11 | Look at the HUD | Score, lives, level and remaining time are shown and update | | |
| F12 | Play a whole game, then Start again from the main menu | Score back to 0, lives back to `lives`, level 1 | | |

## G. Full playthrough (10 levels)

```bash
rm -f $T/test_highscores.json
uv run python3 pac-man.py $T/full_run.json
```

`full_run.json` has 10 levels of 15×15 and a 10-second timer.

| ID | Steps | Expected | Result | Notes |
|----|-------|----------|--------|-------|
| G1 | Start, press C (cheat mode), eat pacgums and wait out each timer | Levels 1 to 10 follow each other, the HUD level number goes up | | |
| G2 | Watch score and lives between levels | Never reset, score never decreases | | |
| G3 | Clear level 10 | Victory screen with the final score | | |
| G4 | Type a name, press Enter | Back to the main menu; Highscores shows the name and score | | |
| G5 | Repeat the run **without** cheat mode, and lose on purpose | Game Over screen, score saved the same way | | |

## H. Packaged build

| ID | Steps | Expected | Result | Notes |
|----|-------|----------|--------|-------|
| H1 | `make package` | `release/pac-man-linux.tar.gz` is created again from scratch | | |
| H2 | Extract it in an empty folder, run `./run.sh` | Game starts with the bundled `config.json` | | |
| H3 | `./pac-man` (no argument) and `./pac-man nope.json` | Same messages as A1 and B1 | | |
| H4 | Open `INSTRUCTIONS.txt` | Controls, rules, config and highscore notes are present | | |
| H5 | Download the build from the published page and launch it | Same as H2 | | |

## I. Code quality

| ID | Steps | Expected | Result | Notes |
|----|-------|----------|--------|-------|
| I1 | `make lint` | flake8 and mypy report zero errors | | |
| I2 | `make test` | All unit tests pass | | |

---

## Test run log

Write one line per full run of this plan.

| Date | Tester | Commit | Passed / total | Notes |
|------|--------|--------|----------------|-------|
| 2026-10-27 | | 8599e2d | A, B, C, D2–D6, E2–E3 checked from the terminal | E1 and D7 fail (known bugs above); window tests not run yet |
