from datetime import date, timedelta

from sqlalchemy.orm import Session

from app import models


def seed_data(db: Session) -> None:
    if db.query(models.Client).first():
        return

    client = models.Client(name="Acme Motors")
    db.add(client)
    db.flush()

    product1 = models.Product(name="Hydraulic Pump")
    product2 = models.Product(name="Control Module")
    db.add_all([product1, product2])
    db.flush()

    contract = models.Contract(
        client_id=client.id,
        name="After-sales Warranty 2024",
        start_date=date.today() - timedelta(days=30),
        end_date=date.today() + timedelta(days=365),
        status="active",
        warranty_start_rule="contract_start",
        warranty_duration_months=12,
        warranty_options=["repair", "replace"],
        out_of_warranty_options=["paid_repair", "refund"],
    )
    db.add(contract)
    db.flush()

    appendix = models.Appendix(
        contract_id=contract.id,
        name="Industrial Equipment",
        start_date=contract.start_date,
        end_date=contract.end_date,
        status="active",
    )
    db.add(appendix)
    db.flush()

    line1 = models.ContractLine(
        appendix_id=appendix.id,
        product_id=product1.id,
        start_date=appendix.start_date,
        end_date=appendix.end_date,
        status="active",
        warranty_start_rule="purchase_date",
        warranty_duration_months=18,
        warranty_options=["repair", "replace", "parts_ship"],
        out_of_warranty_options=["paid_repair", "parts_sale"],
        required_inputs=["serial_number", "purchase_date", "proof_provided"],
    )

    line2 = models.ContractLine(
        appendix_id=appendix.id,
        product_id=product2.id,
        start_date=appendix.start_date,
        end_date=appendix.end_date,
        status="active",
        warranty_start_rule="activation_date",
        warranty_duration_months=24,
        warranty_options=["repair", "replace"],
        out_of_warranty_options=["paid_repair"],
        required_inputs=["serial_number", "activation_date"],
    )

    db.add_all([line1, line2])

    start_day = date.today() - timedelta(days=7)
    for i in range(8):
        day = start_day + timedelta(days=i)
        db.add(
            models.KPIExpected(
                contract_id=contract.id,
                kpi_type="repairs",
                date=day,
                expected_value=5,
            )
        )
        db.add(
            models.KPIActual(
                contract_id=contract.id,
                kpi_type="repairs",
                date=day,
                actual_value=4 + (i % 3),
            )
        )

        db.add(
            models.KPIExpected(
                contract_id=contract.id,
                kpi_type="refunds",
                date=day,
                expected_value=2,
            )
        )
        db.add(
            models.KPIActual(
                contract_id=contract.id,
                kpi_type="refunds",
                date=day,
                actual_value=1 if i % 2 == 0 else 3,
            )
        )

    db.commit()
