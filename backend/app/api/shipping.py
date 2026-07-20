from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.shipping_qa import get_delivery_estimates

router = APIRouter(tags=["Shipping"])


class DeliveryEstimateRequest(BaseModel):
    postal_code: str = Field(pattern=r"^\d{5}(?:-\d{4})?$")
    country: str = Field(default="US", min_length=2, max_length=2)
    item_ids: list[str] = Field(min_length=1, max_length=3)


@router.post("/shipping/estimates")
async def delivery_estimates(payload: DeliveryEstimateRequest) -> dict:
    try:
        return await get_delivery_estimates(
            payload.item_ids,
            payload.postal_code,
            payload.country,
        )
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
    except RuntimeError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"eBay delivery estimate failed: {type(error).__name__}",
        ) from error
