import dataclasses
import struct, functools
import re
from typing import Mapping
from pydantic import BaseModel, model_validator
from class_id import mid, MsgClass, NavID, RxmID, MonID, AidID, TimID, EsfID, LogID, HnrID, CfgID, SecID
import ublox_base, ublox7_patch, ublox8_patch, ublox9_patch
from ublox_base import UbxMsgDesc


GEN6 = ublox_base.GEN6

# ---------- 世代差分を「上書き」だけで表現 ----------
GEN6_PATCH: Mapping[int, dict] = {}
GEN7_PATCH = ublox7_patch.GEN7_PATCH
GEN8_PATCH = ublox8_patch.GEN8_PATCH
GEN9_PATCH = ublox9_patch.GEN9_PATCH

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
TOKENS = sorted(FMT_TO_STRUCT, key=len, reverse=True)  # 長い順に！
FMT_RE = re.compile("|".join(TOKENS))


@functools.lru_cache(maxsize=None)
def convert_fmt(fmt: str) -> str:
    """UBX フォーマット文字列 → struct フォーマット文字列"""
    return FMT_RE.sub(lambda m: FMT_TO_STRUCT[m.group(0)], fmt)


class UbxDescValidator(BaseModel):
    name: str | None = None
    payload_len_fix: int | None = None
    fmt_fix: str | None = None
    payload_len_var: int | None = None
    fmt_var: str | None = None
    scale_fix: tuple[float, ...] | None = None
    hdr_fix: tuple[str, ...] | None = None
    scale_var: tuple[float, ...] | None = None
    hdr_var: tuple[str, ...] | None = None

    model_config = dict(extra="forbid")

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
                raise ValueError(
                    f"scale_fix と hdr_fix の長さが一致しません: {len(self.scale_fix)} != {len(self.hdr_fix)}"
                )
        return self

    @model_validator(mode="after")
    def check_lengths_var(self):
        if self.scale_var is not None and self.hdr_var is not None:
            if len(self.scale_var) != len(self.hdr_var):
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


# ---------------- パッチ側 -----------------
def validate_patch_keys(raw_patch: Mapping[int, dict]) -> None:
    valid_keys = set(UbxMsgDesc.__annotations__)  # 全フィールド名
    for mid, patch_dict in raw_patch.items():
        unknown = set(patch_dict) - valid_keys
        if unknown:
            raise ValueError(f"unknown keys {unknown} in patch 0x{mid:04X}")


def build_desc(
    base: Mapping[int, UbxMsgDesc], patch: Mapping[int, dict]
) -> dict[int, UbxMsgDesc]:
    """
    base + patch をマージして完全な UbxMsgDesc 辞書を返す。
    * 生成した **最終 dict** は必ず UbxDescValidator で検証する。
    """
    result: dict[int, UbxMsgDesc] = {}

    # ① base をコピー
    for mid, base_desc in base.items():
        result[mid] = UbxMsgDesc(**dataclasses.asdict(base_desc))

    # ② patch を適用
    for mid, overrides in patch.items():
        unknown = set(overrides) - set(UbxMsgDesc.__annotations__)
        if unknown:
            raise ValueError(f"unknown patch keys for 0x{mid:04X}: {unknown}")

        merged_dict = {
            **dataclasses.asdict(result.get(mid, UbxMsgDesc(name="__dummy__"))),
            **overrides,
        }

        # ③ ★完成形をバリデート★
        try:
            UbxDescValidator(**merged_dict)  # ← ここで整合性を検査
        except Exception as e:
            raise RuntimeError(
                f"フォーマット定義 0x{mid:04X} の検証に失敗: {e}"
            ) from None

        # ④ OK なら dataclass 化して格納
        result[mid] = UbxMsgDesc(**merged_dict)

    return result


validate_patch_keys(GEN6_PATCH)
validate_patch_keys(GEN7_PATCH)
validate_patch_keys(GEN8_PATCH)
validate_patch_keys(GEN9_PATCH)

ubx_messages_6 = build_desc(GEN6, GEN6_PATCH)
ubx_messages_7 = build_desc(GEN6, GEN7_PATCH)
ubx_messages_8 = build_desc(GEN6, GEN8_PATCH)
ubx_messages_9 = build_desc(GEN6, GEN9_PATCH)
