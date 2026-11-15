"""
Dimension Library router for saving recurring company tolerances, standard hole bores,
and recurring stock parameters.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.api.database import get_db
from apps.api.models import DimensionLibraryItem, User, AuditLog
from apps.api.auth.dependencies import get_current_user, require_permission
from apps.api.auth.rbac import Permission

router = APIRouter(prefix="/dimension-library", tags=["Dimension Library & Recurring Standards"])


class LibraryItemCreateRequest(BaseModel):
    category: str = Field(description="Category: hole, thread, boss, slot, tolerance, plate_thickness")
    name: str = Field(min_length=2, max_length=100)
    standard_value: float
    tolerance_plus: float = 0.0
    tolerance_minus: float = 0.0
    unit: str = "mm"
    notes: Optional[str] = None


class LibraryItemResponse(BaseModel):
    id: str
    category: str
    name: str
    standard_value: float
    tolerance_plus: float
    tolerance_minus: float
    unit: str
    notes: Optional[str] = None
    created_at: str


@router.get("", response_model=List[LibraryItemResponse])
async def list_library_items(
    category: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve recurring company standard dimensions and tolerances."""
    query = select(DimensionLibraryItem).where(DimensionLibraryItem.org_id == current_user.org_id)
    if category:
        query = query.where(DimensionLibraryItem.category == category)

    res = await db.execute(query)
    items = res.scalars().all()
    return [
        LibraryItemResponse(
            id=item.id,
            category=item.category,
            name=item.name,
            standard_value=item.standard_value,
            tolerance_plus=item.tolerance_plus,
            tolerance_minus=item.tolerance_minus,
            unit=item.unit,
            notes=item.notes,
            created_at=item.created_at.isoformat(),
        )
        for item in items
    ]


@router.post("", response_model=LibraryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_library_item(
    payload: LibraryItemCreateRequest,
    current_user: User = Depends(require_permission(Permission.ORG_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    """Add a recurring company standard part, tolerance, or thread size."""
    item = DimensionLibraryItem(
        org_id=current_user.org_id,
        category=payload.category,
        name=payload.name,
        standard_value=payload.standard_value,
        tolerance_plus=payload.tolerance_plus,
        tolerance_minus=payload.tolerance_minus,
        unit=payload.unit,
        notes=payload.notes,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)

    return LibraryItemResponse(
        id=item.id,
        category=item.category,
        name=item.name,
        standard_value=item.standard_value,
        tolerance_plus=item.tolerance_plus,
        tolerance_minus=item.tolerance_minus,
        unit=item.unit,
        notes=item.notes,
        created_at=item.created_at.isoformat(),
    )


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_library_item(
    item_id: str,
    current_user: User = Depends(require_permission(Permission.ORG_UPDATE)),
    db: AsyncSession = Depends(get_db),
):
    """Remove a standard dimension from the organization library."""
    res = await db.execute(
        select(DimensionLibraryItem).where(
            DimensionLibraryItem.id == item_id,
            DimensionLibraryItem.org_id == current_user.org_id,
        )
    )
    item = res.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="Library item not found")

    await db.delete(item)
    await db.commit()
