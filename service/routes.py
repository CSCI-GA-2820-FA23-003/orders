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
PUT /orders/{id}/cancel - cancel an Order

GET /orders/{order_id}/items - Returns a list all of the Items of the given Order id
GET /orders/{order_id}/items/{item_id} - Returns the Order Item with a given id number
POST /orders/{order_id}/items - creates a new Order Item record in the database
PUT /orders/{order_id}/items/{item_id} - updates an Order Item record in the database
DELETE /orders/{order_id}/items/{item_id} - deletes an Order Item record in the database
"""
from flask import jsonify, request, url_for, abort, make_response
from service.common import status  # HTTP Status Codes
from service.models import Order, Item


# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


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
    # print(f"request.args = {request.args.to_dict(flat=False)}")

    orders = []  # A list of all orders satisfying requirements

    # Process the query string if any
    # Supported formats:
    # - All orders: "?"
    # - A particular order:
    #       "?order_id={some integer}" or
    #       "?order_id={some integer}&user_id={user id having this order}"
    # - All orders of a particular user ID: "?user_id={some integer}"

    # This corresponds to "?"
    query = Order.query
    query_params = request.args

    if len(query_params) == 0:
        orders = Order.all()

    # This corresponds to "?order_id={some integer}"
    if "order_id" in query_params:
        order_id = int(query_params.get("order_id"))
        query = query.filter(Order.id == order_id)

    # Check for 'user_id'
    if "user_id" in query_params:
        user_id = int(query_params.get("user_id"))
        query = query.filter(Order.user_id == user_id)

    # Check for 'status'
    if "status" in query_params:
        status_ = query_params.get("status")
        query = query.filter(Order.status == status_)

    if "name" in query_params:
        name = query_params.get("name")
        query = query.filter(Order.name == name)

    # Execute the query
    orders = query.all()

    # Return as an array of dictionaries
    results = [order.serialize() for order in orders]

    return make_response(jsonify(results), status.HTTP_200_OK)


@app.route("/orders/<order_id>", methods=["GET"])
def read_an_order(order_id):
    """Find an order by ID or Returns all of the Orders"""
    app.logger.info("Request for Read an Order")
    order = Order.find(order_id)

    if order:
        results = order.serialize()
        return make_response(jsonify(results), status.HTTP_200_OK)

    abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")


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
def update_item(order_id, item_id):
    """
    Adds an item by item ID to an existing order
    This endpoint will add an item (specified by item_id) to the specified order
    """
    app.logger.info("Request to update item with ID %d", item_id)
    check_content_type("application/json")

    order = Order.find(order_id)
    if not order:
        abort(status.HTTP_404_NOT_FOUND, "Order not found")

    # Check if the item exists
    data = request.get_json()

    item = Item.find(item_id)
    if item is None:
        # Handle the case when the order does not exist
        return make_response(jsonify(error="Item not found"), status.HTTP_404_NOT_FOUND)

    if "title" in data:
        item.title = data["title"]
    if "amount" in data:
        item.amount = data["amount"]
    if "status" in data:
        item.status = data["status"]

    item.update()
    order.update()

    location_url = url_for(
        "update_item", order_id=order_id, item_id=item_id, _external=True
    )

    return make_response(
        jsonify(item.serialize()),
        status.HTTP_202_ACCEPTED,
        {"Location": location_url},
    )


######################################################################
# List all items in an order
######################################################################
@app.route("/orders/<order_id>/items", methods=["GET"])
def list_items_in_one_order(order_id):
    """
    List all items in one order
    """
    app.logger.info("Request for Item list in one order")
    # order_id = request.args.get("order_id")
    order = Order.find(order_id)
    if order:
        order = order.serialize()
        results = order["items"]
        # Process the query string if any

        return make_response(jsonify(results), status.HTTP_200_OK)

    abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")


######################################################################
# List one item in an order
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
def list_one_item_in_one_order(order_id, item_id):
    """
    Get one item in one order
    """
    app.logger.info("Request for Item list in one order")
    # order_id = request.args.get("order_id")
    order = Order.find(order_id)
    order = order.serialize()
    results = order["items"]
    for item in results:
        if item["id"] == item_id:
            return make_response(jsonify(item), status.HTTP_200_OK)
    return make_response(jsonify(error="Item not in Order"), status.HTTP_404_NOT_FOUND)
    # Process the query string if any


######################################################################
# List one item in an order
######################################################################
@app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
def delete_one_item_in_one_order(order_id, item_id):
    """
    Delete one item in one order
    """
    app.logger.info("Request for Item list in one order")
    # order_id = request.args.get("order_id")
    order = Order.find(order_id)
    if order:
        order = order.serialize()
        item = Item.find(item_id)
        if (item is not None) and (item.order_id == order_id):
            item.delete()
            app.logger.info(
                "Item with ID [%s] and order ID [%s] delete complete.",
                item_id,
                order_id,
            )

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# UPDATE AN ORDER
######################################################################
@app.route("/orders/<int:order_id>", methods=["PUT"])
def update_an_order(order_id):
    """
    Update information (e.g., address, name) for an order.
    """
    app.logger.info("Update order information with ID: %d", order_id)

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
    if "status" in data:
        order.status = data["status"]

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
    app.logger.info("Delete an order with order ID %d", order_id)

    order = Order.find(order_id)
    if order:
        order.delete()

    return make_response("", status.HTTP_204_NO_CONTENT)


######################################################################
# CANCEL AN ORDER
######################################################################
@app.route("/orders/<int:order_id>/cancel", methods=["PUT"])
def cancel_an_order(order_id):
    """
    Cancel an order by order ID.
    """
    app.logger.info("Cancel an order with order ID %d", order_id)
    order = Order.find(order_id)

    if not order:
        abort(status.HTTP_404_NOT_FOUND, "Order not found")
    else:
        order.status = "CANCELED"

    order.update()
    return make_response(jsonify(order.serialize()), status.HTTP_200_OK)
