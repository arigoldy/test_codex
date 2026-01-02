from sqlalchemy import Column, Integer, String, Date, ForeignKey, JSON, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database import Base


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    contracts = relationship("Contract", back_populates="client")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)

    lines = relationship("ContractLine", back_populates="product")


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    warranty_start_rule = Column(String, nullable=False)
    warranty_duration_months = Column(Integer, nullable=False)
    warranty_options = Column(JSON, nullable=False)
    out_of_warranty_options = Column(JSON, nullable=False)

    client = relationship("Client", back_populates="contracts")
    appendices = relationship("Appendix", back_populates="contract")


class Appendix(Base):
    __tablename__ = "appendices"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)

    contract = relationship("Contract", back_populates="appendices")
    lines = relationship("ContractLine", back_populates="appendix")


class ContractLine(Base):
    __tablename__ = "contract_lines"

    id = Column(Integer, primary_key=True, index=True)
    appendix_id = Column(Integer, ForeignKey("appendices.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    status = Column(String, nullable=False)
    warranty_start_rule = Column(String, nullable=False)
    warranty_duration_months = Column(Integer, nullable=False)
    warranty_options = Column(JSON, nullable=False)
    out_of_warranty_options = Column(JSON, nullable=False)
    required_inputs = Column(JSON, nullable=False)

    appendix = relationship("Appendix", back_populates="lines")
    product = relationship("Product", back_populates="lines")

    __table_args__ = (UniqueConstraint("appendix_id", "product_id", name="uq_appendix_product"),)


class KPIExpected(Base):
    __tablename__ = "kpi_expected"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    kpi_type = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    expected_value = Column(Integer, nullable=False)


class KPIActual(Base):
    __tablename__ = "kpi_actual"

    id = Column(Integer, primary_key=True, index=True)
    contract_id = Column(Integer, ForeignKey("contracts.id"), nullable=False)
    kpi_type = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    actual_value = Column(Integer, nullable=False)
