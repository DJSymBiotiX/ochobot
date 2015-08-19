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
