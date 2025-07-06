from palworld_save_tools.compressor import Compressor
from palworld_save_tools.compressor.oozlib import OozLib
from palworld_save_tools.compressor.zlib import Zlib
from palworld_save_tools.compressor.enums import SaveType

compressor = Compressor()
oozlib = OozLib()
z_lib = Zlib()


def decompress_sav_to_gvas(data: bytes, zlib: bool = False) -> tuple[bytes, int]:
    format = compressor.check_sav_format(data)

    if format is None:
        raise Exception("Unknown save format")

    match format:
        case SaveType.PLZ | SaveType.CNK:
            return z_lib.decompress(data)
        case SaveType.PLM:
            return oozlib.decompress(data)
        case _:
            raise Exception("Unknown save format")


def compress_gvas_to_sav(data: bytes, save_type: int, zlib: bool = False) -> bytes:
    format = compressor.check_savtype_format(save_type)

    if format is None:
        raise Exception("Unknown save type format")

    match format:
        case SaveType.PLZ | SaveType.CNK:
            return z_lib.compress(data, save_type)
        case SaveType.PLM:
            return oozlib.compress(data, save_type)
