from alembic.config import Config
from alembic.script import ScriptDirectory
from flask import current_app, g
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from werkzeug.local import LocalProxy

__all__ = ('Base', 'ensure_shutdown_session', 'get_engine', 'get_session',
           'get_alembic_config')


Base = declarative_base()
Session = sessionmaker()


def get_alembic_config(engine):
    if engine is not None:
        url = str(engine.url)
        config = Config()
        config.set_main_option('script_location',
                               current_app.config['ALEMBIC_SCRIPT_LOCATION'])
        config.set_main_option('sqlalchemy.url', url)
        config.set_main_option('url', url)
        return config, ScriptDirectory.from_config(config)
    else:
        raise 'no engine founded. DATABASE_URL can be misconfigured.'


def ensure_shutdown_session(app):
    def rollback_close(exc=None):
        if hasattr(g, 'sess'):
            if exc:
                g.sess.rollback()
            g.sess.close()

    app.teardown_appcontext(rollback_close)


def get_engine(app=None):
    app = app if app else current_app
    if app.config.get('DATABASE_URL', None) is not None:
        return create_engine(app.config.get('DATABASE_URL', None))


def get_session(engine=None):
    if not engine:
        engine = get_engine()
    if not hasattr(g, 'sess'):
        setattr(g, 'sess', Session(bind=engine))
    return getattr(g, 'sess')


session = LocalProxy(get_session)
