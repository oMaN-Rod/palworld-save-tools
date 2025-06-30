import enum
import zlib
import ctypes
from pathlib import Path

MAGIC_BYTES = [b"PlZ", b"PlM"]

# Oodle constants
OODLE_FUZ_YES = 1
OODLE_FUZ_NO = 0


class OODLELZ_COMPRESSOR(int, enum.Enum):
    OodleLZ_Compressor_None = 3
    OodleLZ_Compressor_Kraken = 8
    OodleLZ_Compressor_Mermaid = 9
    OodleLZ_Compressor_Selkie = 11
    OodleLZ_Compressor_Hydra = 12
    OodleLZ_Compressor_Leviathan = 13


class OODLELZ_COMPRESSION_LEVEL(int, enum.Enum):
    OodleLZ_CompressionLevel_None = 0
    OodleLZ_CompressionLevel_SuperFast = 1
    OodleLZ_CompressionLevel_VeryFast = 2
    OodleLZ_CompressionLevel_Fast = 3
    OodleLZ_CompressionLevel_Normal = 4
    OodleLZ_CompressionLevel_Optimal1 = 5
    OodleLZ_CompressionLevel_Optimal2 = 6
    OodleLZ_CompressionLevel_Optimal3 = 7
    OodleLZ_CompressionLevel_Optimal4 = 8
    OodleLZ_CompressionLevel_Optimal5 = 9

    OodleLZ_CompressionLevel_HyperFast1 = -1
    OodleLZ_CompressionLevel_HyperFast2 = -2
    OodleLZ_CompressionLevel_HyperFast3 = -3
    OodleLZ_CompressionLevel_HyperFast4 = -4


def _load_oodle_lib(lib_path: str):
    try:
        oodle_lib = ctypes.CDLL(lib_path)

        # Define the function signature for OodleLZ_Decompress
        # int OodleLZ_Decompress(const void *compBuf, SINTa compBufSize, void *rawBuf, SINTa rawLen,
        #                        int fuzzSafe, int checkCRC, int verbosity, void *decBufBase,
        #                        SINTa decBufSize, void *fpCallback, void *callbackUserData,
        #                        void *decoderMemory, SINTa decoderMemorySize, int threadPhase)
        oodle_decompress = oodle_lib.OodleLZ_Decompress
        oodle_decompress.argtypes = [
            ctypes.c_void_p,  # compBuf
            ctypes.c_int64,  # compBufSize
            ctypes.c_void_p,  # rawBuf
            ctypes.c_int64,  # rawLen
            ctypes.c_int,  # fuzzSafe
            ctypes.c_int,  # checkCRC
            ctypes.c_int,  # verbosity
            ctypes.c_void_p,  # decBufBase
            ctypes.c_int64,  # decBufSize
            ctypes.c_void_p,  # fpCallback
            ctypes.c_void_p,  # callbackUserData
            ctypes.c_void_p,  # decoderMemory
            ctypes.c_int64,  # decoderMemorySize
            ctypes.c_int,  # threadPhase
        ]
        oodle_decompress.restype = ctypes.c_int64

        # Define the function signature for OodleLZ_Compress
        # SINTa OodleLZ_Compress(int codec, const void *rawBuf, SINTa rawLen, void *compBuf, int level,
        #                        const void *pOptions, SINTa offsetOfDecodeBuffer, SINTa decBufSize,
        #                        void *scratchMem, SINTa scratchSize)
        oodle_compress = oodle_lib.OodleLZ_Compress
        oodle_compress.argtypes = [
            ctypes.c_int,  # codec
            ctypes.c_void_p,  # rawBuf
            ctypes.c_int64,  # rawLen
            ctypes.c_void_p,  # compBuf
            ctypes.c_int,  # level
            ctypes.c_void_p,  # pOptions
            ctypes.c_int64,  # offsetOfDecodeBuffer
            ctypes.c_int64,  # decBufSize
            ctypes.c_void_p,  # scratchMem
            ctypes.c_int64,  # scratchSize
        ]
        oodle_compress.restype = ctypes.c_int64

        return oodle_decompress, oodle_compress
    except Exception:
        return None


def _decompress_with_oodle(
    compressed_data: bytes, uncompressed_len: int, oodle_path: str
) -> bytes:
    oodle_lib_result = _load_oodle_lib(oodle_path)
    if oodle_lib_result is None:
        raise Exception("Failed to load Oodle library")

    oodle_decompress, _ = oodle_lib_result

    output_buffer = ctypes.create_string_buffer(uncompressed_len)

    result = oodle_decompress(
        compressed_data,  # compBuf
        len(compressed_data),  # compBufSize
        output_buffer,  # rawBuf
        uncompressed_len,  # rawLen
        OODLE_FUZ_YES,  # fuzzSafe
        0,  # checkCRC
        0,  # verbosity
        None,  # decBufBase
        0,  # decBufSize
        None,  # fpCallback
        None,  # callbackUserData
        None,  # decoderMemory
        0,  # decoderMemorySize
        0,  # threadPhase
    )

    if result <= 0:
        raise Exception(f"Oodle decompression failed with result: {result}")

    return output_buffer.raw[:result]


def _compress_with_oodle(data: bytes, oodle_path: str) -> bytes:
    oodle_lib_result = _load_oodle_lib(oodle_path)
    if oodle_lib_result is None:
        raise Exception("Failed to load Oodle library")

    _, oodle_compress = oodle_lib_result

    # Estimate maximum compressed size (usually 1.1x the original size should be enough)
    max_compressed_size = len(data) + len(data) // 10 + 1024
    output_buffer = ctypes.create_string_buffer(max_compressed_size)

    result = oodle_compress(
        OODLELZ_COMPRESSOR.OodleLZ_Compressor_Mermaid.value,  # codec
        data,  # rawBuf
        len(data),  # rawLen
        output_buffer,  # compBuf
        OODLELZ_COMPRESSION_LEVEL.OodleLZ_CompressionLevel_Normal.value,  # level
        None,  # pOptions
        0,  # offsetOfDecodeBuffer
        0,  # decBufSize
        None,  # scratchMem
        0,  # scratchSize
    )

    if result <= 0:
        raise Exception(f"Oodle compression failed with result: {result}")

    return output_buffer.raw[:result]


def decompress_sav_to_gvas(data: bytes, oodle_path: str) -> tuple[bytes, int]:
    uncompressed_len = int.from_bytes(data[0:4], byteorder="little")
    compressed_len = int.from_bytes(data[4:8], byteorder="little")
    magic_bytes = data[8:11]
    save_type = data[11]
    data_start_offset = 12
    # Check for magic bytes
    if magic_bytes == b"CNK":
        uncompressed_len = int.from_bytes(data[12:16], byteorder="little")
        compressed_len = int.from_bytes(data[16:20], byteorder="little")
        magic_bytes = data[20:23]
        save_type = data[23]
        data_start_offset = 24
    if magic_bytes not in MAGIC_BYTES:
        if (
            magic_bytes == b"\x00\x00\x00"
            and uncompressed_len == 0
            and compressed_len == 0
        ):
            raise Exception(
                "not a compressed Palworld save, found too many null bytes, this is likely corrupted"
            )
        raise Exception(
            f"not a compressed Palworld save, found {magic_bytes!r} instead of {MAGIC_BYTES!r}"
        )
    # Valid save types
    if save_type not in [0x30, 0x31, 0x32]:
        raise Exception(f"unknown save type: {save_type}")
    # We only have 0x31 (single zlib) and 0x32 (double zlib) saves
    if save_type not in [0x31, 0x32]:
        raise Exception(f"unhandled compression type: {save_type}")

    if magic_bytes == b"PlM":
        compressed_data = data[data_start_offset:]
        if compressed_len != len(compressed_data):
            raise Exception(f"incorrect compressed length: {compressed_len}")

        uncompressed_data = _decompress_with_oodle(
            compressed_data, uncompressed_len, oodle_path
        )
        # Verify the uncompressed length
        if uncompressed_len != len(uncompressed_data):
            raise Exception(
                f"incorrect uncompressed length after Oodle decompression: expected {uncompressed_len}, got {len(uncompressed_data)}"
            )
        return uncompressed_data, save_type

    # Decompress file
    uncompressed_data = zlib.decompress(data[data_start_offset:])
    if save_type == 0x32:
        # Check if the compressed length is correct
        if compressed_len != len(uncompressed_data):
            raise Exception(f"incorrect compressed length: {compressed_len}")
        # Decompress file
        uncompressed_data = zlib.decompress(uncompressed_data)
    # Check if the uncompressed length is correct
    if uncompressed_len != len(uncompressed_data):
        raise Exception(f"incorrect uncompressed length: {uncompressed_len}")
    return uncompressed_data, save_type


def compress_gvas_to_sav(
    data: bytes, save_type: int, use_oodle: bool = True, oodle_path: str | None = None
) -> bytes:
    uncompressed_len = len(data)

    if use_oodle and oodle_path:
        # Use Oodle compression with PlM magic bytes
        compressed_data = _compress_with_oodle(data, oodle_path)
        compressed_len = len(compressed_data)
        magic_bytes = b"PlM"
    else:
        # Use zlib compression with PlZ magic bytes
        compressed_data = zlib.compress(data)
        compressed_len = len(compressed_data)
        if save_type == 0x32:
            compressed_data = zlib.compress(compressed_data)
        magic_bytes = b"PlZ"

    # Create a byte array and append the necessary information
    result = bytearray()
    result.extend(uncompressed_len.to_bytes(4, byteorder="little"))
    result.extend(compressed_len.to_bytes(4, byteorder="little"))
    result.extend(magic_bytes)
    result.extend(bytes([save_type]))
    result.extend(compressed_data)

    return bytes(result)
