CREATE TABLE candidate_votes (
    candidate_id UUID        NOT NULL,
    user_id      UUID        NOT NULL,
    vote_value   SMALLINT    NOT NULL DEFAULT 1,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_candidate_votes              PRIMARY KEY (candidate_id, user_id),
    CONSTRAINT fk_candidate_votes_candidate_id FOREIGN KEY (candidate_id) REFERENCES trip_candidates (id) ON DELETE CASCADE,
    CONSTRAINT fk_candidate_votes_user_id      FOREIGN KEY (user_id)      REFERENCES users (id),
    CONSTRAINT chk_candidate_votes_vote_value  CHECK (vote_value = 1)
);

CREATE INDEX idx_candidate_votes_candidate_id ON candidate_votes (candidate_id);
CREATE INDEX idx_candidate_votes_user_id      ON candidate_votes (user_id);
