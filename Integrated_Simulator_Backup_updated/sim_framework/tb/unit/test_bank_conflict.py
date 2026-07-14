"""Unit tests for bank conflict modelling.

Covers:
  - software_ref  estimate_bank_conflicts() for all num_banks sweep points
  - SimConfig num_banks field and its propagation to verilator_params /
    cocotb_env
  - Invariant checks (num_banks=1 → zero conflicts always)

Cocotb RTL tests (guarded by COCOTB_AVAILABLE):
  - flat baseline: no conflicts regardless of address pattern
  - 4-bank same-bank access: all N_PORTS target bank 0 → N_PORTS-1 stalls
  - 4-bank no-conflict: ports target distinct banks → no stall
"""
from __future__ import annotations

try:
    import cocotb
    from cocotb.triggers import RisingEdge
    COCOTB_AVAILABLE = True
except ImportError:
    COCOTB_AVAILABLE = False

import pytest
from pysim.sim_config import SimConfig
from pysim.software_ref import estimate_bank_conflicts, run_software_ref


# ---------------------------------------------------------------------------
# Software-ref: estimate_bank_conflicts()
# ---------------------------------------------------------------------------

class TestEstimateBankConflicts:
    """Invariant and monotonicity checks for the analytical estimate."""

    def test_flat_single_bank_always_zero(self):
        """num_banks=1 must produce zero conflict cycles and zero stall cycles."""
        for n_ports in range(1, 9):
            bc, sc = estimate_bank_conflicts(10_000, n_ports, num_banks=1)
            assert bc == 0, f"num_banks=1 n_ports={n_ports}: expected 0 conflict cycles, got {bc}"
            assert sc == 0, f"num_banks=1 n_ports={n_ports}: expected 0 stall cycles, got {sc}"

    def test_single_port_always_zero(self):
        """A single read port can never conflict with itself."""
        for num_banks in [2, 4, 8, 16]:
            bc, sc = estimate_bank_conflicts(10_000, n_ports=1, num_banks=num_banks)
            assert bc == 0
            assert sc == 0

    def test_conflict_cycles_nonnegative(self):
        for n_ports in [2, 4, 8]:
            for num_banks in [2, 4, 8, 16]:
                bc, sc = estimate_bank_conflicts(5_000, n_ports, num_banks)
                assert bc >= 0
                assert sc >= 0

    def test_more_banks_fewer_conflicts(self):
        """Doubling the banks should reduce estimated conflict cycles."""
        bc4, _ = estimate_bank_conflicts(100_000, n_ports=4, num_banks=4)
        bc8, _ = estimate_bank_conflicts(100_000, n_ports=4, num_banks=8)
        assert bc8 <= bc4, (
            f"Expected fewer conflicts with 8 banks than 4 banks, "
            f"got {bc8} vs {bc4}"
        )

    def test_more_ports_more_conflicts(self):
        """More simultaneous ports on the same bank count → more conflicts."""
        bc2, _ = estimate_bank_conflicts(100_000, n_ports=2, num_banks=4)
        bc4, _ = estimate_bank_conflicts(100_000, n_ports=4, num_banks=4)
        assert bc4 >= bc2, (
            f"Expected more conflicts with 4 ports than 2 ports on 4 banks, "
            f"got {bc4} vs {bc2}"
        )

    def test_zero_cycles_gives_zero(self):
        bc, sc = estimate_bank_conflicts(0, n_ports=4, num_banks=4)
        assert bc == 0
        assert sc == 0

    def test_stall_port_cycles_geq_conflict_cycles(self):
        """Each conflict cycle has ≥1 stalled port, so stall_ports ≥ conflict_cycles."""
        bc, sc = estimate_bank_conflicts(50_000, n_ports=4, num_banks=4)
        assert sc >= bc


# ---------------------------------------------------------------------------
# SimConfig: num_banks field and its mapping to RTL / env
# ---------------------------------------------------------------------------

class TestSimConfigBankKnob:

    def test_default_num_banks_is_4(self):
        cfg = SimConfig()
        assert cfg.num_banks == 4

    def test_num_banks_in_verilator_params(self):
        cfg = SimConfig(num_banks=8)
        params = cfg.verilator_params()
        assert "-GNUM_BANKS=8" in params

    def test_num_banks_1_in_verilator_params(self):
        cfg = SimConfig(num_banks=1)
        assert "-GNUM_BANKS=1" in cfg.verilator_params()

    def test_num_banks_in_cocotb_env(self):
        cfg = SimConfig(num_banks=2)
        env = cfg.cocotb_env()
        assert env["SIM_NUM_BANKS"] == "2"

    def test_num_banks_survives_yaml_roundtrip(self, tmp_path):
        cfg = SimConfig(num_banks=8)
        p = str(tmp_path / "cfg.yaml")
        cfg.to_yaml(p)
        cfg2 = SimConfig.from_yaml(p)
        assert cfg2.num_banks == 8

    def test_num_banks_affects_config_hash(self):
        cfg4 = SimConfig(num_banks=4)
        cfg8 = SimConfig(num_banks=8)
        assert cfg4.hash() != cfg8.hash()


# ---------------------------------------------------------------------------
# software_ref integration: bank conflict stats appear in run output
# ---------------------------------------------------------------------------

class TestSoftRefBankConflictStats:

    def test_stats_keys_present(self):
        cfg = SimConfig(num_banks=4)
        result = run_software_ref(cfg)
        assert "num_banks" in result.stats
        assert "bank_conflict_cycles_est" in result.stats
        assert "bank_conflict_stall_ports_est" in result.stats

    def test_flat_baseline_zero_stats(self):
        cfg = SimConfig(num_banks=1)
        result = run_software_ref(cfg)
        assert result.stats["bank_conflict_cycles_est"] == 0
        assert result.stats["bank_conflict_stall_ports_est"] == 0

    def test_4bank_nonzero_stats(self):
        cfg = SimConfig(num_banks=4, n_mem_ports=4)
        result = run_software_ref(cfg)
        assert result.stats["bank_conflict_cycles_est"] >= 0
        assert result.stats["bank_conflict_stall_ports_est"] >= 0

    def test_backend_tag_present(self):
        cfg = SimConfig()
        result = run_software_ref(cfg)
        assert result.stats.get("backend") == "software_ref"


# ---------------------------------------------------------------------------
# Cocotb RTL tests (require Verilator + cocotb)
# ---------------------------------------------------------------------------

if COCOTB_AVAILABLE:

    @cocotb.test()
    async def test_flat_no_conflict(dut):
        """NUM_BANKS=1: concurrent same-address reads must never set conflict."""
        dut.rst_n.value = 0
        for _ in range(3):
            await RisingEdge(dut.clk)
        dut.rst_n.value = 1

        # Drive all ports to address 0 -- would conflict in a banked design
        N = int(dut.N_PORTS.value)
        dut.rd_en.value  = (1 << N) - 1
        for i in range(N):
            dut.rd_addr[i].value = 0
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

        assert dut.bank_conflict_detected.value == 0, (
            "NUM_BANKS=1: expected no conflict when all ports hit addr 0"
        )
        assert int(dut.stats_bank_conflicts.value) == 0

    @cocotb.test()
    async def test_4bank_all_same_bank_conflict(dut):
        """NUM_BANKS=4: all ports address words 0,4,8,12 (all in bank 0) → conflict."""
        dut.rst_n.value = 0
        for _ in range(3):
            await RisingEdge(dut.clk)
        dut.rst_n.value = 1

        N = int(dut.N_PORTS.value)
        dut.rd_en.value = (1 << N) - 1
        for i in range(N):
            dut.rd_addr[i].value = i * 4   # addresses 0,4,8,12 → all bank 0 (addr[1:0]=0)
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

        assert dut.bank_conflict_detected.value == 1, (
            "NUM_BANKS=4: expected conflict when all ports hit bank 0"
        )
        assert int(dut.stats_bank_conflicts.value) >= 1

    @cocotb.test()
    async def test_4bank_distinct_banks_no_conflict(dut):
        """NUM_BANKS=4: ports 0-3 address words 0,1,2,3 (banks 0,1,2,3) → no conflict."""
        dut.rst_n.value = 0
        for _ in range(3):
            await RisingEdge(dut.clk)
        dut.rst_n.value = 1

        N = int(dut.N_PORTS.value)
        dut.rd_en.value = (1 << N) - 1
        for i in range(N):
            dut.rd_addr[i].value = i   # addresses 0,1,2,3 → banks 0,1,2,3
        await RisingEdge(dut.clk)
        await RisingEdge(dut.clk)

        assert dut.bank_conflict_detected.value == 0, (
            "NUM_BANKS=4: expected no conflict when each port hits a distinct bank"
        )
