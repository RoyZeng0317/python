from fastapi import APIRouter

# created a router, and setting prefix
router = APIRouter(prefix="/items", tags["item API"])

# asking URL: GET /items/
@router.get("/")
def get_all_items():
    return {"msg": "get all item list"}

# asking URL: GET /items/123
@router.get("/{item_id}")
def get_a_item(item_id: int):
    return {"item_id": item_id, "name": "iPhone"}