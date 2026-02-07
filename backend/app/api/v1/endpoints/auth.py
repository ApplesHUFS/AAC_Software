"""인증 API 엔드포인트"""

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.api.deps import UserServiceDep, CurrentUserDep
from app.core.response import success_response
from app.core.security import TokenService, get_token_service
from app.core.rate_limit import limiter, RATE_LIMIT_LOGIN
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    ProfileUpdateRequest,
    TokenResponse,
    RefreshTokenRequest,
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
@limiter.limit(RATE_LIMIT_LOGIN)
async def login(
    request: Request,
    login_data: LoginRequest,
    user_service: UserServiceDep,
    token_service: TokenService = Depends(get_token_service),
):
    """로그인 - JWT 토큰 발급 (Rate Limit: 5/minute)"""
    result = await user_service.authenticate_user(
        user_id=login_data.user_id,
        password=login_data.password,
    )

    if not result.authenticated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=result.message,
        )

    access_token = token_service.create_access_token(login_data.user_id)
    refresh_token = token_service.create_refresh_token(login_data.user_id)

    return success_response(
        data={
            "userId": login_data.user_id,
            "authenticated": True,
            "user": result.user_info,
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "tokenType": "bearer",
        },
        message=result.message,
    )


@router.post("/refresh")
async def refresh_token(
    request: RefreshTokenRequest,
    token_service: TokenService = Depends(get_token_service),
):
    """리프레시 토큰으로 새 액세스 토큰 발급"""
    user_id = token_service.verify_token(request.refresh_token, token_type="refresh")

    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 리프레시 토큰입니다.",
        )

    new_access_token = token_service.create_access_token(user_id)

    return success_response(
        data={
            "accessToken": new_access_token,
            "tokenType": "bearer",
        },
        message="토큰이 갱신되었습니다.",
    )


@router.get("/profile/{user_id}")
async def get_profile(
    user_id: str,
    current_user: CurrentUserDep,
    user_service: UserServiceDep,
):
    """프로필 조회 (인증 필요)"""
    # 본인 프로필만 조회 가능
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 프로필을 조회할 수 없습니다.",
        )

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


@router.get("/me")
async def get_my_profile(
    current_user: CurrentUserDep,
):
    """내 프로필 조회 (인증 필요)"""
    return success_response(
        data={"userId": current_user.user_id, **current_user.to_response_dict()},
        message="프로필 조회에 성공했습니다.",
    )


@router.put("/profile/{user_id}")
async def update_profile(
    user_id: str,
    request: ProfileUpdateRequest,
    current_user: CurrentUserDep,
    user_service: UserServiceDep,
):
    """프로필 업데이트 (인증 필요)"""
    # 본인 프로필만 수정 가능
    if current_user.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="다른 사용자의 프로필을 수정할 수 없습니다.",
        )

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
