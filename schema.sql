CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS contracts (
    id INTEGER PRIMARY KEY,
    client_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status TEXT NOT NULL,
    warranty_start_rule TEXT NOT NULL,
    warranty_duration_months INTEGER NOT NULL,
    warranty_options JSON NOT NULL,
    out_of_warranty_options JSON NOT NULL,
    FOREIGN KEY (client_id) REFERENCES clients(id)
);

CREATE TABLE IF NOT EXISTS appendices (
    id INTEGER PRIMARY KEY,
    contract_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status TEXT NOT NULL,
    FOREIGN KEY (contract_id) REFERENCES contracts(id)
);

CREATE TABLE IF NOT EXISTS contract_lines (
    id INTEGER PRIMARY KEY,
    appendix_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    status TEXT NOT NULL,
    warranty_start_rule TEXT NOT NULL,
    warranty_duration_months INTEGER NOT NULL,
    warranty_options JSON NOT NULL,
    out_of_warranty_options JSON NOT NULL,
    required_inputs JSON NOT NULL,
    FOREIGN KEY (appendix_id) REFERENCES appendices(id),
    FOREIGN KEY (product_id) REFERENCES products(id),
    UNIQUE (appendix_id, product_id)
);

CREATE TABLE IF NOT EXISTS kpi_expected (
    id INTEGER PRIMARY KEY,
    contract_id INTEGER NOT NULL,
    kpi_type TEXT NOT NULL,
    date DATE NOT NULL,
    expected_value INTEGER NOT NULL,
    FOREIGN KEY (contract_id) REFERENCES contracts(id)
);

CREATE TABLE IF NOT EXISTS kpi_actual (
    id INTEGER PRIMARY KEY,
    contract_id INTEGER NOT NULL,
    kpi_type TEXT NOT NULL,
    date DATE NOT NULL,
    actual_value INTEGER NOT NULL,
    FOREIGN KEY (contract_id) REFERENCES contracts(id)
);
