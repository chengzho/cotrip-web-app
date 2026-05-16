CREATE TABLE trip_members (
    trip_id   UUID        NOT NULL,
    user_id   UUID        NOT NULL,
    role      VARCHAR     NOT NULL,
    joined_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_trip_members         PRIMARY KEY (trip_id, user_id),
    CONSTRAINT fk_trip_members_trip_id FOREIGN KEY (trip_id) REFERENCES trips (id),
    CONSTRAINT fk_trip_members_user_id FOREIGN KEY (user_id) REFERENCES users (id),
    CONSTRAINT chk_trip_members_role   CHECK (role IN ('owner', 'member'))
);

CREATE INDEX idx_trip_members_user_id        ON trip_members (user_id);
CREATE INDEX idx_trip_members_trip_id        ON trip_members (trip_id);
CREATE INDEX idx_trip_members_trip_id_role   ON trip_members (trip_id, role);
