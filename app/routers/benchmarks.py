from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


@router.post("/", response_model=schemas.Benchmark, status_code=status.HTTP_201_CREATED)
def create_benchmark(payload: schemas.BenchmarkCreate, db: Session = Depends(get_db)):
    return crud.create_benchmark(db, payload)


@router.get("/", response_model=list[schemas.Benchmark])
def list_benchmarks(db: Session = Depends(get_db)):
    return crud.list_benchmarks(db)


@router.get("/{benchmark_id}", response_model=schemas.Benchmark)
def get_benchmark(benchmark_id: int, db: Session = Depends(get_db)):
    benchmark = crud.get_benchmark(db, benchmark_id)
    if not benchmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benchmark not found")
    return benchmark


@router.put("/{benchmark_id}", response_model=schemas.Benchmark)
def update_benchmark(benchmark_id: int, payload: schemas.BenchmarkUpdate, db: Session = Depends(get_db)):
    benchmark = crud.get_benchmark(db, benchmark_id)
    if not benchmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benchmark not found")
    return crud.update_benchmark(db, benchmark, payload)


@router.delete("/{benchmark_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_benchmark(benchmark_id: int, db: Session = Depends(get_db)):
    benchmark = crud.get_benchmark(db, benchmark_id)
    if not benchmark:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Benchmark not found")
    crud.delete_benchmark(db, benchmark)
