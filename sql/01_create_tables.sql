-- ============================================================
-- AI 金融报告分析市场走势 · 建表脚本（MySQL 8.0 / MariaDB 10.4+）
-- 执行：mysql -u<user> -p < 01_create_tables.sql
-- ============================================================
CREATE DATABASE IF NOT EXISTS project_8 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE project_8;

-- 1. 机构
CREATE TABLE IF NOT EXISTS t_institution (
  id          INT UNSIGNED NOT NULL AUTO_INCREMENT,
  name        VARCHAR(64)  NOT NULL COMMENT '机构全称',
  short_name  VARCHAR(32)  DEFAULT NULL COMMENT '简称',
  created_at  DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_inst_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='机构信息';

-- 2. 品种字典
CREATE TABLE IF NOT EXISTS t_variety (
  code          VARCHAR(16) NOT NULL COMMENT '标准代码，如 RB',
  name          VARCHAR(32) NOT NULL COMMENT '中文名',
  exchange      VARCHAR(16) DEFAULT NULL,
  main_contract VARCHAR(16) DEFAULT NULL,
  PRIMARY KEY (code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='品种字典';

-- 3. 研报
CREATE TABLE IF NOT EXISTS t_report (
  id             INT UNSIGNED NOT NULL AUTO_INCREMENT,
  institution_id INT UNSIGNED NOT NULL,
  report_date    DATE         NOT NULL,
  report_no      VARCHAR(64)  DEFAULT NULL COMMENT '业务报告 ID',
  title          VARCHAR(255) DEFAULT NULL,
  file_path      VARCHAR(512) DEFAULT NULL,
  file_hash      CHAR(64)     DEFAULT NULL COMMENT 'SHA-256 去重',
  parse_status   VARCHAR(16)  NOT NULL DEFAULT 'pending' COMMENT 'pending/ok/failed/need_ocr',
  created_at     DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  UNIQUE KEY uk_report_hash (file_hash),
  KEY ix_report_date (report_date),
  KEY ix_report_inst_date (institution_id, report_date),
  CONSTRAINT fk_report_inst FOREIGN KEY (institution_id) REFERENCES t_institution (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='研报元数据';

-- 4. 观点
CREATE TABLE IF NOT EXISTS t_view (
  id                BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  report_id         INT UNSIGNED NOT NULL,
  variety_code      VARCHAR(16)  NOT NULL,
  contract_code     VARCHAR(16)  DEFAULT NULL,
  horizon           VARCHAR(16)  NOT NULL DEFAULT 'short' COMMENT 'intraday/short/medium',
  direction         VARCHAR(8)   NOT NULL COMMENT 'BULL/BEAR/NEUTRAL/UNKNOWN',
  raw_direction     VARCHAR(64)  DEFAULT NULL COMMENT '研报原始表述',
  strategy          VARCHAR(128) DEFAULT NULL,
  reason            VARCHAR(512) DEFAULT NULL,
  evidence          VARCHAR(1024) DEFAULT NULL COMMENT '原文依据',
  source_page       INT          DEFAULT NULL,
  extraction_method VARCHAR(8)   NOT NULL DEFAULT 'AI' COMMENT 'RULE/AI',
  confidence        DECIMAL(3,2) DEFAULT NULL,
  review_status     VARCHAR(16)  NOT NULL DEFAULT 'auto',
  created_at        DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (id),
  KEY ix_view_report (report_id),
  KEY ix_view_variety_dir (variety_code, direction),
  CONSTRAINT fk_view_report FOREIGN KEY (report_id) REFERENCES t_report (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='结构化观点';

-- 5. 每日指标快照
CREATE TABLE IF NOT EXISTS t_daily_sentiment (
  variety_code      VARCHAR(16) NOT NULL,
  trade_date        DATE        NOT NULL,
  bull_count        INT         NOT NULL DEFAULT 0,
  bear_count        INT         NOT NULL DEFAULT 0,
  flat_count        INT         NOT NULL DEFAULT 0,
  institution_count INT         NOT NULL DEFAULT 0,
  report_count      INT         NOT NULL DEFAULT 0,
  consensus_index   DECIMAL(5,1) DEFAULT NULL COMMENT 'N=0 时为 NULL',
  updated_at        DATETIME    NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (variety_code, trade_date),
  KEY ix_sent_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='每日指标快照';

-- 6. 可选价格
CREATE TABLE IF NOT EXISTS t_daily_price (
  variety_code VARCHAR(16) NOT NULL,
  trade_date   DATE        NOT NULL,
  close_price  DECIMAL(12,2) DEFAULT NULL,
  change_pct   DECIMAL(6,2)  DEFAULT NULL,
  sample_count INT           NOT NULL DEFAULT 0,
  PRIMARY KEY (variety_code, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='研报提及价格（可选）';

-- 7. 视图：当日品种多空汇总（需求文档要求 6 表 1 视图）
CREATE OR REPLACE VIEW v_daily_consensus AS
SELECT s.variety_code,
       v.name AS variety_name,
       s.trade_date,
       s.bull_count,
       s.bear_count,
       s.flat_count,
       s.institution_count,
       s.report_count,
       s.consensus_index
FROM t_daily_sentiment s
LEFT JOIN t_variety v ON v.code = s.variety_code;
