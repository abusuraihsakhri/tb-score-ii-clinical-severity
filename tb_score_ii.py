#!/usr/bin/env python3
"""Published TBscore II (Rudolf et al., 2013): a descriptive 0–8 point score.

For adult pulmonary-TB treatment monitoring and research, not diagnosis or an
automated treatment recommendation. DOI: 10.3109/00365548.2013.826876.
"""
import argparse
import csv
import json
import math
import re
import sys
import tempfile
from pathlib import Path

FIELDS = ("cough", "dyspnea", "chest_pain", "anemia", "bmi", "muac_mm")
SYMPTOMS = FIELDS[:4]
OUTPUT_FIELDS = (*FIELDS, "score", "severity_class")


def _yes_no(value, field):
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)
    if isinstance(value, str):
        v = value.strip().lower()
        if v in ("yes", "true", "1"):
            return True
        if v in ("no", "false", "0"):
            return False
    raise ValueError(f"{field}: expected yes/no or 1/0")


def _positive_float(value, field, upper):
    if isinstance(value, bool):
        raise ValueError(f"{field}: expected a numeric measurement")
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field}: expected a numeric measurement") from exc
    if not math.isfinite(number) or not 0 < number <= upper:
        raise ValueError(f"{field}: must be finite and within (0, {upper}]")
    return number


def calculate_metrics(*, cough, dyspnea, chest_pain, anemia, bmi, muac_mm):
    """Compute TBscore II. BMI is kg/m²; MUAC is millimetres.

    Four yes/no findings contribute one point each. BMI <18/<16 and
    MUAC <220/<200 contribute one additional point per threshold, up to 8.
    Anaemia is the clinical finding (e.g. pale conjunctivae), not a
    haemoglobin threshold determined by this program.
    """
    values = {"cough": cough, "dyspnea": dyspnea, "chest_pain": chest_pain, "anemia": anemia}
    flags = {name: _yes_no(values[name], name) for name in SYMPTOMS}
    bmi_value = _positive_float(bmi, "bmi", 100)
    muac_value = _positive_float(muac_mm, "muac_mm", 1000)
    components = {
        **{name: int(value) for name, value in flags.items()},
        "bmi_below_18": int(bmi_value < 18),
        "bmi_below_16": int(bmi_value < 16),
        "muac_below_220_mm": int(muac_value < 220),
        "muac_below_200_mm": int(muac_value < 200),
    }
    score = sum(components.values())
    severity = "I" if score < 2 else "II" if score < 4 else "III" if score < 8 else "IV"
    return {
        "tool": "tb-score-ii-clinical-severity",
        "score": score,
        "severity_class": severity,
        "classification": f"SC-{severity}",
        "components": components,
        "inputs_evaluated": len(FIELDS),
        "clinical_recommendation": "Interpret with the full clinical assessment; not a diagnosis or treatment directive.",
    }


def monitor_change(baseline_score, followup_score):
    """Describe change to a follow-up visit; not a calibrated individual risk."""
    if any(isinstance(x, bool) or not isinstance(x, int) or not 0 <= x <= 8
           for x in (baseline_score, followup_score)):
        raise ValueError("Both scores must be integers from 0 to 8")
    if baseline_score == 0:
        return {"point_reduction": -followup_score, "percent_reduction": None,
                "decreased_at_least_25_percent": None}
    reduction = baseline_score - followup_score
    return {"point_reduction": reduction,
            "percent_reduction": round(100 * reduction / baseline_score, 2),
            "decreased_at_least_25_percent": reduction / baseline_score >= 0.25}


def _safe_resolve_path(value):
    """Restrict CLI files to the current workspace or OS temporary directory."""
    path = Path(value).resolve()
    roots = (Path.cwd().resolve(), Path(tempfile.gettempdir()).resolve())
    if not any(path.is_relative_to(root) for root in roots):
        raise ValueError("File path is outside the current workspace and temporary directory")
    return path


def process_batch(input_csv, output_csv):
    input_path = _safe_resolve_path(input_csv)
    output_path = _safe_resolve_path(output_csv)
    if input_path == output_path:
        raise ValueError("Input and output paths must differ")
    if not input_path.is_file():
        raise FileNotFoundError(f"Input file not found: {input_csv}")

    count = 0
    with input_path.open("r", encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        names = reader.fieldnames or []
        if len(set(names)) != len(names) or set(names) != set(FIELDS):
            raise ValueError("CSV headers must contain exactly: " + ", ".join(FIELDS))
        # Write to a temporary file first so validation never leaves partial output.
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="",
                                         dir=output_path.parent, suffix=".csv",
                                         prefix=".tbscore-", delete=False) as temp:
            staged = Path(temp.name)
            writer = csv.DictWriter(temp, fieldnames=OUTPUT_FIELDS)
            writer.writeheader()
            try:
                for line, row in enumerate(reader, start=2):
                    if None in row or any(value is None for value in row.values()):
                        raise ValueError(f"CSV line {line}: unexpected number of columns")
                    try:
                        result = calculate_metrics(**row)
                    except ValueError as exc:
                        raise ValueError(f"CSV line {line}: {exc}") from exc
                    clean = {name: int(_yes_no(row[name], name)) for name in SYMPTOMS}
                    clean["bmi"] = _positive_float(row["bmi"], "bmi", 100)
                    clean["muac_mm"] = _positive_float(row["muac_mm"], "muac_mm", 1000)
                    writer.writerow({**clean, "score": result["score"],
                                     "severity_class": result["severity_class"]})
                    count += 1
            except BaseException:
                staged.unlink(missing_ok=True)
                raise
    staged.replace(output_path)
    return count


def main(argv=None):
    parser = argparse.ArgumentParser(description="Published eight-point TBscore II calculator")
    commands = parser.add_subparsers(dest="command", required=True)
    single = commands.add_parser("single", help="Calculate score for one anonymized assessment")
    for name in SYMPTOMS:
        single.add_argument("--" + name.replace("_", "-"), choices=("yes", "no"),
                            required=True)
    single.add_argument("--bmi", type=float, required=True, help="Body mass index (kg/m²)")
    single.add_argument("--muac-mm", type=float, required=True, help="Mid-upper arm circumference (mm)")
    batch = commands.add_parser("batch", help="Calculate scores from a six-column CSV")
    batch.add_argument("-i", "--input", required=True)
    batch.add_argument("-o", "--output", default="results.csv")
    args = parser.parse_args(argv)
    try:
        if args.command == "single":
            values = vars(args)
            print(json.dumps(calculate_metrics(**{name: values[name] for name in FIELDS}), indent=2))
        else:
            n = process_batch(args.input, args.output)
            print(f"Processed {n} records -> {args.output}")
        return 0
    except (ValueError, FileNotFoundError, OSError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
