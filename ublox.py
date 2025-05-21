# -*- coding: utf-8 -*-
import struct
import pandas as pd
import re
import dataclasses
import functools
from typing import Tuple, Dict, Mapping
from pydantic import BaseModel, model_validator
from enum import IntEnum

UBX_SYNC: bytes = bytes((0xB5, 0x62))


@dataclasses.dataclass(frozen=True, slots=True)
class UbxMsgDesc:
    name: str
    payload_len_fix: int = 0
    fmt_fix: str = ""
    payload_len_var: int = 0
    fmt_var: str = ""
    scale_fix: Tuple[float, ...] = ()
    hdr_fix: Tuple[str, ...] = ()
    scale_var: Tuple[float, ...] = ()
    hdr_var: Tuple[str, ...] = ()


class MsgClass(IntEnum):
    NAV = 0x01
    RXM = 0x02
    CFG = 0x06
    MON = 0x0A
    AID = 0x0B
    TIM = 0x0D
    ESF = 0x10
    LOG = 0x21
    SEC = 0x27
    HNR = 0x28


class NavID(IntEnum):
    POSECEF = 0x01
    POSLLH = 0x02
    STATUS = 0x03
    DOP = 0x04
    ATT = 0x05
    SOL = 0x06
    PVT = 0x07
    ODO = 0x09
    VELECEF = 0x11
    VELNED = 0x12
    HPPOSECEF = 0x13
    HPPOSLLH = 0x14
    TIMEGPS = 0x20
    TIMEUTC = 0x21
    CLOCK = 0x22
    TIMEGLO = 0x23
    TIMEBDS = 0x24
    TIMEGAL = 0x25
    TIMELS = 0x26
    TIMEQZSS = 0x27
    SVINFO = 0x30
    DGPS = 0x31
    SBAS = 0x32
    ORB = 0x34
    SAT = 0x35
    COV = 0x36
    GEOFENCE = 0x39
    SVIN = 0x3B
    RELPOSNED = 0x3C
    EKFSTATUS = 0x40
    SLAS = 0x42
    SIG = 0x43
    AOPSTATUS = 0x60
    EOE = 0x61


class RxmID(IntEnum):
    RAW = 0x10
    SFRB = 0x11
    SFRBX = 0x13
    MEASX = 0x14
    RAWX = 0x15
    SVSI = 0x20
    ALM = 0x30
    EPH = 0x31
    IMES = 0x61


class MonID(IntEnum):
    IO = 0x02
    VER = 0x04
    MSGPP = 0x06
    RXBUF = 0x07
    TXBUF = 0x08
    HW = 0x09
    HW2 = 0x0B
    PATCH = 0x27
    GNSS = 0x28
    SMGR = 0x2E
    SPAN = 0x31
    COMMS = 0x36
    HW3 = 0x37
    RF = 0x38
    SYS = 0x39


class AidID(IntEnum):
    INI = 0x01
    ALP = 0x50


class TimID(IntEnum):
    TP = 0x01
    TM2 = 0x03
    SVIN = 0x04
    VRFY = 0x06
    VCOCAL = 0x15
    FCHG = 0x16


class CfgID(IntEnum):
    VALGET = 0x8B


class EsfID(IntEnum):
    STATUS = 0x10
    INS = 0x15


class LogID(IntEnum):
    BATCH = 0x11


class SecID(IntEnum):
    SIGLOG = 0x10


class HnrID(IntEnum):
    PVT = 0x00
    INS = 0x02


def mid(cls: MsgClass, id_: int) -> int:
    return (cls << 8) | id_


GEN6: Dict[int, UbxMsgDesc] = {
    mid(MsgClass.NAV, NavID.POSECEF): UbxMsgDesc(
        name="nav_posecef",
        payload_len_fix=20,
        fmt_fix="U4I4I4I4U4",
        scale_fix=(1, 1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "ecefX (cm)", "ecefY (cm)", "ecefZ (cm)", "pAcc (cm)"),
    ),
    mid(MsgClass.NAV, NavID.POSLLH): UbxMsgDesc(
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
    mid(MsgClass.NAV, NavID.STATUS): UbxMsgDesc(
        name="nav_status",
        payload_len_fix=16,
        fmt_fix="U4U1X1X1X1U4U4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "gpsFix", "flags", "fixStat", "flags2", "ttff", "msss"),
    ),
    mid(MsgClass.NAV, NavID.DOP): UbxMsgDesc(
        name="nav_dop",
        payload_len_fix=18,
        fmt_fix="U4U2U2U2U2U2U2U2",
        scale_fix=(1, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01, 0.01),
        hdr_fix=("iTOW (ms)", "gDOP", "pDOP", "tDOP", "vDOP", "hDOP", "nDOP", "eDOP"),
    ),
    mid(MsgClass.NAV, NavID.SOL): UbxMsgDesc(
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
    mid(MsgClass.NAV, NavID.VELECEF): UbxMsgDesc(
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
    mid(MsgClass.NAV, NavID.VELNED): UbxMsgDesc(
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
    mid(MsgClass.NAV, NavID.TIMEGPS): UbxMsgDesc(
        name="nav_timegps",
        payload_len_fix=16,
        fmt_fix="U4I4I2I1X1U4",
        scale_fix=(1, 1, 1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "fTOW (ns)", "week", "leapS (s)", "valid", "tAcc (ns)"),
    ),
    mid(MsgClass.NAV, NavID.TIMEUTC): UbxMsgDesc(
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
    mid(MsgClass.NAV, NavID.CLOCK): UbxMsgDesc(
        name="nav_clock",
        payload_len_fix=20,
        fmt_fix="U4I4I4U4U4",
        scale_fix=(1, 1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "clkB (ns)", "clkD (ns/s)", "tAcc (ns)", "fAcc (ps/s)"),
    ),
    mid(MsgClass.NAV, NavID.SVINFO): UbxMsgDesc(
        # @todo svid, 可変長フォーマット対応
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
    mid(MsgClass.NAV, NavID.DGPS): UbxMsgDesc(
        # @todo svid
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
    mid(MsgClass.NAV, NavID.SBAS): UbxMsgDesc(
        # @todo svid
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
    mid(MsgClass.NAV, NavID.EKFSTATUS): UbxMsgDesc(
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
    mid(MsgClass.NAV, NavID.AOPSTATUS): UbxMsgDesc(
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
    mid(MsgClass.RXM, RxmID.RAW): UbxMsgDesc(
        # @todo svid
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
    mid(MsgClass.RXM, RxmID.SFRB): UbxMsgDesc(
        name="rxm_sfrb",
        payload_len_fix=42,
        fmt_fix="U1U1" + "X4" * 10,
        scale_fix=(1, 1) + (1,) * 10,
        hdr_fix=("chn", "svid") + ("dwrd",) * 10,
    ),
    mid(MsgClass.RXM, RxmID.SVSI): UbxMsgDesc(
        # @todo svid
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
    mid(MsgClass.RXM, RxmID.ALM): UbxMsgDesc(
        # @todo svid
        name="rxm_alm",
        payload_len_fix=8,
        fmt_fix="U4U4",
        payload_len_var=32,
        fmt_var="U4" * 8,
        scale_fix=(1, 1),
        hdr_fix=("svid", "week"),
        scale_var=(1,) * 8,
        hdr_var=("dwrd",) * 8,
    ),
    mid(MsgClass.RXM, RxmID.EPH): UbxMsgDesc(
        # @todo svid
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
    mid(MsgClass.MON, MonID.IO): UbxMsgDesc(
        # @todo 長さチェック
        name="mon_io",
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
    mid(MsgClass.MON, MonID.MSGPP): UbxMsgDesc(
        name="mon_msgpp",
        payload_len_fix=120,
        fmt_fix="U2" * 8
        + "U2" * 8
        + "U2" * 8
        + "U2" * 8
        + "U2" * 8
        + "U2" * 8
        + "U4" * 6,
        scale_fix=(1,) * 8
        + (1,) * 8
        + (1,) * 8
        + (1,) * 8
        + (1,) * 8
        + (1,) * 8
        + (1,) * 6,
        hdr_fix=("msg1 (msgs)") * 8
        + ("msg2 (msgs)") * 8
        + ("msg3 (msgs)") * 8
        + ("msg4 (msgs)") * 8
        + ("msg5 (msgs)") * 8
        + ("msg6 (msgs)") * 8
        + ("skipped (bytes)") * 6,
    ),
    mid(MsgClass.MON, MonID.RXBUF): UbxMsgDesc(
        name="mon_rxbuf",
        payload_len_fix=24,
        fmt_fix="U2" * 6 + "U1" * 6 + "U1" * 6,
        scale_fix=(1,) * 6 + (1,) * 6 + (1,) * 6,
        hdr_fix=("pending (bytes)") * 6 + ("usage (%)") * 6 + ("peakUsage (%)") * 6,
    ),
    mid(MsgClass.MON, MonID.TXBUF): UbxMsgDesc(
        name="mon_txbuf",
        payload_len_fix=28,
        fmt_fix="U2" * 6 + "U1" * 6 + "U1" * 6 + "U1U1X1U1",
        scale_fix=(1,) * 6 + (1,) * 6 + (1,) * 6 + (1, 1, 1, 1),
        hdr_fix=("pending (bytes)",) * 6
        + ("usage (%)",) * 6
        + ("peakUsage (%)",) * 6
        + ("tUsage (%)", "tPeakusage (%)", "errors", "reserved1"),
    ),
    mid(MsgClass.MON, MonID.HW): UbxMsgDesc(
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
    mid(MsgClass.MON, MonID.HW2): UbxMsgDesc(
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
    mid(MsgClass.AID, AidID.INI): UbxMsgDesc(
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
    mid(MsgClass.AID, AidID.ALP): UbxMsgDesc(
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
    mid(MsgClass.TIM, TimID.TP): UbxMsgDesc(
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
    mid(MsgClass.TIM, TimID.TM2): UbxMsgDesc(
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
    mid(MsgClass.TIM, TimID.SVIN): UbxMsgDesc(
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
    mid(MsgClass.TIM, TimID.VRFY): UbxMsgDesc(
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
    mid(MsgClass.NAV, NavID.SOL): dict(
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
    mid(MsgClass.NAV, NavID.PVT): dict(
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
    mid(MsgClass.NAV, NavID.DGPS): dict(fmt_var="U1X1U2R4R4"),
    mid(MsgClass.NAV, NavID.AOPSTATUS): dict(
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
    mid(MsgClass.RXM, RxmID.RAW): dict(
        hdr_fix=("rcvTow (ms)", "week (weeks)", "numSV", "reserved1")
    ),
    mid(MsgClass.RXM, RxmID.SVSI): dict(fmt_fix="U4I2U1U1"),
    mid(MsgClass.MON, MonID.HW): dict(
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
    mid(MsgClass.MON, MonID.HW2): dict(
        fmt_fix="I1U1I1U1U1" + "U1" * 3 + "U4" + "U4" * 2 + "U4U4"
    ),
}
GEN8_PATCH: Mapping[int, dict] = {
    mid(MsgClass.NAV, NavID.STATUS): dict(
        hdr_fix=(
            "iTOW (ms)",
            "gpsFix",
            "flags",
            "fixStat",
            "flags2",
            "ttff (ms)",
            "msss (ms)",
        ),
    ),
    mid(MsgClass.NAV, NavID.ATT): dict(
        name="nav_att",
        payload_len_fix=32,
        fmt_fix="U4U1" + "U1" * 3 + "I4I4I4U4U4U4",
        scale_fix=(1, 1) + (1,) * 3 + (1e-5, 1e-5, 1e-5, 1e-5, 1e-5, 1e-5),
        hdr_fix=("iTOW (ms)", "version")
        + ("reserved1",) * 3
        + (
            "roll (deg)",
            "pitch (deg)",
            "heading (deg)",
            "accRoll (deg)",
            "accPitch (deg)",
            "accHeading (deg)",
        ),
    ),
    mid(MsgClass.NAV, NavID.SOL): dict(
        fmt_fix="U4I4I2U1X1I4I4I4U4I4I4I4U4U2U1U1" + "U1" * 4,
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0.01, 1, 1) + (1,) * 4,
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
        )
        + ("reserved2",) * 4,
    ),
    mid(MsgClass.NAV, NavID.PVT): dict(
        name="nav_pvt",
        payload_len_fix=92,
        fmt_fix="U4U2U1U1U1U1U1X1U4I4U1X1X1U1I4I4I4I4U4U4I4I4I4I4I4U4U4U2X2"
        + "U1" * 4
        + "I4I2U2",
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
        )
        + (1,) * 4
        + (1e-5, 1e-2, 1e-2),
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
            "flags2",
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
            "headMot (deg)",
            "sAcc (mm/s)",
            "headAcc (deg)",
            "pDOP",
            "flags3",
        )
        + ("reserved1",) * 4
        + ("headVeh (deg)", "magDec (deg)", "magAcc (deg)"),
    ),
    mid(MsgClass.NAV, NavID.ODO): dict(
        name="nav_odo",
        payload_len_fix=20,
        fmt_fix="U1" + "U1" * 3 + "U4U4U4U4",
        scale_fix=(1,) + (1,) * 3 + (1, 1, 1, 1),
        hdr_fix=("version",)
        + ("reserved1",) * 3
        + ("iTOW (ms)", "distance (m)", "totalDistance (m)", "distanceStd (m)"),
    ),
    mid(MsgClass.NAV, NavID.HPPOSECEF): dict(
        name="nav_hpposecef",
        payload_len_fix=28,
        fmt_fix="U1" + "U1" * 3 + "U4I4I4I4I1I1I1U1U4",
        scale_fix=(1,) + (1,) * 3 + (1, 1, 1, 1, 0.1, 0.1, 0.1, 1, 0.1),
        hdr_fix=("version",)
        + ("reserved1",) * 3
        + (
            "iTOW (ms)",
            "ecefX (cm)",
            "ecefY (cm)",
            "ecefZ (cm)",
            "ecefXHp (mm)",
            "ecefYHp (mm)",
            "ecefZHp (mm)",
            "reserved2",
            "pAcc (mm)",
        ),
    ),
    mid(MsgClass.NAV, NavID.HPPOSLLH): dict(
        name="nav_hpposllh",
        payload_len_fix=36,
        fmt_fix="U1" + "U1" * 3 + "U4I4I4I4I4I1I1I1I1U4U4",
        scale_fix=(1,)
        + (1,) * 3
        + (1, 1e-7, 1e-7, 1, 1, 1e-9, 1e-9, 0.1, 0.1, 0.1, 0.1),
        hdr_fix=("version",)
        + ("reserved1",) * 3
        + (
            "iTOW (ms)",
            "log (deg)",
            "lat (deg)",
            "height (mm)",
            "hMSL (mm)",
            "lonHp (deg)",
            "latHp (deg)",
            "heightHp (mm)",
            "heightHp (mm)",
            "hAcc (mm)",
            "vAcc (mm)",
        ),
    ),
    mid(MsgClass.NAV, NavID.TIMEGLO): dict(
        name="nav_timeglo",
        payload_len_fix=20,
        fmt_fix="U4U4I4U2U1X1U4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "iTOW (ms)",
            "TOD (s)",
            "fTOD (ns)",
            "Nt (days)",
            "N4",
            "valid",
            "tAcc (ns)",
        ),
    ),
    mid(MsgClass.NAV, NavID.TIMEBDS): dict(
        name="nav_timebds",
        payload_len_fix=20,
        fmt_fix="U4U4I4I2I1X1U4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "iTOW (ms)",
            "SOW (s)",
            "fSOW (ns)",
            "week",
            "leapS (s)",
            "valid",
            "tAcc (ns)",
        ),
    ),
    mid(MsgClass.NAV, NavID.TIMEGAL): dict(
        name="nav_timegal",
        payload_len_fix=20,
        fmt_fix="U4U4I4I2I1X1U4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "iTOW (ms)",
            "galTow (s)",
            "fGalTow (ns)",
            "galWno",
            "leapS (s)",
            "valid",
            "tAcc (ns)",
        ),
    ),
    mid(MsgClass.NAV, NavID.TIMELS): dict(
        name="nav_timels",
        payload_len_fix=24,
        fmt_fix="U4U1" + "U1" * 3 + "U1I1U1I1I4U2U2" + "U1" * 3 + "X1",
        scale_fix=(
            1,
            1,
        )
        + (1,) * 3
        + (1, 1, 1, 1, 1, 1, 1)
        + (1,) * 3
        + (1,),
        hdr_fix=("iTOW (ms)", "version")
        + ("reserved1",) * 3
        + (
            "srcOfCurrLs",
            "currLs (s)",
            "srcOfLsChange",
            "lsChange (s)",
            "timeToLsEvent (s)",
            "dateOfLsGpsWn",
            "dateOfLsGpsDn",
        )
        + ("reserved2",) * 3
        + ("valid",),
    ),
    mid(MsgClass.NAV, NavID.SVINFO): dict(
        fmt_fix="U4U1X1" + "U1" * 2,
        scale_fix=(1, 1, 1) + (1,) * 2,
        hdr_fix=("iTOW (ms)", "numCh", "globalFlags") + ("reserved1",) * 2,
    ),
    mid(MsgClass.NAV, NavID.DGPS): dict(
        # @todo svid
        fmt_fix="U4I4I2I2U1U1" + "U1" * 2,
        scale_fix=(1, 1, 1, 1, 1, 1) + (1,) * 2,
        hdr_fix=("iTOW (ms)", "age (ms)", "baseId", "baseHealth", "numCh", "status")
        + ("reserved1",) * 2,
        fmt_var="U1X1U2R4R4",
    ),
    mid(MsgClass.NAV, NavID.SBAS): dict(
        # @todo svid
        fmt_var="U1U1U1U1U1U1I2" + "U1" * 2 + "I2",
        scale_fix=(1, 1, 1, 1, 1, 1) + (1,) * 3,
        hdr_fix=("iTOW (ms)", "geo", "mode", "sys", "service", "cnt")
        + ("reserved1",) * 3,
        scale_var=(1, 1, 1, 1, 1, 1, 1) + (1,) * 2 + (1,),
        hdr_var=("svid", "flags", "udre", "svSys", "svService", "reserved2", "prc (cm)")
        + ("reserved3",) * 2
        + ("ic (cm)",),
    ),
    mid(MsgClass.NAV, NavID.ORB): dict(
        # @todo svid + gnssid
        name="nav_orb",
        payload_len_fix=8,
        fmt_fix="U4U1U1" + "U1" * 2,
        payload_len_var=6,
        fmt_var="U1U1X1X1X1X1",
        scale_fix=(1, 1, 1) + (1,) * 2,
        hdr_fix=("iTOW (ms)", "version", "numSvs") + ("reserved1",) * 2,
        scale_var=(
            1,
            1,
            1,
            1,
            1,
            1,
        ),
        hdr_var=("gnssId", "svId", "svFlag", "eph", "alm", "otherOrb"),
    ),
    mid(MsgClass.NAV, NavID.SAT): dict(
        # @todo svid + gnssid
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
    mid(MsgClass.NAV, NavID.GEOFENCE): dict(
        # @todo numFences
        name="nav_geofence",
        payload_len_fix=8,
        fmt_fix="U4U1U1U1U1",
        payload_len_var=2,
        fmt_var="U1" + "U1" * 1,
        scale_fix=(1, 1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "version", "status", "numFences", "combState"),
        scale_var=(1,) + (1,) * 1,
        hdr_var=("state",) + ("reserved1",) * 1,
    ),
    mid(MsgClass.NAV, NavID.SVIN): dict(
        name="nav_svin",
        payload_len_fix=40,
        fmt_fix="U1" + "U1" * 3 + "U4U4I4I4I4I1I1I1U1U4U4U1U1" + "U1" * 2,
        scale_fix=(1,) + (1,) * 3 + (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) + (1,) * 2,
        hdr_fix=("version",)
        + ("reserved1",) * 3
        + (
            "iTOW (ms)",
            "dur (s)",
            "meanX (cm)",
            "meanY (cm)",
            "meanZ (cm)",
            "meanXHP (0.1_mm)",
            "meanYHP (0.1_mm)",
            "meanZHP (0.1_mm)",
            "reserved2",
            "meanAcc (0.1_mm)",
            "obs",
            "valid",
            "active",
        )
        + ("reserved3",) * 2,
    ),
    mid(MsgClass.NAV, NavID.RELPOSNED): dict(
        name="nav_relposned",
        payload_len_fix=40,
        fmt_fix="U1U1U2U4I4I4I4I1I1I1U1U4U4U4X4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 0.1, 0.1, 0.1, 1, 0.1, 0.1, 0.1, 1),
        hdr_fix=(
            "version",
            "reserved1",
            "refStationId",
            "iTOW (ms)",
            "relPosN (cm)",
            "relPosE (cm)",
            "relPosD (cm)",
            "relPosHPN (mm)",
            "relPosHPE (mm)",
            "relPosHPD (mm)",
            "reserved2",
            "accN (mm)",
            "accE (mm)",
            "accD (mm)",
            "flags",
        ),
    ),
    mid(MsgClass.NAV, NavID.SLAS): dict(
        # @todo svid + gnssid
        name="nav_slas",
        payload_len_fix=20,
        fmt_fix="U4U1" + "U1" * 3 + "I4I4U1U1X1U1",
        payload_len_var=8,
        fmt_var="U1U1U1" + "U1" * 3 + "I2",
        scale_fix=(1, 1) + (1,) * 3 + (1e-3, 1e-3, 1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "version")
        + ("reserved1",) * 3
        + (
            "gmsLon (deg)",
            "gmsLat (deg)",
            "gmsCode",
            "qzssSvId",
            "serviceFlags",
            "cnt",
        ),
        scale_var=(1, 1, 1) + (1,) * 3 + (1,),
        hdr_var=("gnssId", "svId", "reserved2") + ("reserved3",) * 3 + ("prc (cm)",),
    ),
    mid(MsgClass.NAV, NavID.AOPSTATUS): dict(
        payload_len_fix=16,
        fmt_fix="U4U1U1" + "U1" * 10,
        scale_fix=(1, 1, 1) + (1,) * 10,
        hdr_fix=("iTOW (ms)", "aopCfg", "status") + ("reserved1",) * 10,
    ),
    mid(MsgClass.NAV, NavID.EOE): dict(
        name="nav_eoe",
        payload_len_fix=4,
        fmt_fix="U4",
        scale_fix=(1,),
        hdr_fix=("iTOW (ms)",),
    ),
    mid(MsgClass.RXM, RxmID.SFRBX): dict(
        name="rxm_sfrbx",
        payload_len_fix=8,
        fmt_fix="U1U1U1U1U1U1U1U1",
        payload_len_var=4,
        fmt_var="U4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "gnssId",
            "svId",
            "reserved1",
            "freqId",
            "numWords",
            "reserved2",
            "version",
            "reserved3",
        ),
        scale_var=(1,),
        hdr_var=("dwrd",),
    ),
    mid(MsgClass.RXM, RxmID.MEASX): dict(
        # @todo svid + gnssid
        name="rxm_measx",
        payload_len_fix=44,
        fmt_fix="U1"
        + "U1" * 3
        + "U4U4U4"
        + "U1" * 4
        + "U4U2U2U2"
        + "U1" * 2
        + "U2U1U1"
        + "U1" * 8,
        payload_len_var=24,
        fmt_var="U1U1U1U1I4I4U2U2U4U1U1" + "U1" * 2,
        scale_fix=(1,)
        + (1,) * 3
        + (1, 1, 1)
        + (1,) * 4
        + (1, 2e-4, 2e-4, 2e-4)
        + (1,) * 2
        + (2e-4, 1, 1)
        + (1,) * 8,
        hdr_fix=("version",)
        + ("reserved1",) * 3
        + ("gpsTOW (ms)", "gloTOW (ms)", "bdsTOW (ms)")
        + ("reserved2",) * 4
        + ("qzssTOW (ms)", "gpsTOWacc (ms)", "gloTOWacc (ms)", "bdsTOWacc (ms)")
        + ("reserved3",) * 2
        + ("qzssTOWacc", "numSV", "flags")
        + ("reserved4",) * 8,
        scale_var=(1, 1, 1, 1, 0.04, 0.2, 1, 1, 2e-21, 1, 1) + (1,) * 2,
        hdr_var=(
            "gnssId",
            "svId",
            "cNo",
            "mpathIndic",
            "dopplerMS (m/s)",
            "dopplerHz (Hz)",
            "wholeChips",
            "fracChips",
            "codePhase (ms)",
            "intCodePhase (ms)",
            "pseuRangeRMSErr",
        )
        + ("reserved5",) * 2,
    ),
    mid(MsgClass.RXM, RxmID.RAWX): dict(
        # @todo svid + gnssid
        # @todo nの扱い
        name="rxm_rawx",
        payload_len_fix=16,
        fmt_fix="R8U2I1U1X1" + "U1" * 3,
        payload_len_var=32,
        fmt_var="R8R8R4U1U1U1U1U2U1X1X1X1X1U1",
        scale_fix=(1, 1, 1, 1, 1) + (1,) * 3,
        hdr_fix=("rcvTow (ms)", "week (weeks)", "leapS (s)", "numMeas", "recStat")
        + ("reserved1",) * 3,
        scale_var=(
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
            0.004,
            1,
            1,
            1,
        ),  # (1,1,1,1,1,1,1,1,1,0.01*2**n,0.004,0.002*2**n,1,1),
        hdr_var=(
            "prMes (m)",
            "cpMes (cycles)",
            "doMes (Hz)",
            "gnssId",
            "svId",
            "reserved2",
            "freqId",
            "locktime (ms)",
            "cno (dBHz)",
            "prStdev (unscaled)",
            "cpStdev (cycles)",
            "doStdev (unscaled)",
            "trkStat",
            "reserved3",
        ),  # ["prMes (m)", "cpMes (cycles)", "doMes (Hz)", "gnssId", "svId", "reserved2", "freqId", "locktime (ms)", "cno (dBHz)", "prStdev (m)", "cpStdev (cycles)", "doStdev (Hz)", "trkStat", "reserved3"]
    ),
    mid(MsgClass.RXM, RxmID.SVSI): dict(
        fmt_fix="U4I2U1U1",
    ),
    mid(MsgClass.RXM, RxmID.IMES): dict(
        name="rxm_imes",
        payload_len_fix=4,
        fmt_fix="U1U1" + "U1" * 2,
        payload_len_var=44,
        fmt_var="U1U1" + "U1" * 3 + "U1" + "U1" * 2 + "I4X4X4X4I4I4X4U4X4",
        scale_fix=(1, 1) + (1,) * 2,
        hdr_fix=("numTx", "version") + ("reserved1",) * 2,
        scale_var=(1, 1)
        + (1,) * 3
        + (1,)
        + (1,) * 2
        + (2e-12, 1, 1, 1, 180 * 2e-24, 360 * 2e-25, 1, 1, 1),
        hdr_var=("reserved2", "txId")
        + ("reserved3",) * 3
        + ("cno (dBHz)",)
        + ("reserved4",) * 2
        + (
            "doppler (Hz)",
            "position1_1",
            "position1_2",
            "position2_1",
            "lat (deg)",
            "log (deg)",
            "shortIdFrame",
            "mediumIdLSB",
            "mediumId_2",
        ),
    ),
    mid(MsgClass.MON, MonID.IO): dict(
        fmt_var="U4U4U2U2U2U2" + "U1" * 4,
        scale_var=(1, 1, 1, 1, 1, 1) + (1,) * 4,
        hdr_var=(
            "rxBytes (bytes)",
            "txBytes (bytes)",
            "parityErrs",
            "framingErrs",
            "overrunErrs",
            "breakCond",
        )
        + ("reserved1",) * 4,
    ),
    mid(MsgClass.MON, MonID.VER): dict(
        name="mon_ver",
        payload_len_fix=40,
        fmt_fix="CH" * 30 + "CH" * 10,
        payload_len_var=30,
        fmt_var="CH" * 30,
        scale_fix=(1,) * 30 + (1,) * 10,
        hdr_fix=("swVersion",) * 30 + ("hwVersion",) * 10,
        scale_var=(1,) * 30,
        hdr_var=("extension",) * 30,
    ),
    mid(MsgClass.MON, MonID.HW): dict(
        payload_len_fix=60,
        fmt_fix="X4X4X4X4U2U2U1U1X1U1X4" + "U1" * 17 + "U1" + "U1" * 2 + "X4X4X4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) + (1,) * 17 + (1,) * 2 + (1, 1, 1),
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
        + ("reserved2",) * 2
        + ("pinIrq", "pullH", "pullL"),
    ),
    mid(MsgClass.MON, MonID.HW2): dict(
        fmt_fix="I1U1I1U1U1" + "U1" * 3 + "U4" + "U1" * 8 + "U4" + "U1" * 4,
        scale_fix=(1, 1, 1, 1, 1) + (1,) * 3 + (1,) + (1,) * 8 + (1,) + (1,) * 4,
        hdr_fix=("ofsI", "magI", "ofsQ", "magQ", "cfgSource")
        + ("reserved1",) * 3
        + ("lowLevCfg",)
        + ("reserved2",) * 8
        + ("postStatus",)
        + ("reserved3",) * 4,
    ),
    mid(MsgClass.MON, MonID.PATCH): dict(
        name="mon_patch",
        payload_len_fix=4,
        fmt_fix="U2U2",
        payload_len_var=16,
        fmt_var="X4U4U4U4",
        scale_fix=(
            1,
            1,
        ),
        hdr_fix=("version", "nEntries"),
        scale_var=(
            1,
            1,
            1,
            1,
        ),
        hdr_var=("patchInfo", "comparatorNumber", "patchAddress", "patchData"),
    ),
    mid(MsgClass.MON, MonID.SMGR): dict(
        name="mon_smgr",
        payload_len_fix=16,
        fmt_fix="U1" + "U1" * 3 + "U4X2X2U1X1X1X1",
        scale_fix=(1,) + (1,) * 3 + (1, 1, 1, 1, 1, 1, 1),
        hdr_fix=("version",)
        + ("reserved1",) * 3
        + ("iTOW (ms)", "intOsc", "extOsc", "discSrc", "gnss", "extInt0", "extInt1"),
    ),
    mid(MsgClass.TIM, TimID.TP): dict(
        fmt_fix="U4U4I4U2X1X1",
        hdr_fix=(
            "towMS (ms)",
            "towSubMS (ms)",
            "qErr (ps)",
            "week (weeks)",
            "flags",
            "refInfo",
        ),
    ),
    mid(MsgClass.TIM, TimID.TM2): dict(
        hdr_fix=(
            "ch",
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
    mid(MsgClass.TIM, TimID.SVIN): dict(
        fmt_fix="U4I4I4I4U4U4U1U1" + "U1" * 2,
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1) + (1,) * 2,
        hdr_fix=(
            "dur (s)",
            "meanX (cm)",
            "meanY (cm)",
            "meanZ (cm)",
            "meanV (mm^2)",
            "obs",
            "valid",
            "active",
        )
        + ("reserved1",) * 2,
    ),
    mid(MsgClass.TIM, TimID.VCOCAL): dict(
        name="tim_vcocal",
        payload_len_fix=12,
        fmt_fix="U1U1U1" + "U1" * 3 + "U2I4",
        scale_fix=(1, 1, 1, 1) + (1,) * 2 + (1, 1, 1),
        hdr_fix=("type", "version", "oscId", "srcId")
        + ("reserved1",) * 2
        + ("raw0", "raw1", "maxStepSize (raw value/s)"),
    ),
    mid(MsgClass.TIM, TimID.FCHG): dict(
        name="tim_fchg",
        payload_len_fix=32,
        fmt_fix="U1" + "U1" * 3 + "U4I4U4U4I4U4U4",
        scale_fix=(1,) + (1,) * 3 + (1, 2 ^ -8, 2 ^ -8, 1, 2 ^ -8, 2 ^ -8, 1),
        hdr_fix=("version",)
        + ("reserved1",) * 3
        + (
            "iTOW (ms)",
            "intDeltaFreq (ppb)",
            "intDeltaFreqUnc (ppb)",
            "intRaw",
            "extDeltaFreq (ppb)",
            "extDeltaFreqUnc (ppb)",
            "extRaw",
        ),
    ),
    mid(MsgClass.ESF, EsfID.INS): dict(
        name="esf_ins",
        payload_len_fix=36,
        fmt_fix="U4" + "U1" * 4 + "U4I4I4I4I4I4I4",
        scale_fix=(1,) + (1,) * 4 + (1, 1e-3, 1e-3, 1e-3, 1e-2, 1e-2, 1e-2),
        hdr_fix=("bitfield0",)
        + ("reserved1",) * 4
        + (
            "iTOW (ms)",
            "xAngRate (deg/s)",
            "yAngRate (deg/s)",
            "zAngRate (deg/s)",
            "xAccel (m/s^2)",
            "yAccel (m/s^2)",
            "zAccel (m/s^2)",
        ),
    ),
    mid(MsgClass.ESF, EsfID.STATUS): dict(
        name="esf_status",
        payload_len_fix=16,
        fmt_fix="U4U1" + "U1" * 7 + "U1" + "U1" * 2 + "U1",
        payload_len_var=4,
        fmt_var="X1X1U1X1",
        scale_fix=(
            1,
            1,
        )
        + (1,) * 7
        + (1,)
        + (1,) * 2
        + (1,),
        hdr_fix=(
            "iTOW (ms)",
            "version",
        )
        + ("reserved1",) * 7
        + ("fusionMode",)
        + ("reserved2",) * 2
        + ("numSens",),
        scale_var=(
            1,
            1,
            1,
            1,
        ),
        hdr_var=(
            "sensStatus1",
            "sensStatus2",
            "freq (Hz)",
            "faults",
        ),
    ),
    mid(MsgClass.LOG, LogID.BATCH): dict(
        name="log_batch",
        payload_len_fix=100,
        fmt_fix="U1X1U2U4U2U1U1U1U1U1X1U4I4U1X1X1U1I4I4I4I4U4U4I4I4I4I4I4U4U4U2"
        + "U1" * 2
        + "U4U4U4"
        + "U1" * 4,
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
        )
        + (1,) * 2
        + (
            1,
            1,
            1,
        )
        + (1,) * 4,
        hdr_fix=(
            "version",
            "contentValid",
            "msgCnt",
            "iTOW (ms)",
            "year (y)",
            "month (month)",
            "day (d)",
            "hour (h)",
            "min (min)",
            "sec (s)",
            "valid",
            "tAcc (ns)",
            "fracSec (ns)",
            "fixType",
            "flags",
            "flags2",
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
            "headMot (deg)",
            "sAcc (mm/s)",
            "headAcc (deg)",
            "pDOP",
        )
        + ("reserved1",) * 2
        + (
            "distance (m)",
            "totalDistance (m)",
            "distanceStd (m)",
        )
        + ("reserved2",) * 4,
    ),
    mid(MsgClass.HNR, HnrID.PVT): dict(
        name="hnr_pvt",
        payload_len_fix=72,
        fmt_fix="U4U2U1U1U1U1U1X1I4U1X1"
        + "U1" * 2
        + "I4I4I4I4I4I4I4I4U4U4U4U4"
        + "U1" * 4,
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
        )
        + (1,) * 2
        + (
            1e-7,
            1e-7,
            1,
            1,
            1,
            1,
            1e-5,
            1e-5,
            1,
            1,
            1,
            1e-5,
        )
        + (1,) * 4,
        hdr_fix=(
            "iTOW (ms)",
            "year (y)",
            "month (month)",
            "day (d)",
            "hour (h)",
            "min (min)",
            "sec (s)",
            "valid",
            "nano (ns)",
            "gpsFix",
            "flags",
        )
        + ("reserved1",) * 2
        + (
            "lon (deg)",
            "lat (deg)",
            "height (mm)",
            "hMSL (mm)",
            "gSpeed (mm/s)",
            "speed (mm/s)",
            "headMot (deg)",
            "headVeh (deg)",
            "hAcc (mm)",
            "vAcc (mm)",
            "sAcc (mm)",
            "headAcc (deg)",
        )
        + ("reserved2",) * 4,
    ),
    mid(MsgClass.HNR, HnrID.INS): dict(
        name="hnr_ins",
        payload_len_fix=36,
        fmt_fix="X4" + "U1" * 4 + "U4I4I4I4I4I4I4",
        scale_fix=(1,) + (1,) * 4 + (1, 1, 1, 1, 1, 1, 1),
        hdr_fix=("bitfield0",)
        + ("reserved1",) * 4
        + (
            "iTOW (ms)",
            "xAngRate (deg/s)",
            "yAngRate (deg/s)",
            "zAngRate (deg/s)",
            "xAccel (m/s^2)",
            "yAccel (m/s^2)",
            "zAccel (m/s^2)",
        ),
    ),
}
GEN9_PATCH: Mapping[int, dict] = {
    mid(MsgClass.NAV, NavID.STATUS): dict(
        hdr_fix=(
            "iTOW (ms)",
            "gpsFix",
            "flags",
            "fixStat",
            "flags2",
            "ttff (ms)",
            "msss (ms)",
        ),
    ),
    mid(MsgClass.NAV, NavID.PVT): dict(
        name="nav_pvt",
        payload_len_fix=92,
        fmt_fix="U4U2U1U1U1U1U1X1U4I4U1X1X1U1I4I4I4I4U4U4I4I4I4I4I4U4U4U2X1"
        + "U1" * 5
        + "I4I2U2",
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
        )
        + (1,) * 5
        + (1e-5, 1e-2, 1e-2),
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
            "flags2",
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
            "headMot (deg)",
            "sAcc (mm/s)",
            "headAcc (deg)",
            "pDOP",
            "flags3",
        )
        + ("reserved1",) * 5
        + ("headVeh (deg)", "magDec (deg)", "magAcc (deg)"),
    ),
    mid(MsgClass.NAV, NavID.ODO): dict(
        name="nav_odo",
        payload_len_fix=20,
        fmt_fix="U1" + "U1" * 3 + "U4U4U4U4",
        scale_fix=(1,) + (1,) * 3 + (1, 1, 1, 1),
        hdr_fix=("version",)
        + ("reserved1",) * 3
        + ("iTOW (ms)", "distance (m)", "totalDistance (m)", "distanceStd (m)"),
    ),
    mid(MsgClass.NAV, NavID.HPPOSECEF): dict(
        name="nav_hpposecef",
        payload_len_fix=28,
        fmt_fix="U1" + "U1" * 3 + "U4I4I4I4I1I1I1X1U4",
        scale_fix=(1,) + (1,) * 3 + (1, 1, 1, 1, 0.1, 0.1, 0.1, 1, 0.1),
        hdr_fix=("version",)
        + ("reserved1",) * 3
        + (
            "iTOW (ms)",
            "ecefX (cm)",
            "ecefY (cm)",
            "ecefZ (cm)",
            "ecefXHp (mm)",
            "ecefYHp (mm)",
            "ecefZHp (mm)",
            "flags",
            "pAcc (mm)",
        ),
    ),
    mid(MsgClass.NAV, NavID.HPPOSLLH): dict(
        name="nav_hpposllh",
        fmt_fix="U1" + "U1" * 2 + "X1U4I4I4I4I4I1I1I1I1U4U4",
        scale_fix=(1,)
        + (1,) * 2
        + (1, 1, 1e-7, 1e-7, 1, 1, 1e-9, 1e-9, 0.1, 0.1, 0.1, 0.1),
        hdr_fix=("version",)
        + ("reserved1",) * 2
        + (
            "flags",
            "iTOW (ms)",
            "log (deg)",
            "lat (deg)",
            "height (mm)",
            "hMSL (mm)",
            "lonHp (deg)",
            "latHp (deg)",
            "heightHp (mm)",
            "heightHp (mm)",
            "hAcc (mm)",
            "vAcc (mm)",
        ),
    ),
    mid(MsgClass.NAV, NavID.TIMEGLO): dict(
        name="nav_timeglo",
        payload_len_fix=20,
        fmt_fix="U4U4I4U2U1X1U4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "iTOW (ms)",
            "TOD (s)",
            "fTOD (ns)",
            "Nt (days)",
            "N4",
            "valid",
            "tAcc (ns)",
        ),
    ),
    mid(MsgClass.NAV, NavID.TIMEBDS): dict(
        name="nav_timebds",
        payload_len_fix=20,
        fmt_fix="U4U4I4I2I1X1U4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "iTOW (ms)",
            "SOW (s)",
            "fSOW (ns)",
            "week",
            "leapS (s)",
            "valid",
            "tAcc (ns)",
        ),
    ),
    mid(MsgClass.NAV, NavID.TIMEGAL): dict(
        name="nav_timegal",
        payload_len_fix=20,
        fmt_fix="U4U4I4I2I1X1U4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1),
        hdr_fix=(
            "iTOW (ms)",
            "galTow (s)",
            "fGalTow (ns)",
            "galWno",
            "leapS (s)",
            "valid",
            "tAcc (ns)",
        ),
    ),
    mid(MsgClass.NAV, NavID.TIMELS): dict(
        name="nav_timels",
        payload_len_fix=24,
        fmt_fix="U4U1" + "U1" * 3 + "U1I1U1I1I4U2U2" + "U1" * 3 + "X1",
        scale_fix=(
            1,
            1,
        )
        + (1,) * 3
        + (1, 1, 1, 1, 1, 1, 1)
        + (1,) * 3
        + (1,),
        hdr_fix=("iTOW (ms)", "version")
        + ("reserved1",) * 3
        + (
            "srcOfCurrLs",
            "currLs (s)",
            "srcOfLsChange",
            "lsChange (s)",
            "timeToLsEvent (s)",
            "dateOfLsGpsWn",
            "dateOfLsGpsDn",
        )
        + ("reserved2",) * 3
        + ("valid",),
    ),
    mid(MsgClass.NAV, NavID.TIMEQZSS): dict(
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
    mid(MsgClass.NAV, NavID.SBAS): dict(
        # @todo svid
        fmt_var="U1U1U1U1U1U1I2" + "U1" * 2 + "I2",
        scale_fix=(1, 1, 1, 1, 1, 1) + (1,) * 3,
        hdr_fix=("iTOW (ms)", "geo", "mode", "sys", "service", "cnt")
        + ("reserved0",) * 3,
        scale_var=(1, 1, 1, 1, 1, 1, 1) + (1,) * 2 + (1,),
        hdr_var=("svid", "flags", "udre", "svSys", "svService", "reserved1", "prc")
        + ("reserved2",) * 2
        + ("ic",),
    ),
    mid(MsgClass.NAV, NavID.ORB): dict(
        # @todo svid + gnssid
        name="nav_orb",
        payload_len_fix=8,
        fmt_fix="U4U1U1" + "U1" * 2,
        payload_len_var=6,
        fmt_var="U1U1X1X1X1X1",
        scale_fix=(1, 1, 1) + (1,) * 2,
        hdr_fix=("iTOW (ms)", "version", "numSvs") + ("reserved1",) * 2,
        scale_var=(
            1,
            1,
            1,
            1,
            1,
            1,
        ),
        hdr_var=("gnssId", "svId", "svFlag", "eph", "alm", "otherOrb"),
    ),
    mid(MsgClass.NAV, NavID.SAT): dict(
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
    mid(MsgClass.NAV, NavID.COV): dict(
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
    mid(MsgClass.NAV, NavID.GEOFENCE): dict(
        # @todo numFences
        name="nav_geofence",
        payload_len_fix=8,
        fmt_fix="U4U1U1U1U1",
        payload_len_var=2,
        fmt_var="U1U1",
        scale_fix=(1, 1, 1, 1, 1),
        hdr_fix=("iTOW (ms)", "version", "status", "numFences", "combState"),
        scale_var=(1, 1),
        hdr_var=("state", "id"),
    ),
    mid(MsgClass.NAV, NavID.SVIN): dict(
        name="nav_svin",
        payload_len_fix=40,
        fmt_fix="U1" + "U1" * 3 + "U4U4I4I4I4I1I1I1U1U4U4U1U1" + "U1" * 2,
        scale_fix=(1,) + (1,) * 3 + (1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) + (1,) * 2,
        hdr_fix=("version",)
        + ("reserved1",) * 3
        + (
            "iTOW (ms)",
            "dur (s)",
            "meanX (cm)",
            "meanY (cm)",
            "meanZ (cm)",
            "meanXHP (0.1_mm)",
            "meanYHP (0.1_mm)",
            "meanZHP (0.1_mm)",
            "reserved2",
            "meanAcc (0.1_mm)",
            "obs",
            "valid",
            "active",
        )
        + ("reserved3",) * 2,
    ),
    mid(MsgClass.NAV, NavID.RELPOSNED): dict(
        name="nav_relposned",
        payload_len_fix=64,
        fmt_fix="U1U1U2U4I4I4I4I4I4"
        + "U1" * 4
        + "I1I1I1I1U4U4U4U4U4"
        + "U1" * 4
        + "X4",
        scale_fix=(
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1,
            1e-5,
        )
        + (1,) * 4
        + (
            0.1,
            0.1,
            0.1,
            0.1,
            0.1,
            0.1,
            0.1,
            0.1,
            1e-5,
        )
        + (1,) * 4
        + (1,),
        hdr_fix=(
            "version",
            "reserved1",
            "refStationId",
            "iTOW (ms)",
            "relPosN (cm)",
            "relPosE (cm)",
            "relPosD (cm)",
            "relPosLength (cm)",
            "relPosHeading (deg)",
        )
        + ("reserved2",) * 4
        + (
            "relPosHPN (mm)",
            "relPosHPE (mm)",
            "relPosHPD (mm)",
            "relPosHPLength (mm)",
            "accN (mm)",
            "accE (mm)",
            "accD (mm)",
            "accLength (mm)",
            "accHeading (deg)",
        )
        + ("reserved3",) * 4
        + ("flags",),
    ),
    mid(MsgClass.NAV, NavID.SIG): dict(
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
    mid(MsgClass.RXM, RxmID.MEASX): dict(
        # @todo svid + gnssid
        name="rxm_measx",
        payload_len_fix=44,
        fmt_fix="U1"
        + "U1" * 3
        + "U4U4U4"
        + "U1" * 4
        + "U4U2U2U2"
        + "U1" * 2
        + "U2U1U1"
        + "U1" * 8,
        payload_len_var=24,
        fmt_var="U1U1U1U1I4I4U2U2U4U1U1" + "U1" * 2,
        scale_fix=(1,)
        + (1,) * 3
        + (1, 1, 1)
        + (1,) * 4
        + (1, 2e-4, 2e-4, 2e-4)
        + (1,) * 2
        + (2e-4, 1, 1)
        + (1,) * 8,
        hdr_fix=("version",)
        + ("reserved1",) * 3
        + ("gpsTOW (ms)", "gloTOW (ms)", "bdsTOW (ms)")
        + ("reserved2",) * 4
        + ("qzssTOW (ms)", "gpsTOWacc (ms)", "gloTOWacc (ms)", "bdsTOWacc (ms)")
        + ("reserved3",) * 2
        + ("qzssTOWacc", "numSV", "flags")
        + ("reserved4",) * 8,
        scale_var=(1, 1, 1, 1, 0.04, 0.2, 1, 1, 2e-21, 1, 1) + (1,) * 2,
        hdr_var=(
            "gnssId",
            "svId",
            "cNo",
            "mpathIndic",
            "dopplerMS (m/s)",
            "dopplerHz (Hz)",
            "wholeChips",
            "fracChips",
            "codePhase (ms)",
            "intCodePhase (ms)",
            "pseuRangeRMSErr",
        )
        + ("reserved5",) * 2,
    ),
    mid(MsgClass.RXM, RxmID.RAWX): dict(
        # @todo svid + gnssid
        # @todo nの扱い
        name="rxm_rawx",
        payload_len_fix=16,
        fmt_fix="R8U2I1U1X1" + "U1" * 3,
        payload_len_var=32,
        fmt_var="R8R8R4U1U1U1U1U2U1X1X1X1X1U1",
        scale_fix=(1, 1, 1, 1, 1, 1) + (1,) * 2,
        hdr_fix=(
            "rcvTow (ms)",
            "week (weeks)",
            "leapS (s)",
            "numMeas",
            "recStat",
            "version",
        )
        + ("reserved1",) * 2,
        scale_var=(
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
            0.004,
            1,
            1,
            1,
        ),  # (1,1,1,1,1,1,1,1,1,0.01*2**n,0.004,0.002*2**n,1,1),
        hdr_var=(
            "prMes (m)",
            "cpMes (cycles)",
            "doMes (Hz)",
            "gnssId",
            "svId",
            "reserved2",
            "freqId",
            "locktime (ms)",
            "cno (dBHz)",
            "prStdev (unscaled)",
            "cpStdev (cycles)",
            "doStdev (unscaled)",
            "trkStat",
            "reserved3",
        ),  # ["prMes (m)", "cpMes (cycles)", "doMes (Hz)", "gnssId", "svId", "reserved2", "freqId", "locktime (ms)", "cno (dBHz)", "prStdev (m)", "cpStdev (cycles)", "doStdev (Hz)", "trkStat", "reserved3"]
    ),
    mid(MsgClass.CFG, CfgID.VALGET): dict(
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
    mid(MsgClass.MON, MonID.IO): dict(
        fmt_var="U4U4U2U2U2U2" + "U1" * 4,
        scale_var=(1, 1, 1, 1, 1, 1) + (1,) * 4,
        hdr_var=(
            "rxBytes (bytes)",
            "txBytes (bytes)",
            "parityErrs",
            "framingErrs",
            "overrunErrs",
            "breakCond",
        )
        + ("reserved1",) * 4,
    ),
    mid(MsgClass.MON, MonID.VER): dict(
        name="mon_ver",
        payload_len_fix=40,
        fmt_fix="CH" * 30 + "CH" * 10,
        payload_len_var=30,
        fmt_var="CH" * 30,
        scale_fix=(1,) * 30 + (1,) * 10,
        hdr_fix=("swVersion",) * 30 + ("hwVersion",) * 10,
        scale_var=(1,) * 30,
        hdr_var=("extension",) * 30,
    ),
    mid(MsgClass.MON, MonID.HW): dict(
        payload_len_fix=60,
        fmt_fix="X4X4X4X4U2U2U1U1X1U1X4" + "U1" * 17 + "U1" + "U1" * 2 + "X4X4X4",
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) + (1,) * 17
        # + (1,)
        + (1,) * 2 + (1, 1, 1),
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
        + ("reserved2",) * 2
        + ("pinIrq", "pullH", "pullL"),
    ),
    mid(MsgClass.MON, MonID.HW2): dict(
        fmt_fix="I1U1I1U1U1" + "U1" * 3 + "U4" + "U1" * 8 + "U4" + "U1" * 4,
        scale_fix=(1, 1, 1, 1, 1) + (1,) * 3 + (1,) + (1,) * 8 + (1,) + (1,) * 4,
        hdr_fix=("ofsI", "magI", "ofsQ", "magQ", "cfgSource")
        + ("reserved1",) * 3
        + ("lowLevCfg",)
        + ("reserved2",) * 8
        + ("postStatus",)
        + ("reserved3",) * 4,
    ),
    mid(MsgClass.MON, MonID.PATCH): dict(
        name="mon_patch",
        payload_len_fix=4,
        fmt_fix="U2U2",
        payload_len_var=16,
        fmt_var="X4U4U4U4",
        scale_fix=(
            1,
            1,
        ),
        hdr_fix=("version", "nEntries"),
        scale_var=(
            1,
            1,
            1,
            1,
        ),
        hdr_var=("patchInfo", "comparatorNumber", "patchAddress", "patchData"),
    ),
    mid(MsgClass.MON, MonID.GNSS): dict(
        name="mon_gnss",
        payload_len_fix=8,
        fmt_fix="U1X1X1X1U1" + "U1" * 3,
        scale_fix=(1, 1, 1, 1, 1) + (1,) * 3,
        hdr_fix=("version", "supported", "defaultGnss", "enabled", "simultaneous")
        + ("reserved1",) * 3,
    ),
    mid(MsgClass.MON, MonID.SPAN): dict(
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
    mid(MsgClass.MON, MonID.COMMS): dict(
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
    mid(MsgClass.MON, MonID.HW3): dict(
        # @todo nPins (pinId)
        name="mon_hw3",
        payload_len_fix=22,
        fmt_fix="U1U1X1" + "CH" * 10 + "U1" * 9,
        payload_len_var=6,
        fmt_var="U2X2U1U1",
        scale_fix=(
            1,
            1,
            1,
        )
        + (1,) * 10
        + (1,) * 9,
        hdr_fix=(
            "version",
            "nPins",
            "flags",
        )
        + ("hwVersion",) * 10
        + ("reserved1",) * 9,
        scale_var=(
            1,
            1,
            1,
            1,
        ),
        hdr_var=(
            "pinId",
            "pinMask",
            "VP",
            "reserved2",
        ),
    ),
    mid(MsgClass.MON, MonID.RF): dict(
        # @todo nBlocks (blockId)
        name="mon_rf",
        payload_len_fix=4,
        fmt_fix="U1U1" + "U1" * 2,
        payload_len_var=24,
        fmt_var="U1X1U1U1U4" + "U1" * 4 + "U2U2U1I1U1I1U1" + "U1" * 3,
        scale_fix=(1, 1) + (1,) * 2,
        hdr_fix=("version", "nBlocks") + ("reserved1",) * 2,
        scale_var=(
            1,
            1,
            1,
            1,
            1,
        )
        + (1,) * 4
        + (
            1,
            1,
            1,
            1,
            1,
            1,
            1,
        )
        + (1,) * 3,
        hdr_var=(
            "blockId",
            "flags",
            "antStatus",
            "antPower",
            "postStatus",
        )
        + ("reserved2",) * 4
        + (
            "noisePerMS",
            "agcCnt",
            "jamInd",
            "ofsI",
            "magI",
            "ofsQ",
            "magQ",
        )
        + ("reserved3",) * 3,
    ),
    mid(MsgClass.MON, MonID.SYS): dict(
        name="mon_sys",
        payload_len_fix=24,
        fmt_fix="U1U1U1U1U1U1U1U1U4U2U2U2I1" + "U1" * 5,
        scale_fix=(1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1) + (1,) * 5,
        hdr_fix=(
            "msgVer",
            "bootType",
            "cpuLoad",
            "cpuLoadMax",
            "memUsage",
            "memUsageMax",
            "ioUsage",
            "ioUsageMax",
            "rumTime",
            "noticeCount",
            "warnCount",
            "errorCount",
            "tempValue",
        )
        + ("reserved0",) * 5,
    ),
    mid(MsgClass.TIM, TimID.TP): dict(
        fmt_fix="U4U4I4U2X1X1",
        hdr_fix=(
            "towMS (ms)",
            "towSubMS (ms)",
            "qErr (ps)",
            "week (weeks)",
            "flags",
            "refInfo",
        ),
    ),
    mid(MsgClass.TIM, TimID.TM2): dict(
        hdr_fix=(
            "ch",
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
    mid(MsgClass.SEC, SecID.SIGLOG): dict(
        name="sec_siglog",
        payload_len_fix=8,
        fmt_fix="U1U1" + "U1" * 6,
        payload_len_var=8,
        fmt_var="U4U1U1" + "U1" * 2,
        scale_fix=(1, 1) + (1,) * 6,
        hdr_fix=("version", "numevents") + ("reserved0",) * 6,
        scale_var=(
            1,
            1,
            1,
        )
        + (1,) * 2,
        hdr_var=(
            "timeElasped",
            "detectionType",
            "eventType",
        )
        + ("reserved1",) * 2,
    ),
}


# _RE = re.compile(r"CH|R8|R4|U4|I4|X4|U2|I2|X2|U1|I1|X1")
# --- 1. モジュール定数として一元化 ------------------------
FMT_TO_STRUCT: dict[str, str] = {
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
FMT_RE = re.compile("|".join(FMT_TO_STRUCT))


# --- 2. 共通関数 -----------------------------------------
@functools.lru_cache(maxsize=None)
def convert_fmt(fmt: str) -> str:
    """UBX フォーマット文字列 → struct フォーマット文字列"""
    return FMT_RE.sub(lambda m: FMT_TO_STRUCT[m.group(0)], fmt)


class UbxPatchModel(BaseModel):
    name: str | None = None
    payload_len_fix: int | None = None
    fmt_fix: str | None = None
    payload_len_var: int | None = None
    fmt_var: str | None = None
    scale_fix: Tuple[float, ...] | None = None
    hdr_fix: Tuple[str, ...] | None = None
    scale_var: Tuple[float, ...] | None = None
    hdr_var: Tuple[str, ...] | None = None

    # ① 不明キーを禁止
    model_config = dict(extra="forbid")

    # ② 例: fmt と payload_len の整合性チェック
    @model_validator(mode="after")
    def check_lengths_fmt_fix(self):
        if self.fmt_fix is not None:
            expected = len(self.fmt_fix) // 2  # フォーマット2文字で1フィールドと仮定
            if expected * 2 != len(self.fmt_fix):
                raise ValueError("fmt_fix の長さが2文字単位ではありません")
        return self

    @model_validator(mode="after")
    def check_lengths_fmt_var(self):
        if self.fmt_var is not None:
            expected = len(self.fmt_var) // 2  # フォーマット2文字で1フィールドと仮定
            if expected * 2 != len(self.fmt_var):
                raise ValueError("fmt_var の長さが2文字単位ではありません")
        return self

    @model_validator(mode="after")
    def check_lengths_fix(self):
        if self.scale_fix is not None and self.hdr_fix is not None:
            if len(self.scale_fix) != len(self.hdr_fix):
                # for i, (s, h) in enumerate(zip(self.scale_fix, self.hdr_fix)):
                #     print(f"{i}: {s} {h}")
                raise ValueError(
                    f"scale_fix と hdr_fix の長さが一致しません: {len(self.scale_fix)} != {len(self.hdr_fix)}"
                )
        return self

    @model_validator(mode="after")
    def check_lengths_var(self):
        if self.scale_var is not None and self.hdr_var is not None:
            if len(self.scale_var) != len(self.hdr_var):
                # for i, (s, h) in enumerate(zip(self.scale_var, self.hdr_var)):
                #     print(f"{i}: {s} {h}")
                raise ValueError(
                    f"scale_var と hdr_var の長さが一致しません: {len(self.scale_var)} != {len(self.hdr_var)}"
                )
        return self

    @model_validator(mode="after")
    def check_size_fix(self):
        if self.fmt_fix and self.payload_len_fix is not None:
            struct_fmt = "<" + convert_fmt(self.fmt_fix)
            expected_bytes = struct.calcsize(struct_fmt)
            if expected_bytes != self.payload_len_fix:
                raise ValueError(
                    f"payload_len_fix={self.payload_len_fix} だが "
                    f"fmt_fix から計算したサイズは {expected_bytes} B"
                )
        return self

    @model_validator(mode="after")
    def check_size_var(self):
        if self.fmt_var and self.payload_len_var is not None:
            struct_fmt = "<" + convert_fmt(self.fmt_var)
            expected_bytes = struct.calcsize(struct_fmt)
            if expected_bytes != self.payload_len_var:
                raise ValueError(
                    f"payload_len_var={self.payload_len_var} だが "
                    f"fmt_var から計算したサイズは {expected_bytes} B"
                )
        return self


def validate_patches(raw_patch: Mapping[int, dict]) -> dict[int, UbxPatchModel]:
    validated: dict[int, UbxPatchModel] = {}
    for mid, patch_dict in raw_patch.items():
        try:
            validated[mid] = UbxPatchModel(**patch_dict)
        except Exception as e:
            raise RuntimeError(
                f"パッチ 0x{mid:04X} {patch_dict} の検証に失敗: {e}"
            ) from None
    return validated

GEN6_PATCH_VALID = validate_patches(GEN6_PATCH)
GEN7_PATCH_VALID = validate_patches(GEN7_PATCH)
GEN8_PATCH_VALID = validate_patches(GEN8_PATCH)
GEN9_PATCH_VALID = validate_patches(GEN9_PATCH)


def build_desc(
    base: Mapping[int, UbxMsgDesc], patch: Mapping[int, dict]
) -> Dict[int, UbxMsgDesc]:
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
            print(f"{mid:04X} {overrides}" )
        
        else:
            # (b) 新規定義
            merged = overrides
        result[mid] = UbxMsgDesc(**merged)

    return result


ubx_messages_6 = build_desc(GEN6, GEN6_PATCH)
ubx_messages_7 = build_desc(GEN6, GEN7_PATCH)
ubx_messages_8 = build_desc(GEN6, GEN8_PATCH)
ubx_messages_9 = build_desc(GEN6, GEN9_PATCH)


class Ublox:
    def __init__(self, desc: UbxMsgDesc) -> None:
        self.payload = []
        self.msg_desc = desc

    # @functools.lru_cache(maxsize=None)
    # def _conv(self, format_string: str) -> str:
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
    #     return _RE.sub(lambda m: _MAP[m.group(0)], format_string)

    def _conv(self, fmt: str) -> str:
        return convert_fmt(fmt)

    def unpack(self, dat: bytes) -> list[str | float]:
        desc = self.msg_desc
        if desc.payload_len_var:
            rem = len(dat) - desc.payload_len_fix
            if rem % desc.payload_len_var:
                raise ValueError(
                    f"Payload length {len(dat)} is not multiple of "
                    f"{desc.payload_len_var} for message {desc.name}"
                )
            n_var = rem // desc.payload_len_var
        else:
            n_var = 0

        fmt = self._conv(desc.fmt_fix) + self._conv(desc.fmt_var) * n_var
        # if desc.name == "nav_sbas":
        #     print(len(desc.fmt_fix), len(desc.fmt_var), n_var, len(fmt))
        values = list(struct.unpack("<" + fmt, dat))

        # CH(=bytes) を文字列へ
        if "c" in fmt:
            values = [
                v.decode("ascii", "ignore") if isinstance(v, bytes) else v
                for v in values
            ]
        return values
        # # raw data
        # n_var = 0
        # if self.msg_desc.payload_len_var != 0:
        #     dat_size = len(dat)
        #     n_var = int(
        #         (dat_size - self.msg_desc.payload_len_fix)
        #         / self.msg_desc.payload_len_var
        #     )
        #     if n_var < 0:
        #         raise ValueError(
        #             f"Invalid payload length: {dat_size} < {self.msg_desc.payload_len_fix}"
        #         )

        # payload_format = self._conv(self.msg_desc.fmt_fix)
        # if self.msg_desc.payload_len_var != 0:
        #     payload_format_var = self._conv(self.msg_desc.fmt_var) * n_var
        #     payload_format += payload_format_var
        # raw_data = struct.unpack("<" + payload_format, dat)
        # return raw_data

    def append(self, dat) -> None:
        unpacked = self.unpack(dat)
        self.payload.append(unpacked)

    def save_csv(self, filename: str) -> None:
        if not filename.endswith(".csv"):
            raise ValueError("Filename must end with .csv")
        if len(self.payload) > 0:

            # def conv_func():
            #     return pd.DataFrame(self.payload)

            df = pd.DataFrame(self.payload)
            # df = conv_func()
            df_columns_len = len(df.columns)
            header = list(self.msg_desc.hdr_fix)
            scale_full = list(self.msg_desc.scale_fix)
            if self.msg_desc.payload_len_var != 0:
                headers_number_var = int(
                    (df_columns_len - len(self.msg_desc.hdr_fix))
                    / len(self.msg_desc.hdr_var)
                )
                header += list(self.msg_desc.hdr_var) * headers_number_var
                scale_full += list(self.msg_desc.scale_var) * headers_number_var

            if len(scale_full) != df.shape[1]:
                raise ValueError(
                    f"Scale length mismatch: {len(scale_full)} != {df.shape[1]}\n{df}"
                )

            # def scale_func(dframe, scale):
            # return dframe.mul(scale, axis=1)

            # df = scale_func(df, scale_full)
            df = df.mul(scale_full, axis=1)

            header[0] = "# " + header[0]
            if len(df.columns) == len(header):
                df.columns = header
            else:
                raise ValueError(
                    f"Header length mismatch: {len(df.columns)} != {len(header)}"
                )

            # def save_func(dframe, fname):
            #     dframe.to_csv(fname, index=False)

            df.to_csv(filename, index=False)
            # save_func(df, filename)
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
