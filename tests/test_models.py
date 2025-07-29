# Copyright 2016, 2023 John J. Rofrano. All Rights Reserved.
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
Test cases for Product Model

Test cases can be run with:
    nosetests
    coverage report -m

While debugging just these tests it's convenient to use this:
    nosetests --stop tests/test_models.py:TestProductModel

"""
import os
import logging
import unittest
from decimal import Decimal
from service.models import Product, Category, db, DataValidationError
from service import app
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql://postgres:postgres@localhost:5432/postgres"
)


######################################################################
#  P R O D U C T   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductModel(unittest.TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        Product.init_db(app)

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_a_product(self):
        """It should Create a product and assert that it exists"""
        product = Product(
            name="Fedora",
            description="A red hat",
            price=12.50,
            available=True,
            category=Category.CLOTHS,
        )
        self.assertEqual(str(product), "<Product Fedora id=[None]>")
        self.assertTrue(product is not None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, "Fedora")
        self.assertEqual(product.description, "A red hat")
        self.assertEqual(product.available, True)
        self.assertEqual(product.price, 12.50)
        self.assertEqual(product.category, Category.CLOTHS)

    def test_add_a_product(self):
        """It should Create a product and add it to the database"""
        products = Product.all()
        self.assertEqual(products, [])
        product = ProductFactory()
        product.id = None
        product.create()
        # Assert that it was assigned an id and shows up in the database
        self.assertIsNotNone(product.id)
        products = Product.all()
        self.assertEqual(len(products), 1)
        # Check that it matches the original product
        new_product = products[0]
        self.assertEqual(new_product.name, product.name)
        self.assertEqual(new_product.description, product.description)
        self.assertEqual(Decimal(new_product.price), product.price)
        self.assertEqual(new_product.available, product.available)
        self.assertEqual(new_product.category, product.category)

    #
    # ADD YOUR TEST CASES HERE
    #
    def test_read_a_product(self):
        """It should read the expected product"""
        product = ProductFactory()
        product.id = None  # Id will be created by the database
        product.create()
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_update_a_product(self):
        """It should update a product correctly"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

        product.description = "Paul Atreides"
        product.update()
        found_product = Product.find(product.id)
        self.assertEqual(found_product.id, product.id)
        self.assertEqual(found_product.name, product.name)
        self.assertEqual(found_product.description, product.description)
        self.assertEqual(found_product.price, product.price)
        self.assertEqual(found_product.available, product.available)
        self.assertEqual(found_product.category, product.category)

    def test_delete_a_product(self):
        """It should delete a product correctly"""
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)
        self.assertEqual(len(Product.all()), 1)

        product.delete()
        self.assertEqual(len(Product.all()), 0)

    def test_list_all_products(self):
        """It should detect the correct number of produts"""
        self.assertEqual(len(Product.all()), 0)
        number_new_insertions = 5

        for _ in range(number_new_insertions):
            product = ProductFactory()
            product.create()

        self.assertEqual(len(Product.all()), number_new_insertions)

    def test_find_by_name(self):
        """It should Find a Product by Name"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        name = products[0].name
        count = len([product for product in products if product.name == name])
        found = Product.find_by_name(name)
        self.assertEqual(found.count(), count)
        for product in found:
            self.assertEqual(product.name, name)

    def test_find_by_availability(self):
        """It should find a product by availability"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        availability = products[0].available
        logging.debug("Availability looked for : %s", availability)
        count = len([product for product in products if product.available == availability])
        found = Product.find_by_availability(availability)
        self.assertEqual(found.count(), count)
        for product in found:
            logging.debug(product)
            self.assertEqual(product.available, availability)

    def test_find_by_price(self):
        """It should find a product by price"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        price = products[0].price
        logging.debug("Price looked for : %s", price)
        count = len([product for product in products if product.price == price])
        found = Product.find_by_price(price)
        self.assertEqual(found.count(), count)
        for product in found:
            logging.debug(product)
            self.assertEqual(product.price, price)

    def test_find_by_price(self):
        """It should find a product by price even when price is a string"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        price = products[0].price
        logging.debug("Price looked for : %s", price)
        count = len([product for product in products if product.price == price])
        found = Product.find_by_price(str(price))
        self.assertEqual(found.count(), count)
        for product in found:
            logging.debug(product)
            self.assertEqual(product.price, price)

    def test_find_by_category(self):
        """It should find products by category"""
        products = ProductFactory.create_batch(5)
        for product in products:
            product.create()
        cat = products[0].category
        logging.debug("Category we are looking for : %s", cat)

        count = len([product for product in products if product.category == cat])
        found = Product.find_by_category(cat)

        self.assertEqual(found.count(), count)

        for product in found:
            logging.debug(product)
            self.assertEqual(product.category, cat)

    # The tests given do not allow to reach 65% cover, so here is a few more to cover our basis

    def test_update_a_product_without_id(self):
        """It should refuse to update a product without id"""
        product = ProductFactory()
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        product.id = None
        product.description = "Paul Atreides"
        with self.assertRaises( DataValidationError):
            product.update()

    def test_deserialize_with_bad_available_type(self):
        """It should refuse to deserialize a product with a string availability"""
        product = ProductFactory()
        product_ser = product.serialize()
        product_ser["available"]= str(product_ser["available"])
        with self.assertRaises(DataValidationError):
            product.deserialize(product_ser)

    def test_deserialize_with_incomplete_data(self):
        """It should refuse to deserialize a product missing a name"""
        product = ProductFactory()
        product_ser = product.serialize()
        del product_ser["name"]
        with self.assertRaises(DataValidationError):
            product.deserialize(product_ser) 

    def test_deserialize_with_bad_category(self):
        """It should refuse to deserialize a product with a bad category"""
        product = ProductFactory()
        product_ser = product.serialize()
        product_ser["category"] = "spyce"
        with self.assertRaises(DataValidationError):
            product.deserialize(product_ser) 

    def test_deserialize_with_bad_price(self):
        """It should refuse to deserialize a product with a bad price"""
        product = ProductFactory()
        product_ser = product.serialize()
        product_ser["price"] = None
        with self.assertRaises(DataValidationError):
            product.deserialize(product_ser) 