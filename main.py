from fastapi import FastAPI,status,HTTPException,Query
from pydantic import BaseModel,Field

app=FastAPI(title="newfastapi")

class product_created(BaseModel):
    name:str = Field(max_length=100,min_length=0)
    price:float = Field(gt=0)
    description:str = Field(max_length=1000)

class product_response(BaseModel):
    id:int
    name:str
    price:float
    description:str

products:dict[int,dict]={}
next_id=1


@app.post("/products",
          response_model=product_response,
          status_code=status.HTTP_201_CREATED)

async def sales(product:product_created):
    global next_id

    new_product={
        "id":next_id,
        "name":product.name,
        "price":product.price,
        "description":product.description
    }

    products[next_id]=new_product
    next_id+=1

    return new_product


@app.get("/products", response_model=list[product_response])
async def get_products(
    search: str | None=Query(default="laptop",max_length=1000),
    min_price:float= Query(default=1,ge=0),
    max_price:float =Query(default=0,ge=1,le=100000),
    sort_by:int =Query(default="id"),
    order:str =Query(default="asc"),
    skip:int =Query(default=0,ge=0),
    limit:int =Query(default=10,ge=1,le=100)
    
):


    filtered_products=[
        products
        for products in products.values()
        if min_price<=products["price"]<=max_price
    ]
    if search:
        filtered_products=[
            products
            for products in filtered_products
            if search.strip().lower() in products["name"].lower()
        ]

    if sort_by not in ["id","name","price"]:
        raise HTTPException(
            status_code=404,
            detail="product must sort only by id,name,price"
        )

    if order not in ["asc","desc"]:
        raise HTTPException(
            status_code=404,
            detail="order must be asc or desc"
        )

    filtered_products.sort(
        key=lambda products: products[sort_by],
        reverse=(order == "desc")
    )

    return filtered_products[skip:skip+limit]


@app.get("/products/{product_id}", response_model=product_response)
async def get_product(product_id: int):
    product = products.get(product_id)

    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    return product


@app.put("/products/{product_id}",response_model=product_response)
async def update_product(product_id:int,product:product_created):
    if product_id not in products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="product not found"
        )

    updated_product={
        "id":product_id,
        "name":product.name,
        "price":product.price,
        "description":product.description
    }

    products[product_id]=updated_product
    return updated_product


@app.delete("/products/{product_id}", response_model=product_response)
async def delete_product(product_id:int):
    if product_id not in products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )

    deleted_products=products.pop(product_id)

    return{
        "details":"sucessfully deleted",
        "product":deleted_products
    }