import orjson
import pytest
from aioredis import Redis
from fastapi import HTTPException

from app.core.nice.func import parse_dataVals
from app.core.nice.nice import get_nice_servant_model
from app.core.utils import get_lang_en, sort_by_collection_no
from app.db.engine import engines
from app.routers.utils import list_string_exclude
from app.schemas.basic import BasicServant
from app.schemas.common import Language, Region, ReverseDepth
from app.schemas.gameenums import FuncType
from app.schemas.raw import get_subtitle_svtId


def test_subtitle_svtId() -> None:
    assert get_subtitle_svtId("PLAINDEMO_99100001") == -1


@pytest.mark.asyncio
async def test_parse_dataVals_add_state_6_items(redis: Redis) -> None:
    result = await parse_dataVals(
        redis, Region.NA, FuncType.ADD_STATE, "[1000,3,3,300,1000,10]"
    )
    assert result == {
        "Rate": 1000,
        "Turn": 3,
        "Count": 3,
        "Value": 300,
        "UseRate": 1000,
        "Value2": 10,
    }


@pytest.mark.asyncio
async def test_parse_dataVals_unknown_datavals(
    redis: Redis, caplog: pytest.LogCaptureFixture
) -> None:
    await parse_dataVals(redis, Region.NA, FuncType.SUB_STATE, "[1000,3,3,300]")
    assert (
        "Some datavals weren't parsed for func type 2: "
        "[1000,3,3,300] => {'Rate': 1000, 'Value': 3, 'Value2': 3}" in caplog.text
    )


@pytest.mark.asyncio
async def test_parse_dataVals_class_drop_up_rate(redis: Redis) -> None:
    result = await parse_dataVals(
        redis,
        Region.NA,
        FuncType.CLASS_DROP_UP,
        "[2,400,80017]",
    )
    result = {k: v for k, v in result.items() if "aa" not in k}
    assert result == {
        "EventId": 80017,
        "RateCount": 400,
    }


cases_datavals_fail_dict = {
    "test_dataVals_fail_str_dataVals_no_value": "[HideMiss]",
    "test_dataVals_fail_str_dataVals_str_value": "[HideMiss:123/abc]",
    "test_dataVals_fail_list_str": "[TargetList:123/abc]",
    "test_dataVals_fail_str_not_a_list": "[TargetList:abc]",
}


cases_datavals_fail = [
    pytest.param(value, id=key) for key, value in cases_datavals_fail_dict.items()
]


@pytest.mark.asyncio
@pytest.mark.parametrize("dataVals", cases_datavals_fail)
async def test_parse_datavals_fail_list_str(redis: Redis, dataVals: str) -> None:
    with pytest.raises(HTTPException):
        await parse_dataVals(redis, Region.NA, 1, dataVals)


def test_reverseDepth_str_comparison() -> None:
    assert ReverseDepth.function >= "aaaaa"


def test_sort_by_collection_no() -> None:
    first_item = BasicServant(
        id=100100,
        collectionNo=2,
        name="Altria Pendragon",
        type="normal",
        flag="normal",
        className="saber",
        rarity=5,
        atkMax=11221,
        hpMax=15150,
        face="https://assets.atlasacademy.io/GameData/NA/Faces/f_1001000.png",
    )
    second_item = BasicServant(
        id=202900,
        collectionNo=200,
        name="Asagami Fujino",
        type="normal",
        flag="normal",
        className="archer",
        rarity=4,
        atkMax=10299,
        hpMax=11025,
        face="https://assets.atlasacademy.io/GameData/NA/Faces/f_2029000.png",
    )
    input_data = [second_item, first_item]
    result = sort_by_collection_no(input_data)
    assert result == [first_item, second_item]


@pytest.mark.asyncio
async def test_list_exclude(redis: Redis) -> None:
    with engines[Region.JP].connect() as conn:
        test_data = await get_nice_servant_model(
            conn, redis, Region.JP, 504500, Language.en
        )
        excluded_keys = {"profile"}
        json_data = list_string_exclude([test_data], exclude=excluded_keys)
        for key in excluded_keys:
            assert key not in orjson.loads(json_data)


@pytest.mark.asyncio
async def test_lang_en_export(redis: Redis) -> None:
    with engines[Region.JP].connect() as conn:
        jp_nice_servant = await get_nice_servant_model(
            conn, redis, Region.JP, 202900, Language.jp
        )
        jp_nice_servant_with_en_name = get_lang_en(jp_nice_servant)
        assert jp_nice_servant_with_en_name.name == "Asagami Fujino"
