from typing import Iterable, Optional

from aioredis import Redis
from fastapi import HTTPException
from sqlalchemy.engine import Connection

from ..data.gamedata import masters
from ..db.helpers import ai, event, fetch, item, quest, skill, svt, td
from ..redis.helpers import pydantic_object
from ..schemas.common import Region, ReverseDepth
from ..schemas.enums import FUNC_VALS_NOT_BUFF
from ..schemas.gameenums import CondType, PurchaseType, VoiceCondType
from ..schemas.raw import (
    EXTRA_ATTACK_TD_ID,
    AiCollection,
    AiEntity,
    BuffEntity,
    BuffEntityNoReverse,
    CommandCodeEntity,
    EventEntity,
    FunctionEntity,
    FunctionEntityNoReverse,
    ItemEntity,
    MstBgm,
    MstBoxGacha,
    MstBuff,
    MstCombineCostume,
    MstCombineLimit,
    MstCombineMaterial,
    MstCombineSkill,
    MstCommandCode,
    MstCommandCodeComment,
    MstCommandCodeSkill,
    MstCv,
    MstEquip,
    MstEquipExp,
    MstEquipSkill,
    MstEvent,
    MstEventMission,
    MstEventMissionCondition,
    MstEventMissionConditionDetail,
    MstEventPointBuff,
    MstEventReward,
    MstEventRewardSet,
    MstEventTower,
    MstFriendship,
    MstFunc,
    MstGift,
    MstIllustrator,
    MstItem,
    MstMap,
    MstShop,
    MstSpot,
    MstSvt,
    MstSvtCard,
    MstSvtChange,
    MstSvtComment,
    MstSvtCostume,
    MstSvtExp,
    MstSvtGroup,
    MstSvtLimit,
    MstSvtLimitAdd,
    MstSvtVoiceRelation,
    MstVoice,
    MstWar,
    MstWarAdd,
    MysticCodeEntity,
    QuestEntity,
    QuestPhaseEntity,
    ReversedBuff,
    ReversedBuffType,
    ReversedFunction,
    ReversedFunctionType,
    ReversedSkillTd,
    ReversedSkillTdType,
    ServantEntity,
    SkillEntity,
    SkillEntityNoReverse,
    TdEntity,
    TdEntityNoReverse,
    WarEntity,
)
from . import reverse as reverse_ids


async def get_buff_entity_no_reverse(
    redis: Redis, region: Region, buff_id: int, mstBuff: Optional[MstBuff] = None
) -> BuffEntityNoReverse:
    if mstBuff:
        return BuffEntityNoReverse(mstBuff=mstBuff)

    redis_buff = await pydantic_object.fetch_id(redis, region, MstBuff, buff_id)
    if redis_buff:
        return BuffEntityNoReverse(mstBuff=redis_buff)
    else:
        raise HTTPException(status_code=404, detail="Buff not found")


async def get_buff_entity(
    conn: Connection,
    redis: Redis,
    region: Region,
    buff_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
    mstBuff: Optional[MstBuff] = None,
) -> BuffEntity:
    buff_entity = BuffEntity.parse_obj(
        await get_buff_entity_no_reverse(redis, region, buff_id, mstBuff)
    )
    if reverse and reverseDepth >= ReverseDepth.function:
        buff_reverse = ReversedBuff(
            function=[
                await get_func_entity(
                    conn, redis, region, func_id, reverse, reverseDepth
                )
                for func_id in reverse_ids.buff_to_func(region, buff_id)
            ]
        )
        buff_entity.reverse = ReversedBuffType(raw=buff_reverse)
    return buff_entity


async def get_func_entity_no_reverse(
    redis: Redis,
    region: Region,
    func_id: int,
    expand: bool = False,
    mstFunc: Optional[MstFunc] = None,
) -> FunctionEntityNoReverse:
    if not mstFunc:
        redis_func = await pydantic_object.fetch_id(redis, region, MstFunc, func_id)
        if redis_func:
            mstFunc = redis_func
        else:
            raise HTTPException(status_code=404, detail="Function not found")

    func_entity = FunctionEntityNoReverse(
        mstFunc=mstFunc,
        mstFuncGroup=masters[region].mstFuncGroupId.get(func_id, []),
    )

    if expand and func_entity.mstFunc.funcType not in FUNC_VALS_NOT_BUFF:
        func_entity.mstFunc.expandedVals = [
            await get_buff_entity_no_reverse(redis, region, buff_id)
            for buff_id in func_entity.mstFunc.vals
            if await pydantic_object.check_id(redis, region, MstBuff, buff_id)
        ]
    return func_entity


async def get_func_entity(
    conn: Connection,
    redis: Redis,
    region: Region,
    func_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    expand: bool = False,
    mstFunc: Optional[MstFunc] = None,
) -> FunctionEntity:
    func_entity = FunctionEntity.parse_obj(
        await get_func_entity_no_reverse(redis, region, func_id, expand, mstFunc)
    )
    if reverse and reverseDepth >= ReverseDepth.skillNp:
        func_reverse = ReversedFunction(
            skill=[
                await get_skill_entity(
                    conn, redis, region, skill_id, reverse, reverseDepth
                )
                for skill_id in reverse_ids.func_to_skillId(region, func_id)
            ],
            NP=[
                await get_td_entity(conn, redis, region, td_id, reverse, reverseDepth)
                for td_id in reverse_ids.func_to_tdId(region, func_id)
            ],
        )
        func_entity.reverse = ReversedFunctionType(raw=func_reverse)
    return func_entity


async def get_skill_entity_no_reverse_many(
    conn: Connection,
    redis: Redis,
    region: Region,
    skill_ids: Iterable[int],
    expand: bool = False,
) -> list[SkillEntityNoReverse]:
    if not skill_ids:
        return []
    skill_entities = skill.get_skillEntity(conn, skill_ids)
    if skill_entities:
        if expand:
            for skill_entity in skill_entities:
                for skillLv in skill_entity.mstSkillLv:
                    skillLv.expandedFuncId = [
                        await get_func_entity_no_reverse(redis, region, func_id, expand)
                        for func_id in skillLv.funcId
                        if await pydantic_object.check_id(
                            redis, region, MstFunc, func_id
                        )
                    ]
        return skill_entities
    else:
        raise HTTPException(status_code=404, detail="Skill not found")


async def get_skill_entity_no_reverse(
    conn: Connection, redis: Redis, region: Region, skill_id: int, expand: bool = False
) -> SkillEntityNoReverse:
    return (
        await get_skill_entity_no_reverse_many(conn, redis, region, [skill_id], expand)
    )[0]


async def get_skill_entity(
    conn: Connection,
    redis: Redis,
    region: Region,
    skill_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    expand: bool = False,
) -> SkillEntity:
    skill_entity = SkillEntity.parse_obj(
        await get_skill_entity_no_reverse(conn, redis, region, skill_id, expand)
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        activeSkills = {svt_skill.svtId for svt_skill in skill_entity.mstSvtSkill}
        passiveSkills = reverse_ids.passive_to_svtId(region, skill_id)
        skill_reverse = ReversedSkillTd(
            servant=[
                await get_servant_entity(conn, redis, region, svt_id)
                for svt_id in activeSkills | passiveSkills
            ],
            MC=[
                await get_mystic_code_entity(conn, redis, region, mc_id)
                for mc_id in reverse_ids.skill_to_MCId(region, skill_id)
            ],
            CC=[
                await get_command_code_entity(conn, redis, region, cc_id)
                for cc_id in reverse_ids.skill_to_CCId(region, skill_id)
            ],
        )
        skill_entity.reverse = ReversedSkillTdType(raw=skill_reverse)
    return skill_entity


async def get_td_entity_no_reverse_many(
    conn: Connection,
    redis: Redis,
    region: Region,
    td_ids: Iterable[int],
    expand: bool = False,
) -> list[TdEntityNoReverse]:
    if not td_ids:
        return []
    td_entities = td.get_tdEntity(conn, td_ids)
    if td_entities:
        if expand:
            for td_entity in td_entities:
                for tdLv in td_entity.mstTreasureDeviceLv:
                    tdLv.expandedFuncId = [
                        await get_func_entity_no_reverse(redis, region, func_id, expand)
                        for func_id in tdLv.funcId
                        if await pydantic_object.check_id(
                            redis, region, MstFunc, func_id
                        )
                    ]
        return td_entities
    else:
        raise HTTPException(status_code=404, detail="NP not found")


async def get_td_entity_no_reverse(
    conn: Connection, redis: Redis, region: Region, td_id: int, expand: bool = False
) -> TdEntityNoReverse:
    return (await get_td_entity_no_reverse_many(conn, redis, region, [td_id], expand))[
        0
    ]


async def get_td_entity(
    conn: Connection,
    redis: Redis,
    region: Region,
    td_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    expand: bool = False,
) -> TdEntity:
    td_entity = TdEntity.parse_obj(
        await get_td_entity_no_reverse(conn, redis, region, td_id, expand)
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        td_reverse = ReversedSkillTd(
            servant=[
                await get_servant_entity(conn, redis, region, svt_id.svtId)
                for svt_id in td_entity.mstSvtTreasureDevice
            ]
        )
        td_entity.reverse = ReversedSkillTdType(raw=td_reverse)
    return td_entity


async def get_servant_entity(
    conn: Connection,
    redis: Redis,
    region: Region,
    servant_id: int,
    expand: bool = False,
    lore: bool = False,
    mstSvt: Optional[MstSvt] = None,
) -> ServantEntity:
    svt_db = mstSvt if mstSvt else fetch.get_one(conn, MstSvt, servant_id)
    if not svt_db:
        raise HTTPException(status_code=404, detail="Svt not found")

    mstSvtCard = fetch.get_all(conn, MstSvtCard, servant_id)
    mstSvtLimit = fetch.get_all(conn, MstSvtLimit, servant_id)
    mstCombineSkill = fetch.get_all(conn, MstCombineSkill, svt_db.combineSkillId)
    mstCombineLimit = fetch.get_all(conn, MstCombineLimit, svt_db.combineLimitId)
    mstCombineCostume = fetch.get_all(conn, MstCombineCostume, servant_id)
    mstSvtLimitAdd = fetch.get_all(conn, MstSvtLimitAdd, servant_id)
    mstSvtChange = fetch.get_all(conn, MstSvtChange, servant_id)
    mstSvtCostume = fetch.get_all(conn, MstSvtCostume, servant_id)
    mstSvtExp = fetch.get_all(conn, MstSvtExp, svt_db.expType)
    mstFriendship = fetch.get_all(conn, MstFriendship, svt_db.friendshipId)
    mstCombineMaterial = fetch.get_all(
        conn, MstCombineMaterial, svt_db.combineMaterialId
    )

    mstSvtScript = svt.get_svt_script(conn, servant_id)

    skill_ids = [
        skill.skillId for skill in skill.get_mstSvtSkill(conn, svt_id=servant_id)
    ]
    mstSkill = await get_skill_entity_no_reverse_many(
        conn, redis, region, skill_ids, expand
    )

    td_ids = [
        td.treasureDeviceId
        for td in td.get_mstSvtTreasureDevice(conn, svt_id=servant_id)
        if td.treasureDeviceId != EXTRA_ATTACK_TD_ID
    ]
    mstTreasureDevice = await get_td_entity_no_reverse_many(
        conn, redis, region, td_ids, expand
    )

    svt_entity = ServantEntity(
        mstSvt=svt_db,
        mstSvtCard=mstSvtCard,
        mstSvtLimit=mstSvtLimit,
        mstCombineSkill=mstCombineSkill,
        mstCombineLimit=mstCombineLimit,
        mstCombineCostume=mstCombineCostume,
        mstCombineMaterial=mstCombineMaterial,
        mstSvtLimitAdd=mstSvtLimitAdd,
        mstSvtChange=mstSvtChange,
        # needed costume to get the nice limits and costume ids
        mstSvtCostume=mstSvtCostume,
        # needed this to get CharaFigure available forms
        mstSvtScript=mstSvtScript,
        mstSvtExp=mstSvtExp,
        mstFriendship=mstFriendship,
        mstSkill=mstSkill,
        mstTreasureDevice=mstTreasureDevice,
    )

    if expand:
        svt_entity.mstSvt.expandedClassPassive = await get_skill_entity_no_reverse_many(
            conn, redis, region, svt_entity.mstSvt.classPassive, expand
        )

    if lore:
        svt_entity.mstCv = fetch.get_one(conn, MstCv, svt_db.cvId)
        svt_entity.mstIllustrator = fetch.get_one(
            conn, MstIllustrator, svt_db.illustratorId
        )
        svt_entity.mstSvtComment = fetch.get_all(conn, MstSvtComment, servant_id)

        # Try to match order in the voice tab in game
        voice_ids = []

        for change in svt_entity.mstSvtChange:
            voice_ids.append(change.svtVoiceId)

        voice_ids.append(servant_id)

        for main_id, sub_id in (
            (600700, 600710),  # Jekyll/Hyde
            (800100, 800101),  # Mash
        ):
            if servant_id == main_id:
                voice_ids.append(sub_id)

        # Moriarty deadheat summer lines use his hidden name svt_id
        relation_svt_ids = [change.svtVoiceId for change in svt_entity.mstSvtChange] + [
            servant_id
        ]
        voiceRelations = fetch.get_all_multiple(
            conn, MstSvtVoiceRelation, relation_svt_ids
        )
        for voiceRelation in voiceRelations:
            voice_ids.append(voiceRelation.relationSvtId)

        order = {voice_id: i for i, voice_id in enumerate(voice_ids)}
        mstSvtVoice = svt.get_mstSvtVoice(conn, voice_ids)
        mstSubtitle = svt.get_mstSubtitle(conn, voice_ids)
        mstVoicePlayCond = svt.get_mstVoicePlayCond(conn, voice_ids)

        base_voice_ids = {
            info.get_voice_id()
            for svt_voice in mstSvtVoice
            for script_json in svt_voice.scriptJson
            for info in script_json.infos
        }
        svt_entity.mstVoice = fetch.get_all_multiple(conn, MstVoice, base_voice_ids)

        group_ids = {
            cond.value
            for svt_voice in mstSvtVoice
            for script_json in svt_voice.scriptJson
            for cond in script_json.conds
            if cond.condType == VoiceCondType.SVT_GROUP
        }
        svt_entity.mstSvtGroup = fetch.get_all_multiple(conn, MstSvtGroup, group_ids)

        svt_entity.mstSvtVoice = sorted(mstSvtVoice, key=lambda voice: order[voice.id])
        svt_entity.mstVoicePlayCond = sorted(
            mstVoicePlayCond, key=lambda voice: order[voice.svtId]
        )
        svt_entity.mstSubtitle = sorted(
            mstSubtitle, key=lambda sub: order[sub.get_svtId()]
        )

    return svt_entity


async def get_mystic_code_entity(
    conn: Connection, redis: Redis, region: Region, mc_id: int, expand: bool = False
) -> MysticCodeEntity:
    mc_db = fetch.get_one(conn, MstEquip, mc_id)
    if not mc_db:
        raise HTTPException(status_code=404, detail="Mystic Code not found")

    skill_ids = [mc.skillId for mc in fetch.get_all(conn, MstEquipSkill, mc_id)]
    mstSkill = await get_skill_entity_no_reverse_many(
        conn, redis, region, skill_ids, expand
    )

    mc_entity = MysticCodeEntity(
        mstEquip=mc_db,
        mstSkill=mstSkill,
        mstEquipExp=fetch.get_all(conn, MstEquipExp, mc_id),
    )
    return mc_entity


async def get_command_code_entity(
    conn: Connection, redis: Redis, region: Region, cc_id: int, expand: bool = False
) -> CommandCodeEntity:
    cc_db = fetch.get_one(conn, MstCommandCode, cc_id)
    if not cc_db:
        raise HTTPException(status_code=404, detail="Command Code not found")

    skill_ids = [
        cc_skill.skillId for cc_skill in fetch.get_all(conn, MstCommandCodeSkill, cc_id)
    ]
    mstSkill = await get_skill_entity_no_reverse_many(
        conn, redis, region, skill_ids, expand
    )

    mstCommandCodeComment = fetch.get_all(conn, MstCommandCodeComment, cc_id)[0]
    mstIllustrator = fetch.get_one(
        conn, MstIllustrator, mstCommandCodeComment.illustratorId
    )

    return CommandCodeEntity(
        mstCommandCode=cc_db,
        mstSkill=mstSkill,
        mstCommandCodeComment=mstCommandCodeComment,
        mstIllustrator=mstIllustrator,
    )


async def get_item_entity(redis: Redis, region: Region, item_id: int) -> ItemEntity:
    item_redis = await pydantic_object.fetch_id(redis, region, MstItem, item_id)
    if not item_redis:
        raise HTTPException(status_code=404, detail="Item not found")

    return ItemEntity(mstItem=item_redis)


def get_war_entity(conn: Connection, war_id: int) -> WarEntity:
    war_db = fetch.get_one(conn, MstWar, war_id)
    if not war_db:
        raise HTTPException(status_code=404, detail="War not found")

    maps = fetch.get_all(conn, MstMap, war_id)
    map_ids = [event_map.id for event_map in maps]

    spots = fetch.get_all_multiple(conn, MstSpot, map_ids)
    spot_ids = [spot.id for spot in spots]

    quests = quest.get_quest_by_spot(conn, spot_ids)

    bgm_ids = [war_map.bgmId for war_map in maps] + [war_db.bgmId]
    bgms = fetch.get_all_multiple(conn, MstBgm, bgm_ids)

    return WarEntity(
        mstWar=war_db,
        mstEvent=fetch.get_one(conn, MstEvent, war_db.eventId),
        mstWarAdd=fetch.get_all(conn, MstWarAdd, war_id),
        mstMap=maps,
        mstBgm=bgms,
        mstSpot=spots,
        mstQuest=quests,
    )


def get_event_entity(conn: Connection, event_id: int) -> EventEntity:
    mstEvent = fetch.get_one(conn, MstEvent, event_id)
    if not mstEvent:
        raise HTTPException(status_code=404, detail="Event not found")

    missions = fetch.get_all(conn, MstEventMission, event_id)
    mission_ids = [mission.id for mission in missions]

    conds = fetch.get_all_multiple(conn, MstEventMissionCondition, mission_ids)
    cond_detail_ids = [
        cond.targetIds[0]
        for cond in conds
        if cond.condType == CondType.MISSION_CONDITION_DETAIL
    ]

    cond_details = fetch.get_all_multiple(
        conn, MstEventMissionConditionDetail, cond_detail_ids
    )

    box_gachas = fetch.get_all(conn, MstBoxGacha, event_id)
    box_gacha_base_ids = [
        base_id for box_gacha in box_gachas for base_id in box_gacha.baseIds
    ]

    shops = fetch.get_all(conn, MstShop, event_id)
    set_item_ids = [
        set_id
        for shop in shops
        for set_id in shop.targetIds
        if shop.purchaseType == PurchaseType.SET_ITEM
    ]
    set_items = item.get_mstSetItem(conn, set_item_ids)

    rewards = fetch.get_all(conn, MstEventReward, event_id)

    tower_rewards = event.get_mstEventTowerReward(conn, event_id)

    gacha_bases = event.get_mstBoxGachaBase(conn, box_gacha_base_ids)

    gift_ids = (
        {reward.giftId for reward in rewards}
        | {mission.giftId for mission in missions}
        | {tower_reward.giftId for tower_reward in tower_rewards}
        | {box.targetId for box in gacha_bases}
    )
    gifts = fetch.get_all_multiple(conn, MstGift, gift_ids)

    return EventEntity(
        mstEvent=mstEvent,
        mstWar=event.get_event_wars(conn, event_id),
        mstShop=shops,
        mstGift=gifts,
        mstSetItem=set_items,
        mstEventReward=rewards,
        mstEventRewardSet=fetch.get_all(conn, MstEventRewardSet, event_id),
        mstEventPointBuff=fetch.get_all(conn, MstEventPointBuff, event_id),
        mstEventMission=missions,
        mstEventMissionCondition=conds,
        mstEventMissionConditionDetail=cond_details,
        mstEventTower=fetch.get_all(conn, MstEventTower, event_id),
        mstEventTowerReward=tower_rewards,
        mstBoxGacha=box_gachas,
        mstBoxGachaBase=gacha_bases,
    )


def get_quest_entity_many(conn: Connection, quest_id: list[int]) -> list[QuestEntity]:
    quest_entities = quest.get_quest_entity(conn, quest_id)
    if quest_entities:
        return quest_entities
    else:
        raise HTTPException(status_code=404, detail="Quest not found")


def get_quest_entity(conn: Connection, quest_id: int) -> QuestEntity:
    return get_quest_entity_many(conn, [quest_id])[0]


def get_quest_phase_entity(
    conn: Connection, quest_id: int, phase: int
) -> QuestPhaseEntity:
    quest_phase = quest.get_quest_phase_entity(conn, quest_id, phase)
    if quest_phase:
        return quest_phase
    else:
        raise HTTPException(status_code=404, detail="Quest phase not found")


def get_ai_entities(
    conn: Connection, ai_id: int, field: bool = False, throw_error: bool = True
) -> list[AiEntity]:
    if field:
        ais = ai.get_field_ai_entity(conn, ai_id)
    else:
        ais = ai.get_svt_ai_entity(conn, ai_id)

    if ais or not throw_error:
        return ais
    else:
        raise HTTPException(status_code=404, detail="AI not found")


def get_ai_collection(
    conn: Connection, ai_id: int, field: bool = False
) -> AiCollection:
    main_ais = get_ai_entities(conn, ai_id, field)
    retreived_ais = {ai_id}

    to_be_retrieved_ais = {
        ai.mstAi.avals[0] for ai in main_ais if ai.mstAi.avals[0] > 0
    }
    related_ais: list[AiEntity] = []
    while to_be_retrieved_ais:
        for related_ai_id in to_be_retrieved_ais:
            related_ais += get_ai_entities(
                conn, related_ai_id, field, throw_error=False
            )

        retreived_ais |= to_be_retrieved_ais
        to_be_retrieved_ais = {
            ai.mstAi.avals[0]
            for ai in related_ais
            if ai.mstAi.avals[0] > 0 and ai.mstAi.avals[0] not in retreived_ais
        }

    return AiCollection(
        mainAis=main_ais,
        relatedAis=related_ais,
    )
