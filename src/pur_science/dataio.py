from __future__ import annotations

import base64
import hashlib
import lzma
from pathlib import Path

EXPECTED_CANDIDATE_SHA256 = "d8623116c6a2f60c9e022e52eeb6540573dd9434b5e507c79701abb55635bcd9"


def _encoded_text(encoded: Path) -> str:
    """Read a single base64 snapshot or concatenate deterministic `.partNN` shards."""
    if encoded.is_file():
        return encoded.read_text(encoding="ascii").strip()
    parts = sorted(encoded.parent.glob(encoded.name + ".part*"))
    if not parts:
        raise FileNotFoundError(
            f"Neither compressed source {encoded} nor multipart shards {encoded.name}.part* exist"
        )
    expected_names = [f"{encoded.name}.part{i:02d}" for i in range(len(parts))]
    actual_names = [p.name for p in parts]
    if actual_names != expected_names:
        raise ValueError(
            "Frozen candidate snapshot parts are incomplete or non-contiguous: "
            f"found {actual_names}, expected {expected_names}"
        )
    return "".join(p.read_text(encoding="ascii").strip() for p in parts)


def materialize_pur_sim_v1(
    output_path: str | Path,
    encoded_path: str | Path | None = None,
) -> Path:
    """Materialize the frozen 928-row PUR_SIM_V1 response table losslessly.

    The repository stores the table as XZ-compressed bytes encoded in base64. The encoded
    snapshot may be a single `.xz.b64` file or contiguous `.part00`, `.part01`, ... shards.
    Reconstruction is verified against the frozen SHA256 before the CSV is returned.
    Existing CSVs are also hash-checked to prevent silent drift.
    """
    out = Path(output_path)
    encoded = Path(encoded_path) if encoded_path else out.with_suffix(out.suffix + ".xz.b64")

    if out.is_file():
        digest = hashlib.sha256(out.read_bytes()).hexdigest()
        if digest != EXPECTED_CANDIDATE_SHA256:
            raise ValueError(
                f"Existing candidate table hash mismatch: {digest}; expected {EXPECTED_CANDIDATE_SHA256}"
            )
        return out

    raw = lzma.decompress(base64.b64decode(_encoded_text(encoded)))
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_CANDIDATE_SHA256:
        raise ValueError(
            f"Reconstructed candidate table hash mismatch: {digest}; expected {EXPECTED_CANDIDATE_SHA256}"
        )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(raw)
    return out
