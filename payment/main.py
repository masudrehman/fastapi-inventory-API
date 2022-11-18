from typing import Union
from redis_om import get_redis_connection, HashModel
from fastapi import FastAPI
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from starlette.requests import Request
import requests, time

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:3000"],
    allow_methods=["*"],
    allow_headers=["*"]
)

redis = get_redis_connection(
    host="redis-17080.c281.us-east-1-2.ec2.cloud.redislabs.com",
    port=17080,
    password="iSnsjf4WrRXuyQZB3PFFbUKWUuuC7lcM",
    decode_responses=True
)

class Order(HashModel):
    product_id: str
    price: float
    quantity: int
    status: str #pending, completed, refunded

    class Meta:
        database = redis

@app.get("/orders/{pk}")
def get_order(pk: str):
    return Order.get(pk)

@app.post("/orders")
async def create(request: Request, bg_task: BackgroundTasks):
    body = await request.json()

    req = requests.get('http://localhost:8000/products/%s' % body["id"])
    product = req.json()

    order = Order(
        product_id=body["id"],
        price=product["price"],
        quantity=body["quantity"],
        status="pending"
    )
    order.save()

    bg_task.add_task(order_completed, order)

    return order

def order_completed(order: Order):
    time.sleep(5)
    order.status = "completed"
    order.save()