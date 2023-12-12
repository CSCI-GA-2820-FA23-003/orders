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
from flask_restx import Resource, fields, reqparse, inputs

# Import Flask application
from . import app
from . import api


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


# Define the model for creating an item in an order
create_item_model = api.model(
    "Item",
    {
        "title": fields.String(required=True, description="The title of the item"),
        "amount": fields.Integer(required=True, description="The amount of the item"),
        "price": fields.Float(required=True, description="The price of the item"),
        "product_id": fields.String(
            required=True, description="The product ID of the item"
        ),
        "status": fields.String(
            description="The status of the item",
            enum=["INSTOCK", "LOWSTOCK", "OUTOFSTOCK"],
        ),
    },
)

# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Orders",
    {
        "name": fields.String(required=True, description="The name of the order"),
        "create_time": fields.DateTime(
            description="Creation time of the order"
        ),  # create_time": "2023-01-19T20:18:52.437475+00:00
        "address": fields.String(
            required=True, description="Delivery address of the order"
        ),
        "cost_amount": fields.Float(
            required=True, description="Total cost of the order"
        ),
        "status": fields.String(
            description="Status of the order",
            enum=["NEW", "PENDING", "APPROVED", "SHIPPED", "DELIVERED"],
        ),
        "user_id": fields.Integer(
            required=True, description="User ID associated with the order"
        ),
        "items": fields.List(
            fields.Nested(create_item_model), description="List of items in the order"
        ),
    },
)

Orders_model = api.inherit(
    "OrdersModel",
    create_model,
    {
        "order_id": fields.String(
            readOnly=True,
            description="The unique order_id assigned internally by service",
        ),
    },
)

# query string arguments
orders_args = reqparse.RequestParser()
orders_args.add_argument(
    "order_id", type=int, location="args", required=False, help="Get Order By Id"
)
orders_args.add_argument(
    "user_id", type=int, location="args", required=False, help="Get Order By User ID"
)
orders_args.add_argument(
    "status", type=str, location="args", required=False, help="Get Order By Status"
)
orders_args.add_argument(
    "name", type=str, location="args", required=False, help="Get Order By Name"
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
# CREATE A NEW ORDER
######################################################################
@api.route("/orders", strict_slashes=False)
class OrderCollection(Resource):
    @api.doc("create_order")
    @api.expect(create_model, validate=True)
    @api.response(201, "Order successfully created.")
    @api.response(400, "posted data was not valid")
    @api.marshal_with(Orders_model, code=201)
    def post(self):
        """
        Create a new Order
        """
        app.logger.info("Request to create an Order")

        # Deserialize the order data
        order_data = api.payload
        order = Order()
        order.deserialize(order_data)

        # print(order_data)

        # Save the order to the database
        order.create()

        # Process and save items if present
        if "items" in order_data:
            for item_data in order_data["items"]:
                item = Item()
                item_data["order_id"] = order.id
                item.deserialize(item_data)
                # item.order_id = order.id  # Set the order_id for each item
                item.create()

        app.logger.info("Order with ID [%s] created", order.id)

        location_url = url_for("order_collection", order_id=order.id, _external=True)

        # print(order.serialize())
        # print(location_url)

        return order.serialize(), status.HTTP_201_CREATED, {"Location": location_url}

    @api.doc("get orders")
    @api.expect(orders_args, validate=True)
    @api.marshal_with(Orders_model)
    def get(self):
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
        query_params = orders_args.parse_args()

        # This corresponds to "?order_id={some integer}"
        if query_params["order_id"]:
            order_id = query_params["order_id"]
            query = query.filter(Order.id == order_id)

        # Check for 'user_id'
        elif query_params["user_id"]:
            user_id = query_params["user_id"]
            query = query.filter(Order.user_id == user_id)

        # Check for 'status'
        elif query_params["status"]:
            status_ = query_params["status"]
            query = query.filter(Order.status == status_)

        elif query_params["name"]:
            name = query_params["name"]
            query = query.filter(Order.name == name)

        else:
            orders = Order.all()

        # Execute the query
        orders = query.all()

        # Return as an array of dictionaries
        results = [order.serialize() for order in orders]

        return results, status.HTTP_200_OK


######################################################################
#  PATH: /orders/{id}
######################################################################
@api.route("/orders/<order_id>")
@api.param("order_id", "The Order identifier")
class OrderResource(Resource):
    """
    OrderResource class
    """

    # ------------------------------------------------------------------
    # RETRIEVE an Order
    # ------------------------------------------------------------------
    @api.doc("get_order")
    @api.response(404, "Order not found")
    @api.marshal_with(Orders_model)
    def get(self, order_id):
        """Find an order by ID or Returns all of the Orders"""
        app.logger.info("Request for Read an Order")
        order = Order.find(order_id)

        if order is not None:
            results = order.serialize()
            return results, status.HTTP_200_OK
        else:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING ORDER
    # ------------------------------------------------------------------
    @api.doc("update_orders")
    @api.response(404, "Order not found")
    @api.response(400, "The posted Order data was not valid")
    @api.expect(Orders_model)
    @api.marshal_with(Orders_model)
    def put(self, order_id):
        """
        Update a Order

        This endpoint will update a Order based the body that is posted
        """
        app.logger.info("Request to Update a Order with id [%s]", order_id)

        order = Order.find(order_id)

        if not order:
            abort(status.HTTP_404_NOT_FOUND, "Order not found")

        # Update the 'name' and 'address' fields of the order
        data = api.payload
        if "name" in data:
            order.name = data["name"]
        if "address" in data:
            order.address = data["address"]
        if "status" in data:
            order.status = data["status"]

        order.update()

        return order.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE An order
    # ------------------------------------------------------------------
    @api.doc("delete_orders")
    @api.response(204, "order deleted")
    def delete(self, order_id):
        """
        Delete a order

        This endpoint will delete a order based the id specified in the path
        """
        app.logger.info("Request to Delete a order with id [%s]", order_id)
        order = Order.find(order_id)
        if order:
            order.delete()
            app.logger.info("order with id [%s] was deleted", order_id)

        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /orders/{id}/cancel
######################################################################
@api.route("/orders/<order_id>/cancel")
@api.param("order_id", "The order identifier")
class OrderCancelResource(Resource):
    """cancel actions on a order"""

    @api.doc("cancel_orders")
    @api.response(404, "order not found")
    @api.response(409, "The order is not available for cancel")
    def put(self, order_id):
        """
        cancel a order

        This endpoint will cancel a order and make it unavailable
        """
        app.logger.info("Request to cancel a order")
        order = Order.find(order_id)
        if not order:
            abort(status.HTTP_404_NOT_FOUND, "Order not found")
        else:
            order.status = "CANCELED"

        order.update()
        app.logger.info("order with id [%s] has been canceled!", order.id)

        return order.serialize(), status.HTTP_200_OK


######################################################################
# list items in an order PATH: /orders/{order_id}/items
######################################################################
@api.route("/orders/<int:order_id>/items")
@api.param("order_id", "The order identifier")
class ItemListResource(Resource):
    """
    ItemListResource class
    """

    @api.doc("get_Items")
    @api.response(404, "Items not found")
    @api.marshal_with(create_item_model)
    def get(self, order_id):
        """
        Retrieve Items
        This endpoint will return Items based on the Order's id
        """
        app.logger.info("Request to Retrieve items with order id [%s]", order_id)
        items = Item.find_by_order_id(order_id)
        if not items:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Items with order id '{order_id}' were not found.",
            )
        return [item.serialize() for item in items], status.HTTP_200_OK

    # POST /orders/{order_id}/items  PATH: /orders/{order_id}/items

    @api.doc("Add item to order with order_id as it's identifier")
    @api.response(
        400, "Bad Request: inconsistent customer_id in request payload and url"
    )
    @api.response(409, "Conflict: product already present in the order")
    @api.expect(create_model)
    @api.marshal_with(Orders_model, code=201)
    def post(self, order_id):
        app.logger.info("Request to create an Item for Order with id: %s", order_id)
        order = Order.find(order_id)
        if not order:
            api.abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

        item = Item()
        item.deserialize(api.payload)
        item.order_id = order_id
        item.amount = 1
        item.create()

        # order.items.append(item)
        # order.update()
        # item.order_id = order_id
        # item.update()

        message = item.serialize()
        app.logger.info("Item with ID [%s] created for order: [%s].", item.id, order.id)
        return item, status.HTTP_201_CREATED


#  path: /orders/{order_id}/items/{item_id} -


@api.route("/orders/<int:order_id>/items/<int:item_id>")
@api.param("order_id", "The Order identifier")
@api.param("item_id", "The Item identifier")
class OrderItemResource(Resource):
    # PUT /orders/{order_id}/items/{item_id} - updates an Order Item record in the database
    @api.expect(create_item_model, validate=True)
    @api.marshal_with(create_item_model)
    def put(self, order_id, item_id):
        """
        Adds an item by item ID to an existing order
        This endpoint will add an item (specified by item_id) to the specified order
        """
        app.logger.info("Request to update item with ID %d", item_id)
        order = Order.find(order_id)
        if not order:
            api.abort(status.HTTP_404_NOT_FOUND, "Order not found")

        # Check if the item exists
        data = api.payload
        item = Item.find(item_id)
        if item is None:
            # Handle the case when the order does not exist
            api.abort(status.HTTP_404_NOT_FOUND, "Item not found")

        if "title" in data:
            item.title = data["title"]
        if "amount" in data:
            item.amount = data["amount"]
        if "status" in data:
            item.status = data["status"]

        item.update()
        order.update()

        return item.serialize(), status.HTTP_202_ACCEPTED

    """
    Show a single Order Item and lets you delete them
    """

    # DELETE AN ITEM FROM AN ORDER, deletes an Order Item record in the database
    @api.doc("delete_item_from_order")
    @api.response(404, "Item not found")
    def delete(self, order_id, item_id):
        """
        Delete one item in one order
        """
        app.logger.info(
            "Request for deleting item with ID [%s] from order [%s]", item_id, order_id
        )
        order = Order.find(order_id)
        if order:
            item = Item.find(item_id)
            if (item is not None) and (item.order_id == order_id):
                item.delete()
                app.logger.info(
                    "Item with ID [%s] and order ID [%s] delete complete.",
                    item_id,
                    order_id,
                )
                return "", status.HTTP_204_NO_CONTENT

        return make_response("", status.HTTP_204_NO_CONTENT)


# ######################################################################
# #  R E S T   A P I   E N D P O I N T S
# ######################################################################
# ######################################################################
# # FIND AN ORDER BY ID OR RETURN ALL ORDERS
# ######################################################################
# @app.route("/orders", methods=["GET"])
# def list_orders():
#     """Find an order by ID or Returns all of the Orders"""
#     app.logger.info("Request for Order list")
#     print(f"request.args = {request.args.to_dict(flat=False)}")

#     orders = []  # A list of all orders satisfying requirements

#     # Process the query string if any
#     # Supported formats:
#     # - All orders: "?"
#     # - A particular order:
#     #       "?order_id={some integer}" or
#     #       "?order_id={some integer}&user_id={user id having this order}"
#     # - All orders of a particular user ID: "?user_id={some integer}"

#     # This corresponds to "?"
#     if len(request.args) == 0:
#         orders = Order.all()

#     # This corresponds to "?order_id={some integer}"
#     elif "order_id" in request.args and len(request.args) == 1:
#         order_id = request.args.get("order_id")
#         orders.append(Order.find(order_id))

#     # This corresponds to "?order_id={some integer}&user_id={user id having this order}"
#     elif (
#         "order_id" in request.args
#         and "user_id" in request.args
#         and len(request.args) == 2
#     ):
#         order_id = request.args.get("order_id")
#         user_id = request.args.get("user_id")
#         order = Order.find(order_id)
#         if int(user_id) == order.user_id:
#             orders.append(order)

#     # This corresponds to "?user_id={some integer}"
#     elif "user_id" in request.args and len(request.args) == 1:
#         user_id = request.args.get("user_id")
#         orders = Order.find_by_user_id(user_id)

#     # Return as an array of dictionaries
#     results = [order.serialize() for order in orders]

#     return make_response(jsonify(results), status.HTTP_200_OK)


# @app.route("/orders/<order_id>", methods=["GET"])
# def read_an_order(order_id):
#     """Find an order by ID or Returns all of the Orders"""
#     app.logger.info("Request for Read an Order")
#     order = Order.find(order_id)

#     if order is not None:
#         results = order.serialize()
#         return make_response(jsonify(results), status.HTTP_200_OK)
#     else:
#         abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")


# @app.route("/orders/orders_by_status", methods=["GET"])
# def list_orders_by_status():
#     """List orders filtered by status (user_id field added)"""
#     status_param = request.args.get("status")
#     user_id = request.args.get("user_id")

#     if status_param and user_id:
#         # Filter orders by the specified status and user_id
#         orders = Order.query.filter_by(status=status_param, user_id=user_id).all()
#     elif status_param:
#         # Filter orders by the specified status
#         orders = Order.query.filter_by(status=status_param).all()
#     else:
#         # If no status is specified, return all orders
#         orders = Order.query.all()

#     results = [order.serialize() for order in orders]
#     return jsonify(results), 200


# ######################################################################
# # CREATE A NEW ORDER
# ######################################################################
# @api.route("/orders", strict_slashes=False)
# class OrderCollection(Resource):
#     def get(self):
#         return {}

#     @api.doc("create_order")
#     @api.expect(create_model, validate=True)
#     @api.response(201, "Order successfully created.")
#     @api.response(400, "posted data was not valid")
#     @api.marshal_with(Orders_model, code=201)
#     def post(self):
#         """
#         Create a new Order
#         """
#         app.logger.info("Request to create an Order")

#         # Deserialize the order data
#         order_data = api.payload
#         order = Order()
#         order.deserialize(order_data)

#         # Save the order to the database
#         order.create()

#         # Process and save items if present
#         if "items" in order_data:
#             for item_data in order_data["items"]:
#                 item = Item()
#                 item.deserialize(item_data)
#                 item.order_id = order.id  # Set the order_id for each item
#                 item.create()

#         app.logger.info("Order with ID [%s] created", order.id)
#         return order.serialize(), status.HTTP_201_CREATED


# # delete orders
# @api.route("/orders/<int:order_id>")
# @api.param("order_id", "The Order identifier")
# class OrderResource(Resource):
#     @api.doc("delete_order")
#     @api.response(204, "Order deleted")
#     def delete(self, order_id):
#         """
#         Delete an order by order ID.
#         """
#         app.logger.info("Request to delete an order with ID %s", order_id)

#         order = Order.find(order_id)
#         if not order:
#             api.abort(404, "Order not found")

#         order.delete()
#         return "", status.HTTP_204_NO_CONTENT


# # create an item
# ######################################################################
# # CREATE A NEW ITEM IN ORDER
# ######################################################################
# @app.route("/orders/<order_id>/items", methods=["POST"])
# def create_item_in_an_order(order_id):
#     """
#     Create an item on an order


#     This endpoint will add a new item to an order.
#     """
#     app.logger.info("Request to create an Item for Order with id: %s", order_id)
#     order = Order.find(order_id)
#     if not order:
#         abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

#     item = Item()
#     item.deserialize(request.get_json())
#     item.order_id = order_id
#     item.amount = 1
#     item.create()

#     # order.items.append(item)
#     # order.update()
#     item.order_id = order_id
#     item.update()

#     message = item.serialize()
#     location_url = url_for(
#         "create_item_in_an_order", order_id=order_id, item_id=item.id, _external=True
#     )
#     # print(location_url)
#     app.logger.info("Item with ID [%s] created for order: [%s].", item.id, order.id)
#     return make_response(
#         jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}
#     )


# ######################################################################
# # UPDATE ITEM BY item id IN ORDER
# ######################################################################
# @app.route("/orders/<order_id>/items/<item_id>", methods=["PUT"])
# def update_item(order_id, item_id):
#     """
#     Adds an item by item ID to an existing order
#     This endpoint will add an item (specified by item_id) to the specified order
#     """
#     app.logger.info("Request to update item with ID %d", item_id)
#     check_content_type("application/json")

#     order = Order.find(order_id)
#     if not order:
#         abort(status.HTTP_404_NOT_FOUND, "Order not found")

#     # Check if the item exists
#     data = request.get_json()

#     item = Item.find(item_id)
#     if item is None:
#         # Handle the case when the order does not exist
#         return make_response(jsonify(error="Item not found"), status.HTTP_404_NOT_FOUND)

#     if "title" in data:
#         item.title = data["title"]
#     if "amount" in data:
#         item.amount = data["amount"]
#     if "status" in data:
#         item.status = data["status"]

#     item.update()
#     order.update()

#     location_url = url_for(
#         "update_item", order_id=order_id, item_id=item_id, _external=True
#     )

#     return make_response(
#         jsonify(item.serialize()),
#         status.HTTP_202_ACCEPTED,
#         {"Location": location_url},
#     )


# ######################################################################
# # List one item in an order
# ######################################################################
# @app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["GET"])
# def list_one_item_in_one_order(order_id, item_id):
#     """
#     Get one item in one order
#     """
#     app.logger.info("Request for Item list in one order")
#     # order_id = request.args.get("order_id")
#     order = Order.find(order_id)
#     order = order.serialize()
#     results = order["items"]
#     for item in results:
#         if item["id"] == item_id:
#             return make_response(jsonify(item), status.HTTP_200_OK)
#     return make_response(jsonify(error="Item not in Order"), status.HTTP_404_NOT_FOUND)
#     # Process the query string if any


# ######################################################################
# # List one item in an order
# ######################################################################
# @app.route("/orders/<int:order_id>/items/<int:item_id>", methods=["DELETE"])
# def delete_one_item_in_one_order(order_id, item_id):
#     """
#     Delete one item in one order
#     """
#     app.logger.info("Request for Item list in one order")
#     # order_id = request.args.get("order_id")
#     order = Order.find(order_id)
#     if order:
#         order = order.serialize()
#         item = Item.find(item_id)
#         if (item is not None) and (item.order_id == order_id):
#             item.delete()
#             app.logger.info(
#                 "Item with ID [%s] and order ID [%s] delete complete.",
#                 item_id,
#                 order_id,
#             )

#     return make_response("", status.HTTP_204_NO_CONTENT)


# ######################################################################
# # UPDATE AN ORDER
# ######################################################################
# @app.route("/orders/<int:order_id>", methods=["PUT"])
# def update_an_order(order_id):
#     """
#     Update information (e.g., address, name) for an order.
#     """
#     app.logger.info("Update order information with ID: %d", order_id)

#     # Find the order by ID
#     order = Order.find(order_id)

#     if not order:
#         abort(status.HTTP_404_NOT_FOUND, "Order not found")

#     # Update the 'name' and 'address' fields of the order
#     data = request.get_json()
#     if "name" in data:
#         order.name = data["name"]
#     if "address" in data:
#         order.address = data["address"]
#     if "status" in data:
#         order.status = data["status"]

#     order.update()

#     return make_response(
#         jsonify(order.serialize()), status.HTTP_200_OK, {"Updated_order_id": order_id}
#     )


# ######################################################################
# # CANCEL AN ORDER
# ######################################################################
# @app.route("/orders/<int:order_id>/cancel", methods=["PUT"])
# def cancel_an_order(order_id):
#     """
#     Cancel an order by order ID.
#     """
#     app.logger.info("Cancel an order with order ID %d", order_id)
#     order = Order.find(order_id)

#     if not order:
#         abort(status.HTTP_404_NOT_FOUND, "Order not found")
#     else:
#         order.status = "CANCELED"

#     order.update()
#     return make_response(jsonify(order.serialize()), status.HTTP_200_OK)
