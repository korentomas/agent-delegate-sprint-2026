"""Package the standalone environment table for any static host. No dependencies."""
from pathlib import Path
from shutil import copyfile

ROOT = Path(__file__).resolve().parents[1]
source = ROOT / "web" / "environment-cases" / "index.html"
destination = ROOT / "dist" / "environment-cases" / "index.html"
destination.parent.mkdir(parents=True, exist_ok=True)
copyfile(source, destination)
print(f"Built {destination} ({destination.stat().st_size:,} bytes)")
