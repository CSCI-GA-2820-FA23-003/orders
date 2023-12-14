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
from flask import request, url_for, abort, make_response
from flask_restx import Resource, fields, reqparse
from service.common import status  # HTTP Status Codes
from service.models import Order, Item


# Import Flask application
from . import app
from . import api


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Index page"""
    return app.send_static_file("index.html")


# Define the model for creating an item in an order
create_item_model = api.model(
    "Item",
    {
        "title": fields.String(required=False, description="The title of the item"),
        "amount": fields.Integer(required=False, description="The amount of the item"),
        "price": fields.Float(required=False, description="The price of the item"),
        "product_id": fields.Integer(
            required=False, description="The product ID of the item"
        ),
        "order_id": fields.Integer(
            required=False, description="The order ID of the item"
        ),
        "status": fields.String(description="The status of the item"),
    },
)

Items_model = api.inherit(
    "ItemsModel",
    create_item_model,
    {
        "id": fields.String(
            readOnly=True,
            description="The unique item_id assigned internally by service",
        ),
    },
)

# Define the model so that the docs reflect what can be sent
create_model = api.model(
    "Orders",
    {
        "name": fields.String(required=False, description="The name of the order"),
        "create_time": fields.DateTime(
            description="Creation time of the order"
        ),  # create_time": "2023-01-19T20:18:52.437475+00:00
        "address": fields.String(
            required=False, description="Delivery address of the order"
        ),
        "cost_amount": fields.Float(
            required=False, description="Total cost of the order"
        ),
        "status": fields.String(
            description="Status of the order",
            enum=["NEW", "PENDING", "APPROVED", "SHIPPED", "DELIVERED"],
        ),
        "user_id": fields.Integer(
            required=False, description="User ID associated with the order"
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
        "id": fields.String(
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
    """order collection"""

    @api.doc("create_order")
    @api.expect(create_model)
    @api.response(201, "Order successfully created.")
    @api.marshal_with(Orders_model, code=201)
    def post(self):
        """
        Create a new Order
        """
        app.logger.info("Request to create an Order")

        check_content_type("application/json")

        # Deserialize the order data
        order_data = api.payload
        order = Order()
        order.deserialize(order_data)

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

        # print("After creating:", order.serialize())
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
        if query_params["user_id"]:
            user_id = query_params["user_id"]
            query = query.filter(Order.user_id == user_id)

        # Check for 'status'
        if query_params["status"]:
            status_ = query_params["status"]
            query = query.filter(Order.status == status_)

        if query_params["name"]:
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

        print(order_id, order)

        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

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


@api.route("/orders/<order_id>/items/<item_id>")
@api.param("order_id", "The Order identifier")
@api.param("item_id", "The Item identifier")
class OrderItemResource(Resource):
    """order item res"""

    @api.doc("get order item")
    @api.response(404, "Item not in Order")
    @api.marshal_with(Items_model)
    def get(self, order_id, item_id):
        """list an item in an order"""
        app.logger.info("Request for Read an Order")

        order = Order.find(order_id)
        order = order.serialize()
        results = order["items"]
        for item in results:
            if item["id"] == int(item_id):
                print("found")
                return item, status.HTTP_200_OK

        # api.abort(status.HTTP_404_NOT_FOUND, "Item not in Order")
        return "", status.HTTP_404_NOT_FOUND, "Item not in Order"

    # PUT /orders/{order_id}/items/{item_id} - updates an Order Item record in the database
    @api.doc("update order item")
    @api.expect(create_item_model, validate=True)
    @api.marshal_with(create_item_model)
    def put(self, order_id, item_id):
        """
        updates an item by item_id in an order
        This endpoint will updates an item (specified by item_id) to the specified order
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

        print(data)

        if "title" in data:
            item.title = data["title"]
        if "amount" in data:
            item.amount = data["amount"]
        if "status" in data:
            item.status = data["status"]

        item.update()
        order.update()

        location_url = url_for(
            "order_item_resource", order_id=order_id, item_id=item_id, _external=True
        )

        return (
            item.serialize(),
            status.HTTP_202_ACCEPTED,
            {"Location": location_url},
        )

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
            if (item is not None) and (str(item.order_id) == order_id):
                item.delete()
                app.logger.info(
                    "Item with ID [%s] and order ID [%s] delete complete.",
                    item_id,
                    order_id,
                )
                return "", status.HTTP_204_NO_CONTENT

        return make_response("", status.HTTP_204_NO_CONTENT)


@api.route("/orders/<order_id>/items")
@api.param("order_id", "The order identifier")
class ItemListResource(Resource):
    """
    ItemListResource class
    """

    @api.doc("get_Items")
    @api.response(404, "Items not found")
    @api.marshal_with(Items_model)
    def get(self, order_id):
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

            return results, status.HTTP_200_OK

        abort(status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found.")

    @api.doc("create_items")
    @api.response(404, "Order ID not found")
    @api.marshal_with(Items_model)
    def post(self, order_id):
        """
        Create an item on an order


        This endpoint will add a new item to an order.
        """
        app.logger.info("Request to create an Item for Order with id: %s", order_id)

        order = Order.find(order_id)
        if not order:
            abort(
                status.HTTP_404_NOT_FOUND, f"Order with id '{order_id}' was not found."
            )

        item = Item()
        item.deserialize(self.api.payload)
        item.order_id = order_id
        item.amount = 1
        item.create()

        # order.items.append(item)
        order.update()
        # item.order_id = order_id
        # item.update()

        message = item.serialize()
        location_url = url_for(
            "order_item_resource",
            order_id=order_id,
            item_id=item.id,
            _external=True,
        )

        # print(location_url)
        app.logger.info("Item with ID [%s] created for order: [%s].", item.id, order.id)

        return message, status.HTTP_201_CREATED, {"Location": location_url}
