"""CSV / XLSX output shapes."""

import csv
import io

import pytest

from wrdkit import (
    Basis,
    CellSpec,
    cycles_csv_string,
    extract_profile,
    profiles_csv_string,
    raw_csv_string,
    read_wrd_bytes,
    report_txt_string,
    summarize_cycles,
)
from wrdkit.export import REPORT_COLUMNS, REPORT_UNSOURCED

import synthetic


@pytest.fixture
def cell():
    return CellSpec(total_mass_mg=31.6, active_wt_percent=80, diameter_mm=13).resolve()


def _rows(text):
    return list(csv.reader(io.StringIO(text)))


def test_raw_csv_has_one_row_per_sample_plus_a_header(synthetic_wrd):
    rows = _rows(raw_csv_string(synthetic_wrd))
    assert len(rows) == len(synthetic_wrd) + 1
    assert rows[0][:4] == ["timestamp", "test_time_s", "step_time_s", "cycle_time_s"]


def test_raw_csv_converts_ticks_to_seconds(synthetic_wrd):
    rows = _rows(raw_csv_string(synthetic_wrd))
    assert float(rows[1][1]) == pytest.approx(0.0)
    assert float(rows[2][1]) == pytest.approx(10.0)


def test_raw_csv_drops_the_tick_columns_it_replaced(synthetic_wrd):
    header = _rows(raw_csv_string(synthetic_wrd))[0]
    assert "date_time" not in header
    assert "test_time" not in header
    assert "voltage" in header and "i_range" in header


def test_raw_csv_labels_the_capacity_and_energy_units(synthetic_wrd):
    header = _rows(raw_csv_string(synthetic_wrd))[0]
    assert "charge_q (Ah)" in header
    assert "discharge_q (Ah)" in header
    assert "charge_e (Wh)" in header


def test_raw_csv_labels_a_coulomb_file_differently(synthetic_bytes):
    """UnitCoulomb decides the unit per file; identical headers hide a x3600."""
    from wrdkit import read_wrd_bytes

    coulomb = read_wrd_bytes(synthetic_bytes, source_name="coulomb.wrd")
    coulomb.metadata.unit_coulomb = True
    header = _rows(raw_csv_string(coulomb))[0]
    assert "charge_q (C)" in header
    assert "charge_e (J)" in header
    assert "charge_q (Ah)" not in header


def test_cycles_csv_labels_the_basis(synthetic_wrd, cell):
    rows = _rows(cycles_csv_string(summarize_cycles(synthetic_wrd), cell,
                                   basis=Basis.SPECIFIC))
    assert "discharge_capacity (mAh/g)" in rows[0]
    assert "discharge_capacity (mAh)" in rows[0]  # absolute kept alongside
    assert len(rows) == 4  # header + 3 cycles


def test_cycles_csv_values_are_normalised(synthetic_wrd, cell):
    rows = _rows(cycles_csv_string(summarize_cycles(synthetic_wrd), cell,
                                   basis=Basis.SPECIFIC))
    header, first = rows[0], rows[1]
    column = header.index("discharge_capacity (mAh/g)")
    assert float(first[column]) == pytest.approx(5.0 / 0.02528, rel=1e-4)


def test_cycles_csv_falls_back_to_mah_when_the_basis_is_unavailable(synthetic_wrd):
    bare = CellSpec().resolve()
    rows = _rows(cycles_csv_string(summarize_cycles(synthetic_wrd), bare,
                                   basis=Basis.SPECIFIC))
    assert "discharge_capacity (mAh)" in rows[0]
    assert "discharge_capacity (mAh/g)" not in rows[0]


def test_profiles_csv_puts_each_branch_in_its_own_column_pair(synthetic_wrd, cell):
    cycles = summarize_cycles(synthetic_wrd)
    profiles = [extract_profile(synthetic_wrd, cycles[0], "charge"),
                extract_profile(synthetic_wrd, cycles[0], "discharge")]
    rows = _rows(profiles_csv_string(profiles, cell, basis=Basis.SPECIFIC))
    assert rows[0] == [
        "cycle1_charge_capacity (mAh/g)", "cycle1_charge_voltage (V)",
        "cycle1_discharge_capacity (mAh/g)", "cycle1_discharge_voltage (V)",
    ]
    assert len(rows) == 41  # header + 40 points


def test_profiles_csv_pads_uneven_columns(synthetic_wrd, cell):
    cycles = summarize_cycles(synthetic_wrd)
    long_profile = extract_profile(synthetic_wrd, cycles[0], "charge")
    short = extract_profile(synthetic_wrd, cycles[0], "discharge")
    short.capacity_mah = short.capacity_mah[:5]
    short.voltage = short.voltage[:5]
    rows = _rows(profiles_csv_string([long_profile, short], cell))
    assert rows[10][2] == ""  # short column is blank past its end
    assert rows[10][0] != ""


def test_xlsx_export_writes_every_sheet(tmp_path, synthetic_wrd, cell):
    openpyxl = pytest.importorskip("openpyxl")
    from wrdkit import write_xlsx

    cycles = summarize_cycles(synthetic_wrd)
    profiles = [extract_profile(synthetic_wrd, cycles[0], "discharge")]
    target = tmp_path / "out.xlsx"
    write_xlsx(target, synthetic_wrd, cycles, profiles, cell, basis=Basis.SPECIFIC)

    book = openpyxl.load_workbook(target)
    assert book.sheetnames == ["metadata", "cycles", "profiles"]
    assert book["cycles"].max_row == 4


# --- 미완료 사이클은 기본적으로 나가지 않는다 --------------------------------
#
# 구동 중인 셀의 마지막 사이클은 스텝 중간에서 잘려 있다. 그 용량은 파일이
# 쓰인 순간까지 쌓인 값이라, 측정값처럼 보이지만 측정값이 아니다. API 는 이미
# 빼고 있었는데 라이브러리 CSV 는 그대로 내보내, wrdkit convert 로 만든
# 스프레드시트의 마지막 줄이 셀을 실제보다 나쁘게 보이게 했다.

def _two_cycles():
    from wrdkit.cycles import CycleSummary

    done = CycleSummary(cycle_index=0, cycle_number=1, start=0, stop=10)
    done.charge_capacity_mah = 5.0
    done.discharge_capacity_mah = 4.9
    done.charge_energy_wh = 0.019
    done.discharge_energy_wh = 0.018
    done.mean_charge_voltage = 3.9
    done.mean_discharge_voltage = 3.7
    done.voltage_max = 4.3
    done.voltage_min = 2.5
    done.complete = True

    # 잘린 사이클도 전압을 들고 있다.  파일이 끝난 순간까지의 평균이고, 아직
    # 도달하지 못한 극값이다 — 비우지 않으면 그대로 측정값처럼 나간다.
    cut = CycleSummary(cycle_index=1, cycle_number=2, start=10, stop=15)
    cut.charge_capacity_mah = 1.2      # 아직 쌓이는 중이었다
    cut.discharge_capacity_mah = 0.0
    cut.charge_energy_wh = 0.004
    cut.discharge_energy_wh = 0.0
    cut.mean_charge_voltage = 3.6
    cut.mean_discharge_voltage = 3.5
    cut.voltage_max = 3.7
    cut.voltage_min = 3.4
    cut.complete = False
    return [done, cut]


def test_a_cut_off_cycle_is_left_out_by_default():
    import io

    from wrdkit.export import write_cycles_csv

    stream = io.StringIO()
    write_cycles_csv(_two_cycles(), CellSpec().resolve(), stream)
    rows = stream.getvalue().strip().split("\n")
    assert len(rows) == 2, "헤더 + 완료된 사이클 1줄이어야 한다"
    assert rows[1].startswith("1,")


def test_keeping_it_blanks_the_numbers_rather_than_publishing_them():
    """opt-in 해도 숫자는 비운다 — 숫자 칸의 부분값은 측정값으로 읽힌다.

    전압도 마찬가지다.  평균 전압은 E/Q 라 잘린 구간의 부분값이고, v_max/v_min
    은 아직 도달하지 못한 극값이며, 이력은 두 평균의 차다.  남는 것은 파일에
    무엇이 들어 있는지를 말하는 칸뿐이다 — 사이클 번호, 시간, 점 수, complete.
    """
    import csv
    import io

    from wrdkit.export import write_cycles_csv

    stream = io.StringIO()
    write_cycles_csv(_two_cycles(), CellSpec().resolve(), stream,
                     include_incomplete=True)
    rows = list(csv.DictReader(io.StringIO(stream.getvalue())))
    assert len(rows) == 2
    cut = rows[1]
    assert cut["cycle"] == "2"
    assert cut["complete"] == "no", "complete 칸은 남아 있어야 한다"

    keep = {"cycle", "duration (h)", "points", "complete"}
    filled = {name: value for name, value in cut.items()
              if name not in keep and value != ""}
    assert not filled, f"잘린 사이클의 값이 그대로 나갔다: {filled}"

    # 완료된 사이클은 손대지 않는다.
    assert rows[0]["cycle"] == "1"
    assert rows[0]["discharge_capacity (mAh)"] != ""


def test_the_csv_carries_the_value_not_a_rounded_one():
    """내보내는 숫자는 **원래 값**이다.  보기 좋게 자르는 것은 화면이 한다.

    실제로 일어난 일: 예전 서식이 `.6g` 였고, 그것이 값을 바꿨다.

      쿨롱효율 99.9999666...%  ->  `100`      (100 미만인데 100 으로 읽힌다)
      용량 1234.56789 mAh      ->  `1234.57`  (소수 둘째 자리에서 잘린다)

    다른 도구(Smart Interface 의 엑셀)와 맞춰 보다 어긋나면, 그 차이가 어디서
    왔는지 되짚을 수 없게 된다 -- 우리가 이미 지워 버린 자리이므로.
    """
    import io

    from wrdkit.cycles import CycleSummary
    from wrdkit.export import write_cycles_csv

    cycle = CycleSummary(cycle_index=0, cycle_number=1, start=0, stop=10)
    # 효율이 100 에 아주 가깝지만 100 은 아닌 값 (2.999999 / 3.0).
    cycle.charge_capacity_mah = 3.0
    cycle.discharge_capacity_mah = 2.999999
    cycle.charge_energy_wh = 1.23456789012
    cycle.discharge_energy_wh = 1.2
    cycle.mean_charge_voltage = 3.9
    cycle.mean_discharge_voltage = 3.7
    cycle.voltage_max = 4.3
    cycle.voltage_min = 2.5
    cycle.complete = True

    stream = io.StringIO()
    write_cycles_csv([cycle], CellSpec().resolve(), stream)
    header, row = stream.getvalue().strip().split("\n")
    # strict -- 열 수가 어긋나면 그것부터가 결함이다 (조용히 잘라 내지 않는다).
    cells = dict(zip(header.split(","), row.split(","), strict=True))

    efficiency = cells["coulombic_efficiency (%)"]
    assert efficiency != "100", "100 미만인 효율이 100 으로 나가면 안 된다"
    assert float(efficiency) == pytest.approx(99.9999666667, abs=1e-9)

    # 잘리지 않았는지: 12 유효숫자면 이 값이 그대로 돌아온다.
    assert float(cells["discharge_capacity (mAh)"]) == pytest.approx(2.999999, abs=1e-12)
    assert float(cells["charge_energy (mWh)"]) == pytest.approx(1234.56789012, abs=1e-8)

    # 그러면서 없던 자리는 지어내지 않는다 -- float 잡음이 새어 나오면 안 된다.
    assert "0000000000" not in row, f"부동소수 잡음이 새어 나왔다: {row}"


# --- 계측기 형식의 "일반 데이터 보고서" ------------------------------------------
#
# 랩에는 이 표를 받는 매크로가 이미 있다.  워크벤치가 원본을 들고 있으면서 이
# 표를 못 내주면 `.wrd` 를 도로 내려받아 계측기 PC 에서 다시 뽑는 왕복이 남고,
# 중추 서버를 둔 이유가 거기서 깨진다.
#
# 파생 열의 규칙은 실측 보고서(`260823_PE#1 ... _005_DC.txt`, 22만 행)에서
# 확인했다.  아래 숫자는 그 파일에서 그대로 따온 것이다.


def _report(text):
    head, _, body = text.partition("\n\n")
    lines = body.rstrip("\n").split("\n")
    return head.split("\n"), lines[0].split("\t"), [r.split("\t") for r in lines[1:]]


def test_the_header_row_is_the_instrument_s_own_columns(synthetic_wrd):
    _, header, _ = _report(report_txt_string(synthetic_wrd))
    assert header == list(REPORT_COLUMNS)


def test_one_row_per_sample(synthetic_wrd):
    _, _, rows = _report(report_txt_string(synthetic_wrd))
    assert len(rows) == len(synthetic_wrd)
    assert [r[0] for r in rows[:3]] == ["1", "2", "3"]


def test_time_is_the_instrument_s_duration_shape_not_seconds(synthetic_wrd):
    """헤더는 `(s)` 라고 적혀 있지만 값은 `d:hh:mm:ss.fff` 다.

    실측 파일이 그렇다 (`0:00:10:00.350`).  이름을 믿고 초로 파싱하면 이미
    틀리므로, 우리도 이름이 아니라 **값의 모양**을 맞춘다.
    """
    _, _, rows = _report(report_txt_string(synthetic_wrd))
    assert rows[0][1].count(":") == 3
    assert rows[0][1].split(".")[-1].isdigit() and len(rows[0][1].split(".")[-1]) == 3


def test_numbers_carry_a_three_digit_exponent(synthetic_wrd):
    """`3.85406E-004` — 파이썬 기본은 두 자리(`E-04`) 라 그대로 두면 어긋난다."""
    _, _, rows = _report(report_txt_string(synthetic_wrd))
    voltage = rows[0][7]
    assert "E" in voltage
    assert len(voltage.split("E")[1]) == 4        # 부호 + 세 자리


def test_power_is_current_times_voltage(synthetic_wrd):
    _, header, rows = _report(report_txt_string(synthetic_wrd))
    i, v, p = (header.index(c) for c in ("Current(A)", "Voltage(V)", "Power(W)"))
    row = next(r for r in rows if float(r[i]) != 0.0)
    assert float(row[p]) == pytest.approx(float(row[i]) * float(row[v]), rel=1e-4)


def test_load_is_voltage_over_current_and_zero_at_rest(synthetic_wrd):
    """휴지 구간에서 보고서는 0 을 쓴다 — 무한대가 아니라.

    나눗셈을 그대로 두면 `inf` 가 되고, 그 칸을 읽는 쪽에서 숫자가 아니게 된다.
    """
    _, header, rows = _report(report_txt_string(synthetic_wrd))
    i, v, load = (header.index(c) for c in ("Current(A)", "Voltage(V)", "Load(Ohm)"))
    moving = next(r for r in rows if float(r[i]) != 0.0)
    assert float(moving[load]) == pytest.approx(float(moving[v]) / float(moving[i]), rel=1e-4)
    resting = next(r for r in rows if float(r[i]) == 0.0)
    assert float(resting[load]) == 0.0


def test_accumulated_charge_does_not_reset_at_a_cycle_boundary():
    """`Acc.Q` 는 시험 전체에 걸친 부호 있는 누적이다.

    실측: 1사이클 끝 1.86033E-004 → 2사이클 첫 행 1.86076E-004 로 **이어진다.**
    계측기의 `CHARGE Q`/`DISCHARGE Q` 는 사이클마다 0 이 되므로(§3), 지나간
    사이클의 순증분을 더해 이어 붙이지 않으면 여기서 톱니가 생긴다.
    """
    wrd = read_wrd_bytes(synthetic.build_wrd(synthetic.make_cycles(3, 20)))
    _, header, rows = _report(report_txt_string(wrd))
    acc = header.index("Acc.Q(Ah)")
    cyc = header.index("Cycle_No.")
    starts = [n for n, r in enumerate(rows) if n and r[cyc] != rows[n - 1][cyc]]
    assert starts, "사이클이 하나뿐이면 이 시험이 아무것도 안 본다"
    for n in starts:
        before, after = float(rows[n - 1][acc]), float(rows[n][acc])
        # 경계에서 0 으로 떨어지지 않는다.  방전으로 끝났으므로 값 자체는
        # 작지만, 그 작은 값이 **이어져야** 한다.
        assert after == pytest.approx(before, abs=1e-6), f"{n} 행에서 누적이 끊겼다"


def test_step_charge_restarts_at_every_step():
    """`|Q|` 는 그 스텝 안에서 움직인 전하다.  스텝이 바뀌면 0 부터 다시 센다."""
    wrd = read_wrd_bytes(synthetic.build_wrd(synthetic.make_cycles(2, 20)))
    _, header, rows = _report(report_txt_string(wrd))
    q = header.index("|Q|(Ah)")
    step = header.index("Step_No.")
    starts = [n for n, r in enumerate(rows) if n and r[step] != rows[n - 1][step]]
    assert starts
    for n in starts:
        # 스텝의 첫 행은 경계에서 그 표본까지 흐른 만큼이지 0 이 아니다 --
        # 0 으로 두면 첫 표본의 몫이 표에서 사라진다 (실측 보고서는 스텝 첫
        # 행에 1.07095E-007 을 적는다).  직전 스텝의 총량보다는 작아야 한다.
        assert abs(float(rows[n][q])) < abs(float(rows[n - 1][q])) + 1e-12


def test_columns_the_wrd_cannot_source_are_blank_not_zero(synthetic_wrd):
    """0 을 적으면 "쟀는데 0 이었다" 로 읽힌다 — §0.4 가 금지하는 짓이다.

    계측기의 보고서도 `IR(ohm)` 을 빈칸으로 두므로 빈칸은 이 형식의 어휘 안에
    있다.
    """
    head, header, rows = _report(report_txt_string(synthetic_wrd))
    for name in REPORT_UNSOURCED:
        assert rows[0][header.index(name)] == "", f"{name} 이 비어 있지 않다"
    # 왜 비었는지도 적는다.  안 적으면 "빠뜨렸나" 로 읽힌다.
    assert any("빈 열" in line for line in head)


def test_the_header_block_says_how_many_rows(synthetic_wrd):
    """계측기는 `데이터 개수 : -1` 을 적는다 (세지 않는다).  우리는 센다."""
    head, _, rows = _report(report_txt_string(synthetic_wrd))
    line = next(line for line in head if "데이터 개수" in line)
    assert line.endswith(str(len(rows)))
