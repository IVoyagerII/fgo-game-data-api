from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Iterable

from aioredis import Redis
from sqlalchemy.engine import Connection

from ...config import Settings
from ...schemas.common import Region
from ...schemas.gameenums import CARD_TYPE_NAME
from ...schemas.nice import AssetURL, NiceTd
from ...schemas.raw import TdEntityNoReverse
from ..raw import get_td_entity_no_reverse_many
from ..utils import get_traits_list, strip_formatting_brackets
from .func import get_nice_function


settings = Settings()


async def get_nice_td(
    redis: Redis, tdEntity: TdEntityNoReverse, svtId: int, region: Region
) -> list[dict[str, Any]]:
    nice_td: dict[str, Any] = {
        "id": tdEntity.mstTreasureDevice.id,
        "name": tdEntity.mstTreasureDevice.name,
        "ruby": tdEntity.mstTreasureDevice.ruby,
        "rank": tdEntity.mstTreasureDevice.rank,
        "type": tdEntity.mstTreasureDevice.typeText,
        "individuality": get_traits_list(tdEntity.mstTreasureDevice.individuality),
    }

    if tdEntity.mstTreasureDeviceDetail:
        nice_td["detail"] = strip_formatting_brackets(
            tdEntity.mstTreasureDeviceDetail[0].detail
        )

    nice_td["npGain"] = {
        "buster": [td_lv.tdPointB for td_lv in tdEntity.mstTreasureDeviceLv],
        "arts": [td_lv.tdPointA for td_lv in tdEntity.mstTreasureDeviceLv],
        "quick": [td_lv.tdPointQ for td_lv in tdEntity.mstTreasureDeviceLv],
        "extra": [td_lv.tdPointEx for td_lv in tdEntity.mstTreasureDeviceLv],
        "np": [td_lv.tdPoint for td_lv in tdEntity.mstTreasureDeviceLv],
        "defence": [td_lv.tdPointDef for td_lv in tdEntity.mstTreasureDeviceLv],
    }

    nice_td["functions"] = []

    for funci, _ in enumerate(tdEntity.mstTreasureDeviceLv[0].funcId):
        nice_func = await get_nice_function(
            redis,
            region,
            tdEntity.mstTreasureDeviceLv[0].expandedFuncId[funci],
            svals=[skill_lv.svals[funci] for skill_lv in tdEntity.mstTreasureDeviceLv],
            svals2=[
                skill_lv.svals2[funci] for skill_lv in tdEntity.mstTreasureDeviceLv
            ],
            svals3=[
                skill_lv.svals3[funci] for skill_lv in tdEntity.mstTreasureDeviceLv
            ],
            svals4=[
                skill_lv.svals4[funci] for skill_lv in tdEntity.mstTreasureDeviceLv
            ],
            svals5=[
                skill_lv.svals5[funci] for skill_lv in tdEntity.mstTreasureDeviceLv
            ],
        )

        nice_td["functions"].append(nice_func)

    chosen_svts = [
        svt_td for svt_td in tdEntity.mstSvtTreasureDevice if svt_td.svtId == svtId
    ]
    out_tds = []
    for chosen_svt in chosen_svts:
        out_td = deepcopy(nice_td)
        imageId = chosen_svt.imageIndex
        base_settings_id = {
            "base_url": settings.asset_url,
            "region": region,
            "item_id": svtId,
        }
        if imageId < 2:
            file_i = "np"
        else:
            file_i = "np" + str(imageId // 2)
        out_td |= {
            "icon": AssetURL.commands.format(**base_settings_id, i=file_i),
            "strengthStatus": chosen_svt.strengthStatus,
            "num": chosen_svt.num,
            "priority": chosen_svt.priority,
            "condQuestId": chosen_svt.condQuestId,
            "condQuestPhase": chosen_svt.condQuestPhase,
            "card": CARD_TYPE_NAME[chosen_svt.cardId],
            "npDistribution": chosen_svt.damage,
        }
        out_tds.append(out_td)
    return out_tds


@dataclass(eq=True, frozen=True)
class TdSvt:
    """Required parameters to get a specific nice NP"""

    td_id: int
    svt_id: int


MultipleNiceTds = dict[TdSvt, NiceTd]


async def get_multiple_nice_tds(
    conn: Connection,
    redis: Redis,
    region: Region,
    td_svts: Iterable[TdSvt],
) -> MultipleNiceTds:
    """Get multiple nice NPs at once

    Args:
        `conn`: DB Connection
        `region`: Region
        `skill_svts`: List of skill id - NP id tuple pairs

    Returns:
        Mapping of skill id - svt id tuple to nice NP
    """
    td_ids = [td_svt.td_id for td_svt in td_svts]
    raw_tds = {
        td.mstTreasureDevice.id: td
        for td in await get_td_entity_no_reverse_many(
            conn, redis, region, td_ids, expand=True
        )
    }
    return {
        td_svt: NiceTd.parse_obj(
            (await get_nice_td(redis, raw_tds[td_svt.td_id], td_svt.svt_id, region))[0]
        )
        for td_svt in td_svts
        if td_svt.td_id in raw_tds
    }
