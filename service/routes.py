"""
My Service

Describe what your service does here
Paths:
------
GET /orders - Returns a list all of the Orders
GET /orders/{id} - Returns the Order with a given id number
POST /orders - creates a new Order record in the database
PUT /orders/{id} - updates an Order record in the database
DELETE /orders/{id} - deletes an Order record in the database

GET /orders/{order_id}/items - Returns a list all of the Items of the given Order id
GET /orders/{order_id}/items/{item_id} - Returns the Order Item with a given id number
POST /orders/{order_id}/items - creates a new Order Item record in the database
PUT /orders/{order_id}/items/{item_id} - updates an Order Item record in the database
DELETE /orders/{order_id}/items/{item_id} - deletes an Order Item record in the database
"""
from flask import jsonify, request, url_for, abort, make_response
from service.common import status  # HTTP Status Codes
from service.models import Order, Item
from datetime import datetime, timezone, timedelta

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return (
        jsonify(
            name="Order REST API Service",
            version="1.0",
            paths=url_for("list_orders", _external=True),
        ),
        status.HTTP_200_OK,
    )


######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################


def check_content_type(media_type):
    """Checks that the media type is correct"""
    content_type = request.headers.get("Content-Type")
    if content_type and content_type == media_type:
        return
    app.logger.error("Invalid Content-Type: %s", content_type)
    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}",
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################
######################################################################
# FIND AN ORDER BY ID OR RETURN ALL ORDERS
######################################################################
@app.route("/orders", methods=["GET"])
def list_orders():
    """Find an order by ID or Returns all of the Orders"""
    app.logger.info("Request for Order list")
    orders = []

    # print("request.args = {}".format(request.args.to_dict(flat=False)))

    # Process the query string if any

    if len(request.args) == 0:  # This corresponds to "/orders"
        orders = Order.all()

        # Return as an array of dictionaries
        results = [order.serialize() for order in orders]

    elif "order_id" in request.args:
        order_id = request.args.get("order_id")
        order = Order.find(order_id)
        results = order.serialize()

    else:
        abort(status.HTTP_404_NOT_FOUND)

    return make_response(jsonify(results), status.HTTP_200_OK)


######################################################################
# CREATE A NEW ORDER
######################################################################
@app.route("/orders", methods=["POST"])
def create_orders():
    """
    Creates an Order
    This endpoint will create an Order based the data in the body that is posted
    """
    app.logger.info("Request to create an Order")
    check_content_type("application/json")

    # Create the order
    order = Order()
    order.deserialize(request.get_json())
    order.create()

    # Create a message to return
    message = order.serialize()
    location_url = url_for("create_orders", order_id=order.id, _external=True)
    # print(location_url)

    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# CREATE A NEW ITEM IN ORDER
######################################################################
@app.route("/orders/<order_id>/items", methods=["POST"])
def create_item_in_an_order(order_id):
    """
    Create an item on an order

    This endpoint will add a new item to an order.
    """
    app.logger.info("Request to create an Item for Order with id: %s", order_id)
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    item = Item()
    item.deserialize(request.get_json())
    item.order_id = order_id
    item.amount = 1
    item.status = "Added to order"
    item.create()

    # order.items.append(item)
    # order.update()
    item.order_id = order_id
    item.update()

    message = item.serialize()
    location_url = url_for(
        "create_item_in_an_order", order_id=order_id, item_id=item.id, _external=True
    )
    # print(location_url)
    app.logger.info("Item with ID [%s] created for order: [%s].", item.id, order.id)
    return make_response(
        jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
    )


######################################################################
# UPDATE ITEM BY item id IN ORDER
######################################################################
@app.route("/orders/<order_id>/items/<item_id>", methods=["PUT"])
def update_item_by_id_to_order(order_id, item_id):
    """
    Adds an item by item ID to an existing order
    This endpoint will add an item (specified by item_id) to the specified order
    """
    app.logger.info(f"Request to add item with ID {item_id} to Order {order_id}")
    check_content_type("application/json")

    # Check if the order exists
    order = Order.find(order_id)
    if order is None:
        # Handle the case when the order does not exist
        return make_response(
            jsonify(error="Order not found"), status.HTTP_404_NOT_FOUND
        )

    # Check if the item exists
    item = Item.find(item_id)
    if item is None:
        # Handle the case when the order does not exist
        return make_response(jsonify(error="Item not found"), status.HTTP_404_NOT_FOUND)

    amount = request.args.get("amount", type=int)
    if amount is not None:
        # Update the item amount using the 'amount' query parameter
        original_amount = item.amount
        item.amount = amount
        order.cost_amount += (amount - original_amount) * item.price
    else:
        # Increment the item amount by 1
        item.amount += 1
        item.update()
        order.cost_amount += item.price

    order.update()

    location_url = url_for(
        "update_item_by_id_to_order", order_id=order_id, item_id=item_id, _external=True
    )

    return make_response(
        jsonify(order=order.serialize(), item=item.serialize()),
        status.HTTP_202_ACCEPTED,
        {"Location": location_url},
    )


######################################################################
# List all items in an order
######################################################################
@app.route("/orders/<order_id>/items", methods=["GET"])
def list_items_in_one_order(order_id):
    app.logger.info("Request for Item list in one order")
    # order_id = request.args.get("order_id")
    order = Order.find(order_id)
    order = order.serialize()
    results = order["items"]
    # Process the query string if any
    return make_response(
        jsonify(order_id=int(order_id), items=results), status.HTTP_200_OK
    )


######################################################################
# List one item in an order
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def list_one_item_in_one_order(order_id, item_id):
    app.logger.info("Request for Item list in one order")
    # order_id = request.args.get("order_id")
    order = Order.find(order_id)
    order = order.serialize()
    results = order["items"]
    for item in results:
        if item["id"] == item_id:
            return make_response(jsonify(item), status.HTTP_200_OK)
    return make_response(
        jsonify(error="Item not in Order"), status.HTTP_400_BAD_REQUEST
    )
    # Process the query string if any


######################################################################
# List one item in an order
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_one_item_in_one_order(order_id, item_id):
    app.logger.info("Request for Item list in one order")
    # order_id = request.args.get("order_id")
    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, f"Order not found")

    order = order.serialize()
    item = Item.find(item_id)
    if (item is not None) and (item.order_id == order_id):
        item.delete()
        app.logger.info(
            "Item with ID [%s] and order ID [%s] delete complete.", item_id, order_id
        )
        return make_response("", status.HTTP_204_NO_CONTENT)

    return make_response(
        jsonify(error="Item not in Order"), status.HTTP_400_BAD_REQUEST
    )


######################################################################
# UPDATE AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_an_order(order_id):
    """
    Update information (e.g., address, name) for an order.
    """
    app.logger.info(f"Update order information with ID {order_id}")

    # Find the order by ID
    order = Order.find(order_id)

    if not order:
        abort(status.HTTP_404_NOT_FOUND, "Order not found")

    # Update the 'name' and 'address' fields of the order
    data = request.get_json()
    if "name" in data:
        order.name = data["name"]
    if "address" in data:
        order.address = data["address"]

    order.update()

    return make_response(
        jsonify(order.serialize()), status.HTTP_200_OK, {"Updated_order_id": order_id}
    )


######################################################################
# DELETE AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_an_order(order_id):
    """
    Delete an order by order ID.
    """
    app.logger.info(f"Delete an order with order ID {order_id}")

    order = Order.find(order_id)

    if not order:
        abort(status.HTTP_404_NOT_FOUND, "Order not found")

    order.delete()

    return make_response(
        "",
        status.HTTP_204_NO_CONTENT,
        {"Deleted_order_id": order_id},
    )
