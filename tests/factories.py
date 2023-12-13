# Copyright 2016, 2019 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Test Factory to make fake objects for testing
"""
from datetime import datetime, UTC
import factory
from factory.fuzzy import FuzzyChoice, FuzzyDateTime, FuzzyFloat, FuzzyInteger
from service.models import Order, Item, OrderStatus, ItemStatus


class OrderFactory(factory.Factory):
    """Creates fake Orders"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Order

    id = factory.Sequence(lambda n: n)
    name = factory.Faker("name")
    create_time = FuzzyDateTime(datetime(2008, 1, 1, tzinfo=UTC))
    address = factory.Faker("address")
    cost_amount = FuzzyFloat(1.00, 1000.00)
    status = FuzzyChoice(
        choices=[
            OrderStatus.NEW,
            OrderStatus.PENDING,
            OrderStatus.APPROVED,
            OrderStatus.DELIVERED,
            OrderStatus.SHIPPED,
            OrderStatus.CANCELED,
        ]
    )
    user_id = FuzzyInteger(1000, 9999)

    # the many side of relationships can be a little wonky in factory boy:
    # https://factoryboy.readthedocs.io/en/latest/recipes.html#simple-many-to-many-relationship

    @factory.post_generation
    def items(
        self, create, extracted, **kwargs
    ):  # pylint: disable=method-hidden, unused-argument
        """Creates the items list"""
        if not create:
            return

        if extracted:
            self.items = extracted


class ItemFactory(factory.Factory):
    """Creates fake Items"""

    # pylint: disable=too-few-public-methods
    class Meta:
        """Persistent class"""

        model = Item

    id = factory.Sequence(lambda n: n)
    order_id = None
    title = FuzzyChoice(
        choices=[
            "iPhone15",
            "MacBook Pro",
            "iPad Pro",
            "Mac Pro",
            "iPhone15 Pro",
            "MacBook Air",
        ]
    )
    amount = FuzzyInteger(1, 10)
    price = FuzzyFloat(1.00, 1000.00)
    product_id = FuzzyInteger(1000, 5000)
    status = FuzzyChoice(
        choices=[ItemStatus.INSTOCK, ItemStatus.LOWSTOCK, ItemStatus.OUTOFSTOCK]
    )
    order = factory.SubFactory(OrderFactory)
