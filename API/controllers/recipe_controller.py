from bson import json_util
from utils.config import get_settings
from utils.db_manager import MongoDBManager
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import List
import json
from models.recipe_models import RecipeBase, RecipeCreate
from dao.recipe_dao import RecipeDao
from utils.response_manager import common_responses


router = APIRouter()
dao = RecipeDao()
settings = get_settings()
db_manager = MongoDBManager()
collection = db_manager.get_collection("recipes")


@router.get("/", responses=common_responses)
async def get_all_recipes():
    try:
        recipes = await dao.get_all_recipe()
        serialized_recipes = json.loads(json.dumps(recipes, default=str))
        return JSONResponse(content=serialized_recipes)
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.get("/search")
async def search_recipes_by_title(title: str):
    pipeline = [
        {"$match": {"recipe_title": {"$regex": title, "$options": "i"}}}
    ]
    result_cursor = collection.aggregate(pipeline)
    result = []
    async for document in result_cursor:
        result.append(json_util.loads(json_util.dumps(document)))
    if not result:
        raise HTTPException(status_code=404, detail="No recipes found")
    serialized_recipes = json.loads(json.dumps(result, default=str))
    return JSONResponse(content=serialized_recipes)


@router.get("/{recipe_id}")
async def get_one_recipe(recipe_id: str):
    try:
        recipe = await dao.get_recipe_by_id(recipe_id)
        if recipe is None:
            raise HTTPException(
                status_code=404,
                detail=f"Recipe with id {recipe_id} not found"
            )
        await dao.update_recipe_view(recipe_id)
        serialized_recipes = json.loads(json.dumps(recipe, default=str))
        return JSONResponse(content=serialized_recipes), 200
    except HTTPException as e:
        raise e
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/")
async def register_recipe(recipe: RecipeCreate):
    dao = RecipeDao()
    try:
        result = await dao.register_recipe(recipe)
        if result is None:
            raise HTTPException(
                status_code=500, detail="Failed to insert recipe")
        return {"recipe_id": result['recipe_id']}, 200
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


@router.post("/many", response_model=RecipeCreate, status_code=201, responses=common_responses)
async def register_recipes(recipes: List[RecipeCreate]):
    dao = RecipeDao()
    response = await dao.register_recipes(recipes)
    return HTTPException(status_code=200, detail=f'{response}')


@router.delete("/{recipe_id}")
async def delete_recipe(recipe_id: str):
    result = await dao.delete_one_recipe(recipe_id)
    if result == 1:
        return {"msg": "삭제 성공"}, 204
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Recipe with id {recipe_id} not found"
        )


@router.delete("/")
async def delete_all_recipe():
    result = await dao.delete_all_recipe()
    if result == 1:
        return {"msg": "삭제 성공"}, 204
    else:
        raise HTTPException(
            status_code=404,
            detail=f"Can't delete recipes"
        )


@router.patch("/{recipe_id}")
async def update_recipe(recipe_id: str, updated_recipe: RecipeBase):
    try:
        updated_document = await dao.update_recipe(recipe_id, updated_recipe)
        updated_document_dict = updated_document.copy()
        updated_document_dict.pop("_id")  # ObjectId 필드 삭제
        return JSONResponse(content=updated_document_dict)
    except HTTPException as e:
        raise HTTPException(
            status_code=e.status_code,
            detail=str(e.detail)
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.patch("/{recipe_id}/like")
async def update_like(recipe_id: str):
    try:
        recipe = await dao.get_recipe_by_id(recipe_id)
        if recipe is None:
            raise HTTPException(
                status_code=404,
                detail=f"Recipe with id {recipe_id} not found"
            )
        await dao.update_recipe_like(recipe_id)
        serialized_recipe = json.loads(json.dumps(recipe, default=str))
        return serialized_recipe

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
