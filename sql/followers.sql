CREATE TABLE followers (
    gid             serial                      not null,
    username        varchar                     not null,
    active          boolean                     not null    default true,
    follow_time     timestamp with time zone    not null    default now(),
    unfollow_time   timestamp with time zone,

    primary key (gid)
);
