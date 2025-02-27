from datetime import datetime, UTC

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import NoResultFound, IntegrityError, MultipleResultsFound
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()


class FileUploaded(db.Model):
    __tablename__ = "files_uploaded"

    id: Mapped[int] = mapped_column(db.Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(db.String(200), nullable=False)
    sha256: Mapped[str] = mapped_column(db.String(64), nullable=False, unique=True)
    upload_time: Mapped[datetime] = mapped_column(db.DateTime, default=lambda: datetime.now(UTC), nullable=False)
    filesize: Mapped[int] = mapped_column(db.BigInteger, nullable=False)

    @classmethod
    def create(cls, filename: str, sha256: str, filesize: int):
        try:
            new_data = cls(filename=filename, sha256=sha256, filesize=filesize)
            db.session.add(new_data)
            db.session.commit()
            return new_data
        except IntegrityError as e:
            db.session.rollback()
            if "sha256" in str(e).lower():
                raise DuplicateDataError(f"Duplicated data of sha256: {sha256}")

            raise

    @classmethod
    def overwrite(cls, sha256: str, **kwargs):
        try:
            result = db.session.execute(db.select(cls).filter_by(sha256=sha256)).scalar_one()
            for key, value in kwargs.items():
                setattr(result, key, value)

            db.session.commit()
            return result
        except NoResultFound:
            db.session.rollback()
            raise DataNotFoundError(f"Not found data in database of sha256: {sha256}")
        except MultipleResultsFound:
            db.session.rollback()
            raise DuplicateDataError(f"Duplicated data of sha256: {sha256}")

    @classmethod
    def query(cls, sha256: str):
        return db.session.execute(db.select(cls).filter_by(sha256=sha256)).scalar_one_or_none()


class DuplicateDataError(Exception):
    pass


class DataNotFoundError(Exception):
    pass

# class Log2Battery(db.Model):
#     log_capture_time = db.Column(db.String(20), primary_key=True, nullable=False)
#     estimated_battery_capacity = db.Column(db.Float, nullable=False)
#     last_learned_battery_capacity = db.Column(db.Float, nullable=False)
#     min_learned_battery_capacity = db.Column(db.Float, nullable=False)
#     max_learned_battery_capacity = db.Column(db.Float, nullable=False)
#     phone_brand = db.Column(db.String(10), nullable=False)
#     nickname = db.Column(db.String(20), nullable=False)
#     system_version = db.Column(db.String(30), nullable=False)
