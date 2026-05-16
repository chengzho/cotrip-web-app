CREATE TABLE users (
    id            UUID        NOT NULL,
    cognito_sub   VARCHAR     NOT NULL,
    email         VARCHAR     NOT NULL,
    display_name  VARCHAR     NOT NULL,
    created_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at    TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT pk_users PRIMARY KEY (id)
);

CREATE UNIQUE INDEX uq_users_cognito_sub ON users (cognito_sub);
CREATE UNIQUE INDEX uq_users_email       ON users (email);
