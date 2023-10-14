"""
My Service

Describe what your service does here
"""

from flask import jsonify, request, url_for, abort
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
    return (
        "Reminder: return some useful information in json format about the service here",
        status.HTTP_200_OK,
    )


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

# Place your REST API code here ...

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()

    # Check if the required fields are present in the JSON data
    required_fields = ["name", "address", "cost_amount","create_time",
  "status","items"]

    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"Missing required field: {field}"}), status.HTTP_400_BAD_REQUEST

    # Create a new order
    order = Order()
    order.deserialize(data)
    order.create()

    return jsonify(order.serialize()), status.HTTP_201_CREATED
