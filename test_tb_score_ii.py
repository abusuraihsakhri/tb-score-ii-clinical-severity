import pytest
from tb_score_ii import calculate_metrics, process_batch


def test_tb_score_ii_single():
    res = calculate_metrics(v1=12.0, v2=4.0)
    assert "score" in res
    assert "classification" in res
    assert res["score"] > 0


def test_tb_score_ii_batch(tmp_path):
    csv_in = tmp_path / "in.csv"
    csv_out = tmp_path / "out.csv"
    csv_in.write_text("Patient,v1,v2\nPat_001,15.0,3.0\nPat_002,5.0,1.0\n", encoding="utf-8")

    process_batch(str(csv_in), str(csv_out))
    assert csv_out.exists()
    content = csv_out.read_text(encoding="utf-8")
    assert "Pat_001" in content
    assert "score" in content


def test_calculate_metrics_non_finite():
    """Non-finite values should be handled gracefully."""
    res = calculate_metrics(v1=float("inf"), v2=4.0)
    assert "score" in res
    assert isinstance(res["score"], float)

    res_nan = calculate_metrics(v1=float("nan"), v2=4.0)
    assert "score" in res_nan
    assert isinstance(res_nan["score"], float)


def test_process_batch_missing_file(tmp_path):
    """Missing input file should raise FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        process_batch(str(tmp_path / "nonexistent.csv"), str(tmp_path / "out.csv"))


def test_process_batch_path_traversal():
    """Path traversal attempts should be blocked."""
    with pytest.raises((ValueError, Exception)):
        process_batch("../../../etc/passwd", "results.csv")
