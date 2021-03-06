from flask import g
from pytest import fixture
from sqlalchemy.orm import sessionmaker

from sc2statistics.loader import load_all, load_replay
from sc2web.db import Base, get_engine
from sc2web.web.app import app


@fixture
def f_replay_data():
    n = './tests/assets/test_replay.SC2Replay'
    return load_replay(n)


@fixture
def f_replay_data2():
    n = './tests/assets/test_replay2.SC2Replay'
    return load_replay(n)


@fixture
def f_replay():
    n = list(load_all('./tests/assets'))[0]
    with open(n, 'rb') as f:
        yield f


@fixture
def f_session(request):
    with app.test_request_context() as ctx_:
        Session = sessionmaker(autocommit=False, autoflush=False)
        app.config['DATABASE_URL'] = 'sqlite:///'
        engine = get_engine(app)
        Base.metadata.create_all(engine)
        ctx_.push()
        session = Session(bind=engine)
        setattr(g, 'sess', session)

        def finish():
            session.close()
            Base.metadata.drop_all(engine)
            engine.dispose()

        request.addfinalizer(finish)
        return session
