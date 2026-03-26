#!/usr/bin/env python3
"""Validate and upload a corasdiagram release archive to CTAN."""

from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from pathlib import Path
from urllib import error, request

from versioning import read_repo_version


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_METADATA = REPO_ROOT / "ctan" / "metadata.json"
VALIDATE_URL = "https://www.ctan.org/submit/validate"
UPLOAD_URL = "https://www.ctan.org/submit/upload"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate and upload a CTAN release archive for corasdiagram."
    )
    parser.add_argument(
        "--metadata",
        type=Path,
        default=DEFAULT_METADATA,
        help="Path to the committed CTAN metadata JSON file.",
    )
    parser.add_argument(
        "--archive",
        type=Path,
        required=True,
        help="Path to the CTAN-ready release archive.",
    )
    parser.add_argument(
        "--uploader",
        default=os.environ.get("CTAN_UPLOADER_NAME", ""),
        help="CTAN uploader name. Defaults to CTAN_UPLOADER_NAME.",
    )
    parser.add_argument(
        "--email",
        default=os.environ.get("CTAN_UPLOADER_EMAIL", ""),
        help="CTAN uploader email. Defaults to CTAN_UPLOADER_EMAIL.",
    )
    parser.add_argument(
        "--announcement",
        default=os.environ.get("CTAN_ANNOUNCEMENT", ""),
        help="Optional CTAN announcement text.",
    )
    parser.add_argument(
        "--note",
        default=os.environ.get("CTAN_NOTE", ""),
        help="Optional note to CTAN upload managers.",
    )
    parser.add_argument(
        "--update",
        choices=("true", "false"),
        help="Override the metadata file's update=true/false value.",
    )
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Only run the CTAN validation request, do not upload.",
    )
    return parser.parse_args()


def ensure_path(path: Path) -> Path:
    resolved = path.expanduser().resolve()
    if not resolved.exists():
        raise FileNotFoundError(resolved)
    return resolved


def normalize_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        result: list[str] = []
        for item in value:
            if not isinstance(item, str):
                raise TypeError(f"Expected string list value, got {item!r}")
            result.append(item)
        return result
    raise TypeError(f"Expected string or list of strings, got {value!r}")


def load_metadata(path: Path) -> dict[str, object]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise TypeError(f"Metadata root must be a JSON object: {path}")
    return data


def build_fields(
    metadata: dict[str, object],
    *,
    version: str,
    uploader: str,
    email: str,
    announcement: str,
    note: str,
    update_override: str | None,
) -> list[tuple[str, str]]:
    required_string_keys = ("pkg", "summary", "description", "ctanPath")
    for key in required_string_keys:
        value = metadata.get(key)
        if not isinstance(value, str) or not value.strip():
            raise RuntimeError(f"CTAN metadata field {key!r} must be a non-empty string.")

    if not uploader.strip():
        raise RuntimeError(
            "Missing CTAN uploader name. Set CTAN_UPLOADER_NAME or pass --uploader."
        )
    if not email.strip():
        raise RuntimeError(
            "Missing CTAN uploader email. Set CTAN_UPLOADER_EMAIL or pass --email."
        )

    fields: list[tuple[str, str]] = [
        ("pkg", str(metadata["pkg"])),
        ("summary", str(metadata["summary"])),
        ("description", str(metadata["description"])),
        ("ctanPath", str(metadata["ctanPath"])),
        ("uploader", uploader.strip()),
        ("email", email.strip()),
        ("version", version),
    ]

    update_value = update_override
    if update_value is None:
        update_flag = metadata.get("update", True)
        if not isinstance(update_flag, bool):
            raise RuntimeError("CTAN metadata field 'update' must be a boolean.")
        update_value = "true" if update_flag else "false"
    fields.append(("update", update_value))

    for author in normalize_list(metadata.get("author")):
        fields.append(("author", author))
    for license_name in normalize_list(metadata.get("license")):
        fields.append(("license", license_name))
    for topic in normalize_list(metadata.get("topic")):
        fields.append(("topic", topic))

    optional_keys = (
        "home",
        "repository",
        "development",
        "bugtracker",
        "support",
    )
    for key in optional_keys:
        value = metadata.get(key)
        if isinstance(value, str) and value.strip():
            fields.append((key, value.strip()))

    if announcement.strip():
        fields.append(("announcement", announcement.strip()))

    note_value = note.strip()
    if not note_value and isinstance(metadata.get("note"), str):
        note_value = str(metadata["note"]).strip()
    if note_value:
        fields.append(("note", note_value))

    return fields


def run_ctan_request(
    endpoint: str,
    fields: list[tuple[str, str]],
    archive: Path,
) -> tuple[int, object]:
    boundary = f"----corasdiagram-{uuid.uuid4().hex}"
    body = bytearray()

    for key, value in fields:
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            f'Content-Disposition: form-data; name="{key}"\r\n\r\n'.encode("utf-8")
        )
        body.extend(value.encode("utf-8"))
        body.extend(b"\r\n")

    body.extend(f"--{boundary}\r\n".encode("utf-8"))
    body.extend(
        (
            'Content-Disposition: form-data; name="file"; filename="'
            f'{archive.name}"\r\n'
        ).encode("utf-8")
    )
    body.extend(b"Content-Type: application/zip\r\n\r\n")
    body.extend(archive.read_bytes())
    body.extend(b"\r\n")
    body.extend(f"--{boundary}--\r\n".encode("utf-8"))

    http_request = request.Request(
        endpoint,
        data=bytes(body),
        headers={
            "Accept": "application/json",
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        },
        method="POST",
    )

    try:
        with request.urlopen(http_request) as response:
            http_code = response.getcode()
            body_text = response.read().decode("utf-8", errors="replace")
    except error.HTTPError as exc:
        http_code = exc.code
        body_text = exc.read().decode("utf-8", errors="replace")
    except error.URLError as exc:
        raise RuntimeError(f"CTAN request failed before parsing a response: {exc}") from exc

    try:
        parsed = json.loads(body_text)
    except json.JSONDecodeError:
        parsed = body_text.strip()

    return http_code, parsed


def format_messages(payload: object) -> str:
    if not isinstance(payload, list):
        return str(payload)

    lines: list[str] = []
    for item in payload:
        if isinstance(item, list) and item:
            head = str(item[0])
            tail = " | ".join(str(part) for part in item[1:])
            lines.append(f"{head}: {tail}" if tail else head)
        else:
            lines.append(str(item))
    return "\n".join(lines)


def payload_has_errors(payload: object) -> bool:
    if not isinstance(payload, list):
        return False
    return any(isinstance(item, list) and item and item[0] == "ERROR" for item in payload)


def upload_succeeded(payload: object) -> bool:
    if not isinstance(payload, list):
        return False
    return any(
        isinstance(item, list)
        and len(item) >= 2
        and item[0] == "INFO"
        and item[1] == "Upload succeeded"
        for item in payload
    )


def main() -> int:
    args = parse_args()
    metadata_path = ensure_path(args.metadata)
    archive_path = ensure_path(args.archive)

    metadata = load_metadata(metadata_path)
    version = read_repo_version(REPO_ROOT)
    fields = build_fields(
        metadata,
        version=version,
        uploader=args.uploader,
        email=args.email,
        announcement=args.announcement,
        note=args.note,
        update_override=args.update,
    )

    http_code, validate_payload = run_ctan_request(VALIDATE_URL, fields, archive_path)
    print("CTAN validate response:")
    print(format_messages(validate_payload))
    if http_code != 200 or payload_has_errors(validate_payload):
        raise RuntimeError(f"CTAN validation failed with HTTP {http_code}.")

    if args.validate_only:
        return 0

    http_code, upload_payload = run_ctan_request(UPLOAD_URL, fields, archive_path)
    print("\nCTAN upload response:")
    print(format_messages(upload_payload))
    if http_code != 200 or payload_has_errors(upload_payload) or not upload_succeeded(upload_payload):
        raise RuntimeError(f"CTAN upload failed with HTTP {http_code}.")

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:  # pragma: no cover - surfaced to CI and shell users
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(1)
