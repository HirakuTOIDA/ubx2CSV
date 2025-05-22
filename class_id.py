from enum import IntEnum

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
