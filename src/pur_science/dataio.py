from __future__ import annotations

import base64
import hashlib
import lzma
from pathlib import Path

EXPECTED_CANDIDATE_SHA256 = "d8623116c6a2f60c9e022e52eeb6540573dd9434b5e507c79701abb55635bcd9"


def _read_encoded_snapshot(out: Path, encoded_path: str | Path | None) -> str:
    """Read either one XZ/base64 snapshot or the versioned multipart snapshot."""
    if encoded_path is not None:
        encoded = Path(encoded_path)
        if not encoded.is_file():
            raise FileNotFoundError(f"Compressed source does not exist: {encoded}")
        return encoded.read_text(encoding="ascii").strip()

    single = out.with_suffix(out.suffix + ".xz.b64")
    if single.is_file():
        return single.read_text(encoding="ascii").strip()

    parts_dir = out.parent / "candidates_full_parts"
    parts = sorted(parts_dir.glob("part_*.b64"))
    if not parts:
        raise FileNotFoundError(
            f"Neither {out}, {single}, nor multipart snapshot {parts_dir}/part_*.b64 exists"
        )
    return "".join(p.read_text(encoding="ascii").strip() for p in parts)


def materialize_pur_sim_v1(
    output_path: str | Path,
    encoded_path: str | Path | None = None,
) -> Path:
    """Materialize the frozen 928-row PUR_SIM_V1 response table losslessly.

    The repository stores the table as XZ-compressed bytes encoded in base64 text. The
    snapshot may be one file or a sorted set of `candidates_full_parts/part_*.b64` files.
    Reconstruction is verified against the frozen SHA256 before the CSV is returned.
    Existing CSVs are also hash-checked to prevent silent drift.
    """
    out = Path(output_path)

    if out.is_file():
        digest = hashlib.sha256(out.read_bytes()).hexdigest()
        if digest != EXPECTED_CANDIDATE_SHA256:
            raise ValueError(
                f"Existing candidate table hash mismatch: {digest}; expected {EXPECTED_CANDIDATE_SHA256}"
            )
        return out

    encoded = _read_encoded_snapshot(out, encoded_path)
    raw = lzma.decompress(base64.b64decode(encoded))
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_CANDIDATE_SHA256:
        raise ValueError(
            f"Reconstructed candidate table hash mismatch: {digest}; expected {EXPECTED_CANDIDATE_SHA256}"
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(raw)
    return out
