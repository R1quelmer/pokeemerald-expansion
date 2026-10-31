#!/usr/bin/env python3
"""Create a BPS patch for the FireRed hack without distributing a ROM.

Usage:
    python3 make_patch.py /path/to/clean_firered.gba

The source ROM must be Pokémon FireRed (USA) v1.0 / Rev 0.
The script builds pokefirered.gba if needed, then writes:
    build/patches/pokefirered-hack.bps
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import struct
import subprocess
import sys
import zlib

EXPECTED_FIRERED_SHA1 = "41cb23d8dccc8ebd7c649cd8fbb58eeace6e2fdc"
TARGET_ROM = Path("pokefirered.gba")
PATCH_PATH = Path("build/patches/pokefirered-hack.bps")


def sha1_file(path: Path) -> str:
    h = hashlib.sha1()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def encode_bps_number(value: int) -> bytes:
    """Encode an integer using BPS's variable-length number format."""
    if value < 0:
        raise ValueError("BPS numbers cannot be negative")

    out = bytearray()
    while True:
        x = value & 0x7F
        value >>= 7
        if value == 0:
            out.append(x | 0x80)
            return bytes(out)
        out.append(x)
        value -= 1


def build_bps_patch(source: bytes, target: bytes) -> bytes:
    """Build a standards-compliant BPS1 patch using SourceRead/TargetRead runs."""
    patch = bytearray(b"BPS1")
    patch += encode_bps_number(len(source))
    patch += encode_bps_number(len(target))
    patch += encode_bps_number(0)  # metadata length

    pos = 0
    source_limit = len(source)
    target_limit = len(target)

    while pos < target_limit:
        # SourceRead: bytes already match at the same offset.
        if pos < source_limit and target[pos] == source[pos]:
            end = pos + 1
            limit = min(source_limit, target_limit)
            while end < limit and target[end] == source[end]:
                end += 1
            length = end - pos
            patch += encode_bps_number(((length - 1) << 2) | 0)
            pos = end
            continue

        # TargetRead: embed only the bytes that differ from the source at this offset.
        end = pos + 1
        while end < target_limit:
            if end < source_limit and target[end] == source[end]:
                break
            end += 1
        length = end - pos
        patch += encode_bps_number(((length - 1) << 2) | 1)
        patch += target[pos:end]
        pos = end

    patch += struct.pack("<I", zlib.crc32(source) & 0xFFFFFFFF)
    patch += struct.pack("<I", zlib.crc32(target) & 0xFFFFFFFF)
    patch += struct.pack("<I", zlib.crc32(patch) & 0xFFFFFFFF)
    return bytes(patch)


def ensure_target_rom() -> None:
    if TARGET_ROM.exists():
        return

    jobs = max(1, os.cpu_count() or 1)
    print(f"pokefirered.gba não existe; compilando com make firered -j{jobs}...")
    subprocess.run(["make", "firered", f"-j{jobs}"], check=True)

    if not TARGET_ROM.exists():
        raise RuntimeError("A compilação terminou, mas pokefirered.gba não foi criado.")


def main() -> int:
    if len(sys.argv) != 2:
        print("Uso: python3 make_patch.py /caminho/para/firered.gba")
        return 2

    base_rom = Path(sys.argv[1]).expanduser().resolve()
    if not base_rom.is_file():
        print(f"ROM-base não encontrada: {base_rom}")
        return 2

    print("Verificando a ROM-base...")
    digest = sha1_file(base_rom)
    if digest.lower() != EXPECTED_FIRERED_SHA1:
        print("ROM-base incompatível.")
        print("Este projeto espera Pokémon FireRed (USA) v1.0 / Rev 0.")
        print(f"SHA-1 esperado: {EXPECTED_FIRERED_SHA1}")
        print(f"SHA-1 recebido: {digest}")
        return 3

    ensure_target_rom()

    print("Gerando patch BPS...")
    source = base_rom.read_bytes()
    target = TARGET_ROM.read_bytes()
    patch = build_bps_patch(source, target)

    PATCH_PATH.parent.mkdir(parents=True, exist_ok=True)
    PATCH_PATH.write_bytes(patch)

    print("Pronto.")
    print(f"Patch: {PATCH_PATH}")
    print(f"Tamanho: {PATCH_PATH.stat().st_size / (1024 * 1024):.2f} MiB")
    print("A ROM-base não foi copiada nem adicionada ao repositório.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
