CREATE TABLE itinerary_items (
    id           UUID        NOT NULL,
    trip_id      UUID        NOT NULL,
    day_number   INTEGER     NOT NULL,
    slot         VARCHAR     NOT NULL,
    candidate_id UUID        NULL,
    category     VARCHAR     NOT NULL,
    title        VARCHAR     NOT NULL,
    note         TEXT        NULL,
    sort_order   INTEGER     NOT NULL,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_itinerary_items              PRIMARY KEY (id),
    CONSTRAINT fk_itinerary_items_trip_id      FOREIGN KEY (trip_id)      REFERENCES trips (id),
    CONSTRAINT fk_itinerary_items_candidate_id FOREIGN KEY (candidate_id) REFERENCES trip_candidates (id) ON DELETE SET NULL,
    CONSTRAINT chk_itinerary_items_day_number  CHECK (day_number > 0),
    CONSTRAINT chk_itinerary_items_sort_order  CHECK (sort_order > 0),
    CONSTRAINT chk_itinerary_items_slot        CHECK (slot IN ('morning', 'lunch', 'afternoon', 'dinner', 'evening')),
    CONSTRAINT chk_itinerary_items_category    CHECK (category IN ('attraction', 'restaurant'))
);

CREATE INDEX idx_itinerary_items_trip_id                    ON itinerary_items (trip_id);
CREATE INDEX idx_itinerary_items_category                   ON itinerary_items (category);
CREATE INDEX idx_itinerary_items_trip_id_day_number_sort    ON itinerary_items (trip_id, day_number, sort_order);
