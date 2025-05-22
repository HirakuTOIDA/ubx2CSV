from typing import Mapping
from class_id import mid, MsgClass, NavID, RxmID, MonID, TimID, CfgID, SecID

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
        payload_len_fix=36,
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
