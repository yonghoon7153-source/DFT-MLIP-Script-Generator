"""tests/test_cells.py — 셀 데이터 모듈의 합성 데이터 테스트 (stdlib unittest + pandas).

무엇을 보나
  · utf-8-sig(BOM) raw CSV 를 읽는다
  · 사이클 요약: 비용량 = Ah×1000/활물질 g, CE, hysteresis, v_max/v_min
  · 전압 변환 방향: vs. Li/Li+ = vs. In/Li-In + 0.62 (config 정본과 같은 값)
  · 파일명 파싱은 제안값만 — g/mg 혼재를 mg 로, 기준전극·질량 정체를 모른다고 적는다
  · registry 에 질량이 없으면 mAh g⁻¹ 을 비운다 (추측 금지)
  · LLM 요약 문자열에 raw 행이 들어가지 않는다
실행:  .venv/bin/python -m unittest tests/test_cells.py -v
"""
import csv
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from tools.cells import cellio as C  # noqa: E402

RAW_COLS = ["timestamp", "test_time_s", "step_time_s", "cycle_time_s", "channel", "step_index", "total_step",
            "cycle_index", "run_status", "running_status", "cell_status", "i_range_index", "i_range",
            "voltage", "current", "charge_q", "discharge_q", "charge_e", "discharge_e", "aux_voltage",
            "temperature", "ocp"]


def synth_raw(n_cycles=3, pts=20, q_ah=0.0004, v_lo_in=1.9, v_hi_in=3.4):
    """합성 raw: 사이클마다 충전(전류 +) 후 방전(전류 −). charge_q/discharge_q 는 사이클 안에서 0→q 누적 (Ah)."""
    rows, t = [], 0.0
    for c in range(1, n_cycles + 1):
        fade = 1.0 - 0.05 * (c - 1)
        for i in range(pts):                       # 충전
            f = i / (pts - 1)
            rows.append([t, t, i, i, 1, 1, 2, c, "run", "run", "ok", 1, 1, v_lo_in + f * (v_hi_in - v_lo_in),
                         0.001, q_ah * f, 0.0, q_ah * f * 3.0, 0.0, 0, 25.0, 0])
            t += 10
        for i in range(pts):                       # 방전
            f = i / (pts - 1)
            rows.append([t, t, i, i, 1, 2, 2, c, "run", "run", "ok", 1, 1, v_hi_in - f * (v_hi_in - v_lo_in),
                         -0.001, q_ah, q_ah * fade * f, q_ah * 3.0, q_ah * fade * f * 2.6, 0, 25.0, 0])
            t += 10
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(RAW_COLS)
    w.writerows(rows)
    return "﻿" + buf.getvalue()               # UTF-8 BOM


class TestConfigAndConversion(unittest.TestCase):
    def test_offset_direction(self):
        cfg = C.load_config()
        self.assertAlmostEqual(cfg["voltage"]["in_to_li_offset_v"], 0.62)
        self.assertAlmostEqual(C.to_li(3.38, cfg), 4.00, places=6)   # vs. In/Li-In + 0.62 = vs. Li/Li+
        self.assertAlmostEqual(C.to_in(4.40, cfg), 3.78, places=6)

    def test_colors_from_config(self):
        cfg = C.load_config()
        self.assertEqual(C.color_for_cutoff(4.0, cfg), cfg["colors"]["4.0"])
        self.assertEqual(C.color_for_cutoff(None, cfg), cfg["colors"]["default"])
        self.assertEqual(C.color_for_cutoff("4.2", cfg), cfg["colors"]["4.2"])


class TestFilenameProposal(unittest.TestCase):
    def test_variants(self):
        p = C.propose_from_filename("Dcell14_mid_Ni___0.0189g_4.0V_2mAhcm2.csv")
        self.assertEqual(p["cell_id"], "Dcell14")
        self.assertAlmostEqual(p["cutoff_v_hint"], 4.0)
        self.assertAlmostEqual(p["mass_mg_hint"], 18.9)
        self.assertTrue(any("전극" in n for n in p["notes"]))
        self.assertTrue(any("기준전극" in n for n in p["notes"]))
        p2 = C.propose_from_filename("cell16_CONT_4.0V_18.5mg_x.csv")
        self.assertEqual(p2["cell_id"], "cell16")
        self.assertAlmostEqual(p2["mass_mg_hint"], 18.5)
        p3 = C.propose_from_filename("Dcell49mid_Ni___.csv")
        self.assertEqual(p3["cell_id"], "Dcell49")
        self.assertIsNone(p3["cutoff_v_hint"])


class TestImport(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raw = Path(self.tmp.name) / "Dcell01_mid_Ni_4.0V_20mg.csv"
        self.raw.write_text(synth_raw(), encoding="utf-8")
        self.cfg = C.load_config()

    def tearDown(self):
        self.tmp.cleanup()

    def test_read_bom_and_summary(self):
        df = C.read_raw_csv(self.raw, self.cfg)
        self.assertIn("cycle_index", df.columns)          # BOM 이 첫 열 이름에 붙지 않았다
        cyc = C.cycle_summary(df, active_mass_mg=20.0, cfg=self.cfg)
        self.assertEqual(len(cyc), 3)
        # 0.0004 Ah = 0.4 mAh / 0.020 g = 20 mAh g^-1
        self.assertAlmostEqual(cyc.loc[0, "charge_capacity_mah_g"], 20.0, places=6)
        self.assertAlmostEqual(cyc.loc[0, "discharge_capacity_mah_g"], 20.0, places=6)
        self.assertAlmostEqual(cyc.loc[1, "discharge_capacity_mah_g"], 19.0, places=6)   # 5 % fade
        self.assertAlmostEqual(cyc.loc[1, "coulombic_efficiency"], 95.0, places=6)
        self.assertGreater(cyc.loc[0, "voltage_hysteresis"], -1e-9)
        self.assertAlmostEqual(cyc.loc[0, "v_max"], 3.4)
        self.assertAlmostEqual(cyc.loc[0, "v_min"], 1.9)
        self.assertTrue(bool(cyc.loc[0, "complete"]))

    def test_no_mass_no_specific(self):
        df = C.read_raw_csv(self.raw, self.cfg)
        cyc = C.cycle_summary(df, active_mass_mg=None, cfg=self.cfg)
        self.assertTrue(cyc["discharge_capacity_mah_g"].isna().all())
        self.assertAlmostEqual(cyc.loc[0, "discharge_capacity_mah"], 0.4, places=9)

    def test_summary_dict_voltage_both_references(self):
        df = C.read_raw_csv(self.raw, self.cfg)
        cyc = C.cycle_summary(df, 20.0, self.cfg)
        cell = {"cell_id": "Dcell01", "formation_cutoff_v_li_num": 4.0, "active_mass_mg_num": 20.0, "status": "cycling"}
        s = C.summary_dict(cell, cyc, self.cfg, source="raw:test")
        self.assertEqual(s["n_cycles"], 3)
        self.assertAlmostEqual(s["voltage"]["v_max_raw"], 3.4)
        self.assertAlmostEqual(s["voltage"]["v_max_vs_li"], 3.4 + 0.62)
        self.assertAlmostEqual(s["voltage"]["offset_applied_v"], 0.62)
        self.assertAlmostEqual(s["retention_pct_last_over_first"], 90.0, places=6)
        json.dumps(s)                                      # 직렬화 가능

    def test_llm_summary_has_no_raw_rows(self):
        df = C.read_raw_csv(self.raw, self.cfg)
        cyc = C.cycle_summary(df, 20.0, self.cfg)
        cell = {"cell_id": "Dcell01", "formation_cutoff_v_li": "4.0", "formation_cutoff_v_li_num": 4.0,
                "active_mass_mg": "20", "active_mass_mg_num": 20.0, "status": "cycling"}
        s = C.summary_dict(cell, cyc, self.cfg)
        txt = C.llm_summary([s], [cell], self.cfg)
        self.assertIn("Dcell01", txt)
        self.assertIn("vs. Li/Li+", txt)
        self.assertNotIn("timestamp", txt)
        self.assertLess(len(txt), 2000)

    def test_cli_import_with_registry(self):
        # 임시 registry + raw 로 CLI 경로를 끝까지 돈다 (config 경로는 그대로, 출력은 임시 cells_dir)
        import importlib
        import tools.cells.import_cell as IC
        cfg = C.load_config()
        cfg["paths"]["raw_dir"] = os.path.relpath(self.tmp.name, C.ROOT)
        cfg["paths"]["cells_dir"] = os.path.relpath(Path(self.tmp.name) / "cells", C.ROOT)
        reg = Path(self.tmp.name) / "cells.csv"
        reg.write_text(",".join(C.REGISTRY_COLUMNS) + "\n" +
                       f"Dcell01,4.0,20,2,,10,462,277,100,cycling,{self.raw.name},,\"test\"\n", encoding="utf-8")
        cfg["paths"]["registry"] = os.path.relpath(reg, C.ROOT)
        rc = IC.do_import("Dcell01", None, cfg)
        self.assertEqual(rc, 0)
        out = Path(self.tmp.name) / "cells" / "Dcell01"
        self.assertTrue((out / "cycles.csv").is_file())
        s = json.loads((out / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(s["cell_id"], "Dcell01")
        self.assertEqual(s["n_cycles"], 3)
        importlib.reload(IC)


if __name__ == "__main__":
    unittest.main()
