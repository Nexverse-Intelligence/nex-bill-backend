# Standard library

# Third-party
from fastapi import (
    APIRouter,
    Depends,
    File,
    UploadFile,
)

# Local
from app.api.deps import get_brand_service, require_admin
from app.schemas import (
    BrandSettingsResponse,
    BrandSettingsUpdate,
)
from app.services import BrandService

router = APIRouter(prefix="/brand", tags=["Branding"])


@router.get(
    "/",
    response_model=BrandSettingsResponse,
)
def get_brand_settings(
    service: BrandService = Depends(get_brand_service),
) -> BrandSettingsResponse:
    """
    Return current workspace branding config.
    Accessible to all authenticated users.
    """
    return service.get_brand()


@router.patch(
    "/",
    response_model=BrandSettingsResponse,
    dependencies=[Depends(require_admin)],
)
def update_brand_settings(
    payload: BrandSettingsUpdate,
    service: BrandService = Depends(get_brand_service),
) -> BrandSettingsResponse:
    """
    Update workspace branding. Admin only.
    Only provided fields are updated.
    """
    return service.update_brand(payload)


@router.post(
    "/logo",
    response_model=BrandSettingsResponse,
    dependencies=[Depends(require_admin)],
)
async def upload_logo(
    file: UploadFile = File(...),
    service: BrandService = Depends(get_brand_service),
) -> BrandSettingsResponse:
    """
    Upload a new brand logo. Admin only.
    Accepts PNG, JPG, SVG. Max size: 2MB.
    """
    content = await file.read()
    return service.upload_logo(
        file_bytes=content,
        content_type=file.content_type or "image/png",
    )


@router.post(
    "/reset",
    response_model=BrandSettingsResponse,
    dependencies=[Depends(require_admin)],
)
def reset_brand(
    service: BrandService = Depends(get_brand_service),
) -> BrandSettingsResponse:
    """
    Reset all branding to NexBill defaults.
    Admin only.
    """
    return service.reset_to_defaults()
