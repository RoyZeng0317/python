from fastapi import APIRouter

router = APIRouter()

@router.get("/{user_id}")
def get_usr(usr_id: int):
    return [{"id": usr_id, "name": "Alice"}]
