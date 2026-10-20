-- NexotLab – esquema MySQL/MariaDB
-- Base de datos: proyectodecimo
-- Generado para MariaDB 10.4 / MySQL 8+
-- Ejecutar en phpMyAdmin o con: mysql -u root proyectodecimo < 001_create_schema_mysql.sql

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

-- ─── USUARIOS ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `users` (
  `id`            VARCHAR(36)  NOT NULL,
  `name`          VARCHAR(160) NOT NULL,
  `email`         VARCHAR(180) NOT NULL,
  `password_hash` VARCHAR(255) DEFAULT NULL,
  `profile_type`  VARCHAR(32)  NOT NULL,
  `sector`        VARCHAR(32)  DEFAULT NULL,
  `is_admin`      TINYINT(1)   NOT NULL DEFAULT 0,
  `active`        TINYINT(1)   NOT NULL DEFAULT 1,
  `joined_at`     DATE         NOT NULL,
  `created_at`    DATETIME     NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_users_email` (`email`),
  KEY `ix_users_profile_type` (`profile_type`),
  KEY `ix_users_sector` (`sector`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── PROPUESTAS ──────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `proposals` (
  `id`                VARCHAR(36)  NOT NULL,
  `title`             VARCHAR(240) NOT NULL,
  `category`          VARCHAR(64)  NOT NULL,
  `sector`            VARCHAR(32)  NOT NULL,
  `description`       TEXT         NOT NULL,
  `deliverable`       TEXT         NOT NULL,
  `author_id`         VARCHAR(36)  NOT NULL,
  `status`            VARCHAR(32)  NOT NULL,
  `current_score`     FLOAT        NOT NULL DEFAULT 0,
  `evaluations_count` INT          NOT NULL DEFAULT 0,
  `created_at`        DATE         NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_proposals_category`  (`category`),
  KEY `ix_proposals_sector`    (`sector`),
  KEY `ix_proposals_status`    (`status`),
  KEY `ix_proposals_author_id` (`author_id`),
  CONSTRAINT `fk_proposals_author` FOREIGN KEY (`author_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── SCORES SEMANALES ────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `weekly_scores` (
  `id`          INT     NOT NULL AUTO_INCREMENT,
  `proposal_id` VARCHAR(36) NOT NULL,
  `week_index`  INT     NOT NULL,
  `score`       FLOAT   NOT NULL,
  `recorded_at` DATE    DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_weekly_score_week` (`proposal_id`, `week_index`),
  CONSTRAINT `fk_weekly_scores_proposal`
    FOREIGN KEY (`proposal_id`) REFERENCES `proposals` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─── COLABORADORES ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `collaborators` (
  `id`          INT         NOT NULL AUTO_INCREMENT,
  `proposal_id` VARCHAR(36) NOT NULL,
  `user_id`     VARCHAR(36) NOT NULL,
  `status`      VARCHAR(16) NOT NULL DEFAULT 'pending',
  `applied_at`  DATE        NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_collaborator_membership` (`proposal_id`, `user_id`),
  CONSTRAINT `fk_collaborators_proposal`
    FOREIGN KEY (`proposal_id`) REFERENCES `proposals` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_collaborators_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─── EVALUACIONES ────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `evaluations` (
  `id`           VARCHAR(36) NOT NULL,
  `proposal_id`  VARCHAR(36) NOT NULL,
  `evaluator_id` VARCHAR(36) NOT NULL,
  `viability`    FLOAT NOT NULL,
  `innovation`   FLOAT NOT NULL,
  `impact`       FLOAT NOT NULL,
  `clarity`      FLOAT NOT NULL,
  `score`        FLOAT NOT NULL,
  `created_at`   DATE  NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_evaluations_proposal_id`  (`proposal_id`),
  KEY `ix_evaluations_evaluator_id` (`evaluator_id`),
  CONSTRAINT `fk_evaluations_proposal`
    FOREIGN KEY (`proposal_id`) REFERENCES `proposals` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_evaluations_evaluator`
    FOREIGN KEY (`evaluator_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─── COMENTARIOS ─────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `comments` (
  `id`          VARCHAR(36) NOT NULL,
  `proposal_id` VARCHAR(36) NOT NULL,
  `user_id`     VARCHAR(36) NOT NULL,
  `body`        TEXT        NOT NULL,
  `created_at`  DATE        NOT NULL,
  PRIMARY KEY (`id`),
  KEY `ix_comments_proposal_id` (`proposal_id`),
  CONSTRAINT `fk_comments_proposal`
    FOREIGN KEY (`proposal_id`) REFERENCES `proposals` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_comments_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── NOTIFICACIONES ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `notifications` (
  `id`             VARCHAR(36)  NOT NULL,
  `user_id`        VARCHAR(36)  DEFAULT NULL,
  `type`           VARCHAR(32)  NOT NULL,
  `message`        TEXT         NOT NULL,
  `proposal_title` VARCHAR(240) DEFAULT NULL,
  `date`           DATE         NOT NULL,
  `read`           TINYINT(1)   NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `ix_notifications_user_id` (`user_id`),
  CONSTRAINT `fk_notifications_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── REPORTES DE CONTENIDO ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `content_reports` (
  `id`             VARCHAR(36)  NOT NULL,
  `proposal_title` VARCHAR(240) NOT NULL,
  `reason`         TEXT         NOT NULL,
  `reporter_name`  VARCHAR(160) NOT NULL,
  `date`           DATE         NOT NULL,
  `dismissed`      TINYINT(1)   NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ─── CONFIGURACIÓN DE PLATAFORMA ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `platform_settings` (
  `key`   VARCHAR(64)  NOT NULL,
  `value` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`key`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─── RUNS DE SIMULACIÓN ──────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `simulation_runs` (
  `id`           INT      NOT NULL AUTO_INCREMENT,
  `kind`         VARCHAR(64) NOT NULL,
  `params_json`  TEXT     NOT NULL,
  `results_json` MEDIUMTEXT NOT NULL,
  `created_at`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_simulation_runs_kind` (`kind`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ─── RUNS DE MINERÍA ─────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS `mining_runs` (
  `id`           INT      NOT NULL AUTO_INCREMENT,
  `kind`         VARCHAR(64) NOT NULL,
  `params_json`  TEXT     NOT NULL,
  `results_json` MEDIUMTEXT NOT NULL,
  `created_at`   DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `ix_mining_runs_kind` (`kind`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

SET FOREIGN_KEY_CHECKS = 1;
