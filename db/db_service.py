from abc import ABCMeta, abstractmethod
from typing import List


class SingletonMeta(ABCMeta):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]


class IDatabase(metaclass=ABCMeta):
    @abstractmethod
    def connect(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def list_tables(self) -> List[str]:
        pass

    @abstractmethod
    def insert_values(self, table_name, values):
        pass

    @abstractmethod
    def update_values(self, table_name, values):
        pass

    @abstractmethod
    def select_values(self, table_name, condition):
        pass
    
    @abstractmethod
    def delete_values(self, table_name, condition):
        pass

    # TODO: other DB operations like insert, update, select, delete, etc.
