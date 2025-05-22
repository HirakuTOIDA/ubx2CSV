import dataclasses
from class_id import mid, MsgClass, NavID, RxmID, MonID, TimID, AidID


@dataclasses.dataclass(frozen=True, slots=True)
class UbxMsgDesc:
    name: str
    payload_len_fix: int = 0
    fmt_fix: str = ""
    payload_len_var: int = 0
    fmt_var: str = ""
    scale_fix: tuple[float, ...] = ()
    hdr_fix: tuple[str, ...] = ()
    scale_var: tuple[float, ...] = ()
    hdr_var: tuple[str, ...] = ()


GEN6: dict[int, UbxMsgDesc] = {
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
        hdr_var=("sf1d",) * 8 + ("sf2d",) * 8 + ("sf3d",) * 8,
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
        hdr_fix=("msg1 (msgs)",) * 8
        + ("msg2 (msgs)",) * 8
        + ("msg3 (msgs)",) * 8
        + ("msg4 (msgs)",) * 8
        + ("msg5 (msgs)",) * 8
        + ("msg6 (msgs)",) * 8
        + ("skipped (bytes)",) * 6,
    ),
    mid(MsgClass.MON, MonID.RXBUF): UbxMsgDesc(
        name="mon_rxbuf",
        payload_len_fix=24,
        fmt_fix="U2" * 6 + "U1" * 6 + "U1" * 6,
        scale_fix=(1,) * 6 + (1,) * 6 + (1,) * 6,
        hdr_fix=("pending (bytes)",) * 6 + ("usage (%)",) * 6 + ("peakUsage (%)",) * 6,
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
