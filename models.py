# models.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Boolean,
    BIGINT,
    TIMESTAMP,
    ForeignKey,
    Enum,
    Text,
    ForeignKeyConstraint,
    PrimaryKeyConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from database import Base


class File(Base):
    __tablename__ = "file"

    File_id = Column(Integer, primary_key=True, autoincrement=True)
    File_name = Column(String(255), nullable=False)
    File_type = Column(String(50), nullable=False)
    File_size = Column(BIGINT, nullable=False)
    is_detected = Column(Boolean, nullable=False, default=False)

    scans = relationship("FileScan", back_populates="file", cascade="all, delete-orphan")


class Scan(Base):
    __tablename__ = "scan"

    Scan_id = Column(Integer, primary_key=True, autoincrement=True)
    Scan_at = Column(TIMESTAMP, nullable=False, server_default=func.now())

    files = relationship("FileScan", back_populates="scan", cascade="all, delete-orphan")


class FileScan(Base):
    __tablename__ = "file-scan" 

    File_id = Column(Integer, ForeignKey("file.File_id", ondelete="CASCADE"), primary_key=True)
    Scan_id = Column(Integer, ForeignKey("scan.Scan_id", ondelete="CASCADE"), primary_key=True)

    __table_args__ = (
        PrimaryKeyConstraint("File_id", "Scan_id"),
    )

    file = relationship("File", back_populates="scans")
    scan = relationship("Scan", back_populates="files")

    static_analyses = relationship("StaticAnalysis", back_populates="file_scan", cascade="all, delete-orphan")
    dynamic_analyses = relationship("DynamicAnalysis", back_populates="file_scan", cascade="all, delete-orphan")
    llm_results = relationship("LLM", back_populates="file_scan", cascade="all, delete-orphan")


class StaticAnalysis(Base):
    __tablename__ = "static_analysis"

    Detection_id = Column(Integer, primary_key=True, autoincrement=True)
    File_id = Column(Integer, nullable=False)
    Scan_id = Column(Integer, nullable=False)

    Offset = Column(BIGINT, nullable=True)
    Algorithm_name = Column(String(100), nullable=False)
    Match = Column(String(255), nullable=False)
    Detection_method = Column(Enum("text", "oid", "parameter"), nullable=False)
    Severity = Column(Enum("high", "medium", "low"), nullable=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ["File_id", "Scan_id"],
            ["file-scan.File_id", "file-scan.Scan_id"],
            ondelete="CASCADE"
        ),
    )

    file_scan = relationship("FileScan", back_populates="static_analyses")


class DynamicAnalysis(Base):
    __tablename__ = "dynamic_analysis"

    Detection_id = Column(Integer, primary_key=True, autoincrement=True)
    File_id = Column(Integer, nullable=False)
    Scan_id = Column(Integer, nullable=False)

    Parameter = Column(String(255), nullable=True)
    Algorithm_name = Column(String(100), nullable=True)
    Api = Column(String(255), nullable=True)
    Key_length = Column(Integer, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["File_id", "Scan_id"],
            ["file-scan.File_id", "file-scan.Scan_id"],
            ondelete="CASCADE"
        ),
    )

    file_scan = relationship("FileScan", back_populates="dynamic_analyses")


class LLM(Base):
    __tablename__ = "llm"

    Analysis_id = Column(Integer, primary_key=True, autoincrement=True)
    File_id = Column(Integer, nullable=False)
    Scan_id = Column(Integer, nullable=False)

    File_text = Column(MEDIUMTEXT, nullable=True)
    LLM_analysis = Column(Text, nullable=True)
    Code = Column(Text, nullable=True)
    Log = Column(Text, nullable=True)

    __table_args__ = (
        ForeignKeyConstraint(
            ["File_id", "Scan_id"],
            ["file-scan.File_id", "file-scan.Scan_id"],
            ondelete="CASCADE"
        ),
    )

    file_scan = relationship("FileScan", back_populates="llm_results")