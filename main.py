from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List

import models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# 1. 스캔 시작
@app.post("/scans/", response_model=schemas.Scan)
def start_scan(db: Session = Depends(get_db)):
    db_scan = models.Scan()
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    return db_scan

# 2. 파일 업로드 및 스캔 연결
@app.post("/files/", response_model=schemas.File)
def create_file(scan_id: int, file: schemas.FileCreate, db: Session = Depends(get_db)):
    scan = db.query(models.Scan).filter(models.Scan.Scan_id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")
    
    db_file = models.File(**file.dict())
    db_scan = models.FileScan(File_id=db_file.File_id, Scan_id=scan_id)
    db_file.scans.append(db_scan)

    db.add(db_file)
    db.commit()
    db.refresh(db_file)
    return db_file

# 3. 정적 분석 결과 저장
@app.post("/files/{file_id}/static/", response_model=schemas.StaticAnalysis)
def create_static_analysis(analysis: schemas.StaticAnalysisCreate, db: Session = Depends(get_db)):
    file_scan_link = db.query(models.FileScan).filter_by(
        File_id=analysis.File_id, Scan_id=analysis.Scan_id
    ).first()
    if not file_scan_link:
        raise HTTPException(status_code=404, detail="FileScan link not found. Create it first.")

    db_analysis = models.StaticAnalysis(**analysis.dict())
    db.add(db_analysis)

    db.query(models.File).filter(models.File.File_id == analysis.File_id).update({"is_detected": True})

    db.commit()
    db.refresh(db_analysis)
    return db_analysis

# 4. 동적 분석 결과 저장
@app.post("/files/{file_id}/dynamic/", response_model=schemas.DynamicAnalysis)
def create_dynamic_analysis(analysis: schemas.DynamicAnalysisCreate, db: Session = Depends(get_db)):
    file_scan_link = db.query(models.FileScan).filter_by(
        File_id=analysis.File_id, Scan_id=analysis.Scan_id
    ).first()
    if not file_scan_link:
        raise HTTPException(status_code=404, detail="FileScan link not found. Create it first.")

    db_analysis = models.DynamicAnalysis(**analysis.dict())
    db.add(db_analysis)

    db.query(models.File).filter(models.File.File_id == analysis.File_id).update({"is_detected": True})

    db.commit()
    db.refresh(db_analysis)
    return db_analysis

# 5. LLM로 보낼 어셈블리 파일 저장
@app.post("/files/{file_id}/llm/", response_model=schemas.LLMAssemblyResult)
def create_llm_result(result: schemas.LLMAssemblyCreate, db: Session = Depends(get_db)):
    file_scan_link = db.query(models.FileScan).filter_by(
        File_id=result.File_id, Scan_id=result.Scan_id
    ).first()
    if not file_scan_link:
        raise HTTPException(status_code=404, detail="FileScan link not found. Create it first.")

    db_result = models.LLM(**result.dict())
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

# 6. LLM 분석 결과 저장
@app.post("/files/{file_id}/llm_analysis/", response_model=schemas.LLMResult)
def create_llm_analysis(analysis: schemas.LLMResult, db: Session = Depends(get_db)):
    file_scan_link = db.query(models.FileScan).filter_by(
        File_id=analysis.File_id, Scan_id=analysis.Scan_id
    ).first()
    if not file_scan_link:
        raise HTTPException(status_code=404, detail="FileScan link not found. Create it first.")

    db_analysis = models.LLM(**analysis.dict())
    db.add(db_analysis)

    db.query(models.File).filter(models.File.File_id == analysis.File_id).update({"is_detected": True})

    db.commit()
    db.refresh(db_analysis)
    return db_analysis

#7. LLM 코드 저장
@app.post("/files/{file_id}/llm_code/", response_model=schemas.LLMCodeCreate)
def create_llm_code(code: schemas.LLMCodeCreate, db: Session = Depends(get_db)):
    file_scan_link = db.query(models.FileScan).filter_by(
        File_id=code.File_id, Scan_id=code.Scan_id
    ).first()
    if not file_scan_link:
        raise HTTPException(status_code=404, detail="FileScan link not found. Create it first.")

    db_code = models.LLM(**code.dict())
    db.add(db_code)
    db.commit()
    db.refresh(db_code)
    return db_code

# 8. LLM 로그 저장
@app.post("/files/{file_id}/llm_log/", response_model=schemas.LLMLogCreate)
def create_llm_log(log: schemas.LLMLogCreate, db: Session = Depends(get_db)):
    file_scan_link = db.query(models.FileScan).filter_by(
        File_id=log.File_id, Scan_id=log.Scan_id
    ).first()
    if not file_scan_link:
        raise HTTPException(status_code=404, detail="FileScan link not found. Create it first.")

    db_log = models.LLM(**log.dict())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

# 9. LLM 어셈블리어 파일 가져오기
@app.get("/files/{file_id}/llm/", response_model=List[schemas.LLMAssemblyGet])
def get_llm_assembly(file_id: int, scan_id: int, db: Session = Depends(get_db)):
    llm_assembly = db.query(models.LLM).filter_by(File_id=file_id, Scan_id=scan_id).all()
    if not llm_assembly:
        raise HTTPException(status_code=404, detail="LLM Assembly not found")
    return llm_assembly

# 10. LLM 코드 가져오기
@app.get("/files/{file_id}/llm_code/", response_model=List[schemas.LLMCodeGet])
def get_llm_code(file_id: int, scan_id: int, db: Session = Depends(get_db)):
    llm_code = db.query(models.LLM).filter_by(File_id=file_id, Scan_id=scan_id).all()
    if not llm_code:
        raise HTTPException(status_code=404, detail="LLM Code not found")
    return llm_code

# 11. LLM 로그 가져오기
@app.get("/files/{file_id}/llm_log/", response_model=List[schemas.LLMLogGet])
def get_llm_log(file_id: int, scan_id: int, db: Session = Depends(get_db)):
    llm_log = db.query(models.LLM).filter_by(File_id=file_id, Scan_id=scan_id).all()
    if not llm_log:
        raise HTTPException(status_code=404, detail="LLM Log not found")
    return llm_log


# 12. 파일 상세 정보 조회
@app.get("/files/{file_id}", response_model=schemas.FileDetailResponse)
def read_file_details(file_id: int, db: Session = Depends(get_db)):
    db_file = db.query(models.File).options(
        joinedload(models.File.scans).subqueryload(models.FileScan.static_analyses),
        joinedload(models.File.scans).subqueryload(models.FileScan.dynamic_analyses),
        joinedload(models.File.scans).subqueryload(models.FileScan.llm_results),
    ).filter(models.File.File_id == file_id).first()

    if db_file is None:
        raise HTTPException(status_code=404, detail="File not found")
    
    for scan in db_file.scans:
        scan.llm_results = [r for r in scan.llm_results if r.LLM_analysis is not None]

    return db_file


# 13. 스캔별 파일 목록 조회
@app.get("/scans/{scan_id}/files", response_model=List[schemas.FileDetailResponse])
def read_scan_files_with_details(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(models.Scan).filter(models.Scan.Scan_id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    files = db.query(models.File).join(
        models.FileScan
    ).filter(
        models.FileScan.Scan_id == scan_id
    ).options(
        joinedload(models.File.scans).subqueryload(models.FileScan.static_analyses),
        joinedload(models.File.scans).subqueryload(models.FileScan.dynamic_analyses),
        joinedload(models.File.scans).subqueryload(models.FileScan.llm_results)
    ).all()

    for file in files:
        for scan_link in file.scans:
            scan_link.llm_results = [r for r in scan_link.llm_results if r.LLM_analysis is not None]

    return files

# 14. 종합 결과 통계
@app.get("/stats/", response_model=schemas.StatsResponse)
def get_scan_statistics(db: Session = Depends(get_db)):
    total_files = db.query(models.File).count()
    files_with_findings = db.query(models.File).filter(models.File.is_detected == True).count()

    top_10_algorithms_query = db.query(
        models.StaticAnalysis.Algorithm_name,
        func.count(models.StaticAnalysis.Algorithm_name).label("count")
    ).group_by(
        models.StaticAnalysis.Algorithm_name
    ).order_by(
        func.count(models.StaticAnalysis.Algorithm_name).desc()
    ).limit(10).all()

    top_10_algorithms = [
        schemas.AlgorithmStat(Algorithm_name=name, count=count)
        for name, count in top_10_algorithms_query
    ]

    return schemas.StatsResponse(
        total_files=total_files,
        files_with_findings=files_with_findings,
        top_10_algorithms=top_10_algorithms
    )

# 15. 스캔 ID별 종합 결과 통계
@app.get("/stats/{scan_id}/", response_model=schemas.StatsResponse)
def get_scan_statistics_by_scan_id(scan_id: int, db: Session = Depends(get_db)):
    scan = db.query(models.Scan).filter(models.Scan.Scan_id == scan_id).first()
    if not scan:
        raise HTTPException(status_code=404, detail="Scan not found")

    total_files = db.query(models.File).join(
        models.FileScan
    ).filter(
        models.FileScan.Scan_id == scan_id
    ).count()

    files_with_findings = db.query(models.File).join(
        models.FileScan
    ).filter(
        models.FileScan.Scan_id == scan_id,
        models.File.is_detected == True
    ).count()

    top_10_algorithms_query = db.query(
        models.StaticAnalysis.Algorithm_name,
        func.count(models.StaticAnalysis.Algorithm_name).label("count")
    ).filter(
        models.StaticAnalysis.Scan_id == scan_id
    ).group_by(
        models.StaticAnalysis.Algorithm_name
    ).order_by(
        func.count(models.StaticAnalysis.Algorithm_name).desc()
    ).limit(10).all()

    top_10_algorithms = [
        schemas.AlgorithmStat(Algorithm_name=name, count=count)
        for name, count in top_10_algorithms_query
    ]

    return schemas.StatsResponse(
        total_files=total_files,
        files_with_findings=files_with_findings,
        top_10_algorithms=top_10_algorithms
    )
    
# # 16. ASM/BIN 파일 업로드
# @app.post("/files/{file_id}/upload_files/")
# async def upload_asm_bin_files(
#     file_id: int,
#     scan_id: int,
#     asm_file: bytes = None,
#     bin_file: bytes = None,
#     asm_filename: str = None,
#     bin_filename: str = None,
#     db: Session = Depends(get_db)
# ):
#     # FileScan 존재 확인
#     file_scan_link = db.query(models.FileScan).filter_by(
#         File_id=file_id, Scan_id=scan_id
#     ).first()
#     if not file_scan_link:
#         raise HTTPException(status_code=404, detail="FileScan link not found. Create it first.")

#     # LLM 레코드 생성 또는 업데이트
#     llm_record = db.query(models.LLM).filter_by(
#         File_id=file_id, Scan_id=scan_id
#     ).first()

#     if not llm_record:
#         llm_record = models.LLM(File_id=file_id, Scan_id=scan_id)
#         db.add(llm_record)

#     # 파일 저장
#     if asm_file:
#         llm_record.Asm_file = asm_file
#         llm_record.Asm_filename = asm_filename
#     if bin_file:
#         llm_record.Bin_file = bin_file
#         llm_record.Bin_filename = bin_filename

#     db.commit()
#     db.refresh(llm_record)

#     return {
#         "Analysis_id": llm_record.Analysis_id,
#         "Asm_filename": llm_record.Asm_filename,
#         "Bin_filename": llm_record.Bin_filename,
#         "success": True
#     }

# # 17. ASM 파일 다운로드
# @app.get("/files/{file_id}/download_asm/")
# async def download_asm_file(file_id: int, scan_id: int, db: Session = Depends(get_db)):
#     llm_record = db.query(models.LLM).filter_by(
#         File_id=file_id, Scan_id=scan_id, Asm_file__isnot=None
#     ).first()
    
#     if not llm_record or not llm_record.Asm_file:
#         raise HTTPException(status_code=404, detail="ASM file not found")
    
#     from fastapi.responses import Response
#     return Response(
#         content=llm_record.Asm_file,
#         media_type="application/octet-stream",
#         headers={"Content-Disposition": f"attachment; filename={llm_record.Asm_filename}"}
#     )

# # 18. BIN 파일 다운로드
# @app.get("/files/{file_id}/download_bin/")
# async def download_bin_file(file_id: int, scan_id: int, db: Session = Depends(get_db)):
#     llm_record = db.query(models.LLM).filter_by(
#         File_id=file_id, Scan_id=scan_id, Bin_file__isnot=None
#     ).first()
    
#     if not llm_record or not llm_record.Bin_file:
#         raise HTTPException(status_code=404, detail="BIN file not found")
    
#     from fastapi.responses import Response
#     return Response(
#         content=llm_record.Bin_file,
#         media_type="application/octet-stream",
#         headers={"Content-Disposition": f"attachment; filename={llm_record.Bin_filename}"}
#     )
