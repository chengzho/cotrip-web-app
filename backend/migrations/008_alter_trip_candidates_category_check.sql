BEGIN;

ALTER TABLE trip_candidates
    DROP CONSTRAINT IF EXISTS chk_trip_candidates_category;

ALTER TABLE trip_candidates
    ADD CONSTRAINT chk_trip_candidates_category
    CHECK (category IN ('attraction', 'restaurant', 'accommodation', 'transport', 'other'));

COMMIT;
