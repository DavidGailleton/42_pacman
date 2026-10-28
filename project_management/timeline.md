# Timeline and Kanban

## Epics

The subject was split into 4 epics, each broken down into small issues.
One issue = one branch = one pull request.

| Epic | Goal | Issues |
| ---- | ---- | ------ |
| **#14 Foundation** | Everything the game needs before gameplay | config parsing, highscores, pygame setup, maze generator import, ghost AI (BFS) |
| **#15 Gameplay** | A playable level | #5 maze display, #7 Pac-Man move, #8 ghosts in game, #9 pacgums, #30 Pac-Man / pacgum link, #10 scoring, #11 game progression, #20 cheat mode |
| **#16 UI & Highscores** | Every screen of the game | #12 windows and menus, #38 layouts interaction (highscore and instructions screens included) |
| **#17 Deliverables** | What the defense needs | #13 packaging, #23 acceptance test plan, #22 project management directory, README |

## Kanban

The board was kept on GitHub Projects with 4 columns. State at the end
of the project (2026-10-28): every issue is done.

| Todo | In progress | In review | Done |
| ---- | ----------- | --------- | ---- |
| | | | #5, #7, #8, #9, #10, #11, #12, #13, #20, #22, #23, #30, #38, Foundation issues, README |

## Gantt (actual)

```
                      Oct 07  Oct 14  Oct 16  Oct 19  Oct 21  Oct 25  Oct 28
Repo setup            ■
#14 Foundation                ■■■
#15 Gameplay                  ■■■■■■■■■■■■■■■
#16 UI & Highscores                           ■■■■■■■■■■■■■■■■■■■■■■■
#17 Deliverables                                              ■■■■■■■■■■■■■
                                                                            ▲ project finished
```

## Milestones

| Date | Milestone |
| ---- | --------- |
| 2026-10-07 | Repository created |
| 2026-10-14 | Planning (epics and issues); foundation: config parsing, highscores, pygame window, maze generator import, ghost AI |
| 2026-10-16 | Core gameplay: maze display, Pac-Man movement, ghosts, pacgums, scoring |
| 2026-10-19 | Windows and menus, pause / resume, lives and respawn |
| 2026-10-20 | Level progression and time limit, cheat mode |
| 2026-10-21 | Highscore and instructions screens, all screens wired together |
| 2026-10-25 | Packaging with PyInstaller |
| 2026-10-27 | Acceptance test plan, config error tests, README |
| 2026-10-28 | Project management directory: **project finished** |
