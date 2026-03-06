"""
Database models for Burp Suite Montoya API documentation storage.
"""

from sqlalchemy import Column, Integer, String, Text, ForeignKey, Table, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from pathlib import Path

Base = declarative_base()

# Association table for interface-method many-to-many relationship
interface_method_association = Table(
    "interface_method_association",
    Base.metadata,
    Column("interface_id", Integer, ForeignKey("interfaces.id")),
    Column("method_id", Integer, ForeignKey("methods.id")),
)


class Package(Base):
    """Represents a Java package in the API."""

    __tablename__ = "packages"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False, index=True)
    description = Column(Text)
    parent_id = Column(Integer, ForeignKey("packages.id"), nullable=True)

    parent = relationship("Package", remote_side=[id], back_populates="children")
    children = relationship("Package", back_populates="parent")
    interfaces = relationship("Interface", back_populates="package")

    def __repr__(self):
        return f"<Package(name='{self.name}')>"


class Interface(Base):
    """Represents a Java interface in the API."""

    __tablename__ = "interfaces"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    fully_qualified_name = Column(String, unique=True, nullable=False)
    package_id = Column(Integer, ForeignKey("packages.id"), nullable=False)
    description = Column(Text)
    javadoc = Column(Text)
    file_path = Column(String)
    is_public = Column(Integer, default=1)  # 1=True, 0=False

    package = relationship("Package", back_populates="interfaces")
    methods = relationship(
        "Method", secondary=interface_method_association, back_populates="interfaces"
    )
    extends = relationship(
        "Interface",
        secondary="interface_extends",
        primaryjoin="Interface.id==interface_extends.c.interface_id",
        secondaryjoin="Interface.id==interface_extends.c.extends_id",
        backref="extended_by",
    )

    def __repr__(self):
        return f"<Interface(name='{self.name}', package='{self.package.name if self.package else None}')>"


# Association table for interface inheritance
interface_extends = Table(
    "interface_extends",
    Base.metadata,
    Column("interface_id", Integer, ForeignKey("interfaces.id"), primary_key=True),
    Column("extends_id", Integer, ForeignKey("interfaces.id"), primary_key=True),
)


class Method(Base):
    """Represents a method in a Java interface."""

    __tablename__ = "methods"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, index=True)
    signature = Column(Text)  # Full method signature
    return_type = Column(String)
    description = Column(Text)
    javadoc = Column(Text)
    parameters = Column(Text)  # JSON list of parameters
    exceptions = Column(Text)  # JSON list of thrown exceptions
    is_static = Column(Integer, default=0)  # 1=True, 0=False
    is_default = Column(Integer, default=0)  # 1=True, 0=False

    interfaces = relationship(
        "Interface", secondary=interface_method_association, back_populates="methods"
    )

    def __repr__(self):
        return f"<Method(name='{self.name}', signature='{self.signature[:50] if self.signature else None}...')>"


class Import(Base):
    """Represents import statements in a Java file."""

    __tablename__ = "imports"

    id = Column(Integer, primary_key=True)
    interface_id = Column(Integer, ForeignKey("interfaces.id"), nullable=False)
    import_statement = Column(String, nullable=False)
    is_static = Column(Integer, default=0)

    interface = relationship("Interface")

    def __repr__(self):
        return f"<Import(statement='{self.import_statement}')>"


def init_db(db_path: str = "burp_api.db"):
    """Initialize the database with all tables."""
    engine = create_engine(f"sqlite:///{db_path}")
    Base.metadata.create_all(engine)
    return engine


def get_session(engine):
    """Get a database session."""
    Session = sessionmaker(bind=engine)
    return Session()
