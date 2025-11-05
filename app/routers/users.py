from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from typing import Optional

from app.models.schemas import (
    UserCreateRequest,
    UserResponse,
    SuccessResponse,
    ErrorResponse
)
from app.database.users_repo import UsersRepository


router = APIRouter(
    prefix="/api/users",
    tags=["users"]
)


@router.post("/register", response_model=UserResponse, status_code=201)
async def register_user(user_request: UserCreateRequest):
    """
    Register a new user.

    Creates a new user account with the provided email and name.

    Args:
        user_request: User registration details (email and name)

    Returns:
        UserResponse with user details

    Raises:
        HTTPException: If email already exists or registration fails
    """
    try:
        users_repo = UsersRepository()

        # Check if email already exists
        existing_user = users_repo.get_by_email(email=user_request.email)
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail=f"User with email '{user_request.email}' already exists"
            )

        # Create user
        response = users_repo.create_user(
            email=user_request.email,
            name=user_request.name
        )

        if response and response.data:
            user_data = response.data[0] if isinstance(response.data, list) else response.data
            return UserResponse(
                user_id=user_data.get('user_id'),
                email=user_data.get('email'),
                name=user_data.get('name'),
                created_at=user_data.get('created_at')
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="Failed to create user account"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error creating user: {str(e)}"
        )


@router.post("/login", response_model=UserResponse)
async def login_user(email: Optional[str] = None, name: Optional[str] = None):
    """
    Login user by email or name.

    Authenticates a user using either email or name.
    At least one parameter must be provided.

    Args:
        email: User's email address
        name: User's name

    Returns:
        UserResponse with user details

    Raises:
        HTTPException: If user not found or no credentials provided
    """
    try:
        if not email and not name:
            raise HTTPException(
                status_code=400,
                detail="Either email or name must be provided"
            )

        users_repo = UsersRepository()
        user_data = None

        # Try email first if provided
        if email:
            user_data = users_repo.get_by_email(email=email)

        # If email didn't work or wasn't provided, try name
        if not user_data and name:
            user_data = users_repo.get_by_name(name=name)

        if not user_data:
            raise HTTPException(
                status_code=404,
                detail=f"User not found with provided credentials"
            )

        return UserResponse(
            user_id=user_data.get('user_id'),
            email=user_data.get('email'),
            name=user_data.get('name'),
            created_at=user_data.get('created_at')
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during login: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: str):
    """
    Get user details by user ID.

    Args:
        user_id: ID of the user

    Returns:
        UserResponse with user details

    Raises:
        HTTPException: If user not found
    """
    try:
        users_repo = UsersRepository()
        user_data = users_repo.get_by_id(user_id=user_id)

        if not user_data:
            raise HTTPException(
                status_code=404,
                detail=f"User with ID '{user_id}' not found"
            )

        return UserResponse(
            user_id=user_data.get('user_id'),
            email=user_data.get('email'),
            name=user_data.get('name'),
            created_at=user_data.get('created_at')
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user: {str(e)}"
        )


@router.get("/email/{email}", response_model=UserResponse)
async def get_user_by_email(email: str):
    """
    Get user details by email.

    Args:
        email: Email of the user

    Returns:
        UserResponse with user details

    Raises:
        HTTPException: If user not found
    """
    try:
        users_repo = UsersRepository()
        user_data = users_repo.get_by_email(email=email)

        if not user_data:
            raise HTTPException(
                status_code=404,
                detail=f"User with email '{email}' not found"
            )

        return UserResponse(
            user_id=user_data.get('user_id'),
            email=user_data.get('email'),
            name=user_data.get('name'),
            created_at=user_data.get('created_at')
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user: {str(e)}"
        )


@router.get("/name/{name}", response_model=UserResponse)
async def get_user_by_name(name: str):
    """
    Get user details by name.

    Args:
        name: Name of the user

    Returns:
        UserResponse with user details

    Raises:
        HTTPException: If user not found
    """
    try:
        users_repo = UsersRepository()
        user_data = users_repo.get_by_name(name=name)

        if not user_data:
            raise HTTPException(
                status_code=404,
                detail=f"User with name '{name}' not found"
            )

        return UserResponse(
            user_id=user_data.get('user_id'),
            email=user_data.get('email'),
            name=user_data.get('name'),
            created_at=user_data.get('created_at')
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving user: {str(e)}"
        )
