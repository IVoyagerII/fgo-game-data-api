from typing import List, Set

from fastapi import HTTPException
from sqlalchemy.engine import Connection

from ..data.gamedata import masters
from ..db.helpers import ai, skill, svt, td
from ..schemas.common import Region, ReverseDepth
from ..schemas.enums import FUNC_VALS_NOT_BUFF
from ..schemas.raw import (
    AiEntity,
    BuffEntity,
    BuffEntityNoReverse,
    CommandCodeEntity,
    EventEntity,
    FunctionEntity,
    FunctionEntityNoReverse,
    MstAi,
    MysticCodeEntity,
    OneAiEntity,
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


def buff_to_func(region: Region, buff_id: int) -> Set[int]:
    """Returns a set of function ID that uses the given buff ID in vals"""
    return masters[region].buffToFunc.get(buff_id, set())


def func_to_skillId(region: Region, func_id: int) -> Set[int]:
    """Returns a set of skill ID that uses the given function ID"""
    return masters[region].funcToSkill.get(func_id, set())


def func_to_tdId(region: Region, func_id: int) -> Set[int]:
    """Returns a set of treasure device (NP) ID that uses the given function ID"""
    return masters[region].funcToTd.get(func_id, set())


def passive_to_svtId(region: Region, skill_id: int) -> Set[int]:
    """Returns a set of svt ID that has the given skill ID as passive"""
    return masters[region].passiveSkillToSvt.get(skill_id, set())


def skill_to_MCId(region: Region, skill_id: int) -> Set[int]:
    """Returns a set of Mystic Code ID that has the given skill ID"""
    return {
        equip_skill.equipId
        for equip_skill in masters[region].mstEquipSkill
        if equip_skill.skillId == skill_id
    }


def skill_to_CCId(region: Region, skill_id: int) -> Set[int]:
    """Returns a set of Command Code ID that has the given skill ID"""
    return {
        cc_skill.commandCodeId
        for cc_skill in masters[region].mstCommandCodeSkill
        if cc_skill.skillId == skill_id
    }


def get_buff_entity_no_reverse(region: Region, buff_id: int) -> BuffEntityNoReverse:
    buff_entity = BuffEntityNoReverse(mstBuff=masters[region].mstBuffId[buff_id])
    return buff_entity


def get_buff_entity(
    conn: Connection,
    region: Region,
    buff_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.function,
) -> BuffEntity:
    buff_entity = BuffEntity.parse_obj(get_buff_entity_no_reverse(region, buff_id))
    if reverse and reverseDepth >= ReverseDepth.function:
        buff_reverse = ReversedBuff(
            function=(
                get_func_entity(conn, region, func_id, reverse, reverseDepth)
                for func_id in buff_to_func(region, buff_id)
            )
        )
        buff_entity.reverse = ReversedBuffType(raw=buff_reverse)
    return buff_entity


def get_func_entity_no_reverse(
    region: Region, func_id: int, expand: bool = False
) -> FunctionEntityNoReverse:
    func_entity = FunctionEntityNoReverse(
        mstFunc=masters[region].mstFuncId[func_id],
        mstFuncGroup=masters[region].mstFuncGroupId.get(func_id, []),
    )
    if expand and func_entity.mstFunc.funcType not in FUNC_VALS_NOT_BUFF:
        func_entity.mstFunc.expandedVals = [
            get_buff_entity_no_reverse(region, buff_id)
            for buff_id in func_entity.mstFunc.vals
            if buff_id in masters[region].mstBuffId
        ]
    return func_entity


def get_func_entity(
    conn: Connection,
    region: Region,
    func_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.skillNp,
    expand: bool = False,
) -> FunctionEntity:
    func_entity = FunctionEntity.parse_obj(
        get_func_entity_no_reverse(region, func_id, expand)
    )
    if reverse and reverseDepth >= ReverseDepth.skillNp:
        func_reverse = ReversedFunction(
            skill=(
                get_skill_entity(conn, region, skill_id, reverse, reverseDepth)
                for skill_id in func_to_skillId(region, func_id)
            ),
            NP=(
                get_td_entity(conn, region, td_id, reverse, reverseDepth)
                for td_id in func_to_tdId(region, func_id)
            ),
        )
        func_entity.reverse = ReversedFunctionType(raw=func_reverse)
    return func_entity


def get_skill_entity_no_reverse(
    conn: Connection, region: Region, skill_id: int, expand: bool = False
) -> SkillEntityNoReverse:
    main_skill = skill.get_mstSkill(conn, skill_id)
    if main_skill:
        skill_entity = SkillEntityNoReverse(
            mstSkill=main_skill,
            mstSkillDetail=skill.get_mstSkillDetail(conn, skill_id),
            mstSvtSkill=skill.get_mstSvtSkill(conn, skill_id=skill_id),
            mstSkillLv=skill.get_mstSkillLv(conn, skill_id),
        )

        if expand:
            for skillLv in skill_entity.mstSkillLv:
                skillLv.expandedFuncId = [
                    get_func_entity_no_reverse(region, func_id, expand)
                    for func_id in skillLv.funcId
                    if func_id in masters[region].mstFuncId
                ]
        return skill_entity
    else:
        raise HTTPException(status_code=404, detail="Skill not found")


def get_skill_entity(
    conn: Connection,
    region: Region,
    skill_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    expand: bool = False,
) -> SkillEntity:
    skill_entity = SkillEntity.parse_obj(
        get_skill_entity_no_reverse(conn, region, skill_id, expand)
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        activeSkills = {svt_skill.svtId for svt_skill in skill_entity.mstSvtSkill}
        passiveSkills = passive_to_svtId(region, skill_id)
        skill_reverse = ReversedSkillTd(
            servant=(
                get_servant_entity(conn, region, svt_id)
                for svt_id in activeSkills | passiveSkills
            ),
            MC=(
                get_mystic_code_entity(conn, region, mc_id)
                for mc_id in skill_to_MCId(region, skill_id)
            ),
            CC=(
                get_command_code_entity(conn, region, cc_id)
                for cc_id in skill_to_CCId(region, skill_id)
            ),
        )
        skill_entity.reverse = ReversedSkillTdType(raw=skill_reverse)
    return skill_entity


def get_td_entity_no_reverse(
    conn: Connection, region: Region, td_id: int, expand: bool = False
) -> TdEntityNoReverse:
    main_td = td.get_mstTreasureDevice(conn, td_id)
    if main_td:
        td_entity = TdEntityNoReverse(
            mstTreasureDevice=main_td,
            mstTreasureDeviceDetail=td.get_mstTreasureDeviceDetail(conn, td_id),
            mstSvtTreasureDevice=td.get_mstSvtTreasureDevice(conn, td_id),
            mstTreasureDeviceLv=td.get_mstTreasureDeviceLv(conn, td_id),
        )

        if expand:
            for tdLv in td_entity.mstTreasureDeviceLv:
                tdLv.expandedFuncId = [
                    get_func_entity_no_reverse(region, func_id, expand)
                    for func_id in tdLv.funcId
                    if func_id in masters[region].mstFuncId
                ]
        return td_entity
    else:
        raise HTTPException(status_code=404, detail="NP not found")


def get_td_entity(
    conn: Connection,
    region: Region,
    td_id: int,
    reverse: bool = False,
    reverseDepth: ReverseDepth = ReverseDepth.servant,
    expand: bool = False,
) -> TdEntity:
    td_entity = TdEntity.parse_obj(
        get_td_entity_no_reverse(conn, region, td_id, expand)
    )

    if reverse and reverseDepth >= ReverseDepth.servant:
        td_reverse = ReversedSkillTd(
            servant=(
                get_servant_entity(conn, region, svt_id.svtId)
                for svt_id in td_entity.mstSvtTreasureDevice
            )
        )
        td_entity.reverse = ReversedSkillTdType(raw=td_reverse)
    return td_entity


def get_servant_entity(
    conn: Connection,
    region: Region,
    servant_id: int,
    expand: bool = False,
    lore: bool = False,
) -> ServantEntity:
    mstSvt = masters[region].mstSvtId[servant_id]

    svt_entity = ServantEntity(
        mstSvt=mstSvt,
        mstSvtCard=masters[region].mstSvtCardId.get(servant_id, []),
        mstSvtLimit=masters[region].mstSvtLimitId.get(servant_id, []),
        mstCombineSkill=masters[region].mstCombineSkillId.get(
            mstSvt.combineSkillId, []
        ),
        mstCombineLimit=masters[region].mstCombineLimitId.get(
            mstSvt.combineLimitId, []
        ),
        mstCombineCostume=masters[region].mstCombineCostumeId.get(servant_id, []),
        mstSvtLimitAdd=masters[region].mstSvtLimitAddId.get(servant_id, []),
        mstSvtChange=masters[region].mstSvtChangeId.get(servant_id, []),
        # needed costume to get the nice limits and costume ids
        mstSvtCostume=masters[region].mstSvtCostumeId.get(servant_id, []),
        # needed this to get CharaFigure available forms
        mstSvtScript=masters[region].mstSvtScriptId.get(servant_id, []),
        mstSkill=(
            get_skill_entity_no_reverse(conn, region, skill.skillId, expand)
            for skill in skill.get_mstSvtSkill(conn, svt_id=servant_id)
            if skill.skillId in masters[region].mstSkillId
        ),
        mstTreasureDevice=(
            get_td_entity_no_reverse(conn, region, td.treasureDeviceId, expand)
            for td in td.get_mstSvtTreasureDevice(conn, svt_id=servant_id)
            if td.treasureDeviceId != 100
        ),
    )

    if expand:
        svt_entity.mstSvt.expandedClassPassive = [
            get_skill_entity_no_reverse(conn, region, passiveSkill, expand)
            for passiveSkill in svt_entity.mstSvt.classPassive
            if passiveSkill in masters[region].mstSkillId
        ]

    if lore:
        svt_entity.mstSvtComment = svt.get_mstSvtComment(conn, servant_id)

        # Try to match order in the voice tab in game
        voices = []
        subtitles = []

        for change in svt_entity.mstSvtChange:
            voices += svt.get_mstSvtVoice(conn, change.svtVoiceId)
            subtitles += masters[region].mstSubtitleId.get(change.svtVoiceId, [])

        voices += svt.get_mstSvtVoice(conn, servant_id)
        subtitles += masters[region].mstSubtitleId.get(servant_id, [])

        for main_id, sub_id in (
            ("JEKYLL_SVT_ID", "HYDE_SVT_ID"),
            ("MASHU_SVT_ID1", "MASHU_SVT_ID2"),
        ):
            if servant_id == masters[region].mstConstantId[main_id]:
                sub_svt_id = masters[region].mstConstantId[sub_id]
                voices += svt.get_mstSvtVoice(conn, sub_svt_id)

        # Moriarty deadheat summer lines use his hidden name svt_id
        for svt_id in [change.svtVoiceId for change in svt_entity.mstSvtChange] + [
            servant_id
        ]:
            if voiceRelations := masters[region].mstSvtVoiceRelationId.get(svt_id):
                for voiceRelation in voiceRelations:
                    relation_id = voiceRelation.relationSvtId
                    voices += svt.get_mstSvtVoice(conn, relation_id)
                    subtitles += masters[region].mstSubtitleId.get(relation_id, [])

        svt_entity.mstSvtVoice = voices
        svt_entity.mstSubtitle = subtitles

    return svt_entity


def get_mystic_code_entity(
    conn: Connection, region: Region, mc_id: int, expand: bool = False
) -> MysticCodeEntity:
    mc_entity = MysticCodeEntity(
        mstEquip=masters[region].mstEquipId[mc_id],
        mstSkill=(
            get_skill_entity_no_reverse(conn, region, mc.skillId, expand)
            for mc in masters[region].mstEquipSkill
            if mc.equipId == mc_id
        ),
        mstEquipExp=(mc for mc in masters[region].mstEquipExp if mc.equipId == mc_id),
    )
    return mc_entity


def get_command_code_entity(
    conn: Connection, region: Region, cc_id: int, expand: bool = False
) -> CommandCodeEntity:
    cc_entity = CommandCodeEntity(
        mstCommandCode=masters[region].mstCommandCodeId[cc_id],
        mstSkill=(
            get_skill_entity_no_reverse(conn, region, cc_skill.skillId, expand)
            for cc_skill in masters[region].mstCommandCodeSkill
            if cc_skill.commandCodeId == cc_id
        ),
        mstCommandCodeComment=masters[region].mstCommandCodeCommentId[cc_id][0],
    )
    return cc_entity


def get_war_entity(region: Region, war_id: int) -> WarEntity:
    return WarEntity(
        mstWar=masters[region].mstWarId[war_id],
        mstMap=masters[region].mstMapWarId.get(war_id, []),
        mstSpot=masters[region].mstSpotWarId.get(war_id, []),
    )


def get_event_entity(region: Region, event_id: int) -> EventEntity:
    return EventEntity(
        mstEvent=masters[region].mstEventId[event_id],
        mstShop=masters[region].mstShopEventId.get(event_id, []),
    )


def get_quest_entity(region: Region, quest_id: int) -> QuestEntity:
    return QuestEntity(
        mstQuest=masters[region].mstQuestId[quest_id],
        mstQuestConsumeItem=masters[region].mstQuestConsumeItemId.get(quest_id, []),
        mstQuestRelease=masters[region].mstQuestReleaseId.get(quest_id, []),
    )


def get_quest_phase_entity(
    region: Region, quest_id: int, phase: int
) -> QuestPhaseEntity:
    return QuestPhaseEntity(
        mstQuest=masters[region].mstQuestId[quest_id],
        mstQuestConsumeItem=masters[region].mstQuestConsumeItemId.get(quest_id, []),
        mstQuestRelease=masters[region].mstQuestReleaseId.get(quest_id, []),
        mstQuestPhase=masters[region].mstQuestPhaseId[quest_id][phase],
        mstStage=masters[region].mstStageId.get(quest_id, {}).get(phase, []),
    )


def get_mst_ai(
    conn: Connection, ai_id: int, field: bool = False, throw_error: bool = True
) -> List[MstAi]:
    if field:
        mstAiFields = ai.get_mstAiField(conn, ai_id)
        if mstAiFields or not throw_error:
            return [MstAi.parse_obj(mst_ai) for mst_ai in mstAiFields]
        else:
            raise HTTPException(status_code=404, detail="AI not found")
    else:
        mstAis = ai.get_mstAi(conn, ai_id)
        if mstAis or not throw_error:
            return [MstAi.parse_obj(mst_ai) for mst_ai in mstAis]
        else:
            raise HTTPException(status_code=404, detail="AI not found")


def get_ai_entity(conn: Connection, ai_id: int, field: bool = False) -> AiEntity:
    retreived_ais = {ai_id}

    mainAis = get_mst_ai(conn, ai_id, field)

    to_be_retrieved_ais = {ai.avals[0] for ai in mainAis if ai.avals[0] > 0}
    relatedAis: List[MstAi] = []
    while to_be_retrieved_ais:
        for related_ai_id in to_be_retrieved_ais:
            relatedAis += get_mst_ai(conn, related_ai_id, field, throw_error=False)

        retreived_ais |= to_be_retrieved_ais
        to_be_retrieved_ais = {
            ai.avals[0]
            for ai in relatedAis
            if ai.avals[0] > 0 and ai.avals[0] not in retreived_ais
        }

    return AiEntity(
        mainAis=(
            OneAiEntity(mstAi=main_ai, mstAiAct=ai.get_mstAiAct(conn, main_ai.aiActId))
            for main_ai in mainAis
        ),
        relatedAis=(
            OneAiEntity(
                mstAi=related_ai, mstAiAct=ai.get_mstAiAct(conn, related_ai.aiActId)
            )
            for related_ai in relatedAis
        ),
    )
