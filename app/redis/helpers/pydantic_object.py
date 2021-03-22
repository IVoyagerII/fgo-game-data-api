from typing import Optional, Type, TypeVar

from aioredis import Redis

from ...config import Settings
from ...schemas.base import BaseModelORJson
from ...schemas.common import Region
from ...schemas.raw import (
    MstBuff,
    MstCommandCode,
    MstEquip,
    MstEvent,
    MstFunc,
    MstGift,
    MstItem,
    MstSkill,
    MstSvt,
    MstSvtLimit,
    MstTreasureDevice,
    MstWar,
)


settings = Settings()


pydantic_obj_redis_table: dict[Type[BaseModelORJson], tuple[str, str]] = {
    MstBuff: ("mstBuff", "id"),
    MstFunc: ("mstFunc", "id"),
    MstSvt: ("mstSvt", "id"),
    MstSkill: ("mstSkill", "id"),
    MstGift: ("mstGift", "id"),
    MstTreasureDevice: ("mstTreasureDevice", "id"),
    MstEquip: ("mstEquip", "id"),
    MstWar: ("mstWar", "id"),
    MstEvent: ("mstEvent", "id"),
    MstCommandCode: ("mstCommandCode", "id"),
    MstItem: ("mstItem", "id"),
}

RedisPydantic = TypeVar("RedisPydantic", bound=BaseModelORJson)


async def fetch_id(
    redis: Redis, region: Region, schema: Type[RedisPydantic], item_id: int
) -> Optional[RedisPydantic]:
    redis_table = pydantic_obj_redis_table[schema][0]
    redis_key = f"{settings.redis_prefix}:data:{region.name}:{redis_table}"
    item_redis = await redis.hget(redis_key, item_id)

    if item_redis:
        return schema.parse_raw(item_redis)

    return None


async def check_id(
    redis: Redis, region: Region, schema: Type[RedisPydantic], item_id: int
) -> bool:
    redis_table = pydantic_obj_redis_table[schema][0]
    redis_key = f"{settings.redis_prefix}:data:{region.name}:{redis_table}"

    return await redis.hexists(redis_key, item_id) or False


async def fetch_mstSvtLimit(
    redis: Redis, region: Region, svt_id: int, svt_limit: int = 1
) -> Optional[MstSvtLimit]:
    redis_key = f"{settings.redis_prefix}:data:{region.name}:mstSvtlimit"
    mstSvtLimit = await redis.hget(redis_key, f"{svt_id}:{svt_limit}")

    if mstSvtLimit:
        return MstSvtLimit.parse_raw(mstSvtLimit)

    return None
