#!/usr/bin/env python3
"""Customize the FireRed rival's starter line without changing other trainers."""

import re
import sys

SPECIES_MAP = {
    "Bulbasaur": "Treecko",
    "Ivysaur": "Grovyle",
    "Venusaur": "Sceptile",
    "Squirtle": "Totodile",
    "Wartortle": "Croconaw",
    "Blastoise": "Feraligatr",
    "Charmander": "Fennekin",
    "Charmeleon": "Braixen",
    "Charizard": "Delphox",
}

HEADER_RE = re.compile(r"^===\s+([A-Z0-9_]+)\s+===\s*$")


def is_target_trainer(name: str) -> bool:
    return (
        name.startswith("TRAINER_RIVAL_")
        or name.startswith("TRAINER_CHAMPION_FIRST_")
        or name.startswith("TRAINER_CHAMPION_REMATCH_")
    )


def replace_species(line: str) -> str:
    for old, new in SPECIES_MAP.items():
        line = re.sub(rf"\b{old}\b", new, line)
        line = re.sub(rf"\bSPECIES_{old.upper()}\b", f"SPECIES_{new.upper()}", line)
    return line


def main() -> None:
    target = False
    output = []

    for line in sys.stdin:
        header = HEADER_RE.match(line)
        if header:
            target = is_target_trainer(header.group(1))

        if target:
            line = replace_species(line)

        output.append(line)

    sys.stdout.write("".join(output))


if __name__ == "__main__":
    main()
