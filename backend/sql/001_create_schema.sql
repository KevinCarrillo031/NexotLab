-- NexotLab — esquema PostgreSQL
-- Ejecutar cuando vayan a crear la BD (la API aún no se conecta).
--
--   CREATE USER nexotlab WITH PASSWORD 'nexotlab';
--   CREATE DATABASE nexotlab OWNER nexotlab;
--   \c nexotlab
--   \i sql/001_create_schema.sql

BEGIN;

CREATE TABLE IF NOT EXISTS users (
    id              VARCHAR(36) PRIMARY KEY,
    name            VARCHAR(160) NOT NULL,
    email           VARCHAR(180) NOT NULL UNIQUE,
    password_hash   VARCHAR(255),
    profile_type    VARCHAR(32) NOT NULL,
    sector          VARCHAR(32),
    is_admin        BOOLEAN NOT NULL DEFAULT FALSE,
    active          BOOLEAN NOT NULL DEFAULT TRUE,
    joined_at       DATE NOT NULL,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_users_profile_type ON users (profile_type);
CREATE INDEX IF NOT EXISTS ix_users_sector ON users (sector);

CREATE TABLE IF NOT EXISTS proposals (
    id                  VARCHAR(36) PRIMARY KEY,
    title               VARCHAR(240) NOT NULL,
    category            VARCHAR(64) NOT NULL,
    sector              VARCHAR(32) NOT NULL,
    description         TEXT NOT NULL,
    deliverable         TEXT NOT NULL,
    author_id           VARCHAR(36) NOT NULL REFERENCES users (id),
    status              VARCHAR(32) NOT NULL,
    current_score       DOUBLE PRECISION NOT NULL DEFAULT 0,
    evaluations_count   INTEGER NOT NULL DEFAULT 0,
    created_at          DATE NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_proposals_category ON proposals (category);
CREATE INDEX IF NOT EXISTS ix_proposals_sector ON proposals (sector);
CREATE INDEX IF NOT EXISTS ix_proposals_status ON proposals (status);
CREATE INDEX IF NOT EXISTS ix_proposals_author_id ON proposals (author_id);

CREATE TABLE IF NOT EXISTS weekly_scores (
    id           SERIAL PRIMARY KEY,
    proposal_id  VARCHAR(36) NOT NULL REFERENCES proposals (id) ON DELETE CASCADE,
    week_index   INTEGER NOT NULL,
    score        DOUBLE PRECISION NOT NULL,
    recorded_at  DATE,
    CONSTRAINT uq_weekly_score_week UNIQUE (proposal_id, week_index)
);

CREATE TABLE IF NOT EXISTS collaborators (
    id           SERIAL PRIMARY KEY,
    proposal_id  VARCHAR(36) NOT NULL REFERENCES proposals (id) ON DELETE CASCADE,
    user_id      VARCHAR(36) NOT NULL REFERENCES users (id),
    status       VARCHAR(16) NOT NULL DEFAULT 'pending',
    applied_at   DATE NOT NULL,
    CONSTRAINT uq_collaborator_membership UNIQUE (proposal_id, user_id)
);

CREATE TABLE IF NOT EXISTS evaluations (
    id            VARCHAR(36) PRIMARY KEY,
    proposal_id   VARCHAR(36) NOT NULL REFERENCES proposals (id) ON DELETE CASCADE,
    evaluator_id  VARCHAR(36) NOT NULL REFERENCES users (id),
    viability     DOUBLE PRECISION NOT NULL,
    innovation    DOUBLE PRECISION NOT NULL,
    impact        DOUBLE PRECISION NOT NULL,
    clarity       DOUBLE PRECISION NOT NULL,
    score         DOUBLE PRECISION NOT NULL,
    created_at    DATE NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_evaluations_proposal_id ON evaluations (proposal_id);
CREATE INDEX IF NOT EXISTS ix_evaluations_evaluator_id ON evaluations (evaluator_id);

CREATE TABLE IF NOT EXISTS comments (
    id           VARCHAR(36) PRIMARY KEY,
    proposal_id  VARCHAR(36) NOT NULL REFERENCES proposals (id) ON DELETE CASCADE,
    user_id      VARCHAR(36) NOT NULL REFERENCES users (id),
    body         TEXT NOT NULL,
    created_at   DATE NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_comments_proposal_id ON comments (proposal_id);

CREATE TABLE IF NOT EXISTS notifications (
    id              VARCHAR(36) PRIMARY KEY,
    user_id         VARCHAR(36) REFERENCES users (id),
    type            VARCHAR(32) NOT NULL,
    message         TEXT NOT NULL,
    proposal_title  VARCHAR(240),
    date            DATE NOT NULL,
    read            BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE INDEX IF NOT EXISTS ix_notifications_user_id ON notifications (user_id);

CREATE TABLE IF NOT EXISTS content_reports (
    id              VARCHAR(36) PRIMARY KEY,
    proposal_title  VARCHAR(240) NOT NULL,
    reason          TEXT NOT NULL,
    reporter_name   VARCHAR(160) NOT NULL,
    date            DATE NOT NULL,
    dismissed       BOOLEAN NOT NULL DEFAULT FALSE
);

CREATE TABLE IF NOT EXISTS platform_settings (
    key    VARCHAR(64) PRIMARY KEY,
    value  VARCHAR(255) NOT NULL
);

INSERT INTO platform_settings (key, value) VALUES
    ('high_score_threshold', '4.0'),
    ('low_score_threshold', '2.5')
ON CONFLICT (key) DO NOTHING;

CREATE TABLE IF NOT EXISTS simulation_runs (
    id            SERIAL PRIMARY KEY,
    kind          VARCHAR(64) NOT NULL,
    params_json   TEXT NOT NULL,
    results_json  TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_simulation_runs_kind ON simulation_runs (kind);

CREATE TABLE IF NOT EXISTS mining_runs (
    id            SERIAL PRIMARY KEY,
    kind          VARCHAR(64) NOT NULL,
    params_json   TEXT NOT NULL,
    results_json  TEXT NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ix_mining_runs_kind ON mining_runs (kind);

COMMIT;
