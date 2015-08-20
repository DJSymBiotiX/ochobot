#!/usr/bin/env python

from Util import (
    out,
    err
)
from sys import exit


class PSQL:


    def __init__(self, config_path):
        self.configs = self.__config_reader(config_path)
        self.session = self.__authenticate_to_database()


    def __authenticate_to_database(self):
        from sqlalchemy     import create_engine
        from sqlalchemy.orm import sessionmaker

        session = None
        try:
            psql = self.configs['PSQL']
            uri = "postgresql://%s:%s@%s:%s/%s" % (
                psql['username'],
                psql['password'],
                psql[    'host'],
                psql[    'port'],
                psql['database']
            )

            engine = create_engine(uri)
            Session = sessionmaker(bind=engine)
            session = Session()
        except Exception as e:
            err("[PSQL] Authentication Error: %s" % e)
            exit(1)
        return session


    def __config_reader(self, config_path):
        import ConfigParser
        config = ConfigParser.ConfigParser()
        result = {}

        try:
            config.read(config_path)
        except Exception as e:
            err("[PSQL] Read Config Error: %s" % e)
            exit(1)

        # Read 'PSQL' Section
        result['PSQL'] = {
            'username': config.get('PSQL', 'username', 0),
            'password': config.get('PSQL', 'password', 0),
                'host': config.get('PSQL', 'host',     0),
                'port': config.get('PSQL', 'port',     0),
            'database': config.get('PSQL', 'database', 0)
        }
        return result


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
                last_twitter_id = '%s'
            """ % (last_twitter_id)
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
            ORDER BY
                gid ASC
            LIMIT 1
            """
        ).fetchone()

        if result is not None:
            oldest_follower = result[0]

        return oldest_follower


    def add_new_follower(self, new_follower):
        self.session.execute(
            """
            INSERT INTO
                followers (username)
            VALUES
                ('%s')
            """ % (new_follower)
        )
        self.session.commit()


    def add_contest(self, post_id, post_text, username, followed, favourited):
        self.session.execute(
            """
            INSERT INTO
                contests (post_id, post_Text, username, followed, favourited)
            VALUES
                ('%s', '%s', '%s', '%s', '%s')
            """ % (post_id, post_text, username, followed, favourited)
        )
        self.session.commit()

    def add_activity_log(self, activity, post_id):
        self.session.execute(
            """
            INSERT INTO
                activity_log (activity, post_id)
            VALUES
                ('%s', '%s')
            """ % (activity, post_id)
        )
        self.session.commit()

