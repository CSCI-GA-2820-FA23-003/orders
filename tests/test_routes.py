"""
TestYourResourceModel API Service Test Suite


Test cases can be run with the following:
 nosetests -v --with-spec --spec-color
 coverage report -m
"""
import os
import logging
from unittest import TestCase
from datetime import datetime
from service import app
from service.models import OrderStatus, ItemStatus, Order, db, init_db
from service.common import status  # HTTP Status Codes
from tests.factories import OrderFactory, ItemFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


BASE_URL = "api/orders"


######################################################################
#  T E S T   C A S E S
######################################################################
class TestOrderService(TestCase):
    """Order Service Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        init_db(app)

    @classmethod
    def tearDownClass(cls):
        """Runs once before test suite"""

    def setUp(self):
        """Runs before each test"""
        db.session.query(Order).delete()  # clean up the last tests
        db.session.commit()

        self.client = app.test_client()

    def tearDown(self):
        """Runs once after each test case"""
        db.session.remove()

    ######################################################################
    #  H E L P E R   M E T H O D S
    ######################################################################

    def _create_orders(self, count, user_id=None):
        """Factory method to create orders in bulk"""
        orders = []
        for _ in range(count):
            if user_id:
                order = OrderFactory(user_id=user_id)
            else:
                order = OrderFactory()
            resp = self.client.post(BASE_URL, json=order.serialize())
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Order",
            )
            new_order = resp.get_json()
            order.id = new_order["id"]
            orders.append(order)
        return orders

    def _create_items_in_existing_order(self, order_id, count):
        """Factory method to create items in an existing order in bulk"""
        items = []
        for _ in range(count):
            item = ItemFactory()
            resp = self.client.post(
                f"/api/orders/{order_id}/items",
                json=item.serialize(),
                content_type="application/json",
            )
            self.assertEqual(
                resp.status_code,
                status.HTTP_201_CREATED,
                "Could not create test Item in existing Order",
            )
            new_item = resp.get_json()
            item.order_id = new_item["order_id"]
            item.id = new_item["id"]
            item.amount = new_item["amount"]
            items.append(item)
        return items

    ######################################################################
    #  P L A C E   T E S T   C A S E S   H E R E
    ######################################################################
    def test_create_item_in_order(self):
        """It should create an item in an order"""
        # Create a test order first
        order = self._create_orders(1)[0]

        # Define item data
        item_data = {
            "title": "Test Item",
            "amount": 5,
            "price": 10.99,
            "product_id": 123,
            "status": "NEW",
        }

        # Add the item to the order
        response = self.client.post(
            f"/api/orders/{order.id}/items",
            json=item_data,
            content_type="application/json",
        )

        # Assert that the item was added successfully
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        data = response.get_json()
        self.assertEqual(data["order_id"], order.id)
        self.assertEqual(data["title"], item_data["title"])

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def test_get_order_list(self):
        """It should Get a list of Orders"""
        self._create_orders(5)
        resp = self.client.get(BASE_URL)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 5)

        # TEST INVALID ORDER
        non_exist_order_id = -1
        resp = self.client.get(f"/api/orders/{non_exist_order_id}")
        self.assertEqual(
            resp.status_code, status.HTTP_404_NOT_FOUND, "Invalid Order ID"
        )

    def test_get_order_by_id(self):
        """It should Get an Order by ID"""
        orders = self._create_orders(3)
        resp = self.client.get(BASE_URL, query_string=f"order_id={orders[1].id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()[0]
        # print(data)
        self.assertEqual(data["id"], orders[1].id, "Id does not match")

    def test_get_order_by_id_with_user_id(self):
        """It should get an Order by ID only when the user of the specified
        user ID has the Order"""
        user1_id = 1000
        user_na_id = 1001
        user1_orders = self._create_orders(1, user_id=user1_id)
        order_id = user1_orders[0].id

        # Subtest #1: Check when the user ID matches with the order ID.
        resp = self.client.get(
            BASE_URL, query_string=f"user_id={user1_id}&order_id={order_id}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 1)
        self.assertEqual(order_id, data[0]["id"])

        # Subtest #2: Check when the user ID does not match the order ID.
        resp = self.client.get(
            BASE_URL, query_string=f"user_id={user_na_id}&order_id={order_id}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_get_order_by_user_id(self):
        """It should get all Orders belonging to a user whose user ID is specified"""
        user1_id = 1000
        user2_id = 1001
        user_na_id = 1002
        user1_orders = self._create_orders(3, user_id=user1_id)
        self._create_orders(4, user_id=user2_id)

        # Subtest #1: Check all orders of a user is returned.
        resp = self.client.get(BASE_URL, query_string=f"user_id={user1_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        # print(data)
        self.assertEqual(len(data), len(user1_orders))
        expect_ids = [order.id for order in user1_orders]
        for ret_order in data:
            self.assertTrue(ret_order["id"] in expect_ids)

        # Subtest #2: Check an empty list is returned when a non-existent user ID is supplied.
        resp = self.client.get(BASE_URL, query_string=f"user_id={user_na_id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), 0)

    def test_read_an_order(self):
        """It should test get one order"""
        orders = self._create_orders(3)
        resp = self.client.get(f"api/orders/{orders[0].id}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["id"], orders[0].id, "Id does not match")
        non_existent_order_id = -1  # An order ID that does not exist

        response = self.client.get(f"api/orders/{non_existent_order_id}")

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{non_existent_order_id}' was not found.",
        )

    def test_content_type(self):
        """It should return error with invalid payload type"""
        order = OrderFactory()
        logging.debug("Test order: %s", order.serialize())
        resp = self.client.post(BASE_URL, data=b"abc")
        # self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_create_order(self):
        """It should Create a new Order"""
        order = OrderFactory()
        # logging.debug("Test order: %s", order.serialize())
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # print(order.serialize())

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_order = resp.get_json()
        # print(new_order)
        self.assertEqual(new_order["name"], order.name, "Names does not match")
        self.assertEqual(
            datetime.fromisoformat(new_order["create_time"]),
            order.create_time,
            "Time does not match",
        )
        self.assertEqual(new_order["address"], order.address, "Address does not match")
        self.assertEqual(
            new_order["cost_amount"], order.cost_amount, "Cost does not match"
        )
        self.assertEqual(
            new_order["status"], order.status.name, "Status does not match"
        )

        # Check that the location header was correct by getting it
        # ("test_routes.py: location = %s" % location)
        resp = self.client.get(location, content_type="application/json")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_order = resp.get_json()[0]
        # print(new_order)
        self.assertEqual(new_order["name"], order.name, "Names does not match")
        self.assertEqual(
            datetime.fromisoformat(new_order["create_time"]),
            order.create_time,
            "Time does not match",
        )
        self.assertEqual(new_order["address"], order.address, "Address does not match")
        self.assertEqual(
            new_order["cost_amount"], order.cost_amount, "Cost does not match"
        )
        self.assertEqual(
            new_order["status"], order.status.name, "Status does not match"
        )

    def test_create_order_with_items(self):
        """It should Create a new Order with item"""
        order = OrderFactory()
        order.items = [ItemFactory()]
        # logging.debug("Test order: %s", order.serialize())
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # print(order.serialize())

        # Make sure location header is set
        location = resp.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_order = resp.get_json()
        # print(new_order)
        self.assertEqual(new_order["name"], order.name, "Names does not match")
        self.assertEqual(
            datetime.fromisoformat(new_order["create_time"]),
            order.create_time,
            "Time does not match",
        )
        self.assertEqual(new_order["address"], order.address, "Address does not match")
        self.assertEqual(
            new_order["cost_amount"], order.cost_amount, "Cost does not match"
        )
        self.assertEqual(
            new_order["status"], order.status.name, "Status does not match"
        )

    def test_create_item_in_order(self):
        """It should create an item in an order"""
        # Create a test order and item
        order = self._create_orders(1)[0]
        item = ItemFactory(status=ItemStatus.INSTOCK)
        db.session.add(item)
        db.session.commit()

        response = self.client.post(
            f"api/orders/{order.id}/items",
            json=item.serialize(),
            content_type="application/json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        data = response.get_json()
        self.assertIsNotNone(data["id"])
        self.assertEqual(data["order_id"], int(order.id))
        self.assertEqual(data["product_id"], int(item.product_id))
        self.assertEqual(data["amount"], 1)
        self.assertEqual(data["price"], item.price)

        # test order not found
        non_existent_order_id = -1  # An order ID that does not exist

        response = self.client.post(
            f"/api/orders/{non_existent_order_id}/items",
            content_type="application/json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{non_existent_order_id}' was not found.",
        )

    def test_list_items_in_one_order(self):
        """It should list items in one order."""
        # Create an order with items
        order = self._create_orders(1)[0]
        self._create_items_in_existing_order(order.id, 3)

        resp = self.client.get(
            f"/api/orders/{order.id}/items",
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        # print(data)

        # Verify that items are listed only if the order exists
        self.assertEqual(len(data), 3)

        non_exist_order_id = 999
        resp = self.client.get(
            f"/api/orders/{non_exist_order_id}/items",
            content_type="application/json",
        )

        self.assertEqual(
            resp.status_code,
            status.HTTP_404_NOT_FOUND,
            f"Order with id '{non_exist_order_id}' was not found.",
        )

    def test_list_one_item_in_one_order(self):
        """It should list one item in one order."""
        # Create an order with items
        order = self._create_orders(1)[0]
        item = self._create_items_in_existing_order(order.id, 3)[0]

        resp = self.client.get(
            f"/api/orders/{order.id}/items/{item.id}",
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        # print(data)
        self.assertEqual(data["order_id"], int(order.id), "Order id does not match")
        self.assertEqual(data["id"], item.id, "Item id does not match")
        # Verify that there are items in the response
        # self.assertIn("items", data)
        # print(data)

        non_exist_item_id = 999
        resp = self.client.get(
            f"/api/orders/{order.id}/items/{non_exist_item_id}",
            content_type="application/json",
        )

        # Verify that items are listed only if the order exists
        self.assertEqual(
            resp.status_code, status.HTTP_404_NOT_FOUND, "Item not in Order"
        )

    def test_delete_one_item_in_one_order(self):
        """It should delete one item in one order."""
        # Create an order with items
        order = self._create_orders(1)[0]
        item = self._create_items_in_existing_order(order.id, 3)[0]

        resp = self.client.delete(
            f"/api/orders/{order.id}/items/{item.id}",
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        non_exist_order_id = 999
        resp = self.client.delete(
            f"/api/orders/{non_exist_order_id}/items/{item.id}",
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        non_exist_item_id = 999
        resp = self.client.delete(
            f"/api/orders/{order.id}/items/{non_exist_item_id}",
            content_type="application/json",
        )

        # Verify that items are listed only if the order exists
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_an_order(self):
        """It should Update an Order."""
        order = OrderFactory()

        # Create the order.
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_order = resp.get_json()
        order_id = new_order["id"]

        # Update the order.
        updated_data = {
            "name": "Updated Name",
            "address": "Updated Address",
            "status": "DELIVERED",
        }
        resp = self.client.put(
            f"{BASE_URL}/{order_id}",
            json=updated_data,
            content_type="application/json",
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        # Verify that the order was updated.
        updated_order = resp.get_json()
        self.assertEqual(updated_order["name"], "Updated Name", "Names do not match.")
        self.assertEqual(
            updated_order["address"], "Updated Address", "Addresses do not match."
        )
        self.assertEqual(updated_order["status"], "DELIVERED", "Status do not match.")

        # Choose an order ID that does not exist in your database.
        nonexistent_order_id = 9999  # Replace with an ID that doesn't exist.

        # Attempt to update the nonexistent order.
        updated_data = {"name": "Updated Name", "address": "Updated Address"}
        resp = self.client.put(
            f"{BASE_URL}/{nonexistent_order_id}",
            json=updated_data,
            content_type="application/json",
        )

        # Verify that the response is a 404 error.
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_and_cancel_an_order(self):
        """It should delete an Order, or cancel an order."""
        order = OrderFactory(status=OrderStatus.NEW)

        # Create the order.
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_order = resp.get_json()
        order_id = new_order["id"]

        # Delete the order.
        resp = self.client.delete(
            f"{BASE_URL}/{order_id}", content_type="application/json"
        )

        # Verify that the order was deleted successfully.
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        # Choose an order ID that does not exist in your database.
        nonexistent_order_id = 9999  # Replace with an ID that doesn't exist.

        # Attempt to delete the nonexistent order.
        resp = self.client.delete(
            f"{BASE_URL}/{nonexistent_order_id}", content_type="application/json"
        )

        # Verify that the response is a 204 no content.
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

        order = OrderFactory(status=OrderStatus.NEW)

        # Create the order.
        resp = self.client.post(
            BASE_URL, json=order.serialize(), content_type="application/json"
        )
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        new_order = resp.get_json()
        order_id = new_order["id"]
        self.assertEqual(new_order["status"], "NEW")

        # Delete the order.
        resp = self.client.put(
            f"{BASE_URL}/{order_id}/cancel", content_type="application/json"
        )

        # Verify that the order was deleted successfully.
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_order = resp.get_json()
        self.assertEqual(new_order["status"], "CANCELED")

        # Choose an order ID that does not exist in your database.
        nonexistent_order_id = 9999  # Replace with an ID that doesn't exist.

        # Attempt to delete the nonexistent order.
        resp = self.client.put(
            f"{BASE_URL}/{nonexistent_order_id}/cancel", content_type="application/json"
        )

        # Verify that the response is a 404 error.
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

    def test_update_item_by_id(self):
        """It should update an item to an order by item ID and amount"""

        # Create a test order and item
        order = self._create_orders(1)[0]
        item = self._create_items_in_existing_order(order.id, 3)[0]

        resp = self.client.get(
            f"/api/orders/{order.id}/items/{item.id}",
            content_type="application/json",
        )

        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        order_id = order.id
        item_id = item.id

        # print(order)

        # Update the item
        updated_data = {"title": "Updated Title", "amount": 20, "status": "LOWSTOCK"}

        response = self.client.put(
            f"/api/orders/{-1}/items/{item_id}",
            json=updated_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.put(
            f"/api/orders/{order_id}/items/{item_id}",
            json=updated_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)

        # Verify the item was updated
        updated_item = response.get_json()
        self.assertEqual(updated_item["title"], "Updated Title")
        self.assertEqual(updated_item["amount"], 20)
        self.assertEqual(updated_item["status"], "LOWSTOCK")

        # Test updating a non-existent item
        nonexistent_item_id = 9999  # Adjust as necessary
        response = self.client.put(
            f"/api/orders/{order_id}/items/{nonexistent_item_id}",
            json=updated_data,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_list_orders(self):
        """It should list all orders and list orders filtered by a specific status/user_id."""
        # Explicitly create orders with 'NEW' status
        new_order1 = OrderFactory(status=OrderStatus.NEW)
        new_order2 = OrderFactory(status=OrderStatus.NEW)
        db.session.add(new_order1)
        db.session.add(new_order2)
        db.session.commit()

        # Test for NEW status
        response = self.client.get(BASE_URL, query_string="status=NEW")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        # Check if all orders in response have 'NEW' status
        self.assertTrue(all(order["status"] == "NEW" for order in data))

        # Test for APPROVED status
        approved_order = OrderFactory(status=OrderStatus.APPROVED)
        db.session.add(approved_order)
        db.session.commit()

        # It should list orders filtered by a specific status and user ID
        user_id = approved_order.user_id
        name = approved_order.name

        # Test for APPROVED status with specific user ID
        response = self.client.get(
            BASE_URL, query_string=f"status=APPROVED&user_id={user_id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(
            all(
                order["status"] == "APPROVED" and order["user_id"] == user_id
                for order in data
            )
        )
        self.assertEqual(len(data), 1)

        response = self.client.get(
            BASE_URL, query_string=f"status=APPROVED&name={name}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(
            all(
                order["status"] == "APPROVED" and order["name"] == name
                for order in data
            )
        )
        self.assertEqual(len(data), 1)

        # It should list all orders when no status filter is applied
        self._create_orders(2)  # Create some orders

        # Test for all orders
        response = self.client.get(f"{BASE_URL}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertTrue(len(data) >= 2)  # Check that at least 2 orders are returned
