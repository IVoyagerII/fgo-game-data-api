import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Callable, NamedTuple, Union

from app.config import Settings
from app.core.utils import get_traits_list
from app.schemas.common import Region
from app.schemas.enums import ATTRIBUTE_NAME, CLASS_NAME
from app.schemas.gameenums import (
    BUFF_ACTION_NAME,
    BUFF_LIMIT_NAME,
    BUFF_TYPE_NAME,
    CARD_TYPE_NAME,
    GIFT_TYPE_NAME,
    SERVANT_FRAME_TYPE_NAME,
    BuffAction,
)


CONSTANT_INCLUDE = {
    "ATTACK_RATE",
    "ATTACK_RATE_RANDOM_MAX",
    "ATTACK_RATE_RANDOM_MIN",
    "BACKSIDE_CLASS_IMAGE_ID",
    "BACKSIDE_SVT_EQUIP_IMAGE_ID",
    "BACKSIDE_SVT_IMAGE_ID",
    "BATTLE_EFFECT_ID_AVOIDANCE",
    "BATTLE_EFFECT_ID_AVOIDANCE_PIERCE",
    "BATTLE_EFFECT_ID_INVINCIBLE",
    "BATTLE_EFFECT_ID_INVINCIBLE_PIERCE",
    "BATTLE_ITEM_DISP_COLUMN",
    "BP_EXPRESSION",
    "CHAINBONUS_ARTS_RATE",
    "CHAINBONUS_BUSTER_RATE",
    "CHAINBONUS_QUICK",
    "COMMAND_ARTS",
    "COMMAND_BUSTER",
    "COMMAND_CARD_PRM_UP_MAX",
    "COMMAND_CODE_DETACHING_ITEM_ID",
    "COMMAND_QUICK",
    "CRITICAL_ATTACK_RATE",
    "CRITICAL_INDIVIDUALITY",
    "CRITICAL_RATE_PER_STAR",
    "CRITICAL_STAR_RATE",
    "CRITICAL_TD_POINT_RATE",
    "DECK_MAX",
    "ENEMY_ATTACK_RATE_ARTS",
    "ENEMY_ATTACK_RATE_BUSTER",
    "ENEMY_ATTACK_RATE_QUICK",
    "ENEMY_MAX_BATTLE_COUNT",
    "EXTRA_ATTACK_RATE_GRAND",
    "EXTRA_ATTACK_RATE_SINGLE",
    "EXTRA_CRITICAL_RATE",
    "FOLLOWER_LIST_EXPIRE_AT",
    "FOLLOWER_REFRESH_RESET_TIME",
    "FOLLOW_FRIEND_POINT",
    "FULL_TD_POINT",
    "HEROINE_CHANGECARDVOICE",
    "HYDE_SVT_ID",
    "JEKYLL_SVT_ID",
    "LARGE_SUCCESS_MULT_EXP",
    "LARGE_SUCCESS_RATE",
    "MASHU_CHANGE_QUEST_ID",
    "MASHU_CHANGE_WAR_ID",
    "MASHU_SVT_ID1",
    "MASHU_SVT_ID2",
    "MAX_BLACK_LIST_NUM",
    "MAX_COMMAND_SPELL",
    "MAX_DROP_FACTOR",
    "MAX_EVENT_POINT",
    "MAX_EXP_FACTOR",
    "MAX_FRIENDPOINT",
    "MAX_FRIENDPOINT_BOOST_ITEM_DAILY_RECEIVE",
    "MAX_FRIENDPOINT_BOOST_ITEM_USE",
    "MAX_FRIENDSHIP_RANK",
    "MAX_FRIEND_CODE",
    "MAX_FRIEND_HISTORY_NUM",
    "MAX_FRIEND_SHIP_UP_RATIO",
    "MAX_MANA",
    "MAX_NEAR_PRESENT_OFFSET_NUM",
    "MAX_PRESENT_BOX_HISTORY_NUM",
    "MAX_PRESENT_BOX_NUM",
    "MAX_PRESENT_RECEIVE_NUM",
    "MAX_QP",
    "MAX_QP_DROP_UP_RATIO",
    "MAX_QP_FACTOR",
    "MAX_RARE_PRI",
    "MAX_RP",
    "MAX_STONE",
    "MAX_USER_COMMAND_CODE",
    "MAX_USER_EQUIP_EXP_UP_RATIO",
    "MAX_USER_ITEM",
    "MAX_USER_LV",
    "MAX_USER_SVT",
    "MAX_USER_SVT_EQUIP",
    "MAX_USER_SVT_EQUIP_STORAGE",
    "MAX_USER_SVT_STORAGE",
    "MENU_CHANGE",
    "OVER_KILL_NP_RATE",
    "OVER_KILL_STAR_ADD",
    "OVER_KILL_STAR_RATE",
    "STAR_RATE_MAX",
    "STATUS_UP_ADJUST_ATK",
    "STATUS_UP_ADJUST_HP",
    "STATUS_UP_BUFF",
    "SUPER_SUCCESS_MULT_EXP",
    "SUPER_SUCCESS_RATE",
    "SUPPORT_DECK_MAX",
    "SWIMSUIT_MELT_SVT_ID",
    "TAMAMOCAT_STUN_BUFF_ID",
    "TAMAMOCAT_TREASURE_DEVICE_ID_1",
    "TAMAMOCAT_TREASURE_DEVICE_ID_2",
    "TEMPORARY_IGNORE_SLEEP_MODE_FOR_TREASURE_DEVICE_SVT_ID_1",
    "TEMPORARY_IGNORE_SLEEP_MODE_FOR_TREASURE_DEVICE_SVT_ID_2",
    "TREASUREDEVICE_ID_MASHU3",
    "FRIEND_NUM",
    "USER_COST",
    "USER_ACT",
}


def get_nice_constant(raw_data: Any) -> Any:
    return {
        constant["name"]: constant["value"]
        for constant in raw_data
        if constant["name"] in CONSTANT_INCLUDE
    }


def get_nice_gift(raw_gift: Any) -> dict[Any, Any]:
    return {
        "id": raw_gift["id"],
        "type": GIFT_TYPE_NAME[raw_gift["type"]],
        "objectId": raw_gift["objectId"],
        "priority": raw_gift["priority"],
        "num": raw_gift["num"],
    }


def get_nice_attackrate(raw_data: Any) -> Any:
    return {
        CLASS_NAME[class_data["id"]]: class_data["attackRate"]
        for class_data in raw_data
        if class_data["id"] in CLASS_NAME
    }


def get_nice_card_data(raw_data: Any) -> Any:
    out_data: dict[str, dict[int, Any]] = {}
    for card in raw_data:
        card_id = card["id"]
        card_index = card["num"]
        card["individuality"] = [
            trait.dict(exclude_unset=True)
            for trait in get_traits_list(card["individuality"])
        ]
        card.pop("id")
        card.pop("num")
        if card_id in CARD_TYPE_NAME:
            card_name = CARD_TYPE_NAME[card_id]
            if card_name in out_data:
                out_data[card_name][card_index] = card
            else:
                out_data[card_name] = {card_index: card}
    return out_data


def get_nice_attri_relation(raw_data: Any) -> Any:
    out_data: dict[str, dict[str, int]] = {}
    for attribute_relation in raw_data:
        atkAttri = ATTRIBUTE_NAME[attribute_relation["atkAttri"]]
        defAttri = ATTRIBUTE_NAME[attribute_relation["defAttri"]]
        attackRate = attribute_relation["attackRate"]
        if atkAttri in out_data:
            out_data[atkAttri][defAttri] = attackRate
        else:
            out_data[atkAttri] = {defAttri: attackRate}
    return out_data


def get_nice_class_relation(raw_data: Any) -> Any:
    out_data: dict[str, dict[str, int]] = {}
    for class_relation in raw_data:
        atkAttri = CLASS_NAME.get(class_relation["atkClass"])
        defAttri = CLASS_NAME.get(class_relation["defClass"])
        if atkAttri and defAttri:
            attackRate = class_relation["attackRate"]
            if atkAttri in out_data:
                out_data[atkAttri][defAttri] = attackRate
            else:
                out_data[atkAttri] = {defAttri: attackRate}
    return out_data


def get_nice_svt_exceed(raw_data: Any) -> Any:
    def find_previous_exceed_qp(rarity: int, exceed: int) -> int:
        previous_exceed = next(
            svt_exceed
            for svt_exceed in raw_data
            if svt_exceed["rarity"] == rarity
            and svt_exceed["exceedCount"] == exceed - 1
        )
        previous_exceed_qp: int = previous_exceed["qp"]
        return previous_exceed_qp

    out_data: dict[int, dict[int, dict[str, Union[int, str]]]] = defaultdict(
        lambda: defaultdict(dict)
    )
    for svtExceed in raw_data:
        if svtExceed["exceedCount"] != 0:
            out_data[svtExceed["rarity"]][svtExceed["exceedCount"]] = {
                "qp": find_previous_exceed_qp(
                    svtExceed["rarity"], svtExceed["exceedCount"]
                ),
                "addLvMax": svtExceed["addLvMax"],
                "frameType": SERVANT_FRAME_TYPE_NAME[svtExceed["frameType"]],
            }

    return out_data


def get_nice_buff_action(raw_data: Any) -> Any:
    def get_max_rate(buff_types: list[int]) -> list[int]:
        return list(
            {buff["maxRate"] for buff in raw_data if buff["type"] in buff_types}
        )

    with open(
        Path(__file__).parent / "BuffList.ActionList.json", "r", encoding="utf-8"
    ) as fp:
        data = json.load(fp)

    out_data = {}

    for buff_action in data:
        out_item = data[buff_action]
        out_item["limit"] = BUFF_LIMIT_NAME[out_item["limit"]]
        out_item["maxRate"] = get_max_rate(
            out_item["plusTypes"] + out_item["minusTypes"]
        )
        out_item["plusTypes"] = [
            BUFF_TYPE_NAME[bufft] for bufft in out_item["plusTypes"]
        ]
        out_item["minusTypes"] = [
            BUFF_TYPE_NAME[bufft] for bufft in out_item["minusTypes"]
        ]
        out_data[BUFF_ACTION_NAME[BuffAction[buff_action].value]] = out_item
    return out_data


# pylint: disable=inherit-non-class
class ExportParam(NamedTuple):
    input: str
    converter: Callable[[Any], Any]
    output: str


TO_EXPORT = [
    ExportParam(
        input="mstConstant", converter=get_nice_constant, output="NiceConstant"
    ),
    ExportParam(
        input="mstClass", converter=get_nice_attackrate, output="NiceClassAttackRate"
    ),
    ExportParam(input="mstCard", converter=get_nice_card_data, output="NiceCard"),
    ExportParam(
        input="mstAttriRelation",
        converter=get_nice_attri_relation,
        output="NiceAttributeRelation",
    ),
    ExportParam(
        input="mstClassRelation",
        converter=get_nice_class_relation,
        output="NiceClassRelation",
    ),
    ExportParam(
        input="mstBuff",
        converter=get_nice_buff_action,
        output="NiceBuffList.ActionList",
    ),
    ExportParam(
        input="mstSvtExceed",
        converter=get_nice_svt_exceed,
        output="NiceSvtGrailCost",
    ),
]


def export_constant(region: Region, master_path: Path, export_path: Path) -> None:
    for export in TO_EXPORT:
        print(f"Exporting {export.input} ...")
        with open(
            master_path / "master" / f"{export.input}.json", "r", encoding="utf-8"
        ) as fp:
            raw_data = json.load(fp)
        export_file = export_path / region.value / f"{export.output}.json"
        with open(export_file, "w", encoding="utf-8") as fp:
            json.dump(export.converter(raw_data), fp, ensure_ascii=False)


def export_nice_master_lvl(region: Region, master_path: Path, export_path: Path) -> Any:
    print("Exporting nice master level ...")
    constant_path = export_path / region.value / f"{TO_EXPORT[0].output}.json"
    with open(constant_path, "r", encoding="utf-8") as fp:
        constant = json.load(fp)
    with open(master_path / "master" / "mstUserExp.json", "r", encoding="utf-8") as fp:
        mstUserExp: list[dict[str, int]] = json.load(fp)
    with open(master_path / "master" / "mstGift.json", "r", encoding="utf-8") as fp:
        mstGiftId: dict[int, dict[str, int]] = {
            gift["id"]: gift for gift in json.load(fp)
        }

    def get_current_value(base: int, key: str, current: int) -> int:
        return base + sum(user_exp[key] for user_exp in mstUserExp[: current + 1])

    def get_total_exp(current: int) -> int:
        if current == 0:
            return 0
        else:
            return mstUserExp[current - 1]["exp"]

    nice_data = {
        lvl["lv"]: {
            "requiredExp": get_total_exp(lvli),
            "maxAp": get_current_value(constant["USER_ACT"], "addActMax", lvli),
            "maxCost": get_current_value(constant["USER_COST"], "addCostMax", lvli),
            "maxFriend": get_current_value(
                constant["FRIEND_NUM"], "addFriendMax", lvli
            ),
            "gift": get_nice_gift(mstGiftId[lvl["giftId"]])
            if lvl["giftId"] != 0
            else None,
        }
        for lvli, lvl in enumerate(mstUserExp)
    }

    export_file = export_path / region.value / "NiceUserLevel.json"
    with open(export_file, "w", encoding="utf-8") as fp:
        json.dump(nice_data, fp, ensure_ascii=False)


def main() -> None:
    settings = Settings()
    region_path = [(Region.NA, settings.na_gamedata), (Region.JP, settings.jp_gamedata)]
    export_path = Path(__file__).resolve().parents[1] / "export"
    for region, gamedata in region_path:
        print(region)
        export_constant(region, gamedata, export_path)
        export_nice_master_lvl(region, gamedata, export_path)


if __name__ == "__main__":
    main()
