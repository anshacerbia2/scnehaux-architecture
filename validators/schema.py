from pydantic import BaseModel, Field, field_validator, ValidationInfo
from typing import Optional, List, Union, Literal
from datetime import date
import re

class ExceptionInfo(BaseModel):
    approved_by: str
    expiry_date: date
    risk_classification: str
    exception_reason: str

class DocMeta(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    owner: Optional[str] = None
    version: Optional[str] = None
    status: Optional[Literal['draft', 'proposed', 'review', 'approved', 'rejected', 'accepted', 'deprecated', 'superseded', 'adopted', 'trial', 'assessed', 'hold']] = None
    classification: Optional[Literal['public', 'internal', 'confidential', 'restricted']] = None
    review_cycle_days: Optional[int] = None
    last_reviewed: Optional[date] = None
    
    # Exception/Waiver fields
    exception_info: Optional[ExceptionInfo] = None
    
    # Traceability links
    parent_pad: Optional[Union[str, List[str]]] = None
    parent_sad: Optional[Union[str, List[str]]] = None
    governed_by: Optional[Union[str, List[str]]] = None
    fulfilled_by: Optional[Union[str, List[str]]] = None
    adr_type: Optional[str] = None

    @field_validator('version')
    @classmethod
    def validate_semver(cls, v: Optional[str]) -> Optional[str]:
        if v is not None:
            v_str = str(v)
            if not re.match(r'^\d+\.\d+\.\d+$', v_str):
                raise ValueError(f"Version '{v}' is not in valid semver format (X.Y.Z).")
            return v_str
        return v

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: str, info: ValidationInfo) -> str:
        # We will inject allowed_statuses from the context dynamically in the linter if needed, 
        # but for schema we can just enforce string. 
        # If we need dynamic context, we can handle it at the validator level.
        return str(v).lower()
