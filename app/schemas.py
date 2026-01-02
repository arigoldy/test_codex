from datetime import date
from typing import List, Optional

from pydantic import BaseModel, Field


class ContractBase(BaseModel):
    client_id: int
    name: str
    start_date: date
    end_date: date
    status: str
    warranty_start_rule: str
    warranty_duration_months: int
    warranty_options: List[str]
    out_of_warranty_options: List[str]


class ContractCreate(ContractBase):
    pass


class ContractResponse(ContractBase):
    id: int

    class Config:
        from_attributes = True


class AppendixBase(BaseModel):
    contract_id: int
    name: str
    start_date: date
    end_date: date
    status: str


class AppendixCreate(AppendixBase):
    pass


class AppendixResponse(AppendixBase):
    id: int

    class Config:
        from_attributes = True


class ContractLineBase(BaseModel):
    appendix_id: int
    product_id: int
    start_date: date
    end_date: date
    status: str
    warranty_start_rule: str
    warranty_duration_months: int
    warranty_options: List[str]
    out_of_warranty_options: List[str]
    required_inputs: List[str]


class ContractLineCreate(ContractLineBase):
    pass


class ContractLineResponse(ContractLineBase):
    id: int

    class Config:
        from_attributes = True


class KPIExpectedBase(BaseModel):
    contract_id: int
    kpi_type: str
    date: date
    expected_value: int


class KPIExpectedCreate(KPIExpectedBase):
    pass


class KPIExpectedResponse(KPIExpectedBase):
    id: int

    class Config:
        from_attributes = True


class KPIActualBase(BaseModel):
    contract_id: int
    kpi_type: str
    date: date
    actual_value: int


class KPIActualCreate(KPIActualBase):
    pass


class KPIActualResponse(KPIActualBase):
    id: int

    class Config:
        from_attributes = True


class DecisionInputs(BaseModel):
    serial_number: Optional[str] = None
    purchase_date: Optional[date] = None
    activation_date: Optional[date] = None
    manufacture_date: Optional[date] = None
    proof_provided: Optional[bool] = None
    country: Optional[str] = None
    channel: Optional[str] = None


class DecisionRequest(BaseModel):
    contract_id: Optional[int] = None
    appendix_id: Optional[int] = None
    product_id: int
    event_date: date
    inputs: DecisionInputs


class DecisionResponse(BaseModel):
    eligible: bool
    in_warranty: Optional[bool]
    required_inputs: List[str] = Field(default_factory=list)
    allowed_resolutions: List[str] = Field(default_factory=list)
    reason_codes: List[str] = Field(default_factory=list)
    resolved_contract_id: Optional[int]
    resolved_appendix_id: Optional[int]
    resolved_line_id: Optional[int]
    warranty_end_date: Optional[date]


class KPISeriesPoint(BaseModel):
    date: date
    expected: int
    actual: int
    expected_cumulative: int
    actual_cumulative: int
    delta_percent: float
    alert_level: str
    spike: bool


class KPISeries(BaseModel):
    kpi_type: str
    series: List[KPISeriesPoint]


class KPIAlert(BaseModel):
    kpi_type: str
    date: date
    alert_level: str
    delta_percent: float
    spike: bool
