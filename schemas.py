from typing import List, Optional
from pydantic import BaseModel
from enum import Enum as PyEnum

# ----------------------
# 기본 Scan / File
# ----------------------
class Scan(BaseModel):
    Scan_id: int

    class Config:
        orm_mode = True

class FileCreate(BaseModel):
    File_name: str
    File_type: str
    File_size: int


class File(BaseModel):
    File_id: int
    is_detected: bool = False

    class Config:
        orm_mode = True


# ----------------------
# File-Scan 연결
# ----------------------
class FileScanBase(BaseModel):
    File_id: int
    Scan_id: int


class FileScanCreate(FileScanBase):
    pass


class DetectionMethodEnum(str, PyEnum):
    text = "text"
    oid = "oid"
    parameter = "parameter"

class SeverityEnum(str, PyEnum):
    high = "high"
    medium = "medium"
    low = "low"


class StaticAnalysisBase(BaseModel):
    File_id: int
    Scan_id: int
    Offset: int
    Algorithm_name: str
    Match: str
    Detection_method: DetectionMethodEnum
    Severity: SeverityEnum


class StaticAnalysisCreate(StaticAnalysisBase):
    pass


class StaticAnalysis(StaticAnalysisBase):
    Detection_id: int

    class Config:
        orm_mode = True


# ----------------------
# 동적 분석
# ----------------------
class DynamicAnalysisBase(BaseModel):
    File_id: int
    Scan_id: int
    Parameter: str = None
    Api: str = None
    Key_length: int = None
    Algorithm_name: str


class DynamicAnalysisCreate(DynamicAnalysisBase):
    pass


class DynamicAnalysis(DynamicAnalysisBase):
    Detection_id: int

    class Config:
        orm_mode = True


class LLMAssemblyCreate(BaseModel):
    File_id: int
    Scan_id: int
    File_text: str


class LLMAssemblyResult(BaseModel):
    Analysis_id: int

    class Config:
        orm_mode = True

class LLMResult(BaseModel):
    File_id: int
    Scan_id: int
    LLM_analysis: str

    class Config:
        orm_mode = True

class LLMCodeCreate(BaseModel):
    File_id: int
    Scan_id: int
    Code: str

class LLMLogCreate(BaseModel):
    File_id: int
    Scan_id: int
    Log: str


class LLMAssemblyGet(BaseModel):
    File_text: str

    class Config:
        orm_mode = True
        exclude_none = True

class LLMCodeGet(BaseModel):
    Code: str

    class Config:
        orm_mode = True
        exclude_none = True

class LLMLogGet(BaseModel):
    Log: str

    class Config:
        orm_mode = True
        exclude_none = True

class LLMResultGet(BaseModel):
    LLM_analysis: Optional[str] = None

    class Config:
        orm_mode = True
        exclude_none = True


class FileScan(FileScanBase):
    static_analyses: List[StaticAnalysis] = []
    dynamic_analyses: List[DynamicAnalysis] = []
    llm_results: List[LLMResultGet] = []

    class Config:
        orm_mode = True


class FileDetailResponse(File):
    scans: List[FileScan] = []


class AlgorithmStat(BaseModel):
    Algorithm_name: str
    count: int


class StatsResponse(BaseModel):
    total_files: int
    files_with_findings: int
    top_10_algorithms: List[AlgorithmStat]


# ----------------------
# 종합 결과 요약
# ----------------------
class ScanFileSummary(BaseModel):
    File_id: int
    is_detected: bool
    static_analyses: List[str]
    dynamic_analyses: List[str]
    llm_results: List[str]


class ScanSummary(BaseModel):
    Scan_id: int
    files: List[ScanFileSummary]
