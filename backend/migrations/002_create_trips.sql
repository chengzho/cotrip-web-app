CREATE TABLE trips (
    id          UUID        NOT NULL,
    title       VARCHAR     NOT NULL,
    destination VARCHAR     NOT NULL,
    start_date  DATE        NOT NULL,
    end_date    DATE        NOT NULL,
    description TEXT        NULL,
    created_by  UUID        NOT NULL,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_trips             PRIMARY KEY (id),
    CONSTRAINT fk_trips_created_by  FOREIGN KEY (created_by) REFERENCES users (id),
    CONSTRAINT chk_trips_date_range CHECK (start_date <= end_date)
);

CREATE INDEX idx_trips_created_by ON trips (created_by);
CREATE INDEX idx_trips_start_date ON trips (start_date);
CREATE INDEX idx_trips_end_date   ON trips (end_date);
