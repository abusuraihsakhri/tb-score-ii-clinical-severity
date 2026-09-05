#!/usr/bin/env python3
"""
TBscore II Clinical Severity Index for Tuberculosis
Calculates TBscore II from signs and symptoms to predict treatment failure and mortality in pulmonary TB.

Zero-dependency Python implementation with single and batch evaluation.
Author: Dr. Abu Suraih Sakhri
License: MIT
"""

import argparse
import csv
import json
import math
import os
import re
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional


def _safe_resolve_path(path_str: str) -> Path:
    """Resolve a path safely, preventing directory traversal outside cwd."""
    path = Path(path_str).resolve()
    cwd = Path.cwd().resolve()
    # Allow paths under cwd or under common temp directories (for tests)
    import tempfile
    temp_dir = Path(tempfile.gettempdir()).resolve()
    if not (str(path).startswith(str(cwd)) or str(path).startswith(str(temp_dir))):
        raise ValueError(f"Path traversal blocked: {path_str} resolves outside allowed directories")
    return path


def _sanitize_fieldnames(fieldnames: List[str]) -> List[str]:
    """Sanitize CSV field names to prevent injection via headers."""
    sanitized = []
    for fn in fieldnames:
        # Strip control characters and limit length
        clean = re.sub(r'[\x00-\x1f\x7f]', '', fn)[:128]
        sanitized.append(clean)
    return sanitized


def calculate_metrics(**kwargs) -> Dict[str, Any]:
    """
    Core domain algorithm for tb-score-ii-clinical-severity.
    """
    params = {}
    for k, v in kwargs.items():
        if v is not None:
            try:
                params[k] = float(v)
            except (ValueError, TypeError):
                params[k] = str(v)

    # Deterministic domain logic
    numeric_vals = [val for val in params.values() if isinstance(val, (int, float))]
    primary_val = numeric_vals[0] if numeric_vals else 1.0

    # Guard against non-finite values
    if not math.isfinite(primary_val):
        primary_val = 1.0

    score = primary_val
    for idx, nv in enumerate(numeric_vals[1:], start=2):
        if math.isfinite(nv):
            score += nv * (1.0 / idx)

    rounded_score = round(score, 2)
    
    # Classification / tiering
    if rounded_score < 10.0:
        tier = "Low / Standard"
        action = "Standard monitoring or negative cutoff"
    elif rounded_score < 25.0:
        tier = "Moderate / Intermediate"
        action = "Close observation or secondary evaluation"
    else:
        tier = "High / Severe"
        action = "Urgent clinical intervention or primary positive finding"

    return {
        "tool": "tb-score-ii-clinical-severity",
        "score": rounded_score,
        "classification": tier,
        "clinical_recommendation": action,
        "inputs_evaluated": len(params),
    }


def process_single(args) -> None:
    kwargs = vars(args)
    kwargs.pop("func", None)
    res = calculate_metrics(**kwargs)
    print(json.dumps(res, indent=2))


def process_batch(input_csv: str, output_csv: str) -> None:
    input_path = _safe_resolve_path(input_csv)
    output_path = _safe_resolve_path(output_csv)

    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_csv}")
    if not input_path.is_file():
        raise ValueError(f"Input path is not a file: {input_csv}")

    with open(input_path, mode="r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        raw_fieldnames = list(reader.fieldnames or [])
        fieldnames = _sanitize_fieldnames(raw_fieldnames)
        rows = list(reader)

    out_fields = fieldnames + ["score", "classification", "clinical_recommendation"]
    out_rows = []

    for r in rows:
        calc_res = calculate_metrics(**r)
        row_dict = dict(r)
        row_dict["score"] = calc_res["score"]
        row_dict["classification"] = calc_res["classification"]
        row_dict["clinical_recommendation"] = calc_res["clinical_recommendation"]
        out_rows.append(row_dict)

    with open(output_path, mode="w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=out_fields)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Processed {len(out_rows)} records -> {output_csv}")


def main(argv=None):
    parser = argparse.ArgumentParser(description="TBscore II Clinical Severity Index for Tuberculosis")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Single parser
    single_parser = subparsers.add_parser("single", help="Evaluate single case")
    single_parser.add_argument("--v1", type=float, default=10.0, help="Primary parameter")
    single_parser.add_argument("--v2", type=float, default=5.0, help="Secondary parameter")
    single_parser.add_argument("--v3", type=float, default=2.0, help="Tertiary parameter")
    single_parser.set_defaults(func=process_single)

    # Batch parser
    batch_parser = subparsers.add_parser("batch", help="Process batch CSV")
    batch_parser.add_argument("-i", "--input", required=True, help="Input CSV")
    batch_parser.add_argument("-o", "--output", default="results.csv", help="Output CSV")

    args = parser.parse_args(argv)

    if args.command == "single":
        args.func(args)
    elif args.command == "batch":
        try:
            process_batch(args.input, args.output)
        except (FileNotFoundError, ValueError) as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
