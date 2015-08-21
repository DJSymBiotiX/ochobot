CREATE TABLE contests (
    gid         serial                      not null,
    post_id     bigint                      not null,
    post_text   varchar                     not null,
    username    varchar                     not null,
    followed    boolean                     not null,
    favourited  boolean                     not null,
    entry_time  timestamp with time zone    not null    default now(),

    primary key (gid)
);
