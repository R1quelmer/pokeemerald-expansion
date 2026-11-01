#!/usr/bin/env python3
"""Check actual battle transitions recorded by the mGBA capture cartridge."""
import re
import sys
from pathlib import Path

records = []
for line in Path(sys.argv[1]).read_text().splitlines():
    values = dict(re.findall(r"(\w+)=([0-9a-f]+)", line))
    if "state0" not in values:
        continue
    record = {key: int(value, 16 if key.startswith("state") else 10)
              for key, value in values.items() if key in ("scene", "frame", "age") or key.startswith("state")}
    records.append(record)


def displayed(record, battler):
    word = record[f"state{battler}"]
    count = word >> 24
    return tuple((word >> (8 * index)) & 255 for index in range(count))


def require(scene, battler, types):
    matches = [row for row in records if row["scene"] == scene and displayed(row, battler) == types]
    assert matches, f"scene {scene}, battler {battler}: never displayed {types}"
    return matches


for row in records:
    for battler in range(4):
        types = displayed(row, battler)
        assert len(types) <= 3 and len(types) == len(set(types)), (row, types)

require(51, 0, (13,))                       # Treecko: one Grass badge.
require(51, 1, (13, 4))                     # Opponent Venusaur: Grass/Poison.
require(52, 0, (11, 3))                     # Charizard: Fire/Flying.
require(52, 1, (8, 4))                      # Gengar: Ghost/Poison.
for scene in (53, 54):
    for battler in range(4):
        assert any(row["scene"] == scene and displayed(row, battler) for row in records), (scene, battler)

before = require(55, 0, (11, 3))
after = require(55, 0, (11, 17))             # Real Charizard X Mega evolution.
assert min(row["age"] for row in before) < min(row["age"] for row in after)
assert any(row["state8"] for row in after), "Mega gimmick never activated"
require(56, 1, (13, 4))
require(56, 1, (12,))                       # Soak removes both old badges.
require(57, 0, (1,))
require(57, 0, (8,))                        # Protean: Normal -> Ghost.
require(58, 0, (13, 4))
water = require(58, 0, (12,))               # Tera Water is the defensive type.
assert any(row["state8"] for row in water), "Tera gimmick never activated"
stellar = require(59, 0, (13, 4))
assert any(row["state8"] for row in stellar), "Stellar Tera never activated"
require(60, 1, (11, 3, 13))                 # Forest's Curse adds a third type.
require(61, 0, (11,))                       # Roost temporarily removes Flying.
print("Type badges: mono/dual, four battlers, Mega, Soak, Protean, Tera, Stellar, third type and Roost passed.")
