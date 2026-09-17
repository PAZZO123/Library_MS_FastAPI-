from enum import Enum
from typing import Annotated

from fastapi import FastAPI, Path, Query, status
from pydantic import BaseModel, ConfigDict, Field

app=FastAPI()

class ModelName(str, Enum):
    resnet="resnet"
    alexnet="alexnet"
    lenet="lenet"
    
class Item(BaseModel):
    name:str=Field(min_length=2, max_length=100)
    description:str|None=None
    price:float=Field(gt=0, description="Price must be positive")
    tax:float | None= None
    quantity:float=Field(ge=0, default=0)
    model_config=ConfigDict(
        json_schema_extra={
            "examples":[
                {"name":"Patrick","description":"This goes to ", "price":12.5, "tax":1.3,"quantity":3.0}
            ]
        }
    )

class UpdateModel(BaseModel):
    name:str|None=None
    description:str|None=None
    price:float |None=None
    tax:float | None= None

@app.get("/")
def read_root():
    return {"message":"Hello, FASTAPI"}

@app.get("/items", status_code=status.HTTP_200_OK)
def read_items(q:Annotated[str|None, Query(min_length=3, max_lenth=50, description="Search Term")]=None):
    return{"q":q}
@app.post("/items", status_code=status.HTTP_201_CREATED,)
def add_item(item:Item):
    return item

@app.get("/items/{item_id}")
def get_by_id(item_id: Annotated[int, Path(tittle="Item ID",ge=1, le=1000)]):
    return {"item-ID:item_id"}
# @app.get("/items/{item_id}")
# def get_item(*,item_id:int, q:str |None=None,limit:int=10 ):
#     return {"item_id":item_id, "q":q, "limit":limit}

@app.get("/models/{model_name}")
def get_model(model_name:ModelName):
    return {"model_name":model_name, "message":f"Loading {model_name.value}"}

@app.get("/files/{file_path:path}")
def get_file(file_path:str):
    return {"file_path": file_path}

@app.put("/items/{item_id}")
def update_item(item_id:int, item:UpdateModel, notify:bool=False):
    return {"item_id":item_id, "item":item, "notify":notify}
    
