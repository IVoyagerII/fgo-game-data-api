# pylint: disable=R0201
import pytest
from httpx import AsyncClient

from app.schemas.enums import FUNC_VALS_NOT_BUFF

from .utils import get_response_data


DATA_FOLDER = "test_data_raw"


test_cases_dict: dict[str, tuple[str, str]] = {
    "servant_NA_collectionNo": ("NA/servant/184", "NA_Tomoe"),
    "servant_NA_id": ("NA/servant/202100", "NA_Tomoe"),
    "servant_NA_lore": ("NA/servant/156?lore=True", "NA_Moriarty_lore"),
    "servant_NA_collectionNo_expanded": (
        "NA/servant/200?expand=True",
        "NA_Fujino_expanded",
    ),
    "servant_JP_collectionNo": ("JP/servant/185", "JP_Chiyome"),
    "servant_JP_id": ("JP/servant/602900", "JP_Chiyome"),
    "equip_NA_collectionNo": ("NA/equip/184", "NA_Gentle_affection"),
    "equip_NA_id": ("NA/equip/9401400", "NA_Gentle_affection"),
    "equip_NA_collectionNo_expanded": (
        "NA/equip/375?expand=True",
        "NA_Oni_Mask_expanded",
    ),
    "svt_JP_id": ("NA/svt/9401400", "NA_Gentle_affection"),
    "skill_NA": ("NA/skill/24550", "NA_skill_24550"),
    "skill_NA_reverse": ("NA/skill/446550?reverse=True", "NA_skill_446550_reverse"),
    "skill_NA_expand": ("NA/skill/275551?expand=True", "NA_skill_275551_expand"),
    "skill_NA_reverse_expand": (
        "NA/skill/275551?expand=True&reverse=True",
        "NA_skill_275551_reverse_expand",
    ),
    "skill_JP_reverse_MC": ("JP/skill/980004?reverse=true", "JP_skill_980004_reverse"),
    "NP_NA": ("NA/NP/900101", "NA_NP_900101"),
    "NP_NA_reverse": ("NA/NP/9940531?reverse=True", "NA_NP_9940531_reverse"),
    "NP_NA_expand": ("NA/NP/202401?expand=True", "NA_NP_202401_expand"),
    "NP_NA_reverse_expand": (
        "NA/NP/301202?expand=True&reverse=True",
        "NA_NP_301202_reverse_expand",
    ),
    "function_NA": ("NA/function/433", "NA_function_433"),
    "function_NA_2": ("NA/function/400", "NA_function_400"),
    "function_NA_reverse": ("NA/function/203?reverse=True", "NA_function_203_reverse"),
    "function_NA_expand": ("NA/function/205?expand=True", "NA_function_205_expand"),
    "function_NA_expand_no_buff": (
        "NA/function/433?expand=True",
        "NA_function_433_expand",
    ),
    "function_NA_reverse_expand": (
        "NA/function/300?expand=True&reverse=True",
        "NA_function_300_reverse_expand",
    ),
    "buff_NA": ("NA/buff/200", "NA_buff_200"),
    "buff_NA_reverse": ("NA/buff/190?reverse=True", "NA_buff_190_reverse"),
    "item_JP": ("JP/item/7103", "JP_item_Lancer_Monument"),
    "MC_NA": ("JP/MC/20", "JP_MC_Plugsuit"),
    "CC_NA": ("NA/CC/8400110", "NA_CC_Fou"),
    "CC_NA_collectionNo": ("NA/CC/11", "NA_CC_Fou"),
    "event_NA": ("NA/event/80090", "NA_KNK_rerun"),
    "war_JP": ("JP/war/201", "JP_war_Shimousa"),
    "quest_NA": ("NA/quest/94026514", "NA_Artoria_rank_up_2"),
    "quest_phase_JP": ("JP/quest/94025012/1", "JP_Meaka_Fudou"),
    "ai_beni_cq_monkey_NA": ("NA/ai/svt/94032580", "NA_AI_Beni_CQ_monkey"),
    "kh_cq_JP": ("JP/ai/field/90161870", "JP_KH_CQ_taunt"),
}


test_cases = [pytest.param(*value, id=key) for key, value in test_cases_dict.items()]


@pytest.mark.asyncio
@pytest.mark.parametrize("query,result", test_cases)
async def test_raw(client: AsyncClient, query: str, result: str) -> None:
    response = await client.get(f"/raw/{query}")
    assert response.status_code == 200
    assert response.json() == get_response_data(DATA_FOLDER, result)


cases_404_dict = {
    "servant": "500",
    "equip": "3001",
    "svt": "9321362",
    "skill": "25689",
    "NP": "900205",
    "function": "9000",
    "buff": "765",
    "item": "941234",
    "MC": "62537",
    "CC": "8400111",
    "event": "12345",
    "war": "205",
    "quest": "1234567",
    "quest/94025012": "2",
    "ai/svt": "2384287349",
    "ai/field": "18738131",
}


cases_404 = [pytest.param(key, value, id=key) for key, value in cases_404_dict.items()]


@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,item_id", cases_404)
async def test_404_raw(client: AsyncClient, endpoint: str, item_id: str) -> None:
    response = await client.get(f"/raw/JP/{endpoint}/{item_id}")
    assert response.status_code == 404
    assert response.json()["detail"][-9:] == "not found"


cases_immutable_dict = {
    "servant": ("184", "NA_Tomoe"),
    "skill": ("24550", "NA_skill_24550"),
    "NP": ("900101", "NA_NP_900101"),
    "function": ("400", "NA_function_400"),
}


cases_immutable = [
    pytest.param(key, *value, id=key) for key, value in cases_immutable_dict.items()
]


# These are not really needed anymore since raw data uses the Pydantic objects instead of dicts now
@pytest.mark.asyncio
@pytest.mark.parametrize("endpoint,item_id,result", cases_immutable)
async def test_immutable_master(
    client: AsyncClient, endpoint: str, item_id: str, result: str
) -> None:
    await client.get(f"/raw/NA/{endpoint}/{item_id}")
    await client.get(f"/raw/NA/{endpoint}/{item_id}?expand=True")
    response = await client.get(f"/raw/NA/{endpoint}/{item_id}")
    assert response.status_code == 200
    assert response.json() == get_response_data(DATA_FOLDER, result)


@pytest.mark.asyncio
class TestServantSpecial:
    async def test_NA_not_integer(self, client: AsyncClient) -> None:
        response = await client.get("/raw/NA/servant/asdf")
        assert response.status_code == 422

    async def test_skill_reverse_passive(self, client: AsyncClient) -> None:
        response = await client.get("/raw/NA/skill/320650?reverse=True")
        reverse_servants = {
            servant["mstSvt"]["id"]
            for servant in response.json()["reverse"]["raw"]["servant"]
        }
        assert response.status_code == 200
        assert reverse_servants == {500800}

    async def test_skill_reverse_CC(self, client: AsyncClient) -> None:
        response = await client.get("/raw/JP/skill/991970?reverse=True")
        reverse_ccs = {
            cc["mstCommandCode"]["id"] for cc in response.json()["reverse"]["raw"]["CC"]
        }
        assert response.status_code == 200
        assert reverse_ccs == {8400500}

    async def test_buff_reverse_skillNp(self, client: AsyncClient) -> None:
        response = await client.get(
            "/raw/NA/buff/202?reverse=True&reverseDepth=skillNp"
        )
        assert response.status_code == 200
        assert response.json()["reverse"]["raw"]["function"][0]["reverse"]["raw"][
            "skill"
        ]

    async def test_function_reverse_servant(self, client: AsyncClient) -> None:
        response = await client.get(
            "/raw/NA/function/3410?reverse=True&reverseDepth=servant"
        )
        assert response.status_code == 200
        assert response.json()["reverse"]["raw"]["skill"][0]["reverse"]["raw"][
            "servant"
        ]

    async def test_buff_reverse_function_vals_actual_buff(
        self, client: AsyncClient
    ) -> None:
        response = await client.get("/raw/NA/buff/101?reverse=True")
        assert response.status_code == 200
        assert {
            function["mstFunc"]["funcType"]
            for function in response.json()["reverse"]["raw"]["function"]
        }.isdisjoint(FUNC_VALS_NOT_BUFF)

    async def test_hyde_voice_id(self, client: AsyncClient) -> None:
        response = await client.get("/raw/NA/servant/600700?lore=true")
        assert response.status_code == 200
        assert any(voice["id"] == 600710 for voice in response.json()["mstSvtVoice"])

    async def test_war_spots_from_multiple_maps(self, client: AsyncClient) -> None:
        response = await client.get("/raw/NA/war/9033")
        assert {spot["warId"] for spot in response.json()["mstSpot"]} == {9033, 9034}
