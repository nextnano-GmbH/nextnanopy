"""
Verify the bundled demo input matches the one shipped in the portable build.

The repo keeps a copy of nextnano's DoubleQuantumWell demo under
``templates/input files/`` and runs it as the CI smoke test. This checks that
copy is still identical to the demo shipped in the extracted portable build, so
the smoke test always exercises the canonical example rather than a drifted
fork. The comparison ignores line-ending and BOM encoding (``read_text`` folds
newlines; ``utf-8-sig`` drops a leading BOM) so it does not fail on CRLF/LF
differences introduced at checkout.

**Environment**

NEXTNANO_PORTABLE_DIR
    Directory the portable build was extracted into (default: ``nextnano``).
"""

import os
import sys
from pathlib import Path

repo_root = Path(__file__).resolve().parents[1]
fixture = repo_root / "templates" / "input files" / "DoubleQuantumWell_6nm_demo.nnp"

if not fixture.is_file():
    sys.exit(f"bundled fixture not found: {fixture}")

# The install unpacks into a release-date folder, so locate the shipped demo by
# name rather than hardcoding the path.
base = Path(os.environ.get("NEXTNANO_PORTABLE_DIR", "nextnano")).resolve()
matches = sorted(base.glob(f"**/nextnano++/examples/**/{fixture.name}"))
if not matches:
    near = sorted(base.glob("**/nextnano++/examples/**/DoubleQuantumWell*.nnp"))
    hint = "\n".join(f"  found instead: {p}" for p in near) or (
        "  (no DoubleQuantumWell*.nnp under nextnano++/examples at all)"
    )
    sys.exit(f"no {fixture.name!r} under {base}\\**\\nextnano++\\examples\n{hint}")
shipped = matches[-1]


def normalized(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


fixture_text = normalized(fixture)
shipped_text = normalized(shipped)

if fixture_text == shipped_text:
    print(f"OK: {fixture.name} matches the shipped demo")
    print(f"  fixture: {fixture}")
    print(f"  shipped: {shipped}")
    sys.exit(0)

# Point at the first differing line so a drift is easy to spot in the CI log.
fixture_lines = fixture_text.splitlines()
shipped_lines = shipped_text.splitlines()
for i, (a, b) in enumerate(zip(fixture_lines, shipped_lines, strict=False), start=1):
    if a != b:
        sys.exit(
            f"{fixture.name} differs from the shipped demo at line {i}:\n"
            f"  fixture ({fixture}): {a!r}\n"
            f"  shipped ({shipped}): {b!r}"
        )
sys.exit(
    f"{fixture.name} differs from the shipped demo in length: "
    f"fixture has {len(fixture_lines)} lines, shipped has {len(shipped_lines)}"
)
