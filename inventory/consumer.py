from main import redis, Product
import time
key="order_complete"
group="inventory_group"

try:
    redis.xgroup_create(key, group)
except:
    print("group already exists")

while True:
    try:
        results = redis.xreadgroup(group, key, {key: ">"}, None)
        print(results)
        if results != []:
            for r in results:
                order = r[1][0][1]
                product = Product.get(order["product_id"])
                product.quantity = product.quantity - int(order["quantity"]) 
                print(product)               
                product.save()
    except Exception as e:
        print(str(e))
    time.sleep(1)