#!/usr/bin/env python3
"""
synth_memory_hw.py
==================
Run real Vivado out-of-context synthesis on the Member-2 memory-management
RTL and cache the MEASURED hardware cost (area, power, achievable clock).

This supplies the "hardware cost" axis of the memory-scheme comparison,
which is the one axis the cycle-accurate runs cannot provide.  Three
families of target are synthesised:

  * scratchpad_ram at NUM_BANKS = 1/2/4/8/16
        -> what multi-banking actually costs in silicon, so the
           conflict-reduction benefit can be traded off against area.
  * stamp_memory_backend vs paged_memory_backend
        -> whole-subsystem cost of each management scheme.
  * stamp_based_memory_controller vs page_table
        -> the control logic alone, with the shared scratchpad excluded,
           which is where the two schemes genuinely differ.

Nothing here is modelled or interpolated.  A target that fails to
synthesise is recorded as `unavailable` with Vivado's own error text,
never as an estimate.  Harness/environment failures (missing file, no
licence) abort loudly instead of being published as a false claim that
someone's RTL does not synthesise.

Usage (from sim_framework/):
    python scripts/synth_memory_hw.py                     # everything
    python scripts/synth_memory_hw.py --only spad_b4,stamp_backend
    python scripts/synth_memory_hw.py --period 10.0       # clock constraint

Output: results/member2/hw/memory_hw.csv (+ raw Vivado reports under
results/member2/hw/reports/).

Fmax note: WNS comes from a post-synthesis (opt_design) timing report with
only the clock constrained.  It is a post-synthesis estimate, NOT a
post-route number -- placement and routing will reduce it.  It is reported
as fmax_mhz_post_synth and labelled as such everywhere it is consumed.
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
RTL = ROOT / "rtl" / "memory"

VIVADO = "/home/2025.2/Vivado/bin/vivado"
PART = "xc7a100tcsg324-1"

# Every memory-side source; Vivado resolves the hierarchy itself.
SOURCES = ["scratchpad_ram.sv", "axi_read_adapter.sv", "paged_table.v",
           "stamp_based_memory_controller.sv", "stamp_memory_backend.sv",
           "paged_memory_backend.sv"]

# Depth used for every scratchpad-bearing target.
#
# The simulation build uses SPAD_DEPTH = 4096.  That build does NOT
# synthesise: scratchpad_ram is a *behaviourally modelled* multi-port SRAM
# (4 read + 4 write ports), and Xilinx BRAM has only two ports, so Vivado
# cannot infer a memory and refuses to dissolve 131,072 bits into flip-flops
# -- which would not fit on this part anyway.  Verified, with Vivado's own
# error text, in results/member2/hw/reports/spad_b1_vivado.log.
#
# Synthesising at a reduced depth gives a valid *relative* comparison
# (bank-count cost, and STAMP vs PAGED control cost), which is what the
# comparison needs.  It is labelled as reduced depth everywhere it appears
# and must not be quoted as the area of the simulated 4096-word design.
SYNTH_DEPTH = 256

_DEPTH_NOTE = (f"synthesised at {SYNTH_DEPTH}-word depth; the 4096-word "
               f"simulation build is a behavioural multi-port model and "
               f"does not synthesise (see spad_b1_vivado.log)")

# target -> (top module, {generic: value}, family, human label)
TARGETS: dict[str, tuple[str, dict, str, str]] = {
    "spad_b1":  ("scratchpad_ram", {"NUM_BANKS": 1,  "DEPTH": SYNTH_DEPTH},
                 "scratchpad", "Scratchpad, 1 bank (flat baseline)"),
    "spad_b2":  ("scratchpad_ram", {"NUM_BANKS": 2,  "DEPTH": SYNTH_DEPTH},
                 "scratchpad", "Scratchpad, 2 banks"),
    "spad_b4":  ("scratchpad_ram", {"NUM_BANKS": 4,  "DEPTH": SYNTH_DEPTH},
                 "scratchpad", "Scratchpad, 4 banks"),
    "spad_b8":  ("scratchpad_ram", {"NUM_BANKS": 8,  "DEPTH": SYNTH_DEPTH},
                 "scratchpad", "Scratchpad, 8 banks"),
    "spad_b16": ("scratchpad_ram", {"NUM_BANKS": 16, "DEPTH": SYNTH_DEPTH},
                 "scratchpad", "Scratchpad, 16 banks"),
    "stamp_backend": ("stamp_memory_backend",
                      {"NUM_BANKS": 4, "SPAD_DEPTH": SYNTH_DEPTH}, "backend",
                      "STAMP backend (whole subsystem, 4 banks)"),
    "paged_backend": ("paged_memory_backend",
                      {"NUM_BANKS": 4, "SPAD_DEPTH": SYNTH_DEPTH}, "backend",
                      "PAGED backend (whole subsystem, 4 banks)"),
    "stamp_ctrl": ("stamp_based_memory_controller", {}, "controller",
                   "STAMP controller (control logic only)"),
    "paged_ctrl": ("page_table", {}, "controller",
                   "PAGED page table (control logic only)"),
}

FIELDS = ["target", "family", "label", "top_module", "status", "luts", "ffs",
          "f7_muxes", "dsps", "brams", "constraint_ns", "wns_ns",
          "fmax_mhz_post_synth", "power_total_w", "power_dynamic_w",
          "power_static_w", "power_confidence", "crit_warnings", "part",
          "source", "note"]


def _tcl(top: str, generics: dict, period: float) -> str:
    """TCL run entirely with bare relative filenames.

    Vivado's read_verilog/read_xdc split their file argument on whitespace
    even inside Tcl braces, so an absolute path containing a space (this
    repo lives under '.../Updated Simulator/...') fails with a misleading
    "File ... does not exist".  Everything is therefore copied into a
    space-free temp working directory and referenced by basename; the
    reports are copied back out by Python afterwards.
    """
    gen = " ".join(f"-generic {{{k}={v}}}" for k, v in generics.items())
    sv = " ".join(s for s in SOURCES if s.endswith(".sv"))
    v = " ".join(s for s in SOURCES if s.endswith(".v"))
    reads = f"read_verilog -sv {sv}\n"
    if v:
        reads += f"read_verilog {v}\n"
    return f"""
create_project -part {PART} -in_memory mem_probe
{reads}read_xdc c.xdc
synth_design -top {top} -part {PART} -mode out_of_context {gen}
opt_design
report_utilization    -file util.rpt
report_power          -file power.rpt
report_timing_summary -file timing.rpt
puts "MEM_PROBE_OK"
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
        "brams":    _parse_int(t, r"\|\s*Block RAM Tile\s*\|\s*([\d.]+)"),
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
    top, generics, family, label = TARGETS[name]
    out_prefix = rpt_dir / name
    row = {k: "" for k in FIELDS}
    row.update({"target": name, "family": family, "label": label,
                "top_module": top, "part": PART,
                "constraint_ns": f"{period:.3f}",
                "source": "measured (Vivado 2025.2 OOC synthesis)"})

    work = Path(tempfile.mkdtemp(prefix=f"mem_synth_{name}_"))
    try:
        for s in SOURCES:
            shutil.copy2(RTL / s, work / s)
        (work / "c.xdc").write_text(
            f"create_clock -name clk -period {period:.3f} [get_ports clk]\n")
        (work / "run.tcl").write_text(_tcl(top, generics, period))

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

        if "MEM_PROBE_OK" not in log:
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
            reason = re.sub(re.escape(str(work)) + "/?", "rtl/memory/", reason)
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
        if family in ("scratchpad", "backend"):
            notes.append(_DEPTH_NOTE)
        if crit:
            notes.append(f"{crit} CRITICAL WARNING(s) -- see {name}_vivado.log")
        row["note"] = "; ".join(notes)
        print(f"  [OK] {name}: {row['luts']} LUT / {row['ffs']} FF / "
              f"{row['brams']} BRAM / {row['power_total_w']} W / "
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
        description="Vivado OOC synthesis of the memory-management RTL -> "
                    "cached measured area/power/Fmax table.")
    ap.add_argument("--only", default=None,
                    help="comma-separated target subset")
    ap.add_argument("--period", type=float, default=10.0,
                    help="clock constraint in ns (default 10.0 = 100 MHz)")
    ap.add_argument("--out", default=None, help="output CSV path")
    args = ap.parse_args()

    if not Path(VIVADO).exists():
        raise SystemExit(f"Vivado not found at {VIVADO}")

    names = list(TARGETS)
    if args.only:
        names = [n.strip() for n in args.only.split(",")]
        for n in names:
            if n not in TARGETS:
                raise SystemExit(f"unknown target {n!r}")

    out_csv = Path(args.out) if args.out else (
        ROOT / "results/member2/hw/memory_hw.csv")
    rpt_dir = out_csv.parent / "reports"
    rpt_dir.mkdir(parents=True, exist_ok=True)

    print(f"Vivado OOC synthesis -- part {PART}, clock constraint "
          f"{args.period:.3f} ns, {len(names)} targets\n")
    fresh = {n: synth_one(n, args.period, rpt_dir) for n in names}

    # Re-running a subset must UPDATE the table, not replace it -- otherwise
    # a targeted re-run silently destroys the results for every other target.
    merged: dict[str, dict] = {}
    if out_csv.exists():
        with open(out_csv, newline="") as fh:
            for old in csv.DictReader(fh):
                merged[old["target"]] = old
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
    print(f"\n{ok}/{len(rows)} targets synthesised; wrote {shown}")


if __name__ == "__main__":
    main()
