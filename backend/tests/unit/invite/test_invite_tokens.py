from common.invite_tokens import generate_invite_token, hash_invite_token


class TestGenerateInviteToken:
    def test_returns_nonempty_string(self):
        token = generate_invite_token()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_repeated_calls_produce_different_tokens(self):
        tokens = {generate_invite_token() for _ in range(10)}
        assert len(tokens) == 10


class TestHashInviteToken:
    def test_deterministic(self):
        token = "my-raw-invite-token"
        assert hash_invite_token(token) == hash_invite_token(token)

    def test_distinct_inputs_produce_distinct_hashes(self):
        assert hash_invite_token("token-a") != hash_invite_token("token-b")

    def test_hash_not_equal_to_raw(self):
        token = "my-raw-invite-token"
        assert hash_invite_token(token) != token

    def test_hash_is_hex_string(self):
        h = hash_invite_token("any-token")
        assert all(c in "0123456789abcdef" for c in h)
        assert len(h) == 64
