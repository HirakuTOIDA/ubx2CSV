from typing import Mapping
from class_id import mid, MsgClass, NavID, RxmID, MonID, TimID, EsfID, LogID, HnrID

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
