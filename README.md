# NYU DevOps Orders Team

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)


This is a skeleton you can use to start your projects

## Overview

This project template contains starter code for your class project. The `/service` folder contains your `models.py` file for your model and a `routes.py` file for your service. The `/tests` folder has test case starter code for testing the model and the service separately. All you need to do is add your functionality. You can use the [lab-flask-tdd](https://github.com/nyu-devops/lab-flask-tdd) for code examples to copy from.

## Automatic Setup

The best way to use this repo is to start your own repo using it as a git template. To do this just press the green **Use this template** button in GitHub and this will become the source for your repository.

## Manual Setup

You can also clone this repository and then copy and paste the starter code into your project repo folder on your local computer. Be careful not to copy over your own `README.md` file so be selective in what you copy.

There are 4 hidden files that you will need to copy manually if you use the Mac Finder or Windows Explorer to copy files from this folder into your repo folder.

These should be copied using a bash shell as follows:

```bash
    cp .gitignore  ../<your_repo_folder>/
    cp .flaskenv ../<your_repo_folder>/
    cp .gitattributes ../<your_repo_folder>/
```

## Contents

The project contains the following:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
requirements.txt    - list if Python libraries required by your code
config.py           - configuration parameters

service/                   - service python package
├── __init__.py            - package initializer
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/              - test cases package
├── __init__.py     - package initializer
├── test_models.py  - test suite for business models
└── test_routes.py  - test suite for service routes
```

## Service APIs
### Index
GET `/`

Success Response : `200 OK`
```
{
  "name": "Order REST API Service",
  "paths": "http://localhost:8080/orders",
  "version": "1.0"
}
```
### Orders Operations

| Description | Endpoint |
|----------|----------|
| Create an Order | POST `/orders` |
| Get List of all Orders | GET `/orders` |
| Read/Get an Order by ID | GET `/orders/<order_id>` |
| Update an existing Order | PUT `/orders/<order_id>` |
| Delete an Order | DELETE `/orders/<order_id>` |

### Items Operations
| Description | Endpoint |
|----------|----------|
| Create an Order Item | POST `/orders/<order_id>/items`|
| Read/Get an Order Item | GET `/orders/<order_id>/items/<item_id>` |
| Update an Order Item | PUT `/orders/<order_id>/items/<item_id>` | 
| Delete an Order Item | DELETE `/orders/<order_id>/items/<item_id>` | 
List Items of an Order | GET `/orders/<order_id>/items` | 


## Order Service APIs - Use
### Create an Order

Endpoint: `/orders`

Method: `POST`

Content-Type: `application/json`

Authentication Required: None

Example:

Request Body (JSON)
```
{
    "address": "USNS Steele\nFPO AE 80935",
    "cost_amount": 0,
    "create_time": "2023-10-18T04:40:35.231701+00:00",
    "id": 1234,
    "items": [],
    "name": "Alexander Wang",
    "status": "NEW"
  }
```
Success Response : `201 CREATED`
```
{
  "address": "USNS Steele\nFPO AE 80935",
  "cost_amount": 0.0,
  "create_time": "2023-10-18T04:40:35.231701+00:00",
  "id": 3243,
  "items": [],
  "name": "Alexander Wang",
  "status": "NEW"
}
```
If things are missing (i.e. no status) in JSON, Response: `400 Bad Response`
```
{
  "error": "Bad Request",
  "message": "Invalid Order: missing status",
  "status": 400
}
```


### Get a List of all Orders
Endpoint : `/orders`

Method :  `GET`

Authentication required : None

Example:
 `GET`  `/orders`

Successful Response: `200 OK`


### Read/Get an Order with Order ID

Endpoint : `/orders/<order_id>`

Method :  `GET`

Authentication required : None

Example:
 `GET`  `/orders/43`

Successful Response: `200 OK`
```
{
  "address": "USNS Steele\nFPO AE 80935",
  "cost_amount": 891.495943667253,
  "create_time": "2014-10-19T04:40:35.231701+00:00",
  "id": 43,
  "items": [],
  "name": "Robert Jones",
  "status": "PENDING"
}
```

Failure Response: `404 NOT FOUND`
```
{
  "error": "Not Found",
  "message": "404 Not Found: Order with id '20' was not found.",
  "status": 404
}
```

### Update an Order
Endpoint : `/orders/<order_id>`

Method :  `PUT`

Authentication required : None

Content-Type: `application/json`

Example:
 `PUT`  `/orders/43`

Request Body (JSON):
```
{
    "status": "DELIVERED"
}
```


Successful Response: `200 OK`
```
{
  "address": "PSC 2814, Box 2274\nAPO AE 12563",
  "cost_amount": 145.660919534,
  "create_time": "2018-11-20T16:40:26.483159+00:00",
  "id": 44,
  "items": [
    {
      "amount": 5,
      "id": 16,
      "order_id": 44,
      "price": 352.395907329991,
      "product_id": "2104",
      "status": "In Stock",
      "title": "iPhone15 Pro"
    }
  ],
  "name": "Michael Price",
  "status": "DELIVERED"
}
```

Failure Response: `404 NOT FOUND`
```
{
  "error": "Not Found",
  "message": "404 Not Found: Order not found",
  "status": 404
}
```

### Delete an Order
Endpoint : `/orders/<order_id>`

Method :  `DELETE`

Authentication required : None

Example:
 `DELETE`  `/orders/3242`

Successful Response: `204 NO CONTENT`

Failure Response: `404 NOT FOUND`

### Create an Order Item
Endpoint : `/orders/<order_id>/items`

Method :  `POST`

Authentication required : None

Example:
 `POST`  `/orders/43/items`

Request Body (JSON)
```
{
  "amount": 11,
  "id": 33,
  "order_id": 44,
  "price": 200.05,
  "product_id": "9099",
  "status": "Added to Order",
  "title": "iPhone12 Pro"
}
```

Successful Response: `200 OK`
```
{
  "amount": 11,
  "id": 33,
  "order_id": 44,
  "price": 200.05,
  "product_id": "9099",
  "status": "Added to Order",
  "title": "iPhone12 Pro"
}
```

Failure Response: `404 NOT FOUND`
{
  "error": "Not Found",
  "message": "Item not found",
  "status": 404
}

### Read/Get an Order Item
Endpoint : `/orders/<order_id>/items/<item_id>`

Method :  `GET`

Authentication required : None

Example:
 `GET`  `/orders/44/items/16`

Successful Response: `200 OK`
```
{
  "amount": 11,
  "id": 16,
  "order_id": 44,
  "price": 352.395907329991,
  "product_id": "2104",
  "status": "In Stock",
  "title": "iPhone15 Pro"
}
```

Failure Response: `404 NOT FOUND`

### Update an Order Item
Endpoint : `/orders/<order_id>/items/<item_id>`

Method :  `PUT`

Authentication required : None

Example:
 `PUT`  `/orders/44/items/16`

Successful Response: `200 OK`
```
{
  "item": {
    "amount": 11,
    "id": 16,
    "order_id": 44,
    "price": 352.395907329991,
    "product_id": "2104",
    "status": "In Stock",
    "title": "iPhone15 Pro"
  }
}
```

Failure Response: `404 NOT FOUND`

### Delete an Order Item
Endpoint : `/orders/<order_id>/items/<item_id>`

Method :  `DELETE`

Authentication required : None

Example:
 `DELETE`  `/orders/44/items/16`

Successful Response: `204 NO CONTENT`

Failure Response: `404 NOT FOUND`


### List All Items of an Order
Endpoint : `/orders/<order_id>/items`

Method :  `GET`

Authentication required : None

Example:
 `GET`  `/orders/43/items`

Successful Response: `200 OK`
```
{
  "items": [
    {
      "amount": 5,
      "id": 16,
      "order_id": 44,
      "price": 352.395907329991,
      "product_id": "2104",
      "status": "In Stock",
      "title": "iPhone15 Pro"
    }
  ],
  "order_id": 44
}
```

Failure Response: `404 NOT FOUND`
```
{
  "error": "Not Found",
  "message": "404 Not Found: Order with id '40' was not found.",
  "status": 404
}
```
## Run TDD tests locally
Follow these steps to run TDD locally:
run `make test` in terminal

## License

Copyright (c) John Rofrano. All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the NYU masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by *John Rofrano*, Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
Test GitHub Actions
