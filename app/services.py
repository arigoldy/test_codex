from datetime import date
from typing import Dict, List, Optional, Tuple

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session

from app import models

KPI_TYPES = {
    "repairs",
    "refunds",
    "replacements",
    "parts_shipments",
    "paid_repairs",
    "parts_sales",
}


def add_months(start_date: date, months: int) -> date:
    return start_date + relativedelta(months=months)


def resolve_contract_context(
    db: Session, contract_id: Optional[int], appendix_id: Optional[int]
) -> Tuple[Optional[models.Contract], Optional[models.Appendix], List[str]]:
    reasons: List[str] = []
    contract = None
    appendix = None

    if appendix_id is not None:
        appendix = db.query(models.Appendix).filter(models.Appendix.id == appendix_id).first()
        if appendix is None:
            reasons.append("appendix_not_found")
            return None, None, reasons
        contract = appendix.contract
    elif contract_id is not None:
        contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
        if contract is None:
            reasons.append("contract_not_found")
            return None, None, reasons
    else:
        reasons.append("missing_contract_or_appendix")

    return contract, appendix, reasons


def select_line(
    db: Session,
    contract: models.Contract,
    appendix: Optional[models.Appendix],
    product_id: int,
    event_date: date,
) -> Tuple[Optional[models.Appendix], Optional[models.ContractLine], List[str]]:
    reasons: List[str] = []
    appendices = [appendix] if appendix is not None else contract.appendices

    active_appendices = [
        item
        for item in appendices
        if item is not None
        and item.status == "active"
        and item.start_date <= event_date <= item.end_date
    ]

    for app in active_appendices:
        for line in app.lines:
            if (
                line.product_id == product_id
                and line.status == "active"
                and line.start_date <= event_date <= line.end_date
            ):
                if not (contract.start_date <= app.start_date <= line.start_date):
                    reasons.append("date_hierarchy_invalid")
                    continue
                if not (line.end_date <= app.end_date <= contract.end_date):
                    reasons.append("date_hierarchy_invalid")
                    continue
                return app, line, reasons

    reasons.append("no_active_line_for_product")
    return appendix, None, reasons


def required_inputs_missing(line: models.ContractLine, inputs: Dict[str, Optional[object]]) -> List[str]:
    missing = []
    for key in line.required_inputs:
        if inputs.get(key) is None:
            missing.append(key)
    return missing


def warranty_start_date(
    line: models.ContractLine,
    contract: models.Contract,
    inputs: Dict[str, Optional[object]],
) -> Tuple[Optional[date], List[str]]:
    missing = []
    rule = line.warranty_start_rule
    value = None

    if rule == "purchase_date":
        value = inputs.get("purchase_date")
        if value is None:
            missing.append("purchase_date")
    elif rule == "activation_date":
        value = inputs.get("activation_date")
        if value is None:
            missing.append("activation_date")
    elif rule == "manufacture_date":
        value = inputs.get("manufacture_date")
        if value is None:
            missing.append("manufacture_date")
    elif rule == "contract_start":
        value = contract.start_date
    else:
        missing.append("warranty_start_rule_invalid")

    return value, missing


def decide_coverage(
    db: Session,
    contract_id: Optional[int],
    appendix_id: Optional[int],
    product_id: int,
    event_date: date,
    inputs: Dict[str, Optional[object]],
) -> Dict[str, object]:
    reasons: List[str] = []
    required_inputs: List[str] = []

    contract, appendix, reasons = resolve_contract_context(db, contract_id, appendix_id)
    if contract is None:
        return {
            "eligible": False,
            "in_warranty": None,
            "required_inputs": [],
            "allowed_resolutions": [],
            "reason_codes": reasons,
            "resolved_contract_id": None,
            "resolved_appendix_id": None,
            "resolved_line_id": None,
            "warranty_end_date": None,
        }

    if contract.status != "active" or not (contract.start_date <= event_date <= contract.end_date):
        reasons.append("contract_inactive_or_outside_dates")
        return {
            "eligible": False,
            "in_warranty": None,
            "required_inputs": [],
            "allowed_resolutions": [],
            "reason_codes": reasons,
            "resolved_contract_id": contract.id,
            "resolved_appendix_id": None,
            "resolved_line_id": None,
            "warranty_end_date": None,
        }

    resolved_appendix, line, line_reasons = select_line(db, contract, appendix, product_id, event_date)
    reasons.extend(line_reasons)

    if line is None:
        return {
            "eligible": False,
            "in_warranty": None,
            "required_inputs": [],
            "allowed_resolutions": [],
            "reason_codes": reasons,
            "resolved_contract_id": contract.id,
            "resolved_appendix_id": resolved_appendix.id if resolved_appendix else None,
            "resolved_line_id": None,
            "warranty_end_date": None,
        }

    required_inputs = required_inputs_missing(line, inputs)
    start_date, rule_missing = warranty_start_date(line, contract, inputs)
    required_inputs.extend(rule_missing)

    if required_inputs:
        return {
            "eligible": False,
            "in_warranty": None,
            "required_inputs": sorted(set(required_inputs)),
            "allowed_resolutions": [],
            "reason_codes": reasons + ["missing_required_inputs"],
            "resolved_contract_id": contract.id,
            "resolved_appendix_id": resolved_appendix.id if resolved_appendix else None,
            "resolved_line_id": line.id,
            "warranty_end_date": None,
        }

    warranty_end = add_months(start_date, line.warranty_duration_months)
    in_warranty = event_date <= warranty_end

    options = line.warranty_options if in_warranty else line.out_of_warranty_options

    return {
        "eligible": True,
        "in_warranty": in_warranty,
        "required_inputs": [],
        "allowed_resolutions": options,
        "reason_codes": reasons,
        "resolved_contract_id": contract.id,
        "resolved_appendix_id": resolved_appendix.id if resolved_appendix else None,
        "resolved_line_id": line.id,
        "warranty_end_date": warranty_end,
    }


def build_kpi_series(
    expected_rows: List[models.KPIExpected], actual_rows: List[models.KPIActual]
) -> List[Dict[str, object]]:
    expected_map = {row.date: row.expected_value for row in expected_rows}
    actual_map = {row.date: row.actual_value for row in actual_rows}
    all_dates = sorted(set(expected_map.keys()) | set(actual_map.keys()))

    series = []
    expected_cumulative = 0
    actual_cumulative = 0

    for day in all_dates:
        expected_value = expected_map.get(day, 0)
        actual_value = actual_map.get(day, 0)
        expected_cumulative += expected_value
        actual_cumulative += actual_value

        if expected_value == 0:
            delta_percent = 0.0 if actual_value == 0 else 100.0
        else:
            delta_percent = ((actual_value - expected_value) / expected_value) * 100

        if abs(delta_percent) <= 5:
            alert_level = "GREEN"
        elif abs(delta_percent) <= 10:
            alert_level = "ORANGE"
        else:
            alert_level = "RED"

        spike = expected_value > 0 and actual_value > expected_value * 1.5

        series.append(
            {
                "date": day,
                "expected": expected_value,
                "actual": actual_value,
                "expected_cumulative": expected_cumulative,
                "actual_cumulative": actual_cumulative,
                "delta_percent": round(delta_percent, 2),
                "alert_level": alert_level,
                "spike": spike,
            }
        )

    return series
