from typing import Any

from palworld_save_tools.archive import Any, FArchiveReader, FArchiveWriter


def pal_item_and_num_read(reader: FArchiveReader) -> dict[str, Any]:
    return {
        "item_id": {
            "static_id": reader.fstring(),
            "dynamic_id": {
                "created_world_id": reader.guid(),
                "local_id_in_created_world": reader.guid(),
            },
        },
        "num": reader.u32(),
    }


def pal_item_booth_trade_info_read(reader: FArchiveReader) -> dict[str, Any]:
    return {
        "product": {
            "static_id": reader.fstring(),
            "dynamic_id": {
                "created_world_id": reader.guid(),
                "local_id_in_created_world": reader.guid(),
            },
            "num": reader.u32(),
        },
        "cost": {
            "static_id": reader.fstring(),
            "dynamic_id": {
                "created_world_id": reader.guid(),
                "local_id_in_created_world": reader.guid(),
            },
            "num": reader.u32(),
        },
        "seller_player_uid": reader.guid(),
    }


def pal_item_booth_trade_info_writer(writer: FArchiveWriter, p: dict[str, Any]) -> None:
    writer.fstring(p["product"]["static_id"])
    writer.guid(p["product"]["dynamic_id"]["created_world_id"])
    writer.guid(p["product"]["dynamic_id"]["local_id_in_created_world"])
    writer.u32(p["product"]["num"])
    writer.fstring(p["cost"]["static_id"])
    writer.guid(p["cost"]["dynamic_id"]["created_world_id"])
    writer.guid(p["cost"]["dynamic_id"]["local_id_in_created_world"])
    writer.u32(p["cost"]["num"])
    writer.guid(p["seller_player_uid"])


def pal_pal_booth_trade_info_read(reader: FArchiveReader) -> dict[str, Any]:
    return {
        "pal_id": {
            "player_uid": reader.guid(),
            "instance_id": reader.guid(),
            "debug_name": reader.fstring(),
        },
        "cost": {
            "static_id": reader.fstring(),
            "dynamic_id": {
                "created_world_id": reader.guid(),
                "local_id_in_created_world": reader.guid(),
            },
            "num": reader.u32(),
        },
        "seller_player_uid": reader.guid(),
    }


def pal_pal_booth_trade_info_writer(writer: FArchiveWriter, p: dict[str, Any]) -> None:
    writer.guid(p["pal_id"]["player_uid"])
    writer.guid(p["pal_id"]["instance_id"])
    writer.fstring(p["pal_id"]["debug_name"])
    writer.fstring(p["cost"]["static_id"])
    writer.guid(p["cost"]["dynamic_id"]["created_world_id"])
    writer.guid(p["cost"]["dynamic_id"]["local_id_in_created_world"])
    writer.u32(p["cost"]["num"])
    writer.guid(p["seller_player_uid"])


def pal_item_and_slot_writer(writer: FArchiveWriter, p: dict[str, Any]) -> None:
    writer.fstring(p["item_id"]["static_id"])
    writer.guid(p["item_id"]["dynamic_id"]["created_world_id"])
    writer.guid(p["item_id"]["dynamic_id"]["local_id_in_created_world"])
    writer.u32(p["num"])
