CREATE TABLE trip_invites (
    id          UUID        NOT NULL,
    trip_id     UUID        NOT NULL,
    created_by  UUID        NOT NULL,
    token_hash  VARCHAR     NOT NULL,
    expires_at  TIMESTAMPTZ NOT NULL,
    max_uses    INTEGER     NOT NULL,
    used_count  INTEGER     NOT NULL DEFAULT 0,
    revoked_at  TIMESTAMPTZ NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_trip_invites                   PRIMARY KEY (id),
    CONSTRAINT fk_trip_invites_trip_id           FOREIGN KEY (trip_id)    REFERENCES trips (id),
    CONSTRAINT fk_trip_invites_created_by        FOREIGN KEY (created_by) REFERENCES users (id),
    CONSTRAINT chk_trip_invites_max_uses_positive CHECK (max_uses > 0),
    CONSTRAINT chk_trip_invites_used_count_gte_0  CHECK (used_count >= 0),
    CONSTRAINT chk_trip_invites_used_count_lte_max CHECK (used_count <= max_uses)
);

CREATE UNIQUE INDEX uq_trip_invites_token_hash ON trip_invites (token_hash);
CREATE INDEX idx_trip_invites_trip_id          ON trip_invites (trip_id);
CREATE INDEX idx_trip_invites_expires_at       ON trip_invites (expires_at);
