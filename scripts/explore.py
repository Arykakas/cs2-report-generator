from pathlib import Path
import sys

from awpy import Demo
import polars as pl

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
pl.Config.set_tbl_cols(-1)
pl.Config.set_tbl_width_chars(10000)
pl.Config.set_fmt_str_lengths(10000)


demo = Demo(Path(__file__).resolve().parents[1] / "test.dem")
demo.load("shots", "kills")

print("demo.shots columns:")
print(demo.shots.columns)
print("\ndemo.shots first 3 rows:")
print(demo.shots.head(3))

ticks = demo.shots.get_column("tick").head(5).to_list()
print("\nTicks selected for snapshots:")
print(ticks)

snapshots = demo.snapshots(ticks=ticks)
print("\ndemo.snapshots columns:")
print(snapshots.columns)
print("\ndemo.snapshots first 3 rows:")
print(snapshots.head(3))

print("\ndemo.kills columns:")
print(demo.kills.columns)
print("\ndemo.kills first 3 rows:")
print(demo.kills.head(3))
