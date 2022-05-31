from sqlalchemy import Column, String, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy.ext.declarative import declarative_base
from NestorBriefAutotests.utils.DbManagers.Orm.table_helper import TableHelper
from NestorBriefAutotests.utils.DbManagers.Postgress.db_manager import MainDbManager
from NestorBriefAutotests.utils.enums.import_status import ImportStatus

base = declarative_base()


class DbImportProcess(base, SerializerMixin, TableHelper):
    __tablename__ = 'ImportProcess'

    id = Column("Id", UUID, primary_key=True)
    user_id = Column("UserId", UUID)
    collection_id = Column("CollectionId", UUID)
    name = Column("Name", String)
    type = Column("Type", String)
    status = Column("Status", Integer)
    context = Column("Context", String)
    record_time = Column("RecordTime", DateTime)
    process_video = Column("ProcessVideo", Boolean)
    import_date = Column("ImportDate", DateTime)

    @staticmethod
    def delete_import_processes():
        _import_process = MainDbManager.query(DbImportProcess)
        return MainDbManager.delete(_import_process)

    @staticmethod
    def get_import_processes_by_name(name: str) -> list:
        return MainDbManager.query(DbImportProcess).filter(DbImportProcess.name == name).all()

    @staticmethod
    def get_import_processes() -> list:
        return MainDbManager.query(DbImportProcess).all()

    @staticmethod
    def get_import_processes_by_record_id(record_id: str) -> list:
        return MainDbManager.query(DbImportProcess).filter(DbImportProcess.collection_id == record_id).all()

    @staticmethod
    def get_active_import_processes() -> list:
        return MainDbManager.query(DbImportProcess).filter(DbImportProcess.status < ImportStatus.COMPLETE.value).all()

    @staticmethod
    def get_import_processes_column_by_name(column, name):
        return MainDbManager.query(column).filter(DbImportProcess.name == name).all()