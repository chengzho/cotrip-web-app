CREATE TABLE trip_candidates (
    id          UUID        NOT NULL,
    trip_id     UUID        NOT NULL,
    created_by  UUID        NOT NULL,
    category    VARCHAR     NOT NULL,
    name        VARCHAR     NOT NULL,
    address     TEXT        NULL,
    note        TEXT        NULL,
    source_url  TEXT        NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_trip_candidates              PRIMARY KEY (id),
    CONSTRAINT fk_trip_candidates_trip_id      FOREIGN KEY (trip_id)    REFERENCES trips (id),
    CONSTRAINT fk_trip_candidates_created_by   FOREIGN KEY (created_by) REFERENCES users (id),
    CONSTRAINT chk_trip_candidates_category    CHECK (category IN ('attraction', 'restaurant'))
);

CREATE INDEX idx_trip_candidates_trip_id          ON trip_candidates (trip_id);
CREATE INDEX idx_trip_candidates_created_by       ON trip_candidates (created_by);
CREATE INDEX idx_trip_candidates_category         ON trip_candidates (category);
CREATE INDEX idx_trip_candidates_trip_id_category ON trip_candidates (trip_id, category);
