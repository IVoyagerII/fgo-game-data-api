from sqlalchemy import (
    BigInteger,
    Boolean,
    Column,
    Index,
    Integer,
    Numeric,
    String,
    Table,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, TEXT
from sqlalchemy.sql import func

from .base import metadata


mstConstant = Table(
    "mstConstant",
    metadata,
    Column("name", String, index=True),
    Column("value", Integer),
    Column("createdAt", Integer),
)


mstCommonRelease = Table(
    "mstCommonRelease",
    metadata,
    Column("id", Integer, index=True),
    Column("priority", Integer),
    Column("condGroup", Integer),
    Column("condType", Integer),
    Column("condId", Integer),
    Column("condNum", Integer),
)


mstBuff = Table(
    "mstBuff",
    metadata,
    Column("vals", ARRAY(Integer)),
    Column("tvals", ARRAY(Integer)),
    Column("ckSelfIndv", ARRAY(Integer)),
    Column("ckOpIndv", ARRAY(Integer)),
    Column("script", JSONB),
    Column("id", Integer, primary_key=True),
    Column("buffGroup", Integer, index=True),
    Column("type", Integer, index=True),
    Column("name", String),
    Column("detail", String),
    Column("iconId", Integer),
    Column("maxRate", Integer),
    Column("effectId", Integer),
)


mstClassRelationOverwrite = Table(
    "mstClassRelationOverwrite",
    metadata,
    Column("id", Integer, index=True),
    Column("atkSide", Integer),
    Column("atkClass", Integer),
    Column("defClass", Integer),
    Column("damageRate", Integer),
    Column("type", Integer),
)


mstFunc = Table(
    "mstFunc",
    metadata,
    Column("vals", ARRAY(Integer)),
    Column("tvals", ARRAY(Integer)),
    Column("questTvals", ARRAY(Integer)),
    Column("effectList", ARRAY(Integer)),
    Column("popupTextColor", Integer),
    Column("id", Integer, primary_key=True),
    Column("cond", Integer),
    Column("funcType", Integer, index=True),
    Column("targetType", Integer, index=True),
    Column("applyTarget", Integer, index=True),
    Column("popupIconId", Integer),
    Column("popupText", String),
    Column("categoryId", Integer),
)


mstFuncGroup = Table(
    "mstFuncGroup",
    metadata,
    Column("funcId", Integer, index=True),
    Column("eventId", Integer),
    Column("baseFuncId", Integer),
    Column("nameTotal", String),
    Column("name", String),
    Column("iconId", Integer),
    Column("priority", Integer),
    Column("isDispValue", Boolean),
)


mstSkill = Table(
    "mstSkill",
    metadata,
    Column("effectList", ARRAY(Integer)),
    Column("actIndividuality", ARRAY(Integer)),
    Column("script", JSONB),
    Column("id", Integer, primary_key=True),
    Column("type", Integer, index=True),
    Column("name", String),
    Column("ruby", String),
    Column("maxLv", Integer),
    Column("iconId", Integer),
    Column("motion", Integer),
)


mstSkillDetail = Table(
    "mstSkillDetail",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("detail", String),
    Column("detailShort", String),
)


mstSvtSkill = Table(
    "mstSvtSkill",
    metadata,
    Column("script", JSONB),
    Column("strengthStatus", Integer, index=True),
    Column("skillNum", Integer),
    Column("svtId", Integer, index=True),
    Column("num", Integer, index=True),
    Column("priority", Integer, index=True),
    Column("skillId", Integer, index=True),
    Column("condQuestId", Integer),
    Column("condQuestPhase", Integer),
    Column("condLv", Integer),
    Column("condLimitCount", Integer),
    Column("eventId", Integer),
    Column("flag", Integer),
)


mstSvtPassiveSkill = Table(
    "mstSvtPassiveSkill",
    metadata,
    Column("svtId", Integer, index=True),
    Column("num", Integer),
    Column("priority", Integer),
    Column("skillId", Integer, index=True),
    Column("condQuestId", Integer),
    Column("condQuestPhase", Integer),
    Column("condLv", Integer),
    Column("condLimitCount", Integer),
    Column("condFriendshipRank", Integer),
    Column("eventId", Integer),
    Column("flag", Integer),
    Column("commonReleaseId", Integer),
    Column("startedAt", Integer),
    Column("endedAt", Integer),
)


mstSkillLv = Table(
    "mstSkillLv",
    metadata,
    Column("funcId", ARRAY(Integer)),
    Column("svals", ARRAY(String)),
    Column("script", JSONB),
    Column("skillId", Integer, index=True),
    Column("lv", Integer),
    Column("chargeTurn", Integer, index=True),
    Column("skillDetailId", Integer),
    Column("priority", Integer),
    Column("expandedFuncId", JSONB),
)


Index("ix_mstSkillLv_funcId_length", func.array_length(mstSkillLv.c.funcId, 1))


mstSkillAdd = Table(
    "mstSkillAdd",
    metadata,
    Column("skillId", Integer, index=True),
    Column("priority", Integer),
    Column("commonReleaseId", Integer, index=True),
    Column("name", String),
    Column("ruby", String),
)


mstTreasureDevice = Table(
    "mstTreasureDevice",
    metadata,
    Column("individuality", ARRAY(Integer)),
    Column("script", JSONB),
    Column("id", Integer, primary_key=True),
    Column("seqId", Integer),
    Column("name", String),
    Column("ruby", String),
    Column("rank", String),
    Column("maxLv", Integer),
    Column("typeText", String),
    Column("attackAttri", Integer),
    Column("effectFlag", Integer),
)


mstTreasureDeviceDetail = Table(
    "mstTreasureDeviceDetail",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("detail", String),
    Column("detailShort", String),
)


mstSvtTreasureDevice = Table(
    "mstSvtTreasureDevice",
    metadata,
    Column("damage", ARRAY(Integer)),
    Column("strengthStatus", Integer, index=True),
    Column("svtId", Integer, index=True),
    Column("num", Integer),
    Column("priority", Integer),
    Column("flag", Integer),
    Column("imageIndex", Integer),
    Column("treasureDeviceId", Integer, index=True),
    Column("condQuestId", Integer),
    Column("condQuestPhase", Integer),
    Column("condLv", Integer),
    Column("condFriendshipRank", Integer),
    Column("motion", Integer),
    Column("cardId", Integer, index=True),
)

Index(
    "ix_mstSvtTreasureDevice_damage_length",
    func.array_length(mstSvtTreasureDevice.c.damage, 1),
)


mstTreasureDeviceLv = Table(
    "mstTreasureDeviceLv",
    metadata,
    Column("funcId", ARRAY(Integer)),
    Column("svals", ARRAY(String)),
    Column("svals2", ARRAY(String)),
    Column("svals3", ARRAY(String)),
    Column("svals4", ARRAY(String)),
    Column("svals5", ARRAY(String)),
    Column("treaureDeviceId", Integer, index=True),
    Column("lv", Integer),
    Column("script", JSONB),
    Column("gaugeCount", Integer),
    Column("detailId", Integer),
    Column("tdPoint", Integer, index=True),
    Column("tdPointQ", Integer),
    Column("tdPointA", Integer),
    Column("tdPointB", Integer),
    Column("tdPointEx", Integer),
    Column("tdPointDef", Integer),
    Column("qp", Integer),
    Column("expandedFuncId", JSONB),
)


Index(
    "ix_mstTreasureDeviceLv_funcId_length",
    func.array_length(mstTreasureDeviceLv.c.funcId, 1),
)


mstSvt = Table(
    "mstSvt",
    metadata,
    Column("relateQuestIds", ARRAY(Integer)),
    Column("individuality", ARRAY(Integer)),
    Column("classPassive", ARRAY(Integer)),
    Column("cardIds", ARRAY(Integer)),
    Column("script", JSONB),
    Column("id", Integer, primary_key=True),
    Column("baseSvtId", Integer),
    Column("name", String),
    Column("ruby", String),
    Column("battleName", String),
    Column("classId", Integer, index=True),
    Column("type", Integer, index=True),
    Column("limitMax", Integer),
    Column("rewardLv", Integer),
    Column("friendshipId", Integer),
    Column("maxFriendshipRank", Integer),
    Column("genderType", Integer, index=True),
    Column("attri", Integer, index=True),
    Column("combineSkillId", Integer),
    Column("combineLimitId", Integer),
    Column("sellQp", Integer),
    Column("sellMana", Integer),
    Column("sellRarePri", Integer),
    Column("expType", Integer),
    Column("combineMaterialId", Integer),
    Column("cost", Integer),
    Column("battleSize", Integer),
    Column("hpGaugeY", Integer),
    Column("starRate", Integer),
    Column("deathRate", Integer),
    Column("attackAttri", Integer),
    Column("illustratorId", Integer),
    Column("cvId", Integer),
    Column("collectionNo", Integer, index=True),
    Column("materialStoryPriority", Integer),
    Column("flag", Integer, index=True),
)


mstSvtIndividuality = Table(
    "mstSvtIndividuality",
    metadata,
    Column("individuality", ARRAY(Integer)),
    Column("svtId", Integer, index=True),
    Column("idx", Integer, index=True),
    Column("limitCount", Integer),
    Column("condType", Integer),
    Column("condId", Integer),
    Column("condNum", Integer),
)


mstSvtExtra = Table(
    "mstSvtExtra",
    metadata,
    Column("svtId", Integer, primary_key=True),
    Column("zeroLimitOverwriteName", String),
    Column("bondEquip", Integer),
    Column("bondEquipOwner", Integer),
    Column("valentineEquip", ARRAY(Integer)),
    Column("valentineScript", JSONB),
    Column("valentineEquipOwner", Integer),
    Column("costumeLimitSvtIdMap", JSONB),
)


mstSvtCard = Table(
    "mstSvtCard",
    metadata,
    Column("normalDamage", ARRAY(Integer)),
    Column("singleDamage", ARRAY(Integer)),
    Column("trinityDamage", ARRAY(Integer)),
    Column("unisonDamage", ARRAY(Integer)),
    Column("grandDamage", ARRAY(Integer)),
    Column("attackIndividuality", ARRAY(Integer)),
    Column("svtId", Integer, index=True),
    Column("cardId", Integer),
    Column("motion", Integer),
    Column("attackType", Integer),
)


mstCombineLimit = Table(
    "mstCombineLimit",
    metadata,
    Column("itemIds", ARRAY(Integer)),
    Column("itemNums", ARRAY(Integer)),
    Column("id", Integer, index=True),
    Column("svtLimit", Integer),
    Column("qp", Integer),
)


mstCombineSkill = Table(
    "mstCombineSkill",
    metadata,
    Column("itemIds", ARRAY(Integer)),
    Column("itemNums", ARRAY(Integer)),
    Column("id", Integer, index=True),
    Column("skillLv", Integer),
    Column("qp", Integer),
)


mstCombineCostume = Table(
    "mstCombineCostume",
    metadata,
    Column("itemIds", ARRAY(Integer)),
    Column("itemNums", ARRAY(Integer)),
    Column("svtId", Integer, index=True),
    Column("costumeId", Integer),
    Column("qp", Integer),
)


mstVoice = Table(
    "mstVoice",
    metadata,
    Column("id", String, primary_key=True),
    Column("priority", Integer),
    Column("svtVoiceType", Integer),
    Column("name", String),
    Column("nameDefault", String),
    Column("condType", Integer),
    Column("condValue", Integer),
    Column("voicePlayedValue", Integer),
    Column("firstPlayPriority", Integer),
    Column("closedType", Integer),
    Column("flag", Integer),
)


mstSvtVoice = Table(
    "mstSvtVoice",
    metadata,
    Column("scriptJson", JSONB),
    Column("id", Integer, index=True),
    Column("voicePrefix", Integer),
    Column("type", Integer),
    Index(
        "ix_mstSvtVoice_GIN",
        text('"scriptJson" jsonb_path_ops'),
        postgresql_using="gin",
    ),
)


mstSvtVoiceRelation = Table(
    "mstSvtVoiceRelation",
    metadata,
    Column("svtId", Integer, index=True),
    Column("relationSvtId", Integer),
    Column("ascendOrder", Integer),
)


mstSvtGroup = Table(
    "mstSvtGroup",
    metadata,
    Column("id", Integer, index=True),
    Column("svtId", Integer, index=True),
)


mstVoicePlayCond = Table(
    "mstVoicePlayCond",
    metadata,
    Column("svtId", Integer, index=True),
    Column("voicePrefix", Integer),
    Column("voiceId", String),
    Column("idx", Integer),
    Column("condGroup", Integer),
    Column("condType", Integer, index=True),
    Column("targetId", Integer, index=True),
    Column("condValues", ARRAY(Integer)),
)


mstSvtLimit = Table(
    "mstSvtLimit",
    metadata,
    Column("weaponColor", Integer),
    Column("svtId", Integer, index=True),
    Column("limitCount", Integer),
    Column("rarity", Integer, index=True),
    Column("lvMax", Integer),
    Column("weaponGroup", Integer),
    Column("weaponScale", Integer),
    Column("effectFolder", Integer),
    Column("hpBase", Integer),
    Column("hpMax", Integer),
    Column("atkBase", Integer),
    Column("atkMax", Integer),
    Column("criticalWeight", Integer),
    Column("power", Integer),
    Column("defense", Integer),
    Column("agility", Integer),
    Column("magic", Integer),
    Column("luck", Integer),
    Column("treasureDevice", Integer),
    Column("policy", Integer),
    Column("personality", Integer),
    Column("deity", Integer),
    Column("stepProbability", Integer),
    Column("strParam", String),
)


mstSvtLimitAdd = Table(
    "mstSvtLimitAdd",
    metadata,
    Column("individuality", ARRAY(Integer)),
    Column("script", JSONB),
    Column("svtId", Integer, index=True),
    Column("limitCount", Integer, index=True),
    Column("battleCharaId", Integer),
    Column("fileConvertLimitCount", Integer),
    Column("battleCharaLimitCount", Integer),
    Column("battleCharaOffsetX", Integer),
    Column("battleCharaOffsetY", Integer),
    Column("battleCharaOffsetZ", Integer),
    Column("svtVoiceId", Integer),
    Column("voicePrefix", Integer),
)


mstSvtChange = Table(
    "mstSvtChange",
    metadata,
    Column("beforeTreasureDeviceIds", ARRAY(Integer)),
    Column("afterTreasureDeviceIds", ARRAY(Integer)),
    Column("svtId", Integer, index=True),
    Column("priority", Integer),
    Column("condType", Integer),
    Column("condTargetId", Integer),
    Column("condValue", Integer),
    Column("name", String),
    Column("ruby", String),
    Column("battleName", String),
    Column("svtVoiceId", Integer),
    Column("limitCount", Integer),
    Column("flag", Integer),
    Column("battleSvtId", Integer),
)


mstSvtCostume = Table(
    "mstSvtCostume",
    metadata,
    Column("svtId", Integer, index=True),
    Column("id", Integer, index=True),
    Column("groupIndex", Integer),
    Column("name", String),
    Column("shortName", String),
    Column("detail", String),
    Column("itemGetInfo", String),
    Column("releaseInfo", String),
    Column("costumeReleaseDetail", String),
    Column("priority", Integer),
    Column("flag", Integer),
    Column("costumeCollectionNo", Integer),
    Column("iconId", Integer),
    Column("openedAt", Integer),
    Column("endedAt", Integer),
    Column("script", String),
)


mstSvtExp = Table(
    "mstSvtExp",
    metadata,
    Column("type", Integer, index=True),
    Column("lv", Integer),
    Column("exp", Integer),
    Column("curve", Integer),
)


mstFriendship = Table(
    "mstFriendship",
    metadata,
    Column("itemIds", ARRAY(Integer)),
    Column("itemNums", ARRAY(Integer)),
    Column("id", Integer, index=True),
    Column("rank", Integer),
    Column("friendship", Integer),
    Column("qp", Integer),
)


mstCombineMaterial = Table(
    "mstCombineMaterial",
    metadata,
    Column("id", Integer, index=True),
    Column("lv", Integer),
    Column("value", Integer),
    Column("createdAt", Integer),
)


mstSvtScript = Table(
    "mstSvtScript",
    metadata,
    Column("extendData", JSONB),
    Column("id", BigInteger, index=True),
    Column("form", Integer),
    Column("faceX", Integer),
    Column("faceY", Integer),
    Column("bgImageId", Integer),
    Column("scale", Numeric),
    Column("offsetX", Integer),
    Column("offsetY", Integer),
    Column("offsetXMyroom", Integer),
    Column("offsetYMyroom", Integer),
)


Index("ix_mstSvtScript_svtId", mstSvtScript.c.id / 10)


mstSvtComment = Table(
    "mstSvtComment",
    metadata,
    Column("condValues", ARRAY(Integer)),
    Column("script", JSONB),
    Column("svtId", Integer, index=True),
    Column("id", Integer),
    Column("priority", Integer),
    Column("condMessage", String),
    Column("comment", String),
    Column("condType", Integer),
    Column("condValue2", Integer),
)


mstSubtitle = Table(
    "mstSubtitle",
    metadata,
    Column("id", String),
    Column("serif", String),
    Column("svtId", Integer, index=True),
)


mstSvtAdd = Table(
    "mstSvtAdd",
    metadata,
    Column("svtId", Integer, index=True),
    Column("script", JSONB),
)


mstSvtAppendPassiveSkill = Table(
    "mstSvtAppendPassiveSkill",
    metadata,
    Column("svtId", Integer, index=True),
    Column("num", Integer),
    Column("priority", Integer),
    Column("skillId", Integer),
)


mstSvtAppendPassiveSkillUnlock = Table(
    "mstSvtAppendPassiveSkillUnlock",
    metadata,
    Column("svtId", Integer, index=True),
    Column("num", Integer),
    Column("itemIds", ARRAY(Integer)),
    Column("itemNums", ARRAY(Integer)),
)


mstCombineAppendPassiveSkill = Table(
    "mstCombineAppendPassiveSkill",
    metadata,
    Column("svtId", Integer, index=True),
    Column("num", Integer, index=True),
    Column("skillLv", Integer),
    Column("qp", Integer),
    Column("itemIds", ARRAY(Integer)),
    Column("itemNums", ARRAY(Integer)),
)


mstSvtCoin = Table(
    "mstSvtCoin",
    metadata,
    Column("svtId", Integer, index=True),
    Column("summonNum", Integer),
    Column("itemId", Integer),
)


mstEquip = Table(
    "mstEquip",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("detail", String),
    Column("condUserLv", Integer),
    Column("maxLv", Integer),
    Column("maleImageId", Integer),
    Column("femaleImageId", Integer),
    Column("imageId", Integer),
    Column("maleSpellId", Integer),
    Column("femaleSpellId", Integer),
)


mstEquipExp = Table(
    "mstEquipExp",
    metadata,
    Column("equipId", Integer, index=True),
    Column("lv", Integer),
    Column("exp", Integer),
    Column("skillLv1", Integer),
    Column("skillLv2", Integer),
    Column("skillLv3", Integer),
)


mstEquipSkill = Table(
    "mstEquipSkill",
    metadata,
    Column("equipId", Integer, index=True),
    Column("num", Integer),
    Column("skillId", Integer),
    Column("condLv", Integer),
)


mstItem = Table(
    "mstItem",
    metadata,
    Column("individuality", ARRAY(Integer)),
    Column("script", JSONB),
    Column("eventId", Integer),
    Column("eventGroupId", Integer),
    Column("id", Integer, primary_key=True),
    Column("name", String),
    Column("detail", String),
    Column("imageId", Integer),
    Column("bgImageId", Integer, index=True),
    Column("type", Integer, index=True),
    Column("unit", String),
    Column("value", Integer),
    Column("sellQp", Integer),
    Column("isSell", Boolean),
    Column("priority", Integer),
    Column("dropPriority", Integer),
    Column("startedAt", Integer),
    Column("endedAt", Integer),
    Column("useSkill", Boolean),
    Column("useAscension", Boolean),
    Column("useCostume", Boolean),
)


mstCommandCode = Table(
    "mstCommandCode",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("collectionNo", Integer),
    Column("name", String),
    Column("ruby", String),
    Column("rarity", Integer),
    Column("sellQp", Integer),
    Column("sellMana", Integer),
    Column("sellRarePri", Integer),
)


mstCommandCodeSkill = Table(
    "mstCommandCodeSkill",
    metadata,
    Column("commandCodeId", Integer, index=True),
    Column("num", Integer),
    Column("priority", Integer),
    Column("skillId", Integer),
    Column("startedAt", Integer),
    Column("endedAt", Integer),
)


mstCommandCodeComment = Table(
    "mstCommandCodeComment",
    metadata,
    Column("commandCodeId", Integer, index=True),
    Column("comment", String),
    Column("illustratorId", Integer),
)


mstCv = Table(
    "mstCv",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, index=True),
    Column("comment", String),
)


mstIllustrator = Table(
    "mstIllustrator",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String, index=True),
    Column("comment", String),
)


mstGift = Table(
    "mstGift",
    metadata,
    Column("id", Integer, index=True),
    Column("type", Integer),
    Column("objectId", Integer),
    Column("priority", Integer),
    Column("num", Integer),
)


mstSetItem = Table(
    "mstSetItem",
    metadata,
    Column("id", Integer, index=True),
    Column("purchaseType", Integer),
    Column("targetId", Integer),
    Column("setNum", Integer),
    Column("createdAt", Integer),
)


mstShop = Table(
    "mstShop",
    metadata,
    Column("itemIds", ARRAY(Integer)),
    Column("prices", ARRAY(Integer)),
    Column("targetIds", ARRAY(Integer)),
    Column("script", JSONB),
    Column("anotherPayType", Integer),
    Column("anotherItemIds", ARRAY(Integer)),
    Column("useAnotherPayCommonReleaseId", Integer),
    Column("id", Integer, primary_key=True),
    Column("baseShopId", Integer),
    Column("eventId", Integer, index=True),
    Column("slot", Integer),
    Column("flag", Integer),
    Column("priority", Integer),
    Column("purchaseType", Integer),
    Column("setNum", Integer),
    Column("payType", Integer),
    Column("shopType", Integer),
    Column("limitNum", Integer),
    Column("defaultLv", Integer),
    Column("defaultLimitCount", Integer),
    Column("name", String),
    Column("detail", String),
    Column("infoMessage", String),
    Column("warningMessage", String),
    Column("imageId", Integer),
    Column("bgImageId", Integer),
    Column("openedAt", Integer),
    Column("closedAt", Integer),
)


mstShopScript = Table(
    "mstShopScript",
    metadata,
    Column("ignoreEventIds", ARRAY(Integer)),
    Column("shopId", Integer, index=True),
    Column("priority", Integer),
    Column("name", String),
    Column("scriptId", String),
    Column("frequencyType", Integer),
    Column("eventId", Integer),
    Column("svtId", Integer),
    Column("limitCount", Integer),
    Column("materialFolderId", Integer),
)


mstEvent = Table(
    "mstEvent",
    metadata,
    Column("script", JSONB),
    Column("id", Integer, primary_key=True),
    Column("baseEventId", Integer),
    Column("type", Integer),
    Column("openType", Integer),
    Column("name", String),
    Column("shortName", String),
    Column("detail", String),
    Column("noticeBannerId", Integer),
    Column("bannerId", Integer),
    Column("iconId", Integer),
    Column("bannerPriority", Integer),
    Column("openHours", Integer),
    Column("intervalHours", Integer),
    Column("noticeAt", Integer),
    Column("startedAt", Integer),
    Column("endedAt", Integer),
    Column("finishedAt", Integer),
    Column("materialOpenedAt", Integer),
    Column("linkType", Integer),
    Column("linkBody", String),
    Column("deviceType", Integer),
    Column("myroomBgId", Integer),
    Column("myroomBgmId", Integer),
    Column("createdAt", Integer),
    Column("warIds", ARRAY(Integer)),
)


mstEventReward = Table(
    "mstEventReward",
    metadata,
    Column("eventId", Integer, index=True),
    Column("groupId", Integer),
    Column("point", Integer),
    Column("type", Integer),
    Column("giftId", Integer),
    Column("bgImageId", Integer),
    Column("presentMessageId", Integer),
)


mstEventPointGroup = Table(
    "mstEventPointGroup",
    metadata,
    Column("eventId", Integer, index=True),
    Column("groupId", Integer),
    Column("name", String),
    Column("iconId", Integer),
)


mstEventPointBuff = Table(
    "mstEventPointBuff",
    metadata,
    Column("funcIds", ARRAY(Integer)),
    Column("id", Integer),
    Column("eventId", Integer, index=True),
    Column("groupId", Integer),
    Column("eventPoint", Integer),
    Column("name", String),
    Column("detail", String),
    Column("imageId", Integer),
    Column("bgImageId", Integer),
    Column("value", Integer),
)


mstMasterMission = Table(
    "mstMasterMission",
    metadata,
    Column("id", Integer),
    Column("priority", Integer),
    Column("startedAt", Integer),
    Column("endedAt", Integer),
    Column("closedAt", Integer),
    Column("imageId", Integer),
    Column("name", String),
)


mstEventMission = Table(
    "mstEventMission",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("flag", Integer),
    Column("type", Integer),
    Column("missionTargetId", Integer, index=True),
    Column("dispNo", Integer),
    Column("notfyPriority", Integer),
    Column("name", String),
    Column("detail", String),
    Column("startedAt", Integer),
    Column("endedAt", Integer),
    Column("closedAt", Integer),
    Column("rewardType", Integer),
    Column("presentMessageId", Integer),
    Column("giftId", Integer),
    Column("bannerGroup", Integer),
    Column("priority", Integer),
    Column("rewardRarity", Integer),
)


mstEventMissionCondition = Table(
    "mstEventMissionCondition",
    metadata,
    Column("targetIds", ARRAY(Integer)),
    Column("missionId", Integer, index=True),
    Column("missionProgressType", Integer),
    Column("priority", Integer),
    Column("id", Integer),
    Column("missionTargetId", Integer),
    Column("condGroup", Integer),
    Column("condType", Integer),
    Column("targetNum", Integer),
    Column("conditionMessage", String),
    Column("closedMessage", String),
    Column("flag", Integer),
)


mstEventMissionConditionDetail = Table(
    "mstEventMissionConditionDetail",
    metadata,
    Column("targetIds", ARRAY(Integer)),
    Column("addTargetIds", ARRAY(Integer)),
    Column("targetQuestIndividualities", ARRAY(Integer)),
    Column("targetEventIds", ARRAY(Integer)),
    Column("id", Integer, primary_key=True),
    Column("missionTargetId", Integer),
    Column("missionCondType", Integer),
    Column("logicType", Integer),
    Column("conditionLinkType", Integer),
)


mstEventTower = Table(
    "mstEventTower",
    metadata,
    Column("eventId", Integer, index=True),
    Column("towerId", Integer),
    Column("name", String),
    Column("topFloor", Integer),
    Column("floorLabel", String),
    Column("openEffectId", Integer),
    Column("flag", Integer),
)


mstEventTowerReward = Table(
    "mstEventTowerReward",
    metadata,
    Column("eventId", Integer, index=True),
    Column("towerId", Integer),
    Column("floor", Integer),
    Column("giftId", Integer),
    Column("iconId", Integer),
    Column("presentMessageId", Integer),
    Column("boardMessage", String),
    Column("boardImageId", Integer),
)


mstTreasureBox = Table(
    "mstTreasureBox",
    metadata,
    Column("id", Integer, index=True),
    Column("eventId", Integer, index=True),
    Column("slot", Integer),
    Column("idx", Integer),
    Column("iconId", Integer),
    Column("treasureBoxGiftId", Integer, index=True),
    Column("maxDrawNumOnce", Integer),
    Column("commonConsumeId", Integer),
    Column("extraGiftId", Integer),
)


mstTreasureBoxGift = Table(
    "mstTreasureBoxGift",
    metadata,
    Column("id", Integer, index=True),
    Column("idx", Integer),
    Column("giftId", Integer, index=True),
    Column("collateralUpperLimit", Integer),
)


mstCommonConsume = Table(
    "mstCommonConsume",
    metadata,
    Column("id", Integer, index=True),
    Column("priority", Integer),
    Column("type", Integer),
    Column("objectId", Integer),
    Column("num", Integer),
)


mstBoxGacha = Table(
    "mstBoxGacha",
    metadata,
    Column("baseIds", ARRAY(Integer)),
    Column("pickupIds", ARRAY(Integer), nullable=True),
    Column("talkIds", ARRAY(Integer)),
    Column("script", JSONB),
    Column("id", Integer),
    Column("eventId", Integer, index=True),
    Column("slot", Integer),
    Column("guideDisplayName", String),
    Column("payType", Integer),
    Column("payTargetId", Integer),
    Column("payValue", Integer),
    Column("detailUrl", String),
    Column("priority", Integer),
    Column("flag", Integer),
)


mstBoxGachaBase = Table(
    "mstBoxGachaBase",
    metadata,
    Column("id", Integer, index=True),
    Column("no", Integer),
    Column("type", Integer),
    Column("targetId", Integer),
    Column("isRare", Boolean),
    Column("iconId", Integer),
    Column("bannerId", Integer),
    Column("priority", Integer),
    Column("maxNum", Integer),
    Column("detail", String),
)


mstEventRewardSet = Table(
    "mstEventRewardSet",
    metadata,
    Column("rewardSetType", Integer),
    Column("eventId", Integer, index=True),
    Column("id", Integer, index=True),
    Column("iconId", Integer),
    Column("name", String),
    Column("detail", String),
    Column("bgImageId", Integer),
)


mstBgm = Table(
    "mstBgm",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("fileName", String),
    Column("name", String),
    Column("priority", Integer),
    Column("detail", String),
    Column("flag", Integer),
    Column("shopId", Integer),
    Column("logoId", Integer),
)


mstBgmRelease = Table(
    "mstBgmRelease",
    metadata,
    Column("targetIds", ARRAY(Integer)),
    Column("vals", ARRAY(Integer)),
    Column("bgmId", Integer, index=True),
    Column("id", Integer, index=True),
    Column("priority", Integer),
    Column("type", Integer),
    Column("condGroup", Integer),
    Column("closedMessageId", Integer),
)


mstWar = Table(
    "mstWar",
    metadata,
    Column("coordinates", JSONB),
    Column("id", Integer, primary_key=True),
    Column("age", String),
    Column("name", String),
    Column("longName", String),
    Column("bannerId", Integer),
    Column("mapImageId", Integer),
    Column("mapImageW", Integer),
    Column("mapImageH", Integer),
    Column("headerImageId", Integer),
    Column("priority", Integer),
    Column("parentWarId", Integer),
    Column("materialParentWarId", Integer),
    Column("flag", Integer),
    Column("emptyMessage", String),
    Column("bgmId", Integer),
    Column("scriptId", String),
    Column("startType", Integer),
    Column("targetId", BigInteger),
    Column("eventId", Integer),
    Column("lastQuestId", Integer),
    Column("assetId", Integer),
)


mstMap = Table(
    "mstMap",
    metadata,
    Column("script", JSONB),
    Column("id", Integer, primary_key=True),
    Column("warId", Integer),
    Column("mapImageId", Integer),
    Column("mapImageW", Integer),
    Column("mapImageH", Integer),
    Column("headerImageId", Integer),
    Column("bgmId", Integer),
)


mstSpot = Table(
    "mstSpot",
    metadata,
    Column("joinSpotIds", ARRAY(Integer)),
    Column("id", Integer, primary_key=True),
    Column("warId", Integer, index=True),
    Column("mapId", Integer),
    Column("name", String, index=True),
    Column("imageId", Integer),
    Column("x", Integer),
    Column("y", Integer),
    Column("imageOfsX", Integer),
    Column("imageOfsY", Integer),
    Column("nameOfsX", Integer),
    Column("nameOfsY", Integer),
    Column("questOfsX", Integer),
    Column("questOfsY", Integer),
    Column("nextOfsX", Integer),
    Column("nextOfsY", Integer),
    Column("dispCondType1", Integer),
    Column("dispTargetId1", Integer),
    Column("dispTargetValue1", Integer),
    Column("dispCondType2", Integer),
    Column("dispTargetId2", Integer),
    Column("dispTargetValue2", Integer),
    Column("activeCondType", Integer),
    Column("activeTargetId", Integer),
    Column("activeTargetValue", Integer),
    Column("closedMessage", String),
    Column("flag", Integer),
)


mstWarAdd = Table(
    "mstWarAdd",
    metadata,
    Column("script", JSONB),
    Column("warId", Integer, index=True),
    Column("type", Integer),
    Column("priority", Integer),
    Column("overwriteId", Integer),
    Column("overwriteStr", String),
    Column("condType", Integer),
    Column("targetId", Integer),
    Column("value", Integer),
    Column("startedAt", Integer),
    Column("endedAt", Integer),
)


mstQuest = Table(
    "mstQuest",
    metadata,
    Column("beforeActionVals", ARRAY(String)),
    Column("afterActionVals", ARRAY(String)),
    Column("id", Integer, primary_key=True),
    Column("name", String, index=True),
    Column("nameRuby", String),
    Column("type", Integer, index=True),
    Column("consumeType", Integer),
    Column("actConsume", Integer),
    Column("chaldeaGateCategory", Integer),
    Column("spotId", Integer, index=True),
    Column("giftId", Integer),
    Column("priority", Integer),
    Column("bannerType", Integer),
    Column("bannerId", Integer),
    Column("iconId", Integer),
    Column("charaIconId", Integer),
    Column("giftIconId", Integer),
    Column("forceOperation", Integer),
    Column("afterClear", Integer),
    Column("displayHours", Integer),
    Column("intervalHours", Integer),
    Column("chapterId", Integer),
    Column("chapterSubId", Integer),
    Column("chapterSubStr", String),
    Column("recommendLv", String),
    Column("hasStartAction", Integer),
    Column("flag", BigInteger),
    Column("scriptQuestId", Integer),
    Column("noticeAt", Integer),
    Column("openedAt", Integer),
    Column("closedAt", Integer),
)


mstQuestMessage = Table(
    "mstQuestMessage",
    metadata,
    Column("questId", Integer),
    Column("phase", Integer),
    Column("idx", Integer),
    Column("message", String),
    Column("condType", Integer),
    Column("targetId", Integer),
    Column("targetNum", Integer),
    Column("frequencyType", Integer),
    Column("displayType", Integer),
)


mstQuestRelease = Table(
    "mstQuestRelease",
    metadata,
    Column("questId", Integer, index=True),
    Column("type", Integer),
    Column("targetId", Integer),
    Column("value", BigInteger),
    Column("openLimit", Integer),
    Column("closedMessageId", Integer),
    Column("imagePriority", Integer),
)


mstClosedMessage = Table(
    "mstClosedMessage",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("message", String),
)


mstQuestConsumeItem = Table(
    "mstQuestConsumeItem",
    metadata,
    Column("itemIds", ARRAY(Integer)),
    Column("nums", ARRAY(Integer)),
    Column("questId", Integer, primary_key=True),
)


mstQuestPhase = Table(
    "mstQuestPhase",
    metadata,
    Column("classIds", ARRAY(Integer)),
    Column("individuality", ARRAY(Integer), index=True),
    Column("script", JSONB),
    Column("questId", Integer, index=True),
    Column("phase", Integer, index=True),
    Column("isNpcOnly", Boolean),
    Column("battleBgId", Integer, index=True),
    Column("battleBgType", Integer),
    Column("qp", Integer),
    Column("playerExp", Integer),
    Column("friendshipExp", Integer),
    Column("giftId", Integer),
)


mstQuestPhaseDetail = Table(
    "mstQuestPhaseDetail",
    metadata,
    Column("beforeActionVals", ARRAY(String)),
    Column("afterActionVals", ARRAY(String)),
    Column("boardMessage", JSONB),
    Column("questId", Integer, index=True),
    Column("phase", Integer, index=True),
    Column("spotId", Integer),
    Column("consumeType", Integer),
    Column("actConsume", Integer),
    Column("flag", BigInteger),
)


mstStage = Table(
    "mstStage",
    metadata,
    Column("npcDeckIds", ARRAY(Integer)),
    Column("script", JSONB),
    Column("questId", Integer, index=True),
    Column("questPhase", Integer, index=True),
    Column("wave", Integer, index=True),
    Column("enemyInfo", Integer),
    Column("bgmId", Integer, index=True),
    Column("startEffectId", Integer),
    Index(
        "ix_mstStage_script_GIN",
        text('"script" jsonb_path_ops'),
        postgresql_using="gin",
    ),
)


mstStageRemap = Table(
    "mstStageRemap",
    metadata,
    Column("questId", Integer, index=True),
    Column("questPhase", Integer, index=True),
    Column("wave", Integer, index=True),
    Column("remapQuestId", Integer),
    Column("remapPhase", Integer),
    Column("remapWave", Integer),
)


npcFollower = Table(
    "npcFollower",
    metadata,
    Column("id", Integer, index=True),
    Column("questId", Integer, index=True),
    Column("questPhase", Integer, index=True),
    Column("priority", Integer),
    Column("leaderSvtId", Integer),
    Column("svtEquipIds", ARRAY(Integer)),
    Column("flag", Integer),
    Column("npcScript", String),
    Column("createdAt", Integer),
)


npcFollowerRelease = Table(
    "npcFollowerRelease",
    metadata,
    Column("id", Integer, index=True),
    Column("questId", Integer, index=True),
    Column("questPhase", Integer, index=True),
    Column("condType", Integer),
    Column("condTargetId", Integer),
    Column("condValue", Integer),
    Column("createdAt", Integer),
)


npcSvtFollower = Table(
    "npcSvtFollower",
    metadata,
    Column("appendPassiveSkillIds", ARRAY(Integer)),
    Column("appendPassiveSkillLvs", ARRAY(Integer)),
    Column("id", Integer, primary_key=True),
    Column("svtId", Integer),
    Column("name", String),
    Column("lv", Integer),
    Column("limitCount", Integer),
    Column("hp", Integer),
    Column("atk", Integer),
    Column("individuality", String),
    Column("treasureDeviceId", Integer),
    Column("treasureDeviceLv", Integer),
    Column("skillId1", Integer),
    Column("skillId2", Integer),
    Column("skillId3", Integer),
    Column("skillLv1", Integer),
    Column("skillLv2", Integer),
    Column("skillLv3", Integer),
    Column("flag", Integer),
    Column("createdAt", Integer),
)


npcSvtEquip = Table(
    "npcSvtEquip",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("svtId", Integer),
    Column("lv", Integer),
    Column("limitCount", Integer),
)


mstAi = Table(
    "mstAi",
    metadata,
    Column("id", Integer, index=True),
    Column("idx", Integer),
    Column("actNum", Integer),
    Column("priority", Integer),
    Column("probability", Integer),
    Column("cond", Integer),
    Column("vals", ARRAY(Integer)),
    Column("aiActId", Integer),
    Column("avals", ARRAY(Integer)),
    Column("infoText", String),
)

Index("ix_mstAi_avals_first", mstAi.c.avals[1])

mstAiField = Table(
    "mstAiField",
    metadata,
    Column("id", Integer, index=True),
    Column("idx", Integer),
    Column("script", JSONB),
    Column("actNum", Integer),
    Column("priority", Integer),
    Column("probability", Integer),
    Column("cond", Integer),
    Column("vals", ARRAY(Integer)),
    Column("aiActId", Integer),
    Column("avals", ARRAY(Integer)),
    Column("infoText", String),
    Column("timing", Integer),
)

Index("ix_mstAiField_avals_first", mstAiField.c.avals[1])


mstAiAct = Table(
    "mstAiAct",
    metadata,
    Column("targetIndividuality", ARRAY(Integer)),
    Column("skillVals", ARRAY(Integer)),
    Column("id", Integer, primary_key=True),
    Column("type", Integer),
    Column("target", Integer),
    Column("createdAt", Integer),
)

Index("ix_mstAiAct_skillVals", mstAiAct.c.skillVals[1])


ScriptFileList = Table(
    "ScriptFileList",
    metadata,
    Column("scriptFileName", String, index=True),
    Column("questId", Integer, index=True),
    Column("phase", Integer, index=True),
    Column("sceneType", Integer),
    Column("rawScriptSHA1", String),
    Column("rawScript", TEXT),
    Column("textScript", TEXT),
)

Index(
    "ix_ScriptFileList_text", ScriptFileList.c.textScript, postgresql_using="pgroonga"
)

TABLES_TO_BE_LOADED = [
    mstCommonRelease,
    mstSkill,
    mstTreasureDevice,
    mstSvt,
    mstVoice,
    mstEquip,
    mstCommandCode,
    mstCv,
    mstIllustrator,
    mstShop,
    mstShopScript,
    mstBgm,
    mstBgmRelease,
    mstWar,
    mstMap,
    mstSpot,
    mstQuest,
    mstQuestMessage,
    mstClosedMessage,
    mstAiAct,
    mstEventMission,
    mstEventMissionConditionDetail,
    mstConstant,
    mstClassRelationOverwrite,
    mstSkillDetail,
    mstSvtSkill,
    mstSvtPassiveSkill,
    mstSkillAdd,
    mstTreasureDeviceDetail,
    mstSvtTreasureDevice,
    mstSvtIndividuality,
    mstSvtCard,
    mstSvtLimit,
    mstCombineLimit,
    mstCombineSkill,
    mstCombineCostume,
    mstSvtLimitAdd,
    mstSvtChange,
    mstSvtCostume,
    mstSvtVoice,
    mstSvtVoiceRelation,
    mstVoicePlayCond,
    mstSvtComment,
    mstSvtGroup,
    mstSvtScript,
    mstSvtExp,
    mstFriendship,
    mstCombineMaterial,
    mstSvtAdd,
    mstSvtAppendPassiveSkill,
    mstSvtAppendPassiveSkillUnlock,
    mstCombineAppendPassiveSkill,
    mstSvtCoin,
    mstEquipExp,
    mstEquipSkill,
    mstCommandCodeSkill,
    mstCommandCodeComment,
    mstGift,
    mstSetItem,
    mstMasterMission,
    mstEventReward,
    mstEventRewardSet,
    mstEventPointGroup,
    mstEventPointBuff,
    mstEventMissionCondition,
    mstEventTower,
    mstEventTowerReward,
    mstTreasureBox,
    mstTreasureBoxGift,
    mstCommonConsume,
    mstBoxGacha,
    mstBoxGachaBase,
    mstWarAdd,
    mstQuestRelease,
    mstQuestConsumeItem,
    mstQuestPhase,
    mstQuestPhaseDetail,
    mstStage,
    mstStageRemap,
    npcFollower,
    npcFollowerRelease,
    npcSvtFollower,
    npcSvtEquip,
    mstAi,
    mstAiField,
]
