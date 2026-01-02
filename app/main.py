from datetime import date
from typing import Dict, List

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, SessionLocal, engine
from app.seed import seed_data
from app.services import KPI_TYPES, build_kpi_series, decide_coverage

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Service Contract Management Demo")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.on_event("startup")
def startup_seed() -> None:
    db = SessionLocal()
    try:
        seed_data(db)
    finally:
        db.close()


@app.post("/contracts", response_model=schemas.ContractResponse)
def create_contract(payload: schemas.ContractCreate, db: Session = Depends(get_db)):
    client = db.query(models.Client).filter(models.Client.id == payload.client_id).first()
    if client is None:
        raise HTTPException(status_code=400, detail="client_id not found")

    contract = models.Contract(**payload.model_dump())
    db.add(contract)
    db.commit()
    db.refresh(contract)
    return contract


@app.post("/appendices", response_model=schemas.AppendixResponse)
def create_appendix(payload: schemas.AppendixCreate, db: Session = Depends(get_db)):
    contract = db.query(models.Contract).filter(models.Contract.id == payload.contract_id).first()
    if contract is None:
        raise HTTPException(status_code=400, detail="contract_id not found")

    appendix = models.Appendix(**payload.model_dump())
    db.add(appendix)
    db.commit()
    db.refresh(appendix)
    return appendix


@app.post("/contract-lines", response_model=schemas.ContractLineResponse)
def create_contract_line(payload: schemas.ContractLineCreate, db: Session = Depends(get_db)):
    appendix = db.query(models.Appendix).filter(models.Appendix.id == payload.appendix_id).first()
    if appendix is None:
        raise HTTPException(status_code=400, detail="appendix_id not found")

    product = db.query(models.Product).filter(models.Product.id == payload.product_id).first()
    if product is None:
        raise HTTPException(status_code=400, detail="product_id not found")

    line = models.ContractLine(**payload.model_dump())
    db.add(line)
    db.commit()
    db.refresh(line)
    return line


@app.post("/kpi/expected", response_model=schemas.KPIExpectedResponse)
def create_kpi_expected(payload: schemas.KPIExpectedCreate, db: Session = Depends(get_db)):
    if payload.kpi_type not in KPI_TYPES:
        raise HTTPException(status_code=400, detail="invalid kpi_type")

    contract = db.query(models.Contract).filter(models.Contract.id == payload.contract_id).first()
    if contract is None:
        raise HTTPException(status_code=400, detail="contract_id not found")

    row = models.KPIExpected(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.post("/kpi/actual", response_model=schemas.KPIActualResponse)
def create_kpi_actual(payload: schemas.KPIActualCreate, db: Session = Depends(get_db)):
    if payload.kpi_type not in KPI_TYPES:
        raise HTTPException(status_code=400, detail="invalid kpi_type")

    contract = db.query(models.Contract).filter(models.Contract.id == payload.contract_id).first()
    if contract is None:
        raise HTTPException(status_code=400, detail="contract_id not found")

    row = models.KPIActual(**payload.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@app.post("/decisions/coverage", response_model=schemas.DecisionResponse)
def coverage_decision(payload: schemas.DecisionRequest, db: Session = Depends(get_db)):
    inputs = payload.inputs.model_dump()
    decision = decide_coverage(
        db=db,
        contract_id=payload.contract_id,
        appendix_id=payload.appendix_id,
        product_id=payload.product_id,
        event_date=payload.event_date,
        inputs=inputs,
    )
    return decision


@app.get("/kpi/contracts/{contract_id}/series", response_model=List[schemas.KPISeries])
def kpi_series(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if contract is None:
        raise HTTPException(status_code=404, detail="contract not found")

    results: List[schemas.KPISeries] = []
    for kpi_type in sorted(KPI_TYPES):
        expected_rows = (
            db.query(models.KPIExpected)
            .filter(
                models.KPIExpected.contract_id == contract_id,
                models.KPIExpected.kpi_type == kpi_type,
            )
            .all()
        )
        actual_rows = (
            db.query(models.KPIActual)
            .filter(
                models.KPIActual.contract_id == contract_id,
                models.KPIActual.kpi_type == kpi_type,
            )
            .all()
        )
        series = build_kpi_series(expected_rows, actual_rows)
        results.append(schemas.KPISeries(kpi_type=kpi_type, series=series))

    return results


@app.get("/kpi/contracts/{contract_id}/alerts", response_model=List[schemas.KPIAlert])
def kpi_alerts(contract_id: int, db: Session = Depends(get_db)):
    contract = db.query(models.Contract).filter(models.Contract.id == contract_id).first()
    if contract is None:
        raise HTTPException(status_code=404, detail="contract not found")

    alerts: List[schemas.KPIAlert] = []
    for kpi_type in sorted(KPI_TYPES):
        expected_rows = (
            db.query(models.KPIExpected)
            .filter(
                models.KPIExpected.contract_id == contract_id,
                models.KPIExpected.kpi_type == kpi_type,
            )
            .all()
        )
        actual_rows = (
            db.query(models.KPIActual)
            .filter(
                models.KPIActual.contract_id == contract_id,
                models.KPIActual.kpi_type == kpi_type,
            )
            .all()
        )
        series = build_kpi_series(expected_rows, actual_rows)
        for point in series:
            if point["alert_level"] != "GREEN" or point["spike"]:
                alerts.append(
                    schemas.KPIAlert(
                        kpi_type=kpi_type,
                        date=point["date"],
                        alert_level=point["alert_level"],
                        delta_percent=point["delta_percent"],
                        spike=point["spike"],
                    )
                )

    return alerts


@app.get("/health")
def healthcheck() -> Dict[str, str]:
    return {"status": "ok", "date": date.today().isoformat()}
