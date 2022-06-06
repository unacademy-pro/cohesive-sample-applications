from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class App(Base):
    __tablename__ = "app"

    name = Column(String(100), primary_key=True, nullable=False)
    resource_type = Column(String(100), primary_key=True, nullable=False)
    vars = Column(String(10000))
    owner = Column(String(1000))
    proxy_url = Column(String(1000))
    proxy_type = Column(String(20))

    def __repr__(self):
        return f'{self.resource_type}: {self.name}'

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
