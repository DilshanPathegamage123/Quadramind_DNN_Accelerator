#!/usr/bin/env python3
"""
synth_scheduler_hw.py
=====================
Run real Vivado out-of-context synthesis on every multi-DNN scheduler and
cache the MEASURED hardware cost (area, power, achievable clock) so the
scheduler chooser can report those columns without running synthesis per
query.

This produces the only hardware-grounded per-scheduler numbers in the
project: LUT / flip-flop / DSP / BRAM counts, Vivado `report_power`
watts, and a post-synthesis Fmax estimate.  Nothing here is modelled or
interpolated -- a scheduler that fails to synthesise is recorded as
`unavailable` with the tool's own error text, never as an estimate.

Usage (from sim_framework/):
    python scripts/synth_scheduler_hw.py                  # all schedulers
    python scripts/synth_scheduler_hw.py --only FIFO,SJF  # a subset
    python scripts/synth_scheduler_hw.py --period 10.0    # clock constraint

Output: results/sched_chooser/hw/scheduler_hw.csv  (+ per-scheduler raw
Vivado reports under results/sched_chooser/hw/reports/).

Fmax note: WNS is taken from a post-synthesis (opt_design) timing report
with only the clock constrained, so it reflects register-to-register
paths inside the scheduler.  It is a post-synthesis estimate, NOT a
post-route number -- placement and routing will reduce it.  Reported as
fmax_mhz_post_synth and labelled as such everywhere it is consumed.
"""
from __future__ import annotations

import argparse
import csv
import re
import shutil
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RTL = ROOT / "rtl" / "schedulers"

PART = "xc7a100tcsg324-1"

# Vivado's location is NOT hardcoded: the install has already moved once
# (/home/2025.2 -> /vivado/2025.2), which silently stranded this table.
# Resolution order: $VIVADO env var, then PATH, then known install roots.
_VIVADO_CANDIDATES = (
    "/vivado/2025.2/Vivado/bin/vivado",
    "/home/2025.2/Vivado/bin/vivado",
    "/tools/Xilinx/Vivado/2025.2/bin/vivado",
    "/opt/Xilinx/Vivado/2025.2/bin/vivado",
)


def find_vivado() -> str | None:
    import os
    env = os.environ.get("VIVADO")
    if env and Path(env).exists():
        return env
    which = shutil.which("vivado")
    if which:
        return which
    for c in _VIVADO_CANDIDATES:
        if Path(c).exists():
            return c
    return None


VIVADO = find_vivado()

# scheduler -> (source file, top module, {generic: value})
# Order mirrors SimConfig.SCHEDULER_NAMES (select codes 0..13).
TARGETS: dict[str, tuple[str, str, dict]] = {
    "FIFO":        ("task_scheduler.sv",          "task_scheduler",          {"SCHEDULER_TYPE": 0}),
    "LIFO":        ("task_scheduler.sv",          "task_scheduler",          {"SCHEDULER_TYPE": 1}),
    "SJF":         ("task_scheduler.sv",          "task_scheduler",          {"SCHEDULER_TYPE": 2}),
    "RR":          ("task_scheduler.sv",          "task_scheduler",          {"SCHEDULER_TYPE": 3}),
    "PRI":         ("task_scheduler.sv",          "task_scheduler",          {"SCHEDULER_TYPE": 4}),
    "EDF":         ("task_scheduler.sv",          "task_scheduler",          {"SCHEDULER_TYPE": 5}),
    "LRU":         ("task_scheduler.sv",          "task_scheduler",          {"SCHEDULER_TYPE": 6}),
    "SRTF":        ("advanced_task_scheduler.sv", "advanced_task_scheduler", {"SCHEDULER_TYPE": 0}),
    "HRRN":        ("advanced_task_scheduler.sv", "advanced_task_scheduler", {"SCHEDULER_TYPE": 1}),
    "MLQ":         ("advanced_task_scheduler.sv", "advanced_task_scheduler", {"SCHEDULER_TYPE": 2}),
    "MLFQ":        ("advanced_task_scheduler.sv", "advanced_task_scheduler", {"SCHEDULER_TYPE": 3}),
    "AIMT":        ("aimt_scheduler.sv",          "aimt_scheduler",          {}),
    "BATCHDNN":    ("batchdnn_scheduler.sv",      "batchdnn_scheduler",      {}),
    "BATCHDNN_PP": ("batchdnn_pp_scheduler.sv",   "batchdnn_pp_scheduler",   {}),
}

FIELDS = ["scheduler", "status", "luts", "ffs", "f7_muxes", "dsps", "brams",
          "constraint_ns", "wns_ns", "fmax_mhz_post_synth", "power_total_w",
          "power_dynamic_w", "power_static_w", "power_confidence",
          "crit_warnings", "part", "source", "note"]


def _tcl(src_name: str, top: str, generics: dict, period: float) -> str:
    """TCL run entirely with bare relative filenames.

    Vivado's read_verilog/read_xdc split their file argument on whitespace
    even inside Tcl braces, so an absolute path containing a space (this
    repo lives under '.../Updated Simulator/...') fails with a misleading
    "File ... does not exist".  Everything is therefore copied into a
    space-free temp working directory and referenced by basename; the
    reports are copied back out by Python afterwards.
    """
    gen = " ".join(f"-generic {{{k}={v}}}" for k, v in generics.items())
    return f"""
create_project -part {PART} -in_memory sched_probe
read_verilog -sv {src_name}
read_xdc c.xdc
synth_design -top {top} -part {PART} -mode out_of_context {gen}
opt_design
report_utilization    -file util.rpt
report_power          -file power.rpt
report_timing_summary -file timing.rpt
puts "SCHED_PROBE_OK"
exit 0
"""


# Vivado errors that mean the HARNESS is broken, not the RTL.  These must
# never be recorded as "does not synthesise" -- that would turn a setup bug
# into a false finding about someone's design.
_INFRA_ERROR_PATTERNS = (
    r"does not exist",
    r"Unable to find",
    r"no such file",
    r"LICENSE",
    r"Unable to open",
)


def _is_infra_error(log: str) -> str | None:
    for pat in _INFRA_ERROR_PATTERNS:
        m = re.search(rf"^ERROR:.*{pat}.*$", log, re.M | re.I)
        if m:
            return m.group(0).strip()
    return None


def _parse_int(text: str, pattern: str) -> int | None:
    m = re.search(pattern, text)
    if not m:
        return None
    try:
        return int(m.group(1))
    except ValueError:
        return None


def _parse_util(path: Path) -> dict:
    if not path.exists():
        return {}
    t = path.read_text()
    return {
        "luts":     _parse_int(t, r"\|\s*Slice LUTs\*?\s*\|\s*(\d+)"),
        "ffs":      _parse_int(t, r"\|\s*Slice Registers\s*\|\s*(\d+)"),
        "f7_muxes": _parse_int(t, r"\|\s*F7 Muxes\s*\|\s*(\d+)"),
        "dsps":     _parse_int(t, r"\|\s*DSPs\s*\|\s*(\d+)"),
        "brams":    _parse_int(t, r"\|\s*Block RAM Tile\s*\|\s*(\d+)"),
    }


def _parse_power(path: Path) -> dict:
    if not path.exists():
        return {}
    t = path.read_text()

    def f(pat):
        m = re.search(pat, t)
        return float(m.group(1)) if m else None

    conf = re.search(r"\|\s*Confidence Level\s*\|\s*(\w+)", t)
    return {
        "power_total_w":    f(r"\|\s*Total On-Chip Power \(W\)\s*\|\s*([\d.]+)"),
        "power_dynamic_w":  f(r"\|\s*Dynamic \(W\)\s*\|\s*([\d.]+)"),
        "power_static_w":   f(r"\|\s*Device Static \(W\)\s*\|\s*([\d.]+)"),
        "power_confidence": conf.group(1) if conf else None,
    }


def _parse_wns(path: Path) -> float | None:
    if not path.exists():
        return None
    m = re.search(r"Setup :.*?Worst Slack\s+(-?[\d.]+)ns", path.read_text(),
                  re.S)
    return float(m.group(1)) if m else None


def synth_one(name: str, period: float, rpt_dir: Path) -> dict:
    src, top, generics = TARGETS[name]
    src_path = RTL / src
    out_prefix = rpt_dir / name
    row = {k: "" for k in FIELDS}
    row.update({"scheduler": name, "part": PART, "constraint_ns": f"{period:.3f}",
                "source": "measured (Vivado 2025.2 OOC synthesis)"})

    work = Path(tempfile.mkdtemp(prefix=f"sched_synth_{name}_"))
    try:
        # copy sources into the space-free work dir (see _tcl docstring)
        shutil.copy2(src_path, work / src_path.name)
        (work / "c.xdc").write_text(
            f"create_clock -name clk -period {period:.3f} [get_ports clk]\n")
        (work / "run.tcl").write_text(
            _tcl(src_path.name, top, generics, period))

        t0 = time.perf_counter()
        proc = subprocess.run(
            [VIVADO, "-mode", "batch", "-nojournal", "-nolog",
             "-source", "run.tcl"],
            cwd=work, capture_output=True, text=True, timeout=3600)
        elapsed = time.perf_counter() - t0
        log = proc.stdout + proc.stderr
        (rpt_dir / f"{name}_vivado.log").write_text(log)

        crit = len(re.findall(r"^CRITICAL WARNING", log, re.M))
        row["crit_warnings"] = str(crit)

        if "SCHED_PROBE_OK" not in log:
            infra = _is_infra_error(log)
            if infra:
                # A harness/environment failure must abort loudly.  Recording
                # it as "does not synthesise" would publish a false claim
                # about the RTL.
                raise RuntimeError(
                    f"{name}: Vivado harness error (NOT an RTL finding): "
                    f"{infra}\nSee {rpt_dir / f'{name}_vivado.log'}")
            errs = re.findall(r"^ERROR: \[.*?\] (.+)$", log, re.M)
            reason = errs[0].strip() if errs else "synthesis failed"
            # Vivado reports the temp build copy; rewrite it to the real
            # source path so the finding points somewhere a reader can open.
            reason = reason.replace(str(work / src_path.name),
                                    f"rtl/schedulers/{src_path.name}")
            row["status"] = "unavailable"
            row["note"] = f"does not synthesise: {reason}"
            print(f"  [UNAVAILABLE] {name}: {reason}")
            return row

        for tag in ("util", "power", "timing"):
            produced = work / f"{tag}.rpt"
            if produced.exists():
                shutil.copy2(produced, f"{out_prefix}_{tag}.rpt")

        row["status"] = "ok"
        row.update({k: ("" if v is None else str(v))
                    for k, v in _parse_util(Path(f"{out_prefix}_util.rpt")).items()})
        pw = _parse_power(Path(f"{out_prefix}_power.rpt"))
        row.update({k: ("" if v is None else str(v)) for k, v in pw.items()})
        wns = _parse_wns(Path(f"{out_prefix}_timing.rpt"))
        if wns is not None:
            row["wns_ns"] = f"{wns:.3f}"
            achievable = period - wns
            if achievable > 0:
                row["fmax_mhz_post_synth"] = f"{1000.0 / achievable:.1f}"
        notes = []
        if crit:
            notes.append(f"{crit} CRITICAL WARNING(s) in synthesis "
                         f"-- see {name}_vivado.log")
        row["note"] = "; ".join(notes)
        print(f"  [OK] {name}: {row['luts']} LUT / {row['ffs']} FF / "
              f"{row['power_total_w']} W / "
              f"{row['fmax_mhz_post_synth']} MHz  ({elapsed:.0f}s)"
              + (f"  [{crit} CRIT]" if crit else ""))
        return row
    except subprocess.TimeoutExpired:
        row["status"] = "unavailable"
        row["note"] = "synthesis timed out (>3600s)"
        print(f"  [TIMEOUT] {name}")
        return row
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Vivado OOC synthesis of every scheduler -> cached "
                    "measured area/power/Fmax table.")
    ap.add_argument("--only", default=None,
                    help="comma-separated scheduler subset")
    ap.add_argument("--period", type=float, default=10.0,
                    help="clock constraint in ns (default 10.0 = 100 MHz)")
    ap.add_argument("--out", default=None, help="output CSV path")
    args = ap.parse_args()

    if VIVADO is None:
        raise SystemExit(
            "Vivado not found. Set $VIVADO to the vivado binary, put it on "
            "PATH, or install it at one of: "
            + ", ".join(_VIVADO_CANDIDATES))
    print(f"Using Vivado: {VIVADO}")

    names = list(TARGETS)
    if args.only:
        names = [n.strip().upper() for n in args.only.split(",")]
        for n in names:
            if n not in TARGETS:
                raise SystemExit(f"unknown scheduler {n!r}")

    out_csv = Path(args.out) if args.out else (
        ROOT / "results/sched_chooser/hw/scheduler_hw.csv")
    rpt_dir = out_csv.parent / "reports"
    rpt_dir.mkdir(parents=True, exist_ok=True)

    print(f"Vivado OOC synthesis -- part {PART}, clock constraint "
          f"{args.period:.3f} ns, {len(names)} schedulers\n")
    fresh = {n: synth_one(n, args.period, rpt_dir) for n in names}

    # Re-running a subset must UPDATE the table, not replace it with a
    # 3-row file -- otherwise a targeted re-run silently destroys the
    # results for every other scheduler.
    merged: dict[str, dict] = {}
    if out_csv.exists():
        with open(out_csv, newline="") as fh:
            for old in csv.DictReader(fh):
                merged[old["scheduler"]] = old
    merged.update(fresh)
    rows = [merged[n] for n in TARGETS if n in merged]

    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)
    ok = sum(1 for r in rows if r["status"] == "ok")
    try:
        shown = out_csv.relative_to(ROOT)
    except ValueError:          # --out outside the repo
        shown = out_csv
    print(f"\n{ok}/{len(rows)} synthesised. Table: {shown}")


if __name__ == "__main__":
    main()
