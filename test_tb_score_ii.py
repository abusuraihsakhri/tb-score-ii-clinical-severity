"""Regression tests for the published TBscore II definition (Rudolf 2013)."""
import csv
import json
import pytest

from tb_score_ii import calculate_metrics, monitor_change, process_batch, main

BASE = dict(cough="no", dyspnea="no", chest_pain="no", anemia="no",
            bmi=18, muac_mm=220)


def score(**overrides):
    return calculate_metrics(**{**BASE, **overrides})


@pytest.mark.parametrize(("value", "expected"), [
    (15.99, 2), (16, 1), (17.99, 1), (18, 0), (20, 0)
])
def test_bmi_boundaries(value, expected):
    assert score(bmi=value)["score"] == expected


@pytest.mark.parametrize(("value", "expected"), [
    (199.99, 2), (200, 1), (219.99, 1), (220, 0), (230, 0)
])
def test_muac_boundaries(value, expected):
    assert score(muac_mm=value)["score"] == expected


@pytest.mark.parametrize(("symptoms", "expected"), [
    ([], 0), (["cough"], 1), (["cough", "anemia"], 2),
    (["cough", "dyspnea", "anemia"], 3),
    (["cough", "dyspnea", "chest_pain", "anemia"], 4)
])
def test_each_sign_contributes_one_point(symptoms, expected):
    assert score(**{name: "yes" for name in symptoms})["score"] == expected


@pytest.mark.parametrize(("inputs", "expected_score", "expected_class"), [
    ({}, 0, "I"),
    ({"cough": "yes"}, 1, "I"),
    ({"cough": "yes", "dyspnea": "yes"}, 2, "II"),
    ({"cough": "yes", "dyspnea": "yes", "anemia": "yes"}, 3, "II"),
    ({"bmi": 15, "muac_mm": 199}, 4, "III"),
    ({"bmi": 15, "muac_mm": 199, "cough": "yes", "dyspnea": "yes", "chest_pain": "yes"}, 7, "III"),
    ({"bmi": 15, "muac_mm": 199, "cough": "yes", "dyspnea": "yes", "chest_pain": "yes", "anemia": "yes"}, 8, "IV"),
])
def test_severity_classes(inputs, expected_score, expected_class):
    result = score(**inputs)
    assert result["score"] == expected_score
    assert result["severity_class"] == expected_class
    assert sum(result["components"].values()) == expected_score


@pytest.mark.parametrize("overrides", [
    {"cough": ""}, {"cough": "maybe"}, {"anemia": None},
    {"bmi": float("nan")}, {"bmi": float("inf")}, {"bmi": -1},
    {"bmi": ""}, {"muac_mm": 0}, {"muac_mm": "NaN"},
    {"muac_mm": float("inf")}, {"muac_mm": True}
])
def test_invalid_or_missing_data_rejected(overrides):
    with pytest.raises(ValueError):
        score(**overrides)


def test_reject_missing_required_field():
    with pytest.raises(TypeError):
        calculate_metrics(cough="no")


def test_two_month_comparison():
    assert monitor_change(8, 6)["decreased_at_least_25_percent"] is True
    assert monitor_change(4, 4)["decreased_at_least_25_percent"] is False
    assert monitor_change(4, 5)["percent_reduction"] == -25
    assert monitor_change(0, 0)["percent_reduction"] is None
    with pytest.raises(ValueError):
        monitor_change(9, 0)


def test_batch_roundtrip(tmp_path):
    source, dest = tmp_path / "assessments.csv", tmp_path / "scores.csv"
    source.write_text("cough,dyspnea,chest_pain,anemia,bmi,muac_mm\n"
                      "yes,no,no,yes,15.9,199\n"
                      "no,no,no,no,18,220\n", encoding="utf-8")
    assert process_batch(str(source), str(dest)) == 2
    with dest.open(newline="") as f:
        rows = list(csv.DictReader(f))
    assert [(int(r["score"]), r["severity_class"]) for r in rows] == [(6, "III"), (0, "I")]
    assert set(rows[0]) == {"cough", "dyspnea", "chest_pain", "anemia", "bmi", "muac_mm", "score", "severity_class"}


def test_batch_rejects_bad_rows_without_partial_output(tmp_path):
    source, dest = tmp_path / "input.csv", tmp_path / "out.csv"
    source.write_text("cough,dyspnea,chest_pain,anemia,bmi,muac_mm\n"
                      "no,no,no,no,18,220\n"
                      "no,invalid,no,no,18,220\n", encoding="utf-8")
    with pytest.raises(ValueError, match="line 3"):
        process_batch(str(source), str(dest))
    assert not dest.exists()


def test_batch_rejects_extra_columns_and_input_equals_output(tmp_path):
    source, dest = tmp_path / "input.csv", tmp_path / "out.csv"
    source.write_text("Patient_ID,cough,dyspnea,chest_pain,anemia,bmi,muac_mm\n"
                      "PERSON,yes,no,no,no,18,220\n", encoding="utf-8")
    with pytest.raises(ValueError, match="headers"):
        process_batch(str(source), str(dest))
    with pytest.raises(ValueError, match="must differ"):
        process_batch(str(source), str(source))


def test_path_restriction():
    with pytest.raises(ValueError):
        process_batch("../../../etc/passwd", "results.csv")


def test_cli_single(capsys):
    args = ["single", "--cough", "yes", "--dyspnea", "no",
            "--chest-pain", "no", "--anemia", "no", "--bmi", "18", "--muac-mm", "220"]
    assert main(args) == 0
    assert json.loads(capsys.readouterr().out)["score"] == 1
