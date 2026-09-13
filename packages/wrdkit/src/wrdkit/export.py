"""Write parsed data out in the shapes a battery lab pastes into Origin.

Three tables, because three different questions get asked of the same file:

``raw``       every sample, with ticks converted to seconds and a readable
              timestamp -- the direct replacement for hand-exporting from
              Smart Interface;
``cycles``    one row per cycle with capacities in the chosen basis -- what
              goes into a retention or coulombic-efficiency plot;
``profiles``  capacity/voltage column pairs per selected cycle, side by side
              -- the layout Origin wants for an overlay plot.
"""

from __future__ import annotations

import csv
import datetime
import io
from collections.abc import Iterable, Sequence
from typing import TextIO

import numpy as np

from .cycles import CycleSummary, Profile
from .dva import DifferentialVoltage
from .ica import DifferentialCapacity
from .normalize import Basis, ResolvedCell, normalize_capacity, normalize_per_capacity
from .wrd import WrdFile

__all__ = [
    "write_raw_csv", "write_cycles_csv", "write_profiles_csv", "write_dqdv_csv",
    "write_dvdq_csv", "write_report_txt", "raw_csv_string", "cycles_csv_string",
    "profiles_csv_string", "dqdv_csv_string", "dvdq_csv_string",
    "report_txt_string", "REPORT_COLUMNS", "REPORT_UNSOURCED", "write_xlsx",
]

_UNIX_OFFSET = 62_135_596_800.0

#: Raw columns whose unit is decided per file by the ``UnitCoulomb`` flag,
#: as ``(flag off, flag on)``.  The raw table dumps them in the file's own
#: units, so without a tag an Ah file and a C file produce identical headers
#: and a reader who assumes Ah is off by 3600.
_FILE_DEPENDENT_UNITS = {
    "charge_q": ("Ah", "C"),
    "discharge_q": ("Ah", "C"),
    "charge_e": ("Wh", "J"),
    "discharge_e": ("Wh", "J"),
}


def _format_timestamp(seconds: float) -> str:
    try:
        return datetime.datetime.utcfromtimestamp(seconds).isoformat(sep=" ", timespec="milliseconds")
    except (OverflowError, OSError, ValueError):
        return ""


def write_raw_csv(wrd: WrdFile, stream: TextIO, *, columns: Sequence[str] | None = None) -> None:
    """Every sample, one row per line, with derived time columns up front."""
    data = wrd.data
    names = list(columns) if columns else list(data)
    writer = csv.writer(stream, lineterminator="\n")

    derived = ["timestamp", "test_time_s", "step_time_s", "cycle_time_s"]
    body = [n for n in names if n not in ("date_time", "test_time", "step_time", "cycle_time")]
    header = derived + [_raw_label(n, wrd) for n in body]
    writer.writerow(header)

    timestamps = wrd.timestamps() if "date_time" in data else None
    test_s = wrd.seconds("test_time") if "test_time" in data else None
    step_s = wrd.seconds("step_time") if "step_time" in data else None
    cycle_s = wrd.seconds("cycle_time") if "cycle_time" in data else None

    columns_out = [data[n] for n in body]

    for i in range(len(wrd)):
        row = [
            _format_timestamp(float(timestamps[i])) if timestamps is not None else "",
            f"{test_s[i]:.4f}" if test_s is not None else "",
            f"{step_s[i]:.4f}" if step_s is not None else "",
            f"{cycle_s[i]:.4f}" if cycle_s is not None else "",
        ]
        for values in columns_out:
            value = values[i]
            row.append(f"{value:.10g}" if isinstance(value, (float, np.floating)) else value)
        writer.writerow(row)


def _raw_label(name: str, wrd: WrdFile) -> str:
    """Column header for the raw table, carrying the unit when it can vary."""
    choices = _FILE_DEPENDENT_UNITS.get(name)
    if choices is None:
        return name
    declared = next((c.unit for c in wrd.metadata.columns if c.name == name and c.unit), "")
    return f"{name} ({declared or choices[1 if wrd.metadata.unit_coulomb else 0]})"


def write_cycles_csv(cycles: Iterable[CycleSummary], cell: ResolvedCell,
                     stream: TextIO, *, basis: str = Basis.ABSOLUTE,
                     include_absolute: bool = True,
                     include_incomplete: bool = False) -> None:
    """One row per cycle, capacities expressed in *basis*.

    Incomplete cycles are left out by default.  The last cycle of a running
    cell is cut off mid-step, so its capacity is whatever had accumulated when
    the file was written -- a number that looks like a measurement and is not
    one (non-negotiable: never report it).  The API already excluded them; this
    writer did not, so `wrdkit convert` and the Python API handed out a
    spreadsheet whose final row understates the cell.

    Pass ``include_incomplete=True`` to keep those rows for inspection.  They
    come back with their capacity, energy and efficiency columns blank rather
    than filled, because a partial number in a numeric column is read as a
    measurement no matter what the ``complete`` column says.
    """
    cycles = list(cycles)
    if not include_incomplete:
        cycles = [c for c in cycles if c.complete]
    writer = csv.writer(stream, lineterminator="\n")

    usable = basis if cell.divisor(basis) else Basis.ABSOLUTE
    unit = usable.replace("mAh", "").strip("/") or ""
    suffix = f" ({usable})"

    header = ["cycle", "charge_capacity" + suffix, "discharge_capacity" + suffix,
              "coulombic_efficiency (%)"]
    if include_absolute and usable != Basis.ABSOLUTE:
        header += ["charge_capacity (mAh)", "discharge_capacity (mAh)"]
    header += ["charge_energy (mWh)", "discharge_energy (mWh)", "energy_efficiency (%)",
               "mean_charge_voltage (V)", "mean_discharge_voltage (V)",
               "voltage_hysteresis (V)", "v_max (V)", "v_min (V)",
               "duration (h)", "points", "complete"]
    writer.writerow(header)
    del unit

    for cycle in cycles:
        # 무엇을 비우는가.  잘린 사이클에서 *측정처럼 보이는* 값은 전부 비운다:
        # 용량과 에너지는 파일이 끝난 순간까지 쌓인 부분값이고, 효율은 그 둘의
        # 비이며, 평균 전압은 E/Q 라 마찬가지다.  이력은 두 평균의 차라 역시
        # 부분값이고, v_max/v_min 은 아직 도달하지 못한 극값이다.
        #
        # 남기는 것: 사이클 번호, 시간, 점 수, complete 칸.  이것들은 파일에
        # 무엇이 들어 있는지를 정직하게 말할 뿐 셀의 성능을 주장하지 않는다 —
        # 진단하려고 opt-in 한 사람이 보려는 것이 바로 그것이다.
        blank = not cycle.complete
        charge = normalize_capacity(cycle.charge_capacity_mah, cell, usable)
        discharge = normalize_capacity(cycle.discharge_capacity_mah, cell, usable)
        row = [cycle.cycle_number,
               "" if blank else f"{charge:.12g}",
               "" if blank else f"{discharge:.12g}",
               "" if blank else _fmt(cycle.coulombic_efficiency)]
        if include_absolute and usable != Basis.ABSOLUTE:
            row += ["", ""] if blank else [
                f"{cycle.charge_capacity_mah:.12g}",
                f"{cycle.discharge_capacity_mah:.12g}"]
        row += [
            "" if blank else f"{cycle.charge_energy_wh * 1000:.12g}",
            "" if blank else f"{cycle.discharge_energy_wh * 1000:.12g}",
            "" if blank else _fmt(cycle.energy_efficiency),
            "" if blank else _fmt(cycle.mean_charge_voltage),
            "" if blank else _fmt(cycle.mean_discharge_voltage),
            "" if blank else _fmt(cycle.voltage_hysteresis),
            "" if blank else _fmt(cycle.voltage_max),
            "" if blank else _fmt(cycle.voltage_min),
            f"{cycle.duration_s / 3600:.12g}", cycle.n_points,
            "yes" if cycle.complete else "no",
        ]
        writer.writerow(row)


def write_profiles_csv(profiles: Sequence[Profile], cell: ResolvedCell,
                       stream: TextIO, *, basis: str = Basis.ABSOLUTE) -> None:
    """Capacity/voltage column pairs, one pair per profile, side by side."""
    writer = csv.writer(stream, lineterminator="\n")
    usable = basis if cell.divisor(basis) else Basis.ABSOLUTE

    header: list[str] = []
    columns: list[np.ndarray] = []
    for profile in profiles:
        tag = f"cycle{profile.cycle_number}_{profile.branch}"
        header += [f"{tag}_capacity ({usable})", f"{tag}_voltage (V)"]
        columns += [normalize_capacity(profile.capacity_mah, cell, usable), profile.voltage]

    writer.writerow(header or ["capacity", "voltage"])
    depth = max((len(c) for c in columns), default=0)
    for i in range(depth):
        row = []
        for values in columns:
            row.append(f"{values[i]:.12g}" if i < len(values) else "")
        writer.writerow(row)


def write_dqdv_csv(curves: Sequence[DifferentialCapacity], cell: ResolvedCell,
                   stream: TextIO, *, basis: str = Basis.ABSOLUTE) -> None:
    """Voltage/dQdV column pairs, one pair per curve, side by side.

    Laid out like the profile CSV so the two open the same way in the same
    spreadsheet -- somebody comparing a capacity curve against its derivative
    should not have to learn a second layout.

    Unusable curves are written as an empty pair rather than skipped.  A
    reader counting columns against the cycles they asked for would otherwise
    silently line up cycle 51's data under cycle 30's header.
    """
    writer = csv.writer(stream, lineterminator="\n")
    usable = basis if cell.divisor(basis) else Basis.ABSOLUTE
    # mAh/V divided by grams is (mAh/g)/V.  The same divisor, one more slash.
    unit = f"{usable}/V"

    header: list[str] = []
    columns: list[np.ndarray] = []
    for curve in curves:
        tag = f"cycle{curve.cycle_number}_{curve.branch}"
        header += [f"{tag}_voltage (V)", f"{tag}_dQdV ({unit})"]
        columns += [curve.voltage, normalize_capacity(curve.dq_dv, cell, usable)]

    writer.writerow(header or ["voltage", "dQdV"])
    depth = max((len(c) for c in columns), default=0)
    for i in range(depth):
        row = []
        for values in columns:
            row.append(f"{values[i]:.12g}" if i < len(values) else "")
        writer.writerow(row)


def write_dvdq_csv(curves: Sequence[DifferentialVoltage], cell: ResolvedCell,
                   stream: TextIO, *, basis: str = Basis.ABSOLUTE) -> None:
    """Capacity/dVdQ column pairs, one pair per curve, side by side.

    Same layout as the dQ/dV CSV -- the two are read next to each other, and a
    second layout would be one more thing to hold in your head.

    The normalisation runs the *other* way here and that is not a typo: mAh is
    the denominator, so V/mAh expressed per gram is V/(mAh/g), a bigger number
    (ADR 0015).  ``normalize_per_capacity`` is where that inversion lives.

    Unusable curves keep their empty column pair, so a reader counting columns
    against the cycles they asked for never lines cycle 51 up under cycle 30.
    """
    writer = csv.writer(stream, lineterminator="\n")
    usable = basis if cell.divisor(basis) else Basis.ABSOLUTE
    unit = f"V/({usable})" if usable != Basis.ABSOLUTE else "V/mAh"

    header: list[str] = []
    columns: list[np.ndarray] = []
    for curve in curves:
        tag = f"cycle{curve.cycle_number}_{curve.branch}"
        header += [f"{tag}_capacity ({usable})", f"{tag}_dVdQ ({unit})"]
        columns += [normalize_capacity(curve.capacity, cell, usable),
                    normalize_per_capacity(curve.dv_dq, cell, usable)]

    writer.writerow(header or ["capacity", "dVdQ"])
    depth = max((len(c) for c in columns), default=0)
    for i in range(depth):
        row = []
        for values in columns:
            row.append(f"{values[i]:.12g}" if i < len(values) else "")
        writer.writerow(row)


#: 표에 쓰는 숫자 하나.  **12 유효숫자** — 반올림하지 않는다는 뜻이다.
#:
#: 예전에는 `.6g` 였고, 그것이 실제로 값을 바꿨다.  쿨롱효율 99.99996% 가
#: `100` 으로 찍힌다 -- 100 미만인 효율이 화면에서 정확히 100 이 되고, 다른
#: 도구(Smart Interface 의 엑셀)와 맞춰 볼 때 그 차이가 우리 탓처럼 보인다.
#: 큰 셀의 용량 1234.56789 mAh 도 `1234.57` 로 잘렸다.
#:
#: 12 를 고른 이유: double 은 유효숫자 15~17 자리라 12 는 잡음 아래이고
#: (`0.1 + 0.2` 가 `0.30000000000000004` 이 아니라 `0.3` 으로 나온다), 어느
#: 계측기의 분해능보다도 훨씬 깊다.  **없던 자리를 지어내지 않으면서 있던
#: 자리를 안 버리는** 지점이다.
#:
#: 보기 좋게 자르는 것은 화면이 한다 (`num()`).  저장·내보내기는 원래 값이다.
def _fmt(value: float | None) -> str:
    return "" if value is None else f"{value:.12g}"


#: Smart Interface 의 "일반 데이터 보고서" 열, 그 순서 그대로.
#:
#: 순서를 바꾸면 안 된다.  이 표를 받는 쪽은 헤더 이름이 아니라 **열 번호**로
#: 읽는 매크로일 때가 많다 (실측 파일의 헤더에는 `Test_Time(s)` 라고 적혀
#: 있는데 값은 `0:00:10:00.350` 이다 — 이름을 믿고 읽으면 이미 틀린다).
REPORT_COLUMNS = (
    "Index", "Test_Time(s)", "Cycle_No.", "Cycle_Time(s)", "Step_No.",
    "Step_Time(s)", "Current(A)", "Voltage(V)", "IR(ohm)", "AuxV1(V)",
    "AuxV2(V)", "AuxV3(V)", "Temp.('C)", "OCP(V)", "Power(W)", "Load(Ohm)",
    "Acc.Q(Ah)", "|Q|(Ah)", "Range",
)

#: `.wrd` 에 대응하는 값이 없는 열.  **0 으로 채우지 않고 비운다.**
#:
#: 계측기의 보고서도 `IR(ohm)` 을 빈칸으로 둔다 — 빈칸은 이 형식의 어휘 안에
#: 있다.  0 을 적으면 "쟀는데 0 이었다" 로 읽히고, 그것은 §0.4 가 금지하는
#: 짓이다.  `AuxV1` 은 `.wrd` 의 `aux_voltage` 로 채우고, 두 번째·세 번째
#: 보조 전압과 전류 레인지는 이 파일에 없다.
REPORT_UNSOURCED = ("IR(ohm)", "AuxV2(V)", "AuxV3(V)", "Range")


def _report_duration(seconds: float) -> str:
    """`d:hh:mm:ss.fff` — 보고서가 쓰는 시간 표기.

    헤더는 `(s)` 라고 적혀 있지만 값은 초가 아니라 이 꼴이다.  실측 파일에서
    확인한 그대로 따른다 (`0:00:10:00.350`).
    """
    if not np.isfinite(seconds) or seconds < 0:
        seconds = 0.0
    # 밀리초에서 반올림한다.  초에서 자르고 나중에 밀리초를 붙이면 59.9996 초가
    # `0:00:00:59.1000` 처럼 나온다.
    total_ms = int(round(seconds * 1000.0))
    days, rest = divmod(total_ms, 86_400_000)
    hours, rest = divmod(rest, 3_600_000)
    minutes, rest = divmod(rest, 60_000)
    secs, ms = divmod(rest, 1000)
    return f"{days}:{hours:02d}:{minutes:02d}:{secs:02d}.{ms:03d}"


def _report_number(value: float) -> str:
    """`3.85406E-004` — 지수 세 자리.

    파이썬의 `%E` 는 지수를 두 자리로 낸다 (`3.85406E-04`).  이 형식을 읽는
    쪽이 고정폭을 가정할 수 있으므로 자릿수까지 맞춘다.
    """
    if value is None or not np.isfinite(value):
        return ""
    text = f"{value:.5E}"
    mantissa, _, exponent = text.partition("E")
    sign, digits = exponent[0], exponent[1:]
    return f"{mantissa}E{sign}{int(digits):03d}"


def write_report_txt(wrd: WrdFile, stream: TextIO, *, cycle_offset: int = 0,
                     step_count: int | None = None) -> None:
    """Smart Interface 의 "일반 데이터 보고서" 와 같은 모양으로 쓴다.

    사람들이 이미 이 표를 받는 매크로와 스크립트를 갖고 있다.  워크벤치가
    원본을 들고 있으면서 그 표를 못 내주면, `.wrd` 를 도로 내려받아 계측기
    PC 에서 다시 뽑는 왕복이 남는다 — 중추 서버를 둔 이유가 거기서 깨진다.

    파생 열은 실측 보고서에서 규칙을 확인하고 맞췄다
    (`260823_PE#1 ... _005_DC.txt`, 22만 행):

    ``Power(W)``    ``I × V``.  601행: 3.85406E-004 × 3.12971 = 1.20621E-003 ✓
    ``Load(Ohm)``   ``V / I``.  같은 행: 3.12971 / 3.85406E-004 = 8.12055E+003 ✓
                    전류가 0 이면 0 이다 (보고서가 그렇게 쓴다 — 무한대가 아니라).
    ``Acc.Q(Ah)``   **시험 전체에 걸친 부호 있는 누적**이다.  스텝에서도
                    사이클에서도 안 리셋된다 (실측: 1사이클 끝 1.86033E-004 →
                    2사이클 첫 행 1.86076E-004 로 이어진다).  계측기의
                    ``CHARGE Q``/``DISCHARGE Q`` 는 사이클마다 0 이 되므로
                    (§3), 지나간 사이클의 순증분을 더해 이어 붙인다.
    ``|Q|(Ah)``     **그 스텝 안에서** 움직인 전하의 절댓값.  스텝이 바뀌면
                    0 부터 다시 센다 (실측으로 확인).

    적분하지 않고 계측기의 누적값을 쓴다.  같은 파일에서 사다리꼴 적분은
    44.590 mAh, 계측기는 49.942 mAh 였다 — 샘플링이 고르지 않아서다.  둘 중
    맞는 것은 계측기 쪽이다 (§"항상 charge_mah()/discharge_mah() 를 거친다").
    """
    data = wrd.data
    rows = len(wrd)

    def column(name: str):
        values = data.get(name)
        return values if values is not None else None

    test_s = wrd.seconds("test_time") if "test_time" in data else None
    step_s = wrd.seconds("step_time") if "step_time" in data else None
    cycle_s = wrd.seconds("cycle_time") if "cycle_time" in data else None
    current = column("current")
    voltage = column("voltage")
    temperature = column("temperature")
    ocp = column("ocp")
    aux = column("aux_voltage")
    total_step = column("total_step")
    cycle_index = column("cycle_index")
    charge = wrd.charge_mah() if "charge_q" in data else None
    discharge = wrd.discharge_mah() if "discharge_q" in data else None

    _write_report_header(wrd, stream, rows, step_count)
    stream.write("\t".join(REPORT_COLUMNS) + "\n")

    #: 사이클마다 0 이 되는 누적값을 이어 붙이기 위한 받침 (mAh).
    base_mah = 0.0
    previous_cycle = None if cycle_index is None else int(cycle_index[0])
    #: |Q| 를 재기 시작하는 자리 (mAh).  **직전 스텝의 마지막 값**이지 이 스텝의
    #: 첫 행이 아니다 — 첫 표본은 이미 스텝 경계에서 얼마쯤 흐른 뒤에 찍히므로,
    #: 이 행에서 0 을 쓰면 그 몫이 사라진다 (실측 보고서는 스텝 첫 행에
    #: 1.07095E-007 을 적는다).
    step_base = 0.0
    previous_step = None if total_step is None else int(total_step[0])
    previous_net = 0.0

    for i in range(rows):
        net = 0.0
        if charge is not None and discharge is not None:
            net = float(charge[i]) - float(discharge[i])
        if cycle_index is not None:
            here = int(cycle_index[i])
            if here != previous_cycle:
                # 새 사이클이 시작됐다.  직전 사이클이 남긴 순증분을 받침에
                # 더하고 나서 이 행을 센다 — 안 그러면 사이클 경계마다
                # 누적이 0 으로 떨어진다 (계측기의 보고서는 이어서 올라간다).
                base_mah += previous_net
                previous_cycle = here
                # 사이클이 바뀌면 누적값도 0 부터 다시 세므로 스텝 받침도 그렇다.
                previous_net = 0.0
        if total_step is not None:
            step_here = int(total_step[i])
            if step_here != previous_step:
                step_base = previous_net
                previous_step = step_here

        amps = float(current[i]) if current is not None else 0.0
        volts = float(voltage[i]) if voltage is not None else 0.0
        row = [
            str(i + 1),
            _report_duration(float(test_s[i])) if test_s is not None else "",
            str(int(cycle_index[i]) + 1 + cycle_offset) if cycle_index is not None else "",
            _report_duration(float(cycle_s[i])) if cycle_s is not None else "",
            str(int(total_step[i])) if total_step is not None else "",
            _report_duration(float(step_s[i])) if step_s is not None else "",
            _report_number(amps),
            _report_number(volts),
            "",                                            # IR(ohm) — 없는 값
            _report_number(float(aux[i])) if aux is not None else "",
            "",                                            # AuxV2 — 없는 값
            "",                                            # AuxV3 — 없는 값
            f"{float(temperature[i]):.2f}" if temperature is not None else "",
            _report_number(float(ocp[i])) if ocp is not None else "",
            _report_number(amps * volts),
            # 전류가 0 인 휴지 구간에서 보고서는 0 을 쓴다.  나눗셈을 그대로
            # 두면 inf 가 되고, 그 칸을 읽는 쪽에서 숫자가 아니게 된다.
            _report_number(volts / amps if amps else 0.0),
            _report_number((base_mah + net) / 1000.0),
            _report_number(abs(net - step_base) / 1000.0),
            "",                                            # Range — 없는 값
        ]
        stream.write("\t".join(row) + "\n")
        previous_net = net


def _write_report_header(wrd: WrdFile, stream: TextIO, rows: int,
                         step_count: int | None) -> None:
    """보고서 머리 — 계측기가 쓰는 그 여덟 줄.

    `데이터 개수` 만 다르다.  계측기는 거기에 `-1` 을 적는데(세지 않는다),
    우리는 실제 행 수를 적는다 — 그 칸의 이름이 곧 그 뜻이고, 빈 자리를
    거짓말로 채울 이유가 없다.

    `step_count` 는 스케줄 객체 없이 부를 때를 위한 것이다.  API 는 캐시된
    컬럼으로 `WrdFile` 을 짓는데 그 껍데기에는 스케줄이 안 들어 있고, 스텝
    개수는 `schedule_json` 에 따로 남아 있다.
    """
    meta = wrd.metadata
    schedule = meta.schedule
    started = meta.start_time.strftime("%Y-%m-%d %H:%M:%S") if meta.start_time else ""
    if step_count is None:
        step_count = len(schedule.steps) if schedule else 0
    condition = meta.schedule_path or (schedule.source_path if schedule else "") or ""
    stream.write("일반 데이터 보고서\n")
    stream.write(f"  * 시험 데이타 파일 : {meta.instrument_path or meta.source_name}\n")
    stream.write(f"  * 테스트 기간 : {started}~\n")
    stream.write(f"  * 데이터 개수 : {rows}\n")
    stream.write("  * 시험자 성명 : \n")
    stream.write("  * 상품 번호 : \n")
    stream.write(f"  * 메모 : {meta.memo or ''}\n")
    stream.write(f"  * 조건 파일명 : {condition}\n")
    stream.write(f"  * 단계 개수 : {step_count}\n")
    # 빈 열이 있으면 그 사실을 적는다.  같은 `  * 이름 : 값` 꼴이라 표를 읽는
    # 쪽(빈 줄 다음부터 읽는다)은 그대로고, 파일을 열어 본 사람은 그 칸이 왜
    # 비었는지 여기서 안다 — 안 적으면 "빠뜨렸나" 로 읽힌다.
    stream.write(f"  * 빈 열 : {', '.join(REPORT_UNSOURCED)} — 이 .wrd 에 없는 값입니다\n")
    stream.write("\n")


def raw_csv_string(wrd: WrdFile, **kwargs) -> str:
    buffer = io.StringIO()
    write_raw_csv(wrd, buffer, **kwargs)
    return buffer.getvalue()


def report_txt_string(wrd: WrdFile, **kwargs) -> str:
    buffer = io.StringIO()
    write_report_txt(wrd, buffer, **kwargs)
    return buffer.getvalue()


def cycles_csv_string(cycles, cell, **kwargs) -> str:
    buffer = io.StringIO()
    write_cycles_csv(cycles, cell, buffer, **kwargs)
    return buffer.getvalue()


def profiles_csv_string(profiles, cell, **kwargs) -> str:
    buffer = io.StringIO()
    write_profiles_csv(profiles, cell, buffer, **kwargs)
    return buffer.getvalue()


def dqdv_csv_string(curves, cell, **kwargs) -> str:
    buffer = io.StringIO()
    write_dqdv_csv(curves, cell, buffer, **kwargs)
    return buffer.getvalue()


def dvdq_csv_string(curves, cell, **kwargs) -> str:
    buffer = io.StringIO()
    write_dvdq_csv(curves, cell, buffer, **kwargs)
    return buffer.getvalue()


def write_xlsx(path, wrd: WrdFile, cycles: Sequence[CycleSummary],
               profiles: Sequence[Profile], cell: ResolvedCell, *,
               basis: str = Basis.ABSOLUTE, include_raw: bool = False) -> None:
    """Write a multi-sheet workbook (metadata / cycles / profiles [/ raw]).

    Requires ``openpyxl``; CSV export has no third-party dependency and stays
    the guaranteed path.
    """
    try:
        from openpyxl import Workbook
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("xlsx export needs openpyxl (pip install openpyxl)") from exc

    book = Workbook()
    meta_sheet = book.active
    meta_sheet.title = "metadata"
    metadata = wrd.metadata
    rows = [
        ("source file", metadata.source_name),
        ("instrument", f"{metadata.model} ({metadata.serial_no})"),
        ("channel", metadata.channel),
        ("start time", metadata.start_time.isoformat(sep=" ") if metadata.start_time else ""),
        ("end time", metadata.end_time.isoformat(sep=" ") if metadata.end_time else ""),
        ("samples", metadata.row_count),
        ("cycles in file", len(cycles)),
        ("active mass (mg)", (cell.active_mass_g or 0) * 1000 or ""),
        ("electrode area (cm2)", cell.area_cm2 or ""),
        ("loading (mg/cm2)", cell.loading_mg_cm2 or ""),
        ("nominal capacity (mAh)", cell.nominal_capacity_mah or ""),
        ("capacity basis", basis),
        # The raw sheet keeps the file's own units; say which they are.
        ("raw capacity unit", "C" if metadata.unit_coulomb else "Ah"),
    ]
    if metadata.schedule:
        schedule = metadata.schedule
        rows += [
            ("schedule", schedule.source_path or ""),
            ("upper cutoff (V)", schedule.upper_cutoff_v or ""),
            ("lower cutoff (V)", schedule.lower_cutoff_v or ""),
            ("planned cycles", schedule.planned_cycles or ""),
        ]
        rows += [(f"step {step.index}", step.describe()) for step in schedule.steps]
    for row in rows:
        meta_sheet.append(list(row))

    _sheet_from_csv(book, "cycles", cycles_csv_string(cycles, cell, basis=basis))
    if profiles:
        _sheet_from_csv(book, "profiles", profiles_csv_string(profiles, cell, basis=basis))
    if include_raw:
        _sheet_from_csv(book, "raw", raw_csv_string(wrd))

    book.save(path)


def _sheet_from_csv(book, title: str, text: str) -> None:
    sheet = book.create_sheet(title)
    for row in csv.reader(io.StringIO(text)):
        sheet.append([_maybe_number(v) for v in row])


def _maybe_number(value: str):
    if value in ("", "yes", "no"):
        return value
    try:
        return float(value) if ("." in value or "e" in value.lower()) else int(value)
    except ValueError:
        return value
