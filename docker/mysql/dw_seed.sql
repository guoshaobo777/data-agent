USE dw;

CREATE TABLE IF NOT EXISTS dim_region (
  region_id INT PRIMARY KEY,
  province VARCHAR(64) NOT NULL,
  region_name VARCHAR(64) NOT NULL,
  country VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_customer (
  customer_id INT PRIMARY KEY,
  customer_name VARCHAR(128) NOT NULL,
  gender VARCHAR(16) NOT NULL,
  member_level VARCHAR(32) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_product (
  product_id INT PRIMARY KEY,
  product_name VARCHAR(128) NOT NULL,
  category VARCHAR(64) NOT NULL,
  brand VARCHAR(64) NOT NULL
);

CREATE TABLE IF NOT EXISTS dim_date (
  date_id INT PRIMARY KEY,
  year INT NOT NULL,
  quarter VARCHAR(8) NOT NULL,
  month INT NOT NULL,
  day INT NOT NULL
);

CREATE TABLE IF NOT EXISTS fact_order (
  order_id INT PRIMARY KEY,
  customer_id INT NOT NULL,
  product_id INT NOT NULL,
  date_id INT NOT NULL,
  region_id INT NOT NULL,
  order_quantity INT NOT NULL,
  order_amount DECIMAL(12, 2) NOT NULL
);

INSERT INTO dim_region (region_id, province, region_name, country) VALUES
  (1, '广东', '华南', '中国'),
  (2, '浙江', '华东', '中国'),
  (3, '四川', '西南', '中国')
ON DUPLICATE KEY UPDATE
  province = VALUES(province),
  region_name = VALUES(region_name),
  country = VALUES(country);

INSERT INTO dim_customer (customer_id, customer_name, gender, member_level) VALUES
  (1001, '张三', '男', '金卡'),
  (1002, '李四', '女', '银卡'),
  (1003, '王五', '男', '普通')
ON DUPLICATE KEY UPDATE
  customer_name = VALUES(customer_name),
  gender = VALUES(gender),
  member_level = VALUES(member_level);

INSERT INTO dim_product (product_id, product_name, category, brand) VALUES
  (2001, '无线耳机', '数码', '声动'),
  (2002, '运动鞋', '服饰', '飞跃'),
  (2003, '电饭煲', '家电', '家悦')
ON DUPLICATE KEY UPDATE
  product_name = VALUES(product_name),
  category = VALUES(category),
  brand = VALUES(brand);

INSERT INTO dim_date (date_id, year, quarter, month, day) VALUES
  (20260318, 2026, 'Q1', 3, 18),
  (20260325, 2026, 'Q1', 3, 25),
  (20260401, 2026, 'Q2', 4, 1)
ON DUPLICATE KEY UPDATE
  year = VALUES(year),
  quarter = VALUES(quarter),
  month = VALUES(month),
  day = VALUES(day);

INSERT INTO fact_order (order_id, customer_id, product_id, date_id, region_id, order_quantity, order_amount) VALUES
  (90001, 1001, 2001, 20260318, 1, 2, 599.00),
  (90002, 1002, 2002, 20260325, 2, 1, 399.00),
  (90003, 1003, 2003, 20260401, 3, 3, 899.00)
ON DUPLICATE KEY UPDATE
  customer_id = VALUES(customer_id),
  product_id = VALUES(product_id),
  date_id = VALUES(date_id),
  region_id = VALUES(region_id),
  order_quantity = VALUES(order_quantity),
  order_amount = VALUES(order_amount);

