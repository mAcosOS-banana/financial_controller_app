from contextlib import contextmanager
from server.extensions import db

@contextmanager
def db_transaction():
    try:
        yield
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise RuntimeError("Erro na transação.") from e