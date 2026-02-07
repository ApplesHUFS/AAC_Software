"""인증 API 엔드포인트"""

from fastapi import APIRouter, HTTPException, status

from app.api.deps import UserServiceDep
from app.core.response import success_response
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ProfileUpdateRequest,
)

router = APIRouter()


@router.get("/check-id/{user_id}")
async def check_user_id(
    user_id: str,
    user_service: UserServiceDep,
):
    """아이디 중복 확인"""
    exists = await user_service.check_user_exists(user_id)

    return success_response(
        data={
            "userId": user_id,
            "available": not exists,
        },
        message="사용 가능한 아이디입니다." if not exists else "이미 사용 중인 아이디입니다.",
    )


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    user_service: UserServiceDep,
):
    """회원가입"""
    result = await user_service.register_user(
        user_id=request.user_id,
        name=request.name,
        age=request.age,
        gender=request.gender,
        disability_type=request.disability_type,
        communication_characteristics=request.communication_characteristics,
        interesting_topics=request.interesting_topics,
        password=request.password,
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message,
        )

    return success_response(
        data={
            "userId": result.user_id,
            "name": request.name,
            "status": "created",
        },
        message=result.message,
    )


@router.post("/login")
async def login(
    request: LoginRequest,
    user_service: UserServiceDep,
):
    """로그인"""
    result = await user_service.authenticate_user(
        user_id=request.user_id,
        password=request.password,
    )

    if not result.authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.message,
        )

    return success_response(
        data={
            "userId": request.user_id,
            "authenticated": True,
            "user": result.user_info,
        },
        message=result.message,
    )


@router.get("/profile/{user_id}")
async def get_profile(
    user_id: str,
    user_service: UserServiceDep,
):
    """프로필 조회"""
    result = await user_service.get_user_info(user_id)

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=result.message,
        )

    return success_response(
        data={"userId": user_id, **result.user},
        message=result.message,
    )


@router.put("/profile/{user_id}")
async def update_profile(
    user_id: str,
    request: ProfileUpdateRequest,
    user_service: UserServiceDep,
):
    """프로필 업데이트"""
    updates = request.model_dump(exclude_none=True, by_alias=True)

    result = await user_service.update_user_persona(
        user_id=user_id,
        updates=updates,
    )

    if not result.success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.message,
        )

    return success_response(
        data={
            "updatedFields": result.updated_fields,
        },
        message=result.message,
    )
