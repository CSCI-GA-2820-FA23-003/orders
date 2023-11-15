"""
Test cases for Order Model

"""
import logging
import unittest
import os
from datetime import datetime
from service import app
from service.models import Order, Item, DataValidationError, db
from tests.factories import OrderFactory, ItemFactory
from datetime import datetime

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  Order   M O D E L   T E S T   C A S E S
######################################################################
class TestOrder(unittest.TestCase):
    """Test Cases for Order Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Order.init_db(app)
        Item.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""

    def setUp(self):
        """This runs before each test"""
        db.session.query(Order).delete()  # clean up the last tests
        db.session.query(Item).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_an_order(self):
        """It should Create an Order and assert that it exists"""
        fake_order = OrderFactory()
        # pylint: disable=unexpected-keyword-arg
        order = Order(
            name=fake_order.name,
            address=fake_order.address,
            cost_amount=fake_order.cost_amount,
            status=fake_order.status,
            items=fake_order.items,
            user_id=fake_order.user_id,
        )
        self.assertIsNotNone(order)
        self.assertEqual(order.id, None)
        self.assertEqual(order.name, fake_order.name)
        self.assertEqual(order.address, fake_order.address)
        self.assertEqual(order.cost_amount, fake_order.cost_amount)
        self.assertEqual(order.status, fake_order.status)
        self.assertEqual(order.items, fake_order.items)
        self.assertEqual(order.user_id, fake_order.user_id)

    def test_add_a_order(self):
        """It should Create an order and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

    def test_add_an_item(self):
        """It should Create an item and add it to the database"""
        items = Item.all()
        self.assertEqual(items, [])
        item = ItemFactory()
        item.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(item.id)
        items = Item.all()
        self.assertEqual(len(items), 1)

    def test_read_order(self):
        """It should Read an order"""
        order = OrderFactory()
        order.create()

        # Read it back
        found_order = Order.find(order.id)
        self.assertEqual(found_order.id, order.id)
        self.assertEqual(found_order.name, order.name)
        self.assertEqual(found_order.address, order.address)
        self.assertEqual(found_order.cost_amount, order.cost_amount)
        self.assertEqual(found_order.status, order.status)
        self.assertEqual(found_order.items, [])
        self.assertEqual(found_order.user_id, order.user_id)

    def test_update_order(self):
        """It should Update an order"""
        order = OrderFactory(name="Unknown")
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        self.assertEqual(order.name, "Unknown")

        # Fetch it back
        order = Order.find(order.id)
        order.name = "Known"
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        self.assertEqual(order.name, "Known")

    def test_delete_an_order(self):
        """It should Delete an order from the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)
        order = orders[0]
        order.delete()
        orders = Order.all()
        self.assertEqual(len(orders), 0)

    def test_list_all_orders(self):
        """It should List all Orders in the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        for order in OrderFactory.create_batch(5):
            order.create()
        # Assert that there are not 5 orders in the database
        orders = Order.all()
        self.assertEqual(len(orders), 5)

    def test_find_order_by_name(self):
        """It should Find an Order by name"""
        order = OrderFactory()
        order.create()

        # Fetch it back by name
        same_order = Order.find_by_name(order.name)[0]
        self.assertEqual(same_order.id, order.id)
        self.assertEqual(same_order.name, order.name)

    def test_find_item_by_name(self):
        """It should Find an Item by title"""
        item = ItemFactory()
        item.create()

        # Fetch it back by name
        same_item = Item.find_by_title(item.title)[0]
        self.assertEqual(same_item.id, item.id)
        self.assertEqual(same_item.title, item.title)

    def test_serialize_an_order(self):
        """It should Serialize an order"""
        order = OrderFactory()
        item = ItemFactory()
        order.items.append(item)
        serial_order = order.serialize()
        self.assertEqual(serial_order["id"], order.id)
        self.assertEqual(serial_order["name"], order.name)
        self.assertEqual(
            datetime.fromisoformat(serial_order["create_time"]), order.create_time
        )

        self.assertEqual(serial_order["address"], order.address)
        self.assertEqual(serial_order["cost_amount"], order.cost_amount)
        self.assertEqual(serial_order["status"], order.status.name)
        self.assertEqual(len(serial_order["items"]), 1)
        self.assertEqual(serial_order["user_id"], order.user_id)
        items = serial_order["items"]
        self.assertEqual(items[0]["id"], item.id)
        self.assertEqual(items[0]["order_id"], item.order_id)
        self.assertEqual(items[0]["title"], item.title)
        self.assertEqual(items[0]["amount"], item.amount)
        self.assertEqual(items[0]["price"], item.price)
        self.assertEqual(items[0]["product_id"], item.product_id)
        self.assertEqual(items[0]["status"], item.status)

    def test_deserialize_an_order(self):
        """It should Deserialize an order"""
        order = OrderFactory()
        order.items.append(ItemFactory())
        order.create()
        serial_order = order.serialize()
        new_order = Order()
        new_order.deserialize(serial_order)
        self.assertEqual(new_order.name, order.name)
        self.assertEqual(new_order.create_time, order.create_time)
        self.assertEqual(new_order.address, order.address)
        self.assertEqual(new_order.cost_amount, order.cost_amount)
        self.assertEqual(new_order.status, order.status)
        self.assertEqual(new_order.user_id, order.user_id)

    def test_deserialize_with_key_error(self):
        """It should not Deserialize an order with a KeyError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, {})

    def test_deserialize_with_type_error(self):
        """It should not Deserialize an order with a TypeError"""
        order = Order()
        self.assertRaises(DataValidationError, order.deserialize, [])

    def test_deserialize_item_key_error(self):
        """It should not Deserialize an item with a KeyError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, {})

    def test_deserialize_item_type_error(self):
        """It should not Deserialize an item with a TypeError"""
        item = Item()
        self.assertRaises(DataValidationError, item.deserialize, [])

    def test_add_order_item(self):
        """It should Create an order with an item and add it to the database"""
        orders = Order.all()
        self.assertEqual(orders, [])
        order = OrderFactory()
        item = ItemFactory(order=order)
        order.items.append(item)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        new_order = Order.find(order.id)
        self.assertEqual(new_order.items[0].title, item.title)

        item2 = ItemFactory(order=order)
        order.items.append(item2)
        order.update()

        new_order = Order.find(order.id)
        self.assertEqual(len(new_order.items), 2)
        self.assertEqual(new_order.items[1].title, item2.title)

    def test_update_order_item(self):
        """It should Update an orders item"""
        orders = Order.all()
        self.assertEqual(orders, [])

        order = OrderFactory()
        item = ItemFactory(order=order)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        # Fetch it back
        order = Order.find(order.id)
        old_item = order.items[0]
        # print("%r", old_item)
        self.assertEqual(old_item.title, item.title)
        # Change the city
        old_item.title = "XX"
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        item = order.items[0]
        self.assertEqual(item.title, "XX")

    def test_delete_order_item(self):
        """It should Delete an orders item"""
        orders = Order.all()
        self.assertEqual(orders, [])

        order = OrderFactory()
        item = ItemFactory(order=order)
        order.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(order.id)
        orders = Order.all()
        self.assertEqual(len(orders), 1)

        # Fetch it back
        order = Order.find(order.id)
        item = order.items[0]
        item.delete()
        order.update()

        # Fetch it back again
        order = Order.find(order.id)
        self.assertEqual(len(order.items), 0)

    """ def test_find_by_date_range_orders_within_range(self):
       
        # Create orders with create_time within the specified date range
        order1 = OrderFactory(create_time=datetime(2023, 1, 1))
        order2 = OrderFactory(create_time=datetime(2023, 1, 15))
        order3 = OrderFactory(create_time=datetime(2023, 1, 30))

        # Create an order outside the date range
        OrderFactory(create_time=datetime(2022, 12, 31))

        # Commit orders to the database
        db.session.commit()

        # Make a request to the find_by_date_range method
        orders_within_range = Order.find_by_date_range(
            datetime(2023, 1, 1), datetime(2023, 1, 31)
        )

        # Check that the correct orders are returned
        self.assertIn(order1, orders_within_range)
        self.assertIn(order2, orders_within_range)
        self.assertIn(order3, orders_within_range)
    """

    """
    def test_find_by_date_range_orders_on_start_date(self):
    
        # Create an order with create_time on the start date
        order = OrderFactory(create_time=datetime(2023, 1, 1))

        # Create an order outside the date range
        OrderFactory(create_time=datetime(2022, 12, 31))

        # Commit orders to the database
        db.session.commit()

        # Make a request to the find_by_date_range method
        orders_on_start_date = Order.find_by_date_range(
            datetime(2023, 1, 1), datetime(2023, 1, 31)
        )
    
        # Check that the correct order is returned
        self.assertIn(order, orders_on_start_date)

    def test_find_by_date_range_orders_on_end_date(self):
        # Create an order with create_time on the end date
        order = OrderFactory(create_time=datetime(2023, 1, 31))

        # Create an order outside the date range
        OrderFactory(create_time=datetime(2023, 2, 1))

        # Commit orders to the database
        db.session.commit()

        # Make a request to the find_by_date_range method
        orders_on_end_date = Order.find_by_date_range(
            datetime(2023, 1, 1), datetime(2023, 1, 31)
        )

        # Check that the correct order is returned
        self.assertIn(order, orders_on_end_date)

    def test_find_by_date_range_orders_outside_range(self):
        # Create an order outside the date range
        OrderFactory(create_time=datetime(2022, 12, 31))

        # Commit orders to the database
        db.session.commit()

        # Make a request to the find_by_date_range method
        orders_outside_range = Order.find_by_date_range(
            datetime(2023, 1, 1), datetime(2023, 1, 31)
        )

        # Check that no orders are returned
        self.assertEqual(len(orders_outside_range), 0)
        """
