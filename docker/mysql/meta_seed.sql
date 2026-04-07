USE meta;

CREATE TABLE IF NOT EXISTS table_info (
  id VARCHAR(64) PRIMARY KEY,
  name VARCHAR(128),
  role VARCHAR(32),
  description TEXT
);

CREATE TABLE IF NOT EXISTS column_info (
  id VARCHAR(64) PRIMARY KEY,
  name VARCHAR(128),
  type VARCHAR(64),
  `role` VARCHAR(32),
  examples JSON,
  description TEXT,
  alias JSON,
  table_id VARCHAR(64)
);

CREATE TABLE IF NOT EXISTS metric_info (
  id VARCHAR(64) PRIMARY KEY,
  name VARCHAR(128),
  description TEXT,
  relevant_columns JSON,
  alias JSON
);

CREATE TABLE IF NOT EXISTS column_metric (
  column_id VARCHAR(64) NOT NULL,
  metric_id VARCHAR(64) NOT NULL,
  PRIMARY KEY (column_id, metric_id)
);

