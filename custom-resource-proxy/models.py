from sqlalchemy import Column, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class OAuth2App(Base):
    __tablename__ = "oauth2_app"

    name = Column(String(100), primary_key=True, nullable=False)
    client_id = Column(String(100), nullable=False)
    client_secret = Column(String(100), nullable=False)
    callback_url = Column(String(1000), nullable=False)
    auth_url = Column(String(1000), nullable=False)
    token_url = Column(String(1000), nullable=False)
    owner = Column(String(1000))
    proxy_url = Column(String(1000))

    def __repr__(self):
        return self.name

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
