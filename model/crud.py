from sqlalchemy.orm import Session

from . import models, schemas


def get_user_by_login_and_name(db: Session, login: str, name: str) -> models.User | None:
    return db.query(models.User).filter(models.User.login == login).filter(models.User.name == name).first()


def get_user(db: Session, user_id: int) -> models.User | None:
    return db.query(models.User).filter(models.User.id == user_id).first()


def create_user(db: Session, user: schemas.UserCreate) -> models.User:
    db_user = models.User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def create_user_stream(db: Session, stream: schemas.StreamCreate, user_id: int) -> models.Stream:
    db_stream = models.Stream(**stream.model_dump(), user_id=user_id)
    db.add(db_stream)
    db.commit()
    db.refresh(db_stream)
    return db_stream


def delete_user_stream(db: Session, name: str, user_id: int) -> models.Stream | None:
    db_stream = (
        db.query(models.Stream).filter(models.Stream.name == name).filter(models.Stream.user_id == user_id).first()
    )

    if not db_stream:
        return None

    db.delete(db_stream)
    db.commit()
    return db_stream


def create_user_notificator(db: Session, notificator: schemas.NotificatorCreate, user_id: int) -> models.Notificator:
    db_notificator = models.Notificator(**notificator.model_dump(), user_id=user_id)
    db.add(db_notificator)
    db.commit()
    db.refresh(db_notificator)
    return db_notificator


def delete_user_notificator(db: Session, name: str, user_id: int) -> models.Notificator | None:
    db_notificator = (
        db.query(models.Notificator)
        .filter(models.Notificator.name == name)
        .filter(models.Notificator.user_id == user_id)
        .first()
    )
    if not db_notificator:
        return None

    db.delete(db_notificator)
    db.commit()
    return db_notificator
