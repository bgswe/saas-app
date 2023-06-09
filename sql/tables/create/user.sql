CREATE TABLE bookt_user (
    id uuid PRIMARY KEY,

    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    organization_id uuid NOT NULL,

    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,

    first_name VARCHAR(255),
    last_name VARCHAR(255)
);
