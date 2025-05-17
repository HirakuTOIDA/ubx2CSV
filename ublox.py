# -*- coding: utf-8 -*-
import struct
import numpy as np
import pandas as pd
import copy
import re
import dataclasses
import functools

# from dataclasses import dataclass
from typing import Tuple, Dict, Mapping, List

ubx_sync_char = [0xB5, 0x62]


# @functools.lru_cache(maxsize=None)
# def convert_fmt(fmt: str) -> str:
#     _RE = re.compile(r"CH|R8|R4|U4|I4|X4|U2|I2|X2|U1|I1|X1")
#     _MAP = {
#         "U1": "B",
#         "I1": "b",
#         "X1": "B",
#         "U2": "H",
#         "I2": "h",
#         "X2": "H",
#         "U4": "I",
#         "I4": "i",
#         "X4": "I",
#         "R4": "f",
#         "R8": "d",
#         "CH": "c",
#     }
#     if _RE.sub("", fmt):  # 置換後に文字が残っていれば未知トークン
#         raise ValueError(f'unknown token in "{fmt}"')
#     return _RE.sub(lambda m: _MAP[m.group(0)], fmt)


@dataclasses.dataclass(frozen=True, slots=True)
class UbxMsgDesc:
    name: str
    payload_len_fix: int
    fmt_fix: str
    payload_len_var: int = 0
    fmt_var: str = ""
    scale_fix: Tuple[float, ...] = ()
    hdr_fix: Tuple[str, ...] = ()
    scale_var: Tuple[float, ...] = ()
    hdr_var: Tuple[str, ...] = ()
    # _struct_fix: struct.Struct = dataclasses.field(init=False, repr=False)

    # def __post_init__(self):
    #     object.__setattr__(
    #         self, "_struct_fix", struct.Struct("<" + convert_fmt(self.fmt_fix))
    #     )

    # ❶ `_struct_fix` はフィールドに **保持しない**。
    #    代わりに @cached_property で遅延計算し、fmt が変われば自動再計算される。
    # @functools.cached_property
    # def struct_fix(self) -> struct.Struct:
    #     return struct.Struct("<" + convert_fmt(self.fmt_fix))

    # @functools.lru_cache(maxsize=None)
    # def struct_var(self, n: int) -> struct.Struct:
    #     if self.payload_len_var == 0:
    #         raise ValueError("no variable part")
    #     return struct.Struct(
    #         "<" + convert_fmt(self.fmt_fix) + convert_fmt(self.fmt_var) * n
    #     )


_TOKEN_DT = {
    "U1": "<u1",
    "I1": "<i1",
    "X1": "<u1",
    "U2": "<u2",
    "I2": "<i2",
    "X2": "<u2",
    "U4": "<u4",
    "I4": "<i4",
    "X4": "<u4",
    "R4": "<f4",
    "R8": "<f8",
    "CH": "S1",  # 1 文字。繰り返しは後段で集計
}

# 正規表現でトークン列を切り出す
_RE_TOKEN = re.compile(r"CH|R8|R4|U4|I4|X4|U2|I2|X2|U1|I1|X1")


# def build_dtype(desc: UbxMsgDesc, *, use_var: bool = False) -> np.dtype:
#     fmt = desc.fmt_var if use_var else desc.fmt_fix
#     hdr = desc.hdr_var if use_var else desc.hdr_fix
#     if not fmt:
#         raise ValueError("requested dtype does not exist in descriptor")

#     tokens: List[str] = _RE_TOKEN.findall(fmt)
#     if len(tokens) != len(hdr):
#         raise ValueError("fmt と hdr の要素数が一致しません")

#     # ---------- 重複名を解消するユーティリティ ----------
#     def uniq(name: str, counter: dict) -> str:
#         k = counter.get(name, 0)
#         counter[name] = k + 1
#         return name if k == 0 else f"{name}_{k}"

#     counter: dict[str, int] = {}
#     fields, run_ch, ch_names = [], 0, []

#     for name, tok in zip(hdr, tokens):
#         fields.append((uniq(name, counter), _TOKEN_DT[tok]))

#     return np.dtype(fields)


GEN6: Dict[int, UbxMsgDesc] = {
    0x0101: UbxMsgDesc(
        name="nav_posecef",
        payload_len_fix=20,
        fmt_fix="U4I4I4I4U4",
        scale_fix=(1, 1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "ecefX (cm)", "ecefY (cm)", "ecefZ (cm)", "pAcc (cm)"),
    ),
    0x0102: UbxMsgDesc(
        name="nav_posllh",
        payload_len_fix=28,
        fmt_fix="U4I4I4I4I4U4U4",
        scale_fix=(1, 1e-7, 1e-7, 1, 1, 1, 1),
        hdr_fix=(
            "iTOW (ms)",
            "lon (deg)",
            "lat (deg)",
            "height (mm)",
            "hMSL (mm)",
            "hAcc (mm)",
            "vAcc (mm)",
        ),
    ),
    0x0103: UbxMsgDesc(
        name="nav_status",
        payload_len_fix=16,
        fmt_fix="U4U1X1X1X1U4U4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "gpsFix", "flags", "fixStat", "flags2", "ttff", "msss"),
    ),
    0x0104: UbxMsgDesc(
        name="nav_dop",
        payload_len_fix=18,
        fmt_fix="U4U2U2U2U2U2U2U2",
        scale_fix=(1, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01),
        hdr_fix=("iTOW (ms)", "gDOP", "pDOP", "tDOP", "vDOP", "hDOP", "nDOP", "eDOP"),
    ),
    0x0106: UbxMsgDesc(
        name="nav_sol",
        payload_len_fix=52,
        fmt_fix="U4I4I2U1X1I4I4I4U4I4I4I4U4U2U1U1U4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.01, 1, 1, 1),
        hdr_fix=(
            "iTOW (ms)",
            "fTOW (ns)",
            "week",
            "gpsFix",
            "flags",
            "ecefX (cm)",
            "ecefY (cm)",
            "ecefZ (cm)",
            "pAcc (cm)",
            "ecefVX (cm/s)",
            "ecefVY (cm/s)",
            "ecefVZ (cm/s)",
            "sAcc (cm/s)",
            "pDOP",
            "reserved1",
            "numSV",
            "reserved2",
        ),
    ),
    0x0111: UbxMsgDesc(
        name="nav_velecef",
        payload_len_fix=20,
        fmt_fix="U4I4I4I4U4",
        scale_fix=(1, 1, 1, 1, 1),
        hdr_fix=(
            "iTOW (ms)",
            "ecefVX (cm/s)",
            "ecefVY (cm/s)",
            "ecefVZ (cm/s)",
            "sAcc (cm/s)",
        ),
    ),
    0x0112: UbxMsgDesc(
        name="nav_velned",
        payload_len_fix=36,
        fmt_fix="U4I4I4I4U4U4I4U4U4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1e-5, 1, 1e-5),
        hdr_fix=(
            "iTOW (ms)",
            "velN (cm/s)",
            "velE (cm/s)",
            "velD (cm/s)",
            "speed (cm/s)",
            "gSpeed (cm/s)",
            "heading (deg)",
            "sAcc (cm/s)",
            "cAcc (deg)",
        ),
    ),
    0x0120: UbxMsgDesc(
        name="nav_timegps",
        payload_len_fix=16,
        fmt_fix="U4I4I2I1X1U4",
        scale_fix=(1, 1, 1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "fTOW (ns)", "week", "leapS (s)", "valid", "tAcc (ns)"),
    ),
    0x0121: UbxMsgDesc(
        name="nav_timeutc",
        payload_len_fix=20,
        fmt_fix="U4U4I4U2U1U1U1U1U1X1",
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "iTOW (ms)",
            "tAcc (ns)",
            "nano (ns)",
            "year (y)",
            "month (month)",
            "day (d)",
            "hour (h)",
            "min (min)",
            "sec (s)",
            "valid",
        ),
    ),
    0x0122: UbxMsgDesc(
        name="nav_clock",
        payload_len_fix=20,
        fmt_fix="U4I4I4U4U4",
        scale_fix=(1, 1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "clkB (ns)", "clkD (ns/s)", "tAcc (ns)", "fAcc (ps/s)"),
    ),
    # @todo svid, 可変長フォーマット対応
    0x0130: UbxMsgDesc(
        name="nav_svinfo",
        payload_len_fix=8,
        fmt_fix="U4U1X1U2",
        payload_len_var=12,
        fmt_var="U1U1X1X1U1I1I2I4",
        scale_fix=(1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "numCh", "globalFlags", "reserved2"),
        scale_var=(1, 1, 1, 1, 1, 1, 1, 1),
        hdr_var=(
            "chn",
            "svid",
            "flags",
            "quality",
            "cno (dbHz)",
            "elev (deg)",
            "azim (deg)",
            "prRes (cm)",
        ),
    ),
    # @todo svid
    0x0131: UbxMsgDesc(
        name="nav_dgps",
        payload_len_fix=16,
        fmt_fix="U4I4I2I2U1U1U2",
        payload_len_var=12,
        fmt_var="U1U1U2R4R4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "iTOW (ms)",
            "age (ms)",
            "baseId",
            "baseHealth",
            "numCh",
            "status",
            "reserved1",
        ),
        scale_var=(1, 1, 1, 1, 1),
        hdr_var=("svid", "flags", "ageC (ms)", "prc (m)", "prrc (m/s)"),
    ),
    # @todo svid
    0x0132: UbxMsgDesc(
        name="nav_sbas",
        payload_len_fix=12,
        fmt_fix="U4U1U1I1X1U1" + "U1" * 3,
        payload_len_var=12,
        fmt_var="U1U1U1U1U1U1I2U2I2",
        scale_fix=(1, 1, 1, 1, 1, 1) + (1,) * 3,
        hdr_fix=("iTOW (ms)", "geo", "mode", "sys", "service", "cnt")
        + ("reserved0",) * 3,
        scale_var=(1, 1, 1, 1, 1, 1, 1, 1, 1),
        hdr_var=(
            "svid",
            "flags",
            "udre",
            "svSys",
            "svService",
            "reserved1",
            "prc (cm)",
            "reserved2",
            "ic (cm)",
        ),
    ),
    0x0140: UbxMsgDesc(
        name="nav_ekfstatus",
        payload_len_fix=36,
        fmt_fix="I4I4U4I2I1X1I4I4I4I2I2I2X1U1",
        scale_fix=(1, 1, 1e-2, 2**-8, 1, 1, 1e-5, 1e-5, 1e-5, 1e-4, 1e-4, 1e-4, 1, 1),
        hdr_fix=(
            "pulses",
            "period (ms)",
            "gyroMean",
            "temperature (degC)",
            "direction",
            "calibStatus",
            "pulseScale",
            "gyroBias",
            "gyroScale",
            "accPulseScale",
            "accGyroBias",
            "accGyroScale",
            "measUsed",
            "reserved2",
        ),
    ),
    0x0160: UbxMsgDesc(
        name="nav_aopstatus",
        payload_len_fix=20,
        fmt_fix="U4U1U1U1U1U4U4U4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "iTOW (ms)",
            "config",
            "status",
            "reserved0",
            "reserved1",
            "avail",
            "reserved2",
            "reserved3",
        ),
    ),
    # @todo svid
    0x0210: UbxMsgDesc(
        name="rxm_raw",
        payload_len_fix=8,
        fmt_fix="I4I2U1U1",
        payload_len_var=24,
        fmt_var="R8R8R4U1I1I1U1",
        scale_fix=(1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "week (weeks)", "numSV", "reserved1"),
        scale_var=(1, 1, 1, 1, 1, 1, 1),
        hdr_var=(
            "cpMes (cycles)",
            "prMes (m)",
            "doMes (Hz)",
            "sv",
            "mesQI",
            "cno (dbHz)",
            "lli",
        ),
    ),
    0x0211: UbxMsgDesc(
        name="rxm_sfrb",
        payload_len_fix=42,
        fmt_fix="U1U1" + "X4" * 10,
        scale_fix=(1, 1) + (1,) * 10,
        hdr_fix=("chn", "svid") + ("dwrd",) * 10,
    ),
    # @todo svid
    0x0220: UbxMsgDesc(
        name="rxm_svsi",
        payload_len_fix=8,
        fmt_fix="I4I2U1U1",
        payload_len_var=6,
        fmt_var="U1X1I2I1X1",
        scale_fix=(1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "week (weeks)", "numVis", "numSV"),
        scale_var=(1, 1, 1, 1, 1),
        hdr_var=("svid", "svFlag", "azim", "elev", "age"),
    ),
    # @todo svid
    0x0230: UbxMsgDesc(
        name="rxm_alm",
        payload_len_fix=8,
        fmt_fix="U4U4",
        payload_len_var=32,
        fmt_var="U4" * 8,
        scale_fix=(1, 1),
        hdr_fix=("svid", "week"),
        scale_var=(1,) * 8,
        hdr_var=("dwrd") * 8,
    ),
    # @todo svid
    0x0231: UbxMsgDesc(
        name="rxm_eph",
        payload_len_fix=8,
        fmt_fix="U4U4",
        payload_len_var=96,
        fmt_var="U4" * 8 + "U4" * 8 + "U4" * 8,
        scale_fix=(1, 1),
        hdr_fix=("svid", "how"),
        scale_var=(1,) * 8 + (1,) * 8 + (1,) * 8,
        hdr_var=("sf1d") * 8 + ("sf2d") * 8 + ("sf3d") * 8,
    ),
    # @todo 長さチェック
    0x0A02: UbxMsgDesc(
        name="mon_io",
        payload_len_fix=0,
        fmt_fix="",
        payload_len_var=20,
        fmt_var="U4U4U2U2U2U2U1U1U2",
        scale_fix=(),
        hdr_fix=(),
        scale_var=(1, 1, 1, 1, 1, 1, 1, 1, 1),
        hdr_var=(
            "rxBytes (bytes)",
            "txBytes (bytes)",
            "parityErrs",
            "framingErrs",
            "overrunErrs",
            "breakCond",
            "rxBusy",
            "txBusy",
            "reserved1",
        ),
    ),
    0x0A06: UbxMsgDesc(
        name="mon_msgpp",
        payload_len_fix=120,
        fmt_fix="U2" * 8
        + "U2" * 8
        + "U2" * 8
        + "U2" * 8
        + "U2" * 8
        + "U2" * 8
        + "U4" * 6,
        scale_fix=(1,) * 8 + (1,) * 8 + (1,) * 8 + (1,) * 8 + (1,) * 8 + (1,) * 8 + (1,) * 6,
        hdr_fix=("msg1 (msgs)") * 8
        + ("msg2 (msgs)") * 8
        + ("msg3 (msgs)") * 8
        + ("msg4 (msgs)") * 8
        + ("msg5 (msgs)") * 8
        + ("msg6 (msgs)") * 8
        + ("skipped (bytes)") * 6,
    ),
    0x0A07: UbxMsgDesc(
        name="mon_rxbuf",
        payload_len_fix=24,
        fmt_fix="U2" * 6 + "U1" * 6 + "U1" * 6,
        scale_fix=(1,) * 6 + (1,) * 6 + (1,) * 6,
        hdr_fix=("pending (bytes)") * 6 + ("usage (%)") * 6 + ("peakUsage (%)") * 6,
    ),
    0x0A08: UbxMsgDesc(
        name="mon_txbuf",
        payload_len_fix=28,
        fmt_fix="U2" * 6 + "U1" * 6 + "U1" * 6 + "U1U1X1U1",
        scale_fix=(1,) * 6 + (1,) * 6 + (1,) * 6 + (1, 1, 1, 1),
        hdr_fix=("pending (bytes)",) * 6
        + ("usage (%)",) * 6
        + ("peakUsage (%)",) * 6
        + ("tUsage (%)", "tPeakusage (%)", "errors", "reserved1"),
    ),
    0x0A09: UbxMsgDesc(
        name="mon_hw",
        payload_len_fix=68,
        fmt_fix="X4X4X4X4U2U2U1U1X1U1X4" + "U1" * 25 + "U1U2X4X4X4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) + (1,) * 25 + (1, 1, 1, 1, 1),
        hdr_fix=(
            "pinSel",
            "pinBank",
            "pinDir",
            "pinVal",
            "noisePerMS",
            "agcCnt",
            "aStatus",
            "aPower",
            "flags",
            "reserved1",
            "usedMask",
        )
        + ("VP",) * 25
        + ("jamInd", "reserved3", "pinIrq", "pullH", "pullL"),
    ),
    0x0A0B: UbxMsgDesc(
        name="mon_hw2",
        payload_len_fix=28,
        fmt_fix="I1U1I1U1U1" + "U1" * 3 + "X4" + "U4" * 2 + "X4U4",
        scale_fix=(1, 1, 1, 1, 1) + (1,) * 3 + (1,) + (1,) * 2 + (1, 1),
        hdr_fix=("ofsI", "magI", "ofsQ", "magQ", "cfgSource")
        + ("reserved0",) * 3
        + ("lowLevCfg",)
        + ("reserved1",) * 2
        + ("postStatus", "reserved2"),
    ),
    0x0B01: UbxMsgDesc(
        name="aid_ini",
        payload_len_fix=48,
        fmt_fix="I4I4I4U4X2U2U4I4U4U4I4U4X4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "ecefXOrLat (cm_or_deg*1e-7)",
            "ecefYOrLon (cm_or_deg*1e-7)",
            "ecefZOrAlt (cm)",
            "posAcc (cm)",
            "tmCfg",
            "wn",
            "tow (ms)",
            "towNs (ns)",
            "tAccMs (ms)",
            "tAccNs (ns)",
            "clkDOrFreq (ns/s_or_Hz*1e-2)",
            "clkDAccOrFreqAcc (ns/s_or_ppb)",
            "flags",
        ),
    ),
    0x0B50: UbxMsgDesc(
        name="aid_alp",
        payload_len_fix=24,
        fmt_fix="U4U4I4U2U2U4U1U1U2",
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "predTow (s)",
            "predDur (s)",
            "age (s)",
            "predWno",
            "almWno",
            "reserved1",
            "svs",
            "reserved2",
            "reserved3",
        ),
    ),
    0x0D01: UbxMsgDesc(
        name="tim_tp",
        payload_len_fix=16,
        fmt_fix="U4U4I4U2X1U1",
        scale_fix=(1, 2**-32, 1, 1, 1, 1),
        hdr_fix=(
            "towMS (ms)",
            "towSubMS (ms)",
            "qErr (ps)",
            "week (weeks)",
            "flags",
            "reserved1",
        ),
    ),
    0x0D03: UbxMsgDesc(
        name="tim_tm2",
        payload_len_fix=28,
        fmt_fix="U1X1U2U2U2U4U4U4U4U4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "ch (time)",
            "flags",
            "count",
            "wnR",
            "wnF",
            "towMsR (ms)",
            "towSubMsR (ns)",
            "towMsF (ms)",
            "towSubMsF (ns)",
            "accEst (ns)",
        ),
    ),
    0x0D04: UbxMsgDesc(
        name="tim_svin",
        payload_len_fix=28,
        fmt_fix="U4I4I4I4U4U4U1U1U2",
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "dur (s)",
            "meanX (cm)",
            "meanY (cm)",
            "meanZ (cm)",
            "meanV (mm^2)",
            "obs",
            "valid",
            "active",
            "reserved1",
        ),
    ),
    0x0D06: UbxMsgDesc(
        name="tim_vrfy",
        payload_len_fix=20,
        fmt_fix="I4I4I4I4U2X1U1",
        scale_fix=(1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "itow (ms)",
            "frac (ns)",
            "deltaMs (ms)",
            "deltaNs (ns)",
            "wno (week)",
            "flags",
            "reserved1",
        ),
    ),
}

# ---------- 世代差分を「上書き」だけで表現 ----------
GEN6_PATCH: Mapping[int, dict] = {}
GEN7_PATCH: Mapping[int, dict] = {
    0x0106: dict(
        hdr_fix=(
            "iTOW (ms)",
            "fTOW (ns)",
            "week (weeks)",
            "gpsFix",
            "flags",
            "ecefX (cm)",
            "ecefY (cm)",
            "ecefZ (cm)",
            "pAcc (cm)",
            "ecefVX (cm/s)",
            "ecefVY (cm/s)",
            "ecefVZ (cm/s)",
            "sAcc (cm/s)",
            "pDOP",
            "reserved1",
            "numSV",
            "reserved2",
        ),
    ),
    0x0107: dict(
        name="nav_pvt",
        payload_len_fix=84,
        fmt_fix="U4U2U1U1U1U1U1X1U4I4U1X1U1U1I4I4I4I4U4U4I4I4I4I4I4U4U4U2X2U4",
        scale_fix=(
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1e-7,
            1e-7,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1e-5,
            1,
            1e-5,
            0.01,
            1,
            1,
        ),
        hdr_fix=(
            "iTOW (ms)",
            "year (y)",
            "month (month)",
            "day (d)",
            "hour (h)",
            "min (min)",
            "sec (s)",
            "valid",
            "tAcc (ns)",
            "nano (ns)",
            "fixType",
            "flags",
            "reserved1",
            "numSV",
            "lon (deg)",
            "lat (deg)",
            "height (mm)",
            "hMSL (mm)",
            "hAcc (mm)",
            "vAcc (mm)",
            "velN (mm/s)",
            "velE (mm/s)",
            "velD (mm/s)",
            "gSpeed (mm/s)",
            "heading (deg)",
            "sAcc (mm/s)",
            "headingAcc (deg)",
            "pDOP",
            "reserved2",
            "reserved3",
        ),
    ),
    0x0131: dict(fmt_var="U1X1U2R4R4"),
    0x0160: dict(
        hdr_fix=(
            "iTOW (ms)",
            "aopCfg",
            "status",
            "reserved0",
            "reserved1",
            "availGPS",
            "reserved2",
            "reserved3",
        )
    ),
    0x0210: dict(hdr_fix=("rcvTow (ms)", "week (weeks)", "numSV", "reserved1")),
    0x0220: dict(fmt_fix="U4I2U1U1"),
    0x0A09: dict(
        payload_len_fix=60,
        fmt_fix="X4X4X4X4U2U2U1U1X1U1X4" + "U1" * 17 + "U1U2X4X4X4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) + (1,) * 17 + (1, 1, 1, 1, 1),
        hdr_fix=(
            "pinSel",
            "pinBank",
            "pinDir",
            "pinVal",
            "noisePerMS",
            "agcCnt",
            "aStatus",
            "aPower",
            "flags",
            "reserved1",
            "usedMask",
        )
        + ("VP",) * 17
        + ("jamInd", "reserved3", "pinIrq", "pullH", "pullL"),
    ),
    0x0A0B: dict(fmt_fix="I1U1I1U1U1" + "U1" * 3 + "U4" + "U4" * 2 + "U4U4"),
}
GEN8_PATCH: Mapping[int, dict] = {}
GEN9_PATCH: Mapping[int, dict] = {
    0x0A04: dict(
        name="mon_ver",
        payload_len_fix=40,
        fmt_fix="CH" * 30 + "CH" * 10,
        payload_len_var=30,
        fmt_var="CH" * 30,
        # scale_fix=(1,) + (1,),
        # hdr_fix=("swVersion",) + ("hwVersion",),
        # scale_var=(1,),
        # hdr_var=("extension",),
        scale_fix=(1,) * 30 + (1,) * 10,
        hdr_fix=("swVersion",) * 30 + ("hwVersion",) * 10,
        scale_var=(1,) * 30,
        hdr_var=("extension",) * 30,
    ),
    0x0127: dict(
        name="nav_timeqzss",
        payload_len_fix=20,
        fmt_fix="U4U4I4I2I1X1U4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "iTOW (ms)",
            "qzssTow (s)",
            "fQzssTow (ns)",
            "qzssWno",
            "leapS (s)",
            "valid",
            "tAcc (ns)",
        ),
    ),
    0x0136: dict(
        name="nav_cov",
        payload_len_fix=64,
        fmt_fix="U4U1U1U1" + "U1" * 9 + "R4R4R4R4R4R4R4R4R4R4R4R4",
        scale_fix=(1, 1, 1, 1) + (1,) * 9 + (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "version", "posCovValid", "velCovValid")
        + ("reserved0",) * 9
        + (
            "posCovNN",
            "posCovNE",
            "posCovND",
            "posCovEE",
            "posCovED",
            "posCovDD",
            "velCovNN",
            "velCovNE",
            "velCovND",
            "velCovEE",
            "velCovED",
            "velCovDD",
        ),
    ),
    0x0A31: dict(
        name="mon_span",
        payload_len_fix=4,
        fmt_fix="U1U1" + "U1" * 2,
        payload_len_var=272,
        fmt_var="U1" * 256 + "U4U4U4U1" + "U1" * 3,
        scale_fix=(1, 1) + (1,) * 2,
        hdr_fix=("version", "numRfBlocks") + ("reserved0",) * 2,
        scale_var=(1,) * 256 + (1, 1, 1, 1) + (1,) * 3,
        hdr_var=("spectrum",) * 256
        + ("span", "res", "center", "pga")
        + ("reserved",) * 3,
    ),
    0x068B: dict(
        name="cfg_valget",
        payload_len_fix=4,
        fmt_fix="U1U1U2",
        payload_len_var=1,
        fmt_var="U1",
        scale_fix=(1, 1, 1),
        hdr_fix=("version", "layer", "position"),
        scale_var=(1,),
        hdr_var=("cfgData",),
    ),
    0x0143: dict(
        name="nav_sig",
        payload_len_fix=8,
        fmt_fix="U4U1U1" + "U1" * 2,
        payload_len_var=16,
        fmt_var="U1U1U1U1I2U1U1U1U1X2" + "U1" * 4,
        scale_fix=(1, 1, 1) + (1,) * 2,
        hdr_fix=("iTOW (ms)", "version", "numSigs") + ("reserved1",) * 2,
        scale_var=(1, 1, 1, 1, 0.1, 1, 1, 1, 1, 1) + (1,) * 4,
        hdr_var=(
            "gnssId",
            "svId",
            "sigId",
            "freqId",
            "prRes (m)",
            "cno (dBHz)",
            "qualityInd",
            "corrSource",
            "ionoModel",
            "sigFlags",
        )
        + ("reserved2",) * 4,
    ),
    0x0135: dict(
        name="nav_sat",
        payload_len_fix=8,
        fmt_fix="U4U1U1" + "U1" * 2,
        payload_len_var=12,
        fmt_var="U1U1U1I1I2I2X4",
        scale_fix=(1, 1, 1) + (1,) * 2,
        hdr_fix=("iTOW (ms)", "version", "numSvs") + ("reserved1",) * 2,
        scale_var=(1, 1, 1, 1, 1, 0.1, 1),
        hdr_var=(
            "gnssId",
            "svId",
            "cno (dBHz)",
            "elev (deg)",
            "azim (deg)",
            "prRes (m)",
            "flags",
        ),
    ),
    0x0A36: dict(
        name="mon_comms",
        payload_len_fix=8,
        fmt_fix="U1U1X1" + "U1" * 1 + "U1" * 4,
        payload_len_var=40,
        fmt_var="U2U2U4U1U1U2U4U1U1U2" + "U2" * 4 + "U1" * 8 + "U4",
        scale_fix=(1, 1, 1) + (1,) * 1 + (1,) * 4,
        hdr_fix=("version", "nPorts", "txErrors")
        + ("reserved1",) * 1
        + ("protIds",) * 4,
        scale_var=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1) + (1,) * 4 + (1,) * 8 + (1,),
        hdr_var=(
            "portId",
            "txPending (bytes)",
            "txBytes (bytes)",
            "txUsage (%)",
            "txPeakUsage (%)",
            "rxPending (bytes)",
            "rxBytes (bytes)",
            "rxUsage (%)",
            "rxPeakUsage (%)",
            "overrunErrs",
        )
        + ("msgs (msg)",) * 4
        + ("reserved2",) * 8
        + ("skipped (bytes)",),
    ),
}


def build_desc(
    base: Mapping[int, UbxMsgDesc], patch: Mapping[int, dict]
) -> Dict[int, UbxMsgDesc]:
    # result = dict(base)
    # for mid, overrides in patch.items():
    #     base_desc = result.get(mid)
    #     result[mid] = (
    #         dataclasses.replace(base_desc, **overrides)
    #         if base_desc
    #         else UbxMsgDesc(**overrides)
    #     )
    # return result
    """
    * 各エントリを **必ず新規構築** する。
      - base + overrides を dict に結合 → UbxMsgDesc(**kwargs)
    * overrides に未知キーがあれば ValueError を投げて早期発見。
    """
    result: Dict[int, UbxMsgDesc] = {}

    for mid, base_desc in base.items():
        # パッチが無ければ丸ごとコピー（再構築しても軽量）
        result[mid] = UbxMsgDesc(**dataclasses.asdict(base_desc))

    for mid, overrides in patch.items():
        if mid in result:
            # (a) 既存 + 上書き
            unknown = set(overrides) - set(UbxMsgDesc.__annotations__)
            if unknown:
                raise ValueError(f"unknown patch keys for 0x{mid:04X}: {unknown}")

            merged = {**dataclasses.asdict(result[mid]), **overrides}
        else:
            # (b) 新規定義
            merged = overrides

        result[mid] = UbxMsgDesc(**merged)

    return result


ubx_messages_6 = build_desc(GEN6, GEN6_PATCH)
ubx_messages_7 = build_desc(GEN6, GEN7_PATCH)
ubx_messages_8 = build_desc(GEN6, GEN8_PATCH)
ubx_messages_9 = build_desc(GEN6, GEN9_PATCH)

_RE = re.compile(r"CH|R8|R4|U4|I4|X4|U2|I2|X2|U1|I1|X1")

class Ublox:
    def __init__(self, desc: UbxMsgDesc) -> None:
        self.payload = []
        self.msg_desc = desc
        # self.max_n_var = 0

    @functools.lru_cache(maxsize=None)
    def _conv(self, format_string: str) -> str:
        _MAP = {
            "U1": "B",
            "I1": "b",
            "X1": "B",
            "U2": "H",
            "I2": "h",
            "X2": "H",
            "U4": "I",
            "I4": "i",
            "X4": "I",
            "R4": "f",
            "R8": "d",
            "CH": "c",
        }
        return _RE.sub(lambda m: _MAP[m.group(0)], format_string)

    def unpack(self, dat: bytes) -> list[str | float]:
        # raw data
        n_var = 0
        if self.msg_desc.payload_len_var != 0:
            dat_size = len(dat)
            n_var = int(
                (dat_size - self.msg_desc.payload_len_fix)
                / self.msg_desc.payload_len_var
            )
            if n_var < 0:
                raise ValueError(
                    f"Invalid payload length: {dat_size} < {self.msg_desc.payload_len_fix}"
                )
            # else:
            #     self.max_n_var = max(self.max_n_var, n_var)

        payload_format = self._conv(self.msg_desc.fmt_fix)
        if self.msg_desc.payload_len_var != 0:
            payload_format_var = self._conv(self.msg_desc.fmt_var) * n_var
            payload_format += payload_format_var
        raw_data = struct.unpack("<" + payload_format, dat)
        return raw_data

        # # ---------- 可変部 n レコードをキャッシュ付きで生成 ----------
        # @functools.lru_cache(maxsize=None)
        # def dtype_var_n(n: int) -> np.dtype:
        #     """
        #     固定部 + 可変部 n レコードの構造化 dtype を生成（一意名付き）
        #     """
        #     dt_fix = build_dtype(self.msg_desc)
        #     if n_var > 0:
        #         dt_var_unit = build_dtype(self.msg_desc, use_var=True)

        #     fields = list(dt_fix.descr)  # 固定部そのまま

        #     # 可変部を n 回展開し，「_0」「_1」…で一意化
        #     for i in range(n):
        #         for name, dtyp in dt_var_unit.descr:
        #             fields.append((f"{name}_{i}", dtyp))

        #     return np.dtype(fields)

        # try:
        #     dt = dtype_var_n(n_var)
        # except ValueError as e:
        #     raise ValueError(f"dtype error: {e}") from None

        # try:
        #     raw = np.frombuffer(dat, dtype=dt, count=1)
        # except ValueError as e:
        #     raise ValueError(f"numpy frombuffer error: {e}") from None

        # return raw.tolist()

        # # scale
        # # @todo スケールはCSV出力時に行う
        # @functools.lru_cache(maxsize=None)
        # def scale_full(n: int) -> np.ndarray:
        #     scale_fix = np.asarray(self.msg_desc.scale_fix, dtype=float)
        #     if n == 0:
        #         return scale_fix
        #     else:
        #         scale_var = np.asarray(self.msg_desc.scale_var, dtype=float)
        #         return np.concatenate([scale_fix, np.tile(scale_var, n)])

        # _NUM_KINDS = {
        #     "b",
        #     "u",
        #     "i",
        #     "f",
        #     "c",
        # }  # bool・符号なし/あり int・float・complex
        # _STR_KINDS = {"S", "U"}  # バイト列 / Unicode 文字列

        # @functools.lru_cache(maxsize=None)
        # def _scale_vector(desc, n_var):
        #     """desc → 完全スケール配列 (数値列のみ; 文字列列には 1.0 を入れておく)"""
        #     scale_fix = np.asarray(desc.scale_fix, dtype=np.float64)
        #     if n_var:
        #         scale_var = np.tile(desc.scale_var, n_var).astype(np.float64)
        #         scale = np.concatenate([scale_fix, scale_var])
        #     else:
        #         scale = scale_fix
        #     return scale

        # def scale_packet(arr, desc, *, n_var: int = 0):
        #     scale_vec = _scale_vector(desc, n_var)
        #     records = []

        #     for idx, name in enumerate(arr.dtype.names):
        #         field = arr[name]

        #         if field.dtype.kind in _NUM_KINDS:
        #             records.append(field.astype(np.float64)[0] * scale_vec[idx])
        #         elif field.dtype.kind in _STR_KINDS:
        #             value = str(field[0], encoding="utf-8")  # bytes → str
        #             records.append(value)
        #         else:  # パディングや予約領域 (kind=='V') もそのまま持たせる
        #             records.append(field.item())

        #     return records

        # scaled = scale_packet(raw, self.msg_desc, n_var=n_var)
        # return scaled

    def append(self, dat) -> None:
        unpacked = self.unpack(dat)
        # print()
        self.payload.append(unpacked)
        # self.payload.append(list(unpacked[0]))

    def save_csv(self, filename: str) -> None:
        if len(self.payload) > 0:
            def conv_func():
                return pd.DataFrame(self.payload)
            # df = pd.DataFrame(self.payload)
            df = conv_func()
            df_columns_len = len(df.columns)
            header = list(self.msg_desc.hdr_fix)
            scale_full = list(self.msg_desc.scale_fix)
            if self.msg_desc.payload_len_var != 0:
                headers_number_var = int(
                    (df_columns_len - len(self.msg_desc.hdr_fix))
                    / len(self.msg_desc.hdr_var)
                )
                header += self.msg_desc.hdr_var * headers_number_var
                scale_full += self.msg_desc.scale_var * headers_number_var

            def scale_func(dframe, scale):
                return dframe.mul(scale, axis=1)

            df = scale_func(df, scale_full)

            header[0] = "# " + header[0]
            if len(df.columns) == len(header):
                df.columns = header
            else:
                raise ValueError(
                    f"Header length mismatch: {len(df.columns)} != {len(header)}"
                )
            def save_func(dframe, fname):
                dframe.to_csv(fname, index=False)
            # df.to_csv(filename, index=False)
            save_func(df, filename)
            return len(self.payload)
        else:
            raise ValueError("No data to save")


# Fletcher's checksum
def checksum(dat):
    ck_a = 0
    ck_b = 0
    for dat_ele in dat:
        ck_a = (ck_a + dat_ele) & 0xFF
        ck_b = (ck_b + ck_a) & 0xFF
    return ck_a + ck_b * 256
