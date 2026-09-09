from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

# Any path component matching this pattern is refused by the runtime reader, whatever the root.
FORBIDDEN_PATH_PATTERN = re.compile(r"(gold|evaluator|mapping|oracle|prospective_validation|results)", re.IGNORECASE)
ALLOWED_BUNDLE_FILES = ("candidates.csv", "benchmark_config.json", "task.json", "manifest.json", "provenance.json")


class AccessDenied(PermissionError):
    pass


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True)
class BundleReader:
    """The only file reader the Agent runtime is allowed to use.

    It is rooted at the blind bundle directory. It refuses absolute paths, parent traversal,
    any path outside the root, any path component that names gold/evaluator/mapping/oracle
    material, and any file not on the bundle whitelist.
    """

    root: Path

    def __post_init__(self) -> None:
        object.__setattr__(self, "root", Path(self.root).resolve())
        if not self.root.is_dir():
            raise FileNotFoundError(f"Blind bundle directory not found: {self.root}")
        if FORBIDDEN_PATH_PATTERN.search(self.root.name):
            raise AccessDenied(f"Refusing to root the Agent reader at {self.root}")

    def resolve(self, relative: str | Path) -> Path:
        rel = Path(relative)
        if rel.is_absolute() or ".." in rel.parts:
            raise AccessDenied(f"Absolute or parent-relative paths are not allowed: {relative}")
        for part in rel.parts:
            if FORBIDDEN_PATH_PATTERN.search(part):
                raise AccessDenied(f"Path component {part!r} is evaluator-only")
        target = (self.root / rel).resolve()
        if self.root not in target.parents and target != self.root:
            raise AccessDenied(f"Path escapes the blind bundle: {relative}")
        if target.name not in ALLOWED_BUNDLE_FILES:
            raise AccessDenied(f"{target.name} is not an admissible bundle file")
        if not target.is_file():
            raise FileNotFoundError(target)
        return target

    def read_text(self, relative: str | Path) -> str:
        return self.resolve(relative).read_text(encoding="utf-8")

    def read_json(self, relative: str | Path) -> dict[str, Any]:
        return json.loads(self.read_text(relative))

    def read_csv(self, relative: str | Path) -> pd.DataFrame:
        return pd.read_csv(self.resolve(relative))

    def file_hash(self, relative: str | Path) -> str:
        return sha256_file(self.resolve(relative))


@dataclass(frozen=True)
class BlindBundle:
    reader: BundleReader
    candidates: pd.DataFrame
    config: dict[str, Any]
    task: dict[str, Any]
    manifest: dict[str, Any]
    hashes: dict[str, str]

    @classmethod
    def load(cls, blind_dir: str | Path) -> "BlindBundle":
        reader = BundleReader(Path(blind_dir))
        candidates = reader.read_csv("candidates.csv")
        config = reader.read_json("benchmark_config.json")
        task = reader.read_json("task.json")
        try:
            manifest = reader.read_json("manifest.json")
        except FileNotFoundError:
            manifest = {}
        hashes = {name: reader.file_hash(name) for name in ("candidates.csv", "benchmark_config.json", "task.json")}
        return cls(reader, candidates, config, task, manifest, hashes)
