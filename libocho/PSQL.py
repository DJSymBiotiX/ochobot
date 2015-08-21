#!/usr/bin/env python


class PSQL:
    def __init__(self, config):
        from sqlalchemy     import create_engine
        from sqlalchemy.orm import sessionmaker

        try:
            uri = "postgresql://%s:%s@%s:%s/%s" % (
                config['username'],
                config['password'],
                config[    'host'],
                config[    'port'],
                config['database']
            )

            engine = create_engine(uri)
            Session = sessionmaker(bind=engine)
            self.session = Session()
        except Exception as e:
            raise ('[PSQL.py] %s' % e)


    def get_last_twitter_id(self):
        last_twitter_id = 0

        result = self.session.execute(
            """
            SELECT
                last_twitter_id
            FROM
                info
            """
        ).fetchone()

        if result is not None:
            last_twitter_id = result[0]

        return last_twitter_id


    def set_last_twitter_id(self, last_twitter_id):
        self.session.execute(
            """
            UPDATE
                info
            SET
                last_twitter_id = :last_twitter_id
            """, { 'last_twitter_id': last_twitter_id }
        )
        self.session.commit()


    def get_follower_count(self):
        follower_count = 0

        result = self.session.execute(
            """
            SELECT
                count(*)
            FROM
                followers
            WHERE
                active
            """
        ).fetchone()

        if result is not None:
            follower_count = result[0]

        return follower_count


    def get_oldest_follower(self):
        oldest_follower = None

        result = self.session.execute(
            """
            SELECT
                username
            FROM
                followers
            WHERE
                active
            ORDER BY
                gid ASC
            LIMIT 1
            """
        ).fetchone()

        if result is not None:
            oldest_follower = result[0]

        return oldest_follower


    def follow_user(self, new_follower):
        # Make sure we're not already following that user
        result = self.session.execute(
            """
            SELECT
                true
            FROM
                followers
            WHERE
                username = :username
                AND
                active
            """,
            { 'username': new_follower }
        ).fetchone()

        if result is None:
            self.session.execute(
                """
                INSERT INTO
                    followers (username)
                VALUES
                    (:username)
                """, { 'username': new_follower}
            )
            self.session.commit()


    def unfollow_user(self, old_follower):
        self.session.execute(
            """
            UPDATE
                followers
            SET
                active = 'f',
                unfollow_time = now()
            WHERE
                username = :username
            """,
            { 'username': old_follower }
        )
        self.session.commit()


    def check_favourite(self, post_id):
        result = self.session.execute(
            """
            SELECT
                true
            FROM
                contests
            WHERE
                post_id = :post_id
                AND
                favourited = 't'
            """, { 'post_id': post_id }
        ).fetchone()

        if result is None:
            return True
        return False


    def check_contest(self, post_id):
        result = self.session.execute(
            """
            SELECT
                true
            FROM
                contests
            WHERE
                post_id = :post_id
            """, { 'post_id': post_id }
        )

        if result is None:
            return True
        return False


    def add_contest(self, post_id, post_text, username, followed, favourited):
        self.session.execute(
            """
            INSERT INTO
                contests (post_id, post_text, username, followed, favourited)
            VALUES
                (:post_id, :post_text, :username, :followed, :favourited)
            """,
            {
                'post_id': post_id,
                'post_text': post_text,
                'username': username,
                'followed': followed,
                'favourited': favourited
            }
        )
        self.session.commit()
