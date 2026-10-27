# PyInstaller build spec: run with `make package`
# (or `uv run pyinstaller --clean -y pac-man.spec`).
# Produces a single-file executable dist/pac-man.
# No data files are bundled: sprites are drawn in code and the default
# pygame font is collected automatically. config.json and the highscore
# file stay next to the executable so they can be edited.

a = Analysis(["pac-man.py"], pathex=["."])
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="pac-man",
    # Keep a console so config errors are visible to the player.
    console=True,
)
