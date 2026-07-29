#!/usr/bin/env python3
"""
validate_cycle_model.py
=======================
Check the chooser's absolute cycle predictions against every recorded RTL
run.  This validates the CHOOSER's end-to-end prediction -- modelled beats
and modelled AR requests -- not the calibration fit, so it is a real test
rather than a restatement of the constants.

Reports per-configuration error and the worst case.  Writes
results/chooser/eval_cycle_model.csv.

Usage (from sim_framework/):
    PYTHONPATH=. python scripts/validate_cycle_model.py
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from pysim.sim_config import LayerConfig
from pysim.config_chooser import score_config

RAW = ROOT / "results/golden_check/raw"
OUT = ROOT / "results/chooser/eval_cycle_model.csv"


def _layer(path: str) -> LayerConfig:
    cfg = json.loads((ROOT / path / "config.json").read_text())
    fields = set(LayerConfig.__dataclass_fields__)
    return LayerConfig(**{k: v for k, v in cfg.items() if k in fields})


def main() -> None:
    rows = []
    for vp in sorted(RAW.glob("*_verdict.json")):
        stem = vp.name.replace("_verdict.json", "")
        rp = RAW / f"{stem}.json"
        if not rp.exists() or "probe" in stem:
            continue
        v = json.loads(vp.read_text())
        r = json.loads(rp.read_text())
        if "axi_beats" not in r or v.get("memory") != "STAMP":
            continue

        h, w = (int(t) for t in v["array"].split("x"))
        layer = _layer(v["layer"])
        s = score_config([layer], h, w, 256 * 1024, v["dataflow"],
                         v["layout"], v.get("casting", "MULTICAST"))

        meas_cyc = int(r["total_cycles"])
        meas_beats = int(r["axi_beats"])
        meas_ar = int(r["axi_ar_requests"])
        err_pct = (s.predicted_cycles - meas_cyc) / meas_cyc * 100.0
        rows.append({
            "config": stem,
            "layer": v["layer"].replace("models/", ""),
            "dataflow": v["dataflow"], "layout": v["layout"],
            "casting": v.get("casting", "MULTICAST"), "array": v["array"],
            "measured_cycles": meas_cyc,
            "predicted_cycles": round(s.predicted_cycles),
            "cycle_error_pct": round(err_pct, 3),
            "measured_beats": meas_beats,
            "predicted_beats": round(s.prefetch_beats),
            "beats_exact": meas_beats == round(s.prefetch_beats),
            "measured_ar": meas_ar,
            "predicted_ar": round(s.ar_requests),
            "ar_error_pct": round((s.ar_requests - meas_ar) / meas_ar * 100.0, 2),
            "base_measured": s.base_measured,
        })

    if not rows:
        raise SystemExit("no measured runs found")

    errs = [abs(r["cycle_error_pct"]) for r in rows]
    beats_ok = sum(1 for r in rows if r["beats_exact"])
    within1 = sum(1 for e in errs if e <= 1.0)
    within5 = sum(1 for e in errs if e <= 5.0)

    print(f"{len(rows)} measured configurations\n")
    print(f"{'config':<52}{'measured':>10}{'predicted':>11}{'err %':>9}")
    for r in sorted(rows, key=lambda x: -abs(x["cycle_error_pct"])):
        print(f"{r['config'][:50]:<52}{r['measured_cycles']:>10,}"
              f"{r['predicted_cycles']:>11,}{r['cycle_error_pct']:>9.2f}")

    # Ranking check: within each (layer, dataflow, array) group, does the
    # predicted order of configurations match the measured order?  A model
    # can be off on magnitude and still choose correctly -- that is what the
    # chooser is actually used for.
    groups: dict[tuple, list] = {}
    for r in rows:
        groups.setdefault((r["layer"], r["dataflow"], r["array"]), []).append(r)
    pairs_ok = pairs_total = 0
    inversions = []
    for key, g in groups.items():
        for i in range(len(g)):
            for j in range(i + 1, len(g)):
                a, b = g[i], g[j]
                if a["measured_cycles"] == b["measured_cycles"]:
                    continue
                pairs_total += 1
                meas_order = a["measured_cycles"] < b["measured_cycles"]
                pred_order = a["predicted_cycles"] < b["predicted_cycles"]
                if meas_order == pred_order:
                    pairs_ok += 1
                else:
                    inversions.append((a["config"], b["config"]))

    print(f"\nranking preserved:      {pairs_ok}/{pairs_total} ordered pairs")
    for a, b in inversions:
        print(f"  INVERTED: {a}  vs  {b}")
    print(f"beats exact:            {beats_ok}/{len(rows)}")
    print(f"cycle error <= 1%:      {within1}/{len(rows)}")
    print(f"cycle error <= 5%:      {within5}/{len(rows)}")
    print(f"mean |cycle error|:     {sum(errs)/len(errs):.2f}%")
    print(f"worst |cycle error|:    {max(errs):.2f}%")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", newline="") as fh:
        wtr = csv.DictWriter(fh, fieldnames=list(rows[0]))
        wtr.writeheader()
        wtr.writerows(rows)
    print(f"\nwrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
