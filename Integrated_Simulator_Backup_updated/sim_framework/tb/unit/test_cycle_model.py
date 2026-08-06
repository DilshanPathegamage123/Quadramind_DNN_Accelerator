"""Regression tests for the chooser's absolute cycle model (v2).

The model is

    cycles = 3 * (AXI AR requests) + 2 * (AXI beats) + compute_base

calibrated by scripts/calibrate_cycle_model.py against the recorded RTL
runs.  These tests lock in the properties that matter:

  * the two protocol coefficients stay at their measured integer values,
  * predictions stay close to the measured cycles they were built from,
  * and -- most importantly -- the RANKING of configurations against each
    other is never inverted, which is what the chooser is actually used
    for.  A magnitude error that preserves ordering still picks correctly.

Runs without cocotb, Verilator or Vivado.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from pysim.sim_config import LayerConfig
from pysim.config_chooser import (_CALIB, ar_requests, beats_per_burst,
                                  compute_base, rank_configs, score_config)

RAW = ROOT / "results/golden_check/raw"


def _layer(rel: str) -> LayerConfig:
    cfg = json.loads((ROOT / rel / "config.json").read_text())
    fields = set(LayerConfig.__dataclass_fields__)
    return LayerConfig(**{k: v for k, v in cfg.items() if k in fields})


def _measured_runs():
    runs = []
    for vp in sorted(RAW.glob("*_verdict.json")):
        stem = vp.name.replace("_verdict.json", "")
        rp = RAW / f"{stem}.json"
        if not rp.exists() or "probe" in stem:
            continue
        v = json.loads(vp.read_text())
        r = json.loads(rp.read_text())
        if "axi_beats" not in r or v.get("memory") != "STAMP":
            continue
        runs.append((stem, v, r))
    return runs


def test_protocol_coefficients_are_the_measured_integers():
    """3 cycles per read-address handshake, 2 per delivered beat."""
    assert _CALIB["cycles_per_ar_request"] == pytest.approx(3.0, abs=1e-9)
    assert _CALIB["cycles_per_beat"] == pytest.approx(2.0, abs=1e-9)


def test_calibration_file_is_present_and_populated():
    assert _CALIB.get("compute_base"), "no measured compute_base entries"
    assert _CALIB.get("compute_base_per_mac"), "no fallback rates"


def test_measured_layers_use_the_measured_base_not_an_estimate():
    base, measured = compute_base(_layer("models/tiny_cnn/layer_00"),
                                  "OS", 8, 8)
    assert measured is True
    assert base == pytest.approx(1722.0, abs=1e-6)


def test_unmeasured_shape_falls_back_and_says_so():
    odd = LayerConfig(input_channels=7, input_height=9, input_width=9,
                      weight_k=5, weight_c=7, weight_kh=3, weight_kw=3,
                      output_channels=5, output_height=7, output_width=7)
    base, measured = compute_base(odd, "OS", 8, 8)
    assert measured is False
    assert base > 0


def test_burst_ratio_is_workload_independent_for_casting():
    """HYBRID and UNICAST landed on the same ratio for both anchor layers."""
    tiny = _layer("models/tiny_cnn/layer_00")
    mnist = _layer("models/mnist_cnn/layer_00")
    for casting in ("HYBRID", "UNICAST"):
        assert (beats_per_burst(tiny, "CHANNEL_MAJOR", casting)
                == beats_per_burst(mnist, "CHANNEL_MAJOR", casting))


def test_row_major_burst_ratio_splits_on_channel_count():
    """ROW_MAJOR coalesces well only for single-channel layers."""
    tiny = _layer("models/tiny_cnn/layer_00")     # C = 3
    mnist = _layer("models/mnist_cnn/layer_00")   # C = 1
    assert (beats_per_burst(mnist, "ROW_MAJOR", "MULTICAST")
            > beats_per_burst(tiny, "ROW_MAJOR", "MULTICAST") * 5)


def test_ar_requests_never_exceed_beats():
    tiny = _layer("models/tiny_cnn/layer_00")
    for layout in ("ROW_MAJOR", "COLUMN_MAJOR", "CHANNEL_MAJOR"):
        for casting in ("MULTICAST", "HYBRID", "UNICAST"):
            assert ar_requests(tiny, layout, casting, 1836) <= 1836


@pytest.mark.parametrize("stem,v,r", _measured_runs(),
                         ids=lambda x: x if isinstance(x, str) else "")
def test_prediction_is_close_to_the_measured_run(stem, v, r):
    """Every recorded configuration must predict within 25%.

    Two of the nineteen sit near that bound: ROW_MAJOR and COLUMN_MAJOR on
    mnist_cnn/layer_00, where the hardware changes traffic VOLUME by layout
    and the traffic model does not.  That is a known, documented gap -- the
    bound exists to stop it silently getting worse.
    """
    h, w = (int(t) for t in v["array"].split("x"))
    s = score_config([_layer(v["layer"])], h, w, 256 * 1024, v["dataflow"],
                     v["layout"], v.get("casting", "MULTICAST"))
    measured = int(r["total_cycles"])
    err = abs(s.predicted_cycles - measured) / measured * 100.0
    assert err <= 25.0, f"{stem}: {err:.1f}% off ({s.predicted_cycles:,.0f} vs {measured:,})"


def test_ranking_against_measured_is_never_inverted():
    """The property the chooser depends on: order, not magnitude."""
    groups: dict[tuple, list] = {}
    for stem, v, r in _measured_runs():
        h, w = (int(t) for t in v["array"].split("x"))
        s = score_config([_layer(v["layer"])], h, w, 256 * 1024, v["dataflow"],
                         v["layout"], v.get("casting", "MULTICAST"))
        key = (v["layer"], v["dataflow"], v["array"])
        groups.setdefault(key, []).append(
            (stem, int(r["total_cycles"]), s.predicted_cycles))

    inversions = []
    for key, g in groups.items():
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                (na, ma, pa), (nb, mb, pb) = g[i], g[j]
                if ma == mb:
                    continue
                if (ma < mb) != (pa < pb):
                    inversions.append(f"{na} vs {nb}")
    assert not inversions, f"ranking inverted for: {inversions}"


def test_cycles_goal_picks_the_measured_fastest_dataflow():
    """Closes the old Issue 4: measured hardware runs IS fastest, and the
    cycle model now agrees (the legacy latency rank picked OS)."""
    for model in ("models/tiny_cnn/layer_00", "models/mnist_cnn/layer_00"):
        ranked = rank_configs([_layer(model)], 8, 8, 256 * 1024, "cycles")
        assert ranked[0].dataflow == "IS", f"{model}: picked {ranked[0].dataflow}"
        assert ranked[0].layout == "CHANNEL_MAJOR"
        assert ranked[0].casting == "MULTICAST"


def test_layout_and_casting_ranking_is_independent_of_compute_base():
    """compute_base is constant per (layer, dataflow), so it cannot change
    how layouts or castings rank against each other."""
    layer = _layer("models/tiny_cnn/layer_00")
    def cyc(layout, casting):
        return score_config([layer], 8, 8, 256 * 1024, "OS", layout,
                            casting).predicted_cycles
    base, _ = compute_base(layer, "OS", 8, 8)
    for layout in ("ROW_MAJOR", "COLUMN_MAJOR", "CHANNEL_MAJOR"):
        for casting in ("MULTICAST", "HYBRID", "UNICAST"):
            assert cyc(layout, casting) > base
    assert cyc("CHANNEL_MAJOR", "MULTICAST") < cyc("ROW_MAJOR", "MULTICAST")
    assert cyc("CHANNEL_MAJOR", "MULTICAST") < cyc("CHANNEL_MAJOR", "HYBRID")
    assert cyc("CHANNEL_MAJOR", "HYBRID") < cyc("CHANNEL_MAJOR", "UNICAST")
