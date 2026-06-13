BEGIN;

ALTER TABLE trip_candidates
    ADD COLUMN restaurant_meal_times TEXT[] DEFAULT NULL;

-- Only restaurant candidates may carry meal-time metadata.
ALTER TABLE trip_candidates
    ADD CONSTRAINT chk_restaurant_meal_times_category
    CHECK (
        restaurant_meal_times IS NULL
        OR category = 'restaurant'
    );

-- Every element must be a recognised meal-time value.
ALTER TABLE trip_candidates
    ADD CONSTRAINT chk_restaurant_meal_times_values
    CHECK (
        restaurant_meal_times IS NULL
        OR restaurant_meal_times <@ ARRAY['breakfast','lunch','dinner','snack','late_night','any']::TEXT[]
    );

-- 'any' must not be combined with other values.
ALTER TABLE trip_candidates
    ADD CONSTRAINT chk_restaurant_meal_times_any_exclusive
    CHECK (
        restaurant_meal_times IS NULL
        OR NOT ('any' = ANY(restaurant_meal_times))
        OR cardinality(restaurant_meal_times) = 1
    );

COMMIT;
