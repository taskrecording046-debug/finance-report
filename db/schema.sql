-- Finance reporting schema.
-- Line items belong to departments; the report endpoint aggregates them
-- into per-department and grand totals.
--
-- Amounts are stored as NUMERIC (exact decimal) in the database — that is
-- the correct choice. The bug in this tutorial is introduced later, in the
-- application layer, when these values are pulled into Python floats.

DROP TABLE IF EXISTS line_items;
DROP TABLE IF EXISTS departments;

CREATE TABLE departments (
  id   SERIAL PRIMARY KEY,
  code TEXT NOT NULL UNIQUE,   -- e.g. 'DEPT-OPS', 'DEPT-ENG'
  name TEXT NOT NULL
);

CREATE TABLE line_items (
  id            SERIAL PRIMARY KEY,
  department_id INTEGER NOT NULL REFERENCES departments(id),
  reference     TEXT NOT NULL,            -- e.g. 'INV-2026-0001'
  category      TEXT NOT NULL,            -- e.g. 'cloud', 'travel'
  -- Net amount and tax rate, both exact decimals.
  net_amount    NUMERIC(12, 2) NOT NULL,  -- e.g. 0.10, 19.99
  tax_rate      NUMERIC(5, 4) NOT NULL DEFAULT 0.1000, -- e.g. 0.1000 = 10%
  booked_at     DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE INDEX idx_line_items_department_id ON line_items(department_id);
