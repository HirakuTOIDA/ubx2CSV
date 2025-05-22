# -*- coding: utf-8 -*-
import struct
import pandas as pd
import model

UBX_SYNC: bytes = bytes((0xB5, 0x62))

class Ublox:
    def __init__(self, desc: model.UbxMsgDesc) -> None:
        self.payload = []
        self.msg_desc = desc

    def _conv(self, fmt: str) -> str:
        return model.convert_fmt(fmt)

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
        values = list(struct.unpack("<" + fmt, dat))

        # CH(=bytes) を文字列へ
        if "c" in fmt:
            values = [
                v.decode("ascii", "ignore") if isinstance(v, bytes) else v
                for v in values
            ]
        return values

    def append(self, dat) -> None:
        unpacked = self.unpack(dat)
        self.payload.append(unpacked)

    def save_csv(self, filename: str) -> None:
        if not filename.endswith(".csv"):
            raise ValueError("Filename must end with .csv")
        if len(self.payload) > 0:

            df = pd.DataFrame(self.payload)

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

            df = df.mul(scale_full, axis=1)

            header[0] = "# " + header[0]
            if len(df.columns) == len(header):
                df.columns = header
            else:
                raise ValueError(
                    f"Header length mismatch: {len(df.columns)} != {len(header)}"
                )

            df.to_csv(filename, index=False)
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
