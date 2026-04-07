CREATE DATABASE IF NOT EXISTS meta CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE DATABASE IF NOT EXISTS dw CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

SOURCE /docker-entrypoint-initdb.d/meta_seed.sql;
SOURCE /docker-entrypoint-initdb.d/dw_seed.sql;

