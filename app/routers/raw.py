from typing import Any, Dict, Optional, Union

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from fuzzywuzzy import fuzz, process

from ..data import gamedata
from ..data.models.common import DetailMessage, Region
from ..data.models.raw import (
    BuffEntity,
    FunctionEntity,
    ServantEntity,
    SkillEntity,
    TdEntity,
)


responses: Dict[Union[str, int], Any] = {
    404: {"model": DetailMessage, "description": "Item not found"}
}


router = APIRouter()


@router.get(
    "/{region}/servant/{item_id}",
    summary="Get servant data",
    response_description="Servant Entity",
    response_model=ServantEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_servant(region: Region, item_id: int, expand: bool = False):
    """
    Get servant info from ID

    If the given ID is a servants's collectionNo, the corresponding servant data is returned.
    Otherwise, it will look up the actual ID field. As a result, it can return not servant data.

    - **expand**: Add expanded skill objects to mstSvt.expandedClassPassive
    from the skill IDs in mstSvt.classPassive.
    Expand all other skills and functions as well.
    """
    if item_id in gamedata.masters[region].mstSvtServantCollectionNo:
        item_id = gamedata.masters[region].mstSvtServantCollectionNo[item_id]
    if item_id in gamedata.masters[region].mstSvtId:
        servant_entity = gamedata.get_servant_entity(region, item_id, expand)
        return Response(
            servant_entity.json(exclude_unset=True), media_type="application/json",
        )
    else:
        raise HTTPException(status_code=404, detail="Servant not found")


@router.get(
    "/{region}/servant/search",
    summary="Find and get servant data",
    response_description="Servant Entity",
    response_model=ServantEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def find_servant(
    region: Region, name: Optional[str] = None, expand: bool = False
):
    """
    Get servant info from ID

    Search the servants' names list for the given name and return the best match.

    - **expand**: Add expanded skill objects to mstSvt.expandedClassPassive
    from the skill IDs in mstSvt.classPassive.
    Expand all other skills and functions as well.
    """
    if name:
        servant_found = process.extract(
            name,
            gamedata.masters[region].mstSvtServantName.keys(),
            scorer=fuzz.token_set_ratio,
        )
        # return servant_found
        items_found = [
            gamedata.masters[region].mstSvtServantName[found[0]]
            for found in servant_found
            if found[1] > 85
        ]
        if len(items_found) >= 1:
            svt_entity_found = [
                gamedata.get_servant_entity(region, item_id, expand)
                for item_id in items_found
            ]
            svt_entity_found = sorted(
                svt_entity_found, key=lambda x: x.mstSvt.collectionNo
            )
            return Response(
                svt_entity_found[0].json(exclude_unset=True),
                media_type="application/json",
            )
        else:
            raise HTTPException(status_code=404, detail="Servant not found")


@router.get(
    "/{region}/equip/{item_id}",
    summary="Get CE data",
    response_description="CE entity",
    response_model=ServantEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_equip(region: Region, item_id: int, expand: bool = False):
    """
    Get CE info from ID

    If the given ID is a CE's collectionNo, the corresponding CE data is returned.
    Otherwise, it will look up the actual ID field. As a result, it can return not CE data.

    - **expand**: Add expanded skill objects to mstSvt.expandedClassPassive
    from the skill IDs in mstSvt.classPassive.
    Expand all other skills and functions as well.
    """
    if item_id in gamedata.masters[region].mstSvtEquipCollectionNo:
        item_id = gamedata.masters[region].mstSvtEquipCollectionNo[item_id]
    if item_id in gamedata.masters[region].mstSvtId:
        servant_entity = gamedata.get_servant_entity(region, item_id, expand)
        return Response(
            servant_entity.json(exclude_unset=True), media_type="application/json",
        )
    else:
        raise HTTPException(status_code=404, detail="Equip not found")


@router.get(
    "/{region}/skill/{item_id}",
    summary="Get skill data",
    response_description="Skill entity",
    response_model=SkillEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_skill(
    region: Region, item_id: int, reverse: bool = False, expand: bool = False
):
    """
    Get the skill data from the given ID

    - **reverse**: Reverse lookup the servants that have this skill
    and return the reverse skill objects.
    - **expand**: Add expanded function objects to mstSkillLv.expandedFuncId
    from the function IDs in mstSkillLv.funcId.
    """
    if item_id in gamedata.masters[region].mstSkillId:
        skill_entity = gamedata.get_skill_entity(region, item_id, reverse, expand)
        return Response(
            skill_entity.json(exclude_unset=True), media_type="application/json",
        )
    else:
        raise HTTPException(status_code=404, detail="Skill not found")


@router.get(
    "/{region}/NP/{item_id}",
    summary="Get NP data",
    response_description="NP entity",
    response_model=TdEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_td(
    region: Region, item_id: int, reverse: bool = False, expand: bool = False
):
    """
    Get the NP data from the given ID

    - **reverse**: Reverse lookup the servants that have this NP
    and return the reversed servant objects.
    - **expand**: Add expanded function objects to mstTreasureDeviceLv.expandedFuncId
    from the function IDs in mstTreasureDeviceLv.funcId.
    """
    if item_id in gamedata.masters[region].mstTreasureDeviceId:
        td_entity = gamedata.get_td_entity(region, item_id, reverse, expand)
        return Response(
            td_entity.json(exclude_unset=True), media_type="application/json",
        )
    else:
        raise HTTPException(status_code=404, detail="NP not found")


@router.get(
    "/{region}/function/{item_id}",
    summary="Get function data",
    response_description="Function entity",
    response_model=FunctionEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_function(
    region: Region, item_id: int, reverse: bool = False, expand: bool = False
):
    """
    Get the function data from the given ID

    - **reverse**: Reverse lookup the skills that have this function
    and return the reversed skill objects.
    Will search recursively and return all entities in path: func -> skill -> servant.
    - **expand**: Add buff objects to mstFunc.expandedVals
    from the buff IDs in mstFunc.vals.
    """
    if item_id in gamedata.masters[region].mstFuncId:
        func_entity = gamedata.get_func_entity(region, item_id, reverse, expand)
        return Response(
            func_entity.json(exclude_unset=True), media_type="application/json",
        )
    else:
        raise HTTPException(status_code=404, detail="Function not found")


@router.get(
    "/{region}/buff/{item_id}",
    summary="Get buff data",
    response_description="Buff entity",
    response_model=BuffEntity,
    response_model_exclude_unset=True,
    responses=responses,
)
async def get_buff(region: Region, item_id: int, reverse: bool = False):
    """
    Get the buff data from the given ID

    - **reverse**: Reverse lookup the functions that have this buff
    and return the reversed function objects.
    Will search recursively and return all entities in path: buff -> func -> skill -> servant.
    """
    if item_id in gamedata.masters[region].mstBuffId:
        buff_entity = gamedata.get_buff_entity(region, item_id, reverse)
        return Response(
            buff_entity.json(exclude_unset=True), media_type="application/json",
        )
    else:
        raise HTTPException(status_code=404, detail="Buff not found")
