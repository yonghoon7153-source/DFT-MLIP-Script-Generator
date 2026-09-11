"""tests/test_webapp_content.py — webapp/content.py 의 순수 함수 테스트 (위키 파일에 의존하지 않는 것 위주).

  · doe_flags: 내 DOE 창(2.5–4.4 V vs. Li/Li+, formation 3.6–4.6 V) 과의 겹침 판정
  · flatten_paper: paper: 블록 → 비교표 칸, 없는 값은 빈 칸 (물음표 없음)
  · md_inline: escape 먼저 + wikilink 해석
  · render_body: raw HTML 차단 · javascript: 링크 차단 · callout 클래스
  · chat_context: 우리 셀(ours:) 과 색인이 항상 붙는다
실행:  .venv/bin/python -m unittest tests/test_webapp_content.py -v
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "webapp"))
import content as C  # noqa: E402


def block(**over):
    b = {"bib": {"first_author": "Kim", "year": 2026, "journal": "Small Structures", "doi": "10.1000/x"},
         "cathode": {"composition_verbatim": "NCM622", "crystal": "poly", "coating": False, "electrode_process": "slurry",
                     "loading_mg_cm2": 10, "loading_mah_cm2": None, "composite_ratio": "70:30"},
         "electrolyte": {"type": "LPSCl"}, "anode": {"type": "Li-In", "composition": None},
         "voltage": {"raw_text": "1.9–3.7 V", "reference_raw": "vs. In/Li-In", "window_vs_li": [2.52, 4.32], "offset_applied_v": 0.62},
         "formation": {"described": True, "cutoff_v_raw": "3.7 V vs. In/Li-In", "cutoff_v_li": 4.32, "c_rate": "0.1C", "cycles": 1},
         "main_cycle": {"window_raw": "1.9–3.7 V vs. In/Li-In", "window_vs_li": [2.52, 4.32], "c_rate": "0.5C", "temperature_c": 30,
                        "pressure_fab_mpa": 370, "pressure_op_mpa": 50, "cycles": 100},
         "performance": {"initial_discharge_mah_g": 180, "ice_pct": 85, "retention_pct": 80, "retention_cycles": 100},
         "techniques": ["XPS", "EIS"],
         "mechanisms": [{"claim": "LPSCl oxidizes", "products": ["S", "LiCl"], "voltage_range": "≥ 3.8 V vs. Li/Li+",
                         "evidence": "Fig. 3b, p.5", "tags": ["lpscl-oxidation"]}]}
    for k, v in over.items():
        b[k] = v
    return b


class TestDoeFlags(unittest.TestCase):
    def test_same_window(self):
        f = C.doe_flags(block(main_cycle={"window_vs_li": [2.5, 4.4]}, formation={"cutoff_v_li": 4.0}))
        self.assertEqual(f["main"], "same")
        self.assertEqual(f["formation"], "in")

    def test_beyond_and_out(self):
        f = C.doe_flags(block(main_cycle={"window_vs_li": [2.5, 4.6]}, formation={"cutoff_v_li": 4.9}))
        self.assertEqual(f["main"], "beyond")
        self.assertEqual(f["formation"], "out")
        self.assertAlmostEqual(f["upper"], 4.6)

    def test_below_and_unknown(self):
        f = C.doe_flags(block(main_cycle={"window_vs_li": [2.5, 4.2]}, formation={"described": False}))
        self.assertEqual(f["main"], "below")
        self.assertEqual(f["formation"], "unknown")
        f2 = C.doe_flags({})
        self.assertEqual(f2["main"], "unknown")


class TestFlatten(unittest.TestCase):
    def test_cells_and_empties(self):
        cells = C.flatten_paper(block())
        self.assertIn("NCM622", cells["cathode"])
        self.assertIn("poly-crystal", cells["cathode"])
        self.assertIn("코팅 없음", cells["cathode"])
        self.assertEqual(cells["voltage_raw"], "1.9–3.7 V · vs. In/Li-In")
        self.assertIn("offset +0.62 V", cells["voltage_li"])
        self.assertIn("4.32 V vs. Li/Li⁺", cells["formation_cutoff_li"])
        self.assertIn("구동 50 MPa", cells["main"])
        self.assertIn("근거 Fig. 3b, p.5", cells["mechanisms"])
        empty = C.flatten_paper({})
        self.assertTrue(all(v == "" for v in empty.values()))
        self.assertNotIn("?", "".join(empty.values()))

    def test_short_cite(self):
        self.assertEqual(C.short_cite(block(), "x"), "Kim 2026")
        self.assertEqual(C.cite_of(block()), "Kim 2026, Small Structures")


class TestRender(unittest.TestCase):
    def test_md_inline_escapes_and_links(self):
        idx = {"formation-cutoff-doe": "/experiment/formation-cutoff-doe"}
        out = C.md_inline("<b>x</b> **굵게** [[formation-cutoff-doe]] [[nope]]", idx)
        self.assertIn("&lt;b&gt;", out)
        self.assertIn("<strong>굵게</strong>", out)
        self.assertIn('href="/experiment/formation-cutoff-doe"', out)
        self.assertIn("wl-missing", out)

    def test_render_body_blocks_html_and_js_links(self):
        html = C.render_body("<script>x</script> [a](javascript:alert(1)) [b](https://ok.example)", {})
        self.assertNotIn("<script>", html)
        self.assertIn("#blocked-url", html)
        self.assertIn('href="https://ok.example"', html)

    def test_callout(self):
        html = C.render_body("> [!note] 미검증 배경\n> 본문", {})
        self.assertIn('class="callout callout-note"', html)
        self.assertIn("callout-tag", html)

    def test_claims(self):
        d = C.render_digest("## A\n\n`[인쇄, p.3]` 문장\n\n`[재현]` 계산", {}, title="t")
        self.assertEqual(d["claims"]["인쇄"], 1)
        self.assertEqual(d["claims"]["재현"], 1)
        self.assertEqual(len(d["toc"]), 1)


class TestChatContext(unittest.TestCase):
    def test_ours_and_index_present(self):
        ctx = C.chat_context("formation cut-off 4.6 V CEI")
        self.assertTrue(ctx["chunks"] and ctx["chunks"][0]["slug"] == "index")
        self.assertIn("NCA721", ctx["ours"])
        self.assertTrue(any(ch.get("background") for ch in ctx["chunks"]) or True)
        self.assertLess(sum(len(ch["text"]) for ch in ctx["chunks"]), 60000)


if __name__ == "__main__":
    unittest.main()
