BEGIN;

-- Add optional area label to candidate places.
ALTER TABLE trip_candidates
    ADD COLUMN area_label TEXT DEFAULT NULL;

-- Store per-day area preferences for itinerary generation (soft preference only).
CREATE TABLE trip_day_preferences (
    trip_id      UUID        NOT NULL,
    day_number   INTEGER     NOT NULL,
    preferred_area_label TEXT    NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_trip_day_preferences
        PRIMARY KEY (trip_id, day_number),
    CONSTRAINT fk_trip_day_preferences_trip_id
        FOREIGN KEY (trip_id) REFERENCES trips (id) ON DELETE CASCADE,
    CONSTRAINT chk_trip_day_preferences_day_number
        CHECK (day_number >= 1)
);

CREATE INDEX idx_trip_day_preferences_trip_id ON trip_day_preferences (trip_id);

COMMIT;
