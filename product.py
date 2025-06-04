from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from ... import models, schemas
from ...crud import product as crud_product
from ...database import get_db

router = APIRouter(prefix="/product", tags=["products"])

@router.get("/list", response_model=schemas.ProductListResponse)
def list_products(
    skip: int = 0,
    limit: int = 10,
    name: Optional[str] = None,
    category: Optional[str] = None,
    sku: Optional[str] = None,
    db: Session = Depends(get_db)
):
    
    result = crud_product.get_products(
        db=db,
        skip=skip,
        limit=limit,
        name=name,
        category=category,
        sku=sku
    )
    
    return {
        "items": result["items"],
        "total": result["total"],
        "page": result["page"],
        "size": result["size"]
    }

@router.get("/{product_id}/info", response_model=schemas.ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db)
):

    db_product = crud_product.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return db_product

@router.post("/add", response_model=schemas.ProductResponse, status_code=201)
def create_product(
    product: schemas.ProductCreate,
    db: Session = Depends(get_db)
):

    
    existing_product = db.query(models.Product).filter(models.Product.sku == product.sku).first()
    if existing_product:
        raise HTTPException(
            status_code=400,
            detail="A product with this SKU already exists"
        )
    
    return crud_product.create_product(db=db, product=product)

@router.put("/{product_id}/update", response_model=schemas.ProductResponse)
def update_product(
    product_id: int,
    product_update: schemas.ProductUpdate,
    db: Session = Depends(get_db)
):
    
    db_product = crud_product.get_product(db, product_id=product_id)
    if db_product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    
    
    if product_update.sku and product_update.sku != db_product.sku:
        existing_product = db.query(models.Product).filter(
            models.Product.sku == product_update.sku
        ).first()
        if existing_product:
            raise HTTPException(
                status_code=400,
                detail="A product with this SKU already exists"
            )
    
    return crud_product.update_product(db=db, db_product=db_product, product=product_update)
