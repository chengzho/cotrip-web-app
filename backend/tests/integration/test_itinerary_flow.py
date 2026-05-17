"""
Integration Flows C + D — Itinerary Generation, CRUD, and Category Snapshot

Tests run through real Lambda handler entrypoints against a live PostgreSQL DB.
Requires COTRIP_RUN_INTEGRATION=1 (enforced in conftest.py).
"""

from candidate.app import lambda_handler as candidate_handler
from itinerary.app import lambda_handler as itinerary_handler
from trip_group.app import lambda_handler as trip_handler
from vote.app import lambda_handler as vote_handler

from .helpers import assert_err, assert_ok, make_event

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

_ALICE_SUB = "sub-alice-itinerary"
_ALICE_EMAIL = "alice@cotrip-itinerary.example"

_TRIP_BODY = {
    "title": "Itinerary Test Trip",
    "destination": "Osaka, Japan",
    "start_date": "2026-10-01",
    "end_date": "2026-10-01",  # 1 day → simpler slot math
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_trip(body=None):
    resp = trip_handler(make_event(
        "POST", "/trips", "POST /trips",
        sub=_ALICE_SUB, email=_ALICE_EMAIL,
        body=body or _TRIP_BODY,
    ), {})
    return assert_ok(resp, 201)["trip_id"]


def _create_candidate(trip_id, category, name, note=None):
    body = {"category": category, "name": name}
    if note:
        body["note"] = note
    resp = candidate_handler(make_event(
        "POST", f"/trips/{trip_id}/candidates",
        "POST /trips/{tripId}/candidates",
        sub=_ALICE_SUB, email=_ALICE_EMAIL,
        path_params={"tripId": trip_id},
        body=body,
    ), {})
    return assert_ok(resp, 201)["candidate"]


def _vote(candidate_id):
    return assert_ok(vote_handler(make_event(
        "POST", f"/candidates/{candidate_id}/votes",
        "POST /candidates/{candidateId}/votes",
        sub=_ALICE_SUB, email=_ALICE_EMAIL,
        path_params={"candidateId": candidate_id},
    ), {}), 200)


def _generate(trip_id, overwrite=False):
    body = {}
    if overwrite:
        body["overwrite_existing"] = True
    return itinerary_handler(make_event(
        "POST", f"/trips/{trip_id}/itinerary/generate",
        "POST /trips/{tripId}/itinerary/generate",
        sub=_ALICE_SUB, email=_ALICE_EMAIL,
        path_params={"tripId": trip_id},
        body=body,
    ), {})


def _get_itinerary(trip_id):
    return itinerary_handler(make_event(
        "GET", f"/trips/{trip_id}/itinerary",
        "GET /trips/{tripId}/itinerary",
        sub=_ALICE_SUB, email=_ALICE_EMAIL,
        path_params={"tripId": trip_id},
    ), {})


def _update_item(trip_id, item_id, patch):
    return itinerary_handler(make_event(
        "PATCH", f"/trips/{trip_id}/itinerary/items/{item_id}",
        "PATCH /trips/{tripId}/itinerary/items/{itemId}",
        sub=_ALICE_SUB, email=_ALICE_EMAIL,
        path_params={"tripId": trip_id, "itemId": item_id},
        body=patch,
    ), {})


def _delete_item(trip_id, item_id):
    return itinerary_handler(make_event(
        "DELETE", f"/trips/{trip_id}/itinerary/items/{item_id}",
        "DELETE /trips/{tripId}/itinerary/items/{itemId}",
        sub=_ALICE_SUB, email=_ALICE_EMAIL,
        path_params={"tripId": trip_id, "itemId": item_id},
    ), {})


def _seed_trip_with_candidates():
    """Return (trip_id, attraction_id, restaurant_id)."""
    trip_id = _create_trip()
    attr = _create_candidate(trip_id, "attraction", "Dotonbori", note="Neon lights")
    rest = _create_candidate(trip_id, "restaurant", "Osaka Ramen", note="Local favourite")
    return trip_id, attr["candidate_id"], rest["candidate_id"]


# ---------------------------------------------------------------------------
# Tests — Generate itinerary
# ---------------------------------------------------------------------------

class TestGenerateItinerary:
    def test_generate_returns_200_with_itinerary(self):
        trip_id, _, _ = _seed_trip_with_candidates()
        data = assert_ok(_generate(trip_id), 200)
        assert "itinerary" in data
        itinerary = data["itinerary"]
        assert itinerary["trip_id"] == trip_id
        assert isinstance(itinerary["days"], list)

    def test_generate_creates_db_rows(self, pg_conn):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM itinerary_items WHERE trip_id = %s", (trip_id,)
            )
            count = cur.fetchone()[0]
        assert count >= 1

    def test_generated_items_have_correct_fields(self):
        trip_id, _, _ = _seed_trip_with_candidates()
        data = assert_ok(_generate(trip_id), 200)
        items = data["itinerary"]["days"][0]["items"]
        for item in items:
            assert "item_id" in item
            assert "slot" in item
            assert item["category"] in ("attraction", "restaurant")
            assert item["title"]

    def test_candidate_id_and_category_snapshot_stored(self, pg_conn):
        trip_id, attr_id, rest_id = _seed_trip_with_candidates()
        _generate(trip_id)

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT candidate_id, category, title FROM itinerary_items WHERE trip_id = %s",
                (trip_id,),
            )
            rows = cur.fetchall()

        assert len(rows) >= 1
        # All rows have non-null candidate_id and category snapshot
        for row in rows:
            assert row[0] is not None, "candidate_id must be set after fresh generation"
            assert row[1] in ("attraction", "restaurant")
            assert row[2]  # title is non-empty

    def test_note_copied_as_snapshot(self, pg_conn):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT note FROM itinerary_items WHERE trip_id = %s AND category = 'attraction'",
                (trip_id,),
            )
            row = cur.fetchone()
        assert row is not None
        assert row[0] == "Neon lights"

    def test_higher_voted_candidate_placed_first(self, pg_conn):
        trip_id = _create_trip()
        low = _create_candidate(trip_id, "attraction", "Low Vote Spot")
        high = _create_candidate(trip_id, "attraction", "High Vote Spot")
        _vote(high["candidate_id"])
        _generate(trip_id)

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT title, sort_order FROM itinerary_items "
                "WHERE trip_id = %s AND category = 'attraction' ORDER BY sort_order",
                (trip_id,),
            )
            rows = cur.fetchall()
        # High vote spot should appear at lower sort_order (placed first)
        assert rows[0][0] == "High Vote Spot"


# ---------------------------------------------------------------------------
# Tests — Conflict / overwrite
# ---------------------------------------------------------------------------

class TestGenerateConflict:
    def test_second_generate_without_overwrite_returns_409(self):
        trip_id, _, _ = _seed_trip_with_candidates()
        assert_ok(_generate(trip_id), 200)
        resp = _generate(trip_id, overwrite=False)
        assert_err(resp, 409, "ITINERARY_ALREADY_EXISTS")

    def test_second_generate_with_overwrite_succeeds(self):
        trip_id, _, _ = _seed_trip_with_candidates()
        assert_ok(_generate(trip_id), 200)
        data = assert_ok(_generate(trip_id, overwrite=True), 200)
        assert "itinerary" in data

    def test_overwrite_replaces_items_in_db(self, pg_conn):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)

        with pg_conn.cursor() as cur:
            cur.execute("SELECT id FROM itinerary_items WHERE trip_id = %s", (trip_id,))
            first_ids = {str(r[0]) for r in cur.fetchall()}

        _generate(trip_id, overwrite=True)

        with pg_conn.cursor() as cur:
            cur.execute("SELECT id FROM itinerary_items WHERE trip_id = %s", (trip_id,))
            second_ids = {str(r[0]) for r in cur.fetchall()}

        assert first_ids != second_ids, "Overwrite must generate new item UUIDs"

    def test_generate_with_no_candidates_returns_409_conflict(self):
        trip_id = _create_trip()
        resp = _generate(trip_id)
        assert_err(resp, 409, "CONFLICT")


# ---------------------------------------------------------------------------
# Tests — Get itinerary
# ---------------------------------------------------------------------------

class TestGetItinerary:
    def test_get_returns_200_with_grouped_days(self):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)
        data = assert_ok(_get_itinerary(trip_id), 200)
        assert "itinerary" in data
        assert "days" in data["itinerary"]
        assert data["itinerary"]["trip_id"] == trip_id

    def test_get_empty_itinerary_returns_200_with_empty_days(self):
        trip_id = _create_trip()
        data = assert_ok(_get_itinerary(trip_id), 200)
        assert data["itinerary"]["days"] == []

    def test_get_itinerary_date_matches_trip_start(self):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)
        data = assert_ok(_get_itinerary(trip_id), 200)
        days = data["itinerary"]["days"]
        assert len(days) >= 1
        assert days[0]["date"] == "2026-10-01"

    def test_get_itinerary_items_match_db(self, pg_conn):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)

        api_data = assert_ok(_get_itinerary(trip_id), 200)
        api_items = [item for day in api_data["itinerary"]["days"] for item in day["items"]]

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM itinerary_items WHERE trip_id = %s", (trip_id,)
            )
            db_count = cur.fetchone()[0]

        assert len(api_items) == db_count


# ---------------------------------------------------------------------------
# Tests — Update itinerary item
# ---------------------------------------------------------------------------

class TestUpdateItineraryItem:
    def _get_first_item_id(self, trip_id):
        data = assert_ok(_get_itinerary(trip_id), 200)
        return data["itinerary"]["days"][0]["items"][0]["item_id"]

    def test_update_slot_succeeds(self):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)
        item_id = self._get_first_item_id(trip_id)

        data = assert_ok(_update_item(trip_id, item_id, {"slot": "evening"}), 200)
        assert data["item"]["slot"] == "evening"

    def test_update_persists_in_db(self, pg_conn):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)
        item_id = self._get_first_item_id(trip_id)
        _update_item(trip_id, item_id, {"slot": "evening"})

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT slot FROM itinerary_items WHERE id = %s", (item_id,)
            )
            row = cur.fetchone()
        assert row[0] == "evening"

    def test_update_note_to_new_value(self):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)
        item_id = self._get_first_item_id(trip_id)

        data = assert_ok(_update_item(trip_id, item_id, {"note": "Updated note"}), 200)
        assert data["item"]["note"] == "Updated note"

    def test_invalid_slot_returns_400(self):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)
        item_id = self._get_first_item_id(trip_id)

        resp = _update_item(trip_id, item_id, {"slot": "midnight"})
        assert_err(resp, 400, "VALIDATION_ERROR")

    def test_empty_patch_returns_400(self):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)
        item_id = self._get_first_item_id(trip_id)

        resp = _update_item(trip_id, item_id, {})
        assert_err(resp, 400, "VALIDATION_ERROR")

    def test_day_number_zero_returns_400(self):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)
        item_id = self._get_first_item_id(trip_id)

        resp = _update_item(trip_id, item_id, {"day_number": 0})
        assert_err(resp, 400, "VALIDATION_ERROR")


# ---------------------------------------------------------------------------
# Tests — Delete itinerary item
# ---------------------------------------------------------------------------

class TestDeleteItineraryItem:
    def _get_first_item_id(self, trip_id):
        data = assert_ok(_get_itinerary(trip_id), 200)
        return data["itinerary"]["days"][0]["items"][0]["item_id"]

    def test_delete_returns_200_with_deleted_id(self):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)
        item_id = self._get_first_item_id(trip_id)

        data = assert_ok(_delete_item(trip_id, item_id), 200)
        assert data["deleted_item_id"] == item_id

    def test_delete_removes_row_from_db(self, pg_conn):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)
        item_id = self._get_first_item_id(trip_id)
        _delete_item(trip_id, item_id)

        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) FROM itinerary_items WHERE id = %s", (item_id,)
            )
            count = cur.fetchone()[0]
        assert count == 0

    def test_delete_item_not_found_returns_404(self):
        trip_id, _, _ = _seed_trip_with_candidates()
        fake_id = "00000000-0000-0000-0000-000000000000"
        resp = _delete_item(trip_id, fake_id)
        assert_err(resp, 404, "NOT_FOUND")

    def test_status_is_not_204(self):
        trip_id, _, _ = _seed_trip_with_candidates()
        _generate(trip_id)
        item_id = self._get_first_item_id(trip_id)
        resp = _delete_item(trip_id, item_id)
        assert resp["statusCode"] != 204


# ---------------------------------------------------------------------------
# Tests — Flow D: Category snapshot preservation (ON DELETE SET NULL)
# ---------------------------------------------------------------------------

class TestCategorySnapshotPreservation:
    def test_candidate_deletion_nulls_candidate_id_but_preserves_snapshot(self, pg_conn):
        """
        End-to-end validation of the itinerary category snapshot design:
        1. Generate itinerary from a candidate.
        2. Delete the candidate.
        3. itinerary_items.candidate_id becomes NULL (ON DELETE SET NULL).
        4. itinerary_items.category and title remain intact (snapshot).
        """
        trip_id, attr_id, _ = _seed_trip_with_candidates()
        _generate(trip_id)

        # Capture what was generated for the attraction candidate
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT id, category, title FROM itinerary_items "
                "WHERE trip_id = %s AND candidate_id = %s",
                (trip_id, attr_id),
            )
            row = cur.fetchone()
        assert row is not None, "Attraction item must exist after generation"
        item_id = row[0]
        original_category = row[1]
        original_title = row[2]

        # Delete the attraction candidate directly via DB (simulates cascade)
        with pg_conn.cursor() as cur:
            cur.execute("DELETE FROM trip_candidates WHERE id = %s", (attr_id,))

        # Verify DB state: candidate_id is NULL, category + title unchanged
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT candidate_id, category, title FROM itinerary_items WHERE id = %s",
                (item_id,),
            )
            after = cur.fetchone()

        assert after[0] is None, "candidate_id must be NULL after candidate deletion"
        assert after[1] == original_category, "category snapshot must survive candidate deletion"
        assert after[2] == original_title, "title snapshot must survive candidate deletion"

    def test_get_itinerary_after_candidate_deletion_still_returns_200(self, pg_conn):
        """GET itinerary returns 200 and includes items even after candidates are deleted."""
        trip_id, attr_id, _ = _seed_trip_with_candidates()
        _generate(trip_id)

        # Delete the attraction candidate
        with pg_conn.cursor() as cur:
            cur.execute("DELETE FROM trip_candidates WHERE id = %s", (attr_id,))

        # GET itinerary still works
        data = assert_ok(_get_itinerary(trip_id), 200)
        all_items = [
            item
            for day in data["itinerary"]["days"]
            for item in day["items"]
        ]
        assert len(all_items) >= 1

        # The attraction item should now have candidate_id=None in the response
        nulled = [i for i in all_items if i["candidate_id"] is None]
        assert len(nulled) >= 1, "At least one item must have null candidate_id after deletion"

    def test_delete_via_candidate_handler_also_nulls_itinerary(self, pg_conn):
        """Deletion through the real candidate handler triggers the ON DELETE SET NULL cascade."""
        trip_id, attr_id, _ = _seed_trip_with_candidates()
        _generate(trip_id)

        # Delete via the candidate handler (exercises the full domain path)
        del_resp = candidate_handler(make_event(
            "DELETE", f"/trips/{trip_id}/candidates/{attr_id}",
            "DELETE /trips/{tripId}/candidates/{candidateId}",
            sub=_ALICE_SUB, email=_ALICE_EMAIL,
            path_params={"tripId": trip_id, "candidateId": attr_id},
        ), {})
        assert_ok(del_resp, 200)

        # Confirm itinerary item now has null candidate_id but category survives
        with pg_conn.cursor() as cur:
            cur.execute(
                "SELECT candidate_id, category FROM itinerary_items "
                "WHERE trip_id = %s AND category = 'attraction'",
                (trip_id,),
            )
            row = cur.fetchone()
        assert row is not None
        assert row[0] is None, "candidate_id must be NULL"
        assert row[1] == "attraction", "category snapshot must be preserved"
