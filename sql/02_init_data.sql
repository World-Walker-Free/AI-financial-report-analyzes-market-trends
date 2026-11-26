-- 品种字典初始化（可按实际品种扩充）
INSERT INTO t_variety (code, name, exchange, main_contract) VALUES
  ('RB', '螺纹钢', 'SHFE', 'RB2405'),
  ('I',  '铁矿石', 'DCE',  'I2405'),
  ('P',  '棕榈油', 'DCE',  'P2405'),
  ('CU', '沪铜',   'SHFE', 'CU2405'),
  ('AU', '沪金',   'SHFE', 'AU2406'),
  ('M',  '豆粕',   'DCE',  'M2405'),
  ('TA', 'PTA',    'CZCE', 'TA2405'),
  ('SA', '纯碱',   'CZCE', 'SA2405')
ON DUPLICATE KEY UPDATE name = VALUES(name), main_contract = VALUES(main_contract);
