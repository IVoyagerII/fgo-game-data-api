import hashlib
import time
from collections import defaultdict
from typing import Any, Optional, Sequence, Union

import orjson
from pydantic import DirectoryPath
from sqlalchemy import Table
from sqlalchemy.engine import Connection, Engine

from ..config import logger
from ..data.buff import get_buff_with_classrelation
from ..data.event import get_event_with_warIds
from ..data.item import get_item_with_use
from ..data.script import get_script_path, get_script_text_only
from ..models.raw import (
    TABLES_TO_BE_LOADED,
    ScriptFileList,
    mstBuff,
    mstEvent,
    mstFunc,
    mstFuncGroup,
    mstItem,
    mstSkillLv,
    mstSubtitle,
    mstTreasureDeviceLv,
)
from ..models.rayshift import rayshiftQuest
from ..schemas.base import BaseModelORJson
from ..schemas.common import Region
from ..schemas.enums import FUNC_VALS_NOT_BUFF
from ..schemas.raw import get_subtitle_svtId
from ..schemas.rayshift import QuestDetail, QuestList
from .engine import engines
from .helpers.rayshift import (
    fetch_missing_quest_ids,
    insert_rayshift_quest_db_sync,
    insert_rayshift_quest_list,
)


def recreate_table(conn: Connection, table: Table) -> None:  # pragma: no cover
    table.drop(conn, checkfirst=True)
    table.create(conn, checkfirst=True)


def insert_db(conn: Connection, table: Table, db_data: Any) -> None:  # pragma: no cover
    recreate_table(conn, table)
    conn.execute(table.insert(), db_data)


def check_known_columns(
    data: list[dict[str, Any]], table: Table
) -> bool:  # pragma: no cover
    table_columns = {column.name for column in table.columns}
    return set(data[0].keys()).issubset(table_columns)


def remove_unknown_columns(
    data: list[dict[str, Any]], table: Table
) -> list[dict[str, Any]]:  # pragma: no cover
    table_columns = {column.name for column in table.columns}
    return [{k: v for k, v in item.items() if k in table_columns} for item in data]


def load_skill_td_lv(
    engine: Engine, gamedata_path: DirectoryPath
) -> None:  # pragma: no cover
    master_folder = gamedata_path / "master"

    mstBuff_data = get_buff_with_classrelation(gamedata_path)
    mstBuffId = {buff.id: buff for buff in mstBuff_data}

    with open(master_folder / "mstFunc.json", "rb") as fp:
        mstFunc_data = orjson.loads(fp.read())
        mstFuncId = {func["id"]: func for func in mstFunc_data}

    mstFuncGroupId = defaultdict(list)
    with open(master_folder / "mstFuncGroup.json", "rb") as fp:
        mstFuncGroup_data = orjson.loads(fp.read())
        for funcGroup in mstFuncGroup_data:
            mstFuncGroupId[funcGroup["funcId"]].append(funcGroup)

    with open(master_folder / "mstSkillLv.json", "rb") as fp:
        mstSkillLv_data = orjson.loads(fp.read())

    with open(master_folder / "mstTreasureDeviceLv.json", "rb") as fp:
        mstTreasureDeviceLv_data = orjson.loads(fp.read())

    def get_func_entity(func_id: int) -> dict[Any, Any]:
        func_entity = {
            "mstFunc": mstFuncId[func_id],
            "mstFuncGroup": mstFuncGroupId.get(func_id, []),
        }

        if (
            func_entity["mstFunc"]["funcType"] not in FUNC_VALS_NOT_BUFF
            and func_entity["mstFunc"]["vals"]
            and func_entity["mstFunc"]["vals"][0] in mstBuffId
        ):
            func_entity["mstFunc"]["expandedVals"] = [
                {"mstBuff": mstBuffId[func_entity["mstFunc"]["vals"][0]].dict()}
            ]
        else:
            func_entity["mstFunc"]["expandedVals"] = []

        return func_entity

    for skillLv in mstSkillLv_data:
        skillLv["expandedFuncId"] = [
            get_func_entity(func_id)
            for func_id in skillLv["funcId"]
            if func_id in mstFuncId
        ]

    for treasureDeviceLv in mstTreasureDeviceLv_data:
        treasureDeviceLv["expandedFuncId"] = [
            get_func_entity(func_id)
            for func_id in treasureDeviceLv["funcId"]
            if func_id in mstFuncId
        ]

    load_pydantic_to_db(engine, mstBuff_data, mstBuff)

    with engine.begin() as conn:
        insert_db(conn, mstFunc, mstFunc_data)
        insert_db(conn, mstFuncGroup, mstFuncGroup_data)
        insert_db(conn, mstSkillLv, mstSkillLv_data)
        insert_db(conn, mstTreasureDeviceLv, mstTreasureDeviceLv_data)


def load_event(
    engine: Engine, gamedata_path: DirectoryPath
) -> None:  # pragma: no cover
    mstEvents = get_event_with_warIds(gamedata_path)
    mstEvent_db_data = [svtExtra.dict() for svtExtra in mstEvents]
    with engine.begin() as conn:
        insert_db(conn, mstEvent, mstEvent_db_data)


def load_item(engine: Engine, gamedata_path: DirectoryPath) -> None:  # pragma: no cover
    mstItems = get_item_with_use(gamedata_path)
    mstItem_db_data = [item.dict() for item in mstItems]
    with engine.begin() as conn:
        insert_db(conn, mstItem, mstItem_db_data)


def load_script_list(
    engine: Engine, repo_folder: DirectoryPath
) -> None:  # pragma: no cover
    script_list_file = (
        repo_folder
        / "ScriptActionEncrypt"
        / ScriptFileList.name
        / f"{ScriptFileList.name}.txt"
    )
    db_data: list[dict[str, Union[int, str, None]]] = []

    if script_list_file.exists():
        with open(script_list_file, encoding="utf-8") as fp:
            script_list = [line.strip() for line in fp.readlines()]

        with open(repo_folder / "master" / "mstQuest.json", "rb") as bfp:
            mstQuest = orjson.loads(bfp.read())

        questId = {quest["id"] for quest in mstQuest}

        scriptQuestId = {
            quest["scriptQuestId"]: quest["id"]
            for quest in mstQuest
            if quest["scriptQuestId"] != 0
        }

        for script in script_list:
            script_path = (
                repo_folder
                / "ScriptActionEncrypt"
                / f"{get_script_path(script.removesuffix('.txt'))}.txt"
            )
            if script_path.exists():
                with open(script_path, "r", encoding="utf-8") as fp:
                    script_data = fp.read()
                    script_text = get_script_text_only(script_data)
                    script_sha1 = hashlib.sha1(script_text.encode("utf-8")).hexdigest()
            else:
                script_data = ""
                script_text = ""
                script_sha1 = ""

            script_name = script.removesuffix(".txt")
            quest_ids: list[Optional[int]] = []
            phase: Optional[int] = None
            sceneType: Optional[int] = None

            if len(script) == 14 and script[0] in ("0", "9"):
                script_int = int(script_name[:-2])

                sceneType = int(script_name[-1])
                phase = int(script_name[-2])

                if script_int in scriptQuestId:
                    quest_ids.append(scriptQuestId[script_int])

                if script_int in questId and script_int not in scriptQuestId.values():
                    quest_ids.append(script_int)

            if not quest_ids:
                quest_ids.append(None)

            for quest_id in quest_ids:
                db_data.append(
                    {
                        "scriptFileName": script_name,
                        "questId": quest_id,
                        "phase": phase,
                        "sceneType": sceneType,
                        "rawScriptSHA1": script_sha1,
                        "rawScript": script_data,
                        "textScript": script_text,
                    }
                )

    with engine.begin() as conn:
        insert_db(conn, ScriptFileList, db_data)


def load_subtitle(
    engine: Engine, region: Region, master_folder: DirectoryPath
) -> None:  # pragma: no cover
    subtitle_json = master_folder / "globalNewMstSubtitle.json"
    if subtitle_json.exists():
        with open(subtitle_json, "rb") as fp:
            globalNewMstSubtitle = orjson.loads(fp.read())

        for subtitle in globalNewMstSubtitle:
            subtitle["svtId"] = get_subtitle_svtId(subtitle["id"])
    else:
        if region == Region.NA:
            logger.warning(f"Can't find file {subtitle_json}.")
        globalNewMstSubtitle = []

    with engine.begin() as conn:
        insert_db(conn, mstSubtitle, globalNewMstSubtitle)


def load_pydantic_to_db(
    engine: Engine, pydantic_data: Sequence[BaseModelORJson], db_table: Table
) -> None:  # pragma: no cover
    db_data = [item.dict() for item in pydantic_data]
    with engine.begin() as conn:
        insert_db(conn, db_table, db_data)


def update_db(region_path: dict[Region, DirectoryPath]) -> None:  # pragma: no cover
    logger.info("Loading db …")
    start_loading_time = time.perf_counter()

    for region, repo_folder in region_path.items():
        logger.info(f"Updating {region} tables …")
        master_folder = repo_folder / "master"
        engine = engines[region]

        for table in TABLES_TO_BE_LOADED:
            table_json = master_folder / f"{table.name}.json"
            if table_json.exists():
                with open(table_json, "rb") as fp:
                    data: list[dict[str, Any]] = orjson.loads(fp.read())

                if len(data) > 0 and not check_known_columns(data, table):
                    logger.warning(f"Found unknown columns in {table_json}")
                    data = remove_unknown_columns(data, table)
            else:
                if not (
                    region == Region.NA
                    and table.name
                    in {
                        "mstStageRemap",
                        "mstSvtAdd",
                        "mstSvtAppendPassiveSkill",
                        "mstSvtAppendPassiveSkillUnlock",
                        "mstCombineAppendPassiveSkill",
                        "mstSvtCoin",
                        "mstSkillAdd",
                        "mstTreasureBox",
                        "mstTreasureBoxGift",
                    }
                ):
                    logger.warning(f"Can't find file {table_json}.")
                data = []

            with engine.begin() as conn:
                logger.info(f"Updating {table.name} …")
                insert_db(conn, table, data)

        logger.info("Updating subtitle …")
        load_subtitle(engine, region, master_folder)

        logger.info("Updating parsed skill and td …")
        load_skill_td_lv(engine, repo_folder)

        logger.info("Updating event …")
        load_event(engine, repo_folder)

        logger.info("Updating item …")
        load_item(engine, repo_folder)

        logger.info("Updating script list …")
        load_script_list(engine, repo_folder)

        with engine.begin() as conn:
            rayshiftQuest.create(conn, checkfirst=True)

    db_loading_time = time.perf_counter() - start_loading_time
    logger.info(f"Loaded db in {db_loading_time:.2f}s.")


def load_rayshift_quest_list(region: Region, quest_list: list[QuestList]) -> None:
    with engines[region].begin() as conn:
        rayshiftQuest.create(conn, checkfirst=True)
        insert_rayshift_quest_list(conn, quest_list)


def get_missing_query_ids(region: Region) -> list[int]:
    with engines[region].connect() as conn:
        query_ids = fetch_missing_quest_ids(conn)
    return query_ids


def load_rayshift_quest_details(
    region: Region, quest_details: dict[int, QuestDetail]
) -> None:
    with engines[region].begin() as conn:
        insert_rayshift_quest_db_sync(conn, quest_details)
