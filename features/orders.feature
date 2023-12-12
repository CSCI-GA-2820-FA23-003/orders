Feature: The order service back-end
    As a eCommerce Merchant
    I need a RESTful catalog service
    So that I can keep track of all orders

Background:
    Given the following orders
        | name           | create_time                        | address                                              | cost_amount | status     | user_id   |
        | Ariana Grande  | 2023-10-18T04:40:35.231701+00:00   | 2671 Wilson Pass Apt. 048 Hessmouth, WI 95473        | 0           | NEW        | 25        |
        | Taylor Swift   | 2023-10-18T04:40:35.231701+00:00   | 9458 Rebecca Valley Lake Williamfort, KY 77271       | 0           | NEW        | 6524      |
        | Kanye West     | 2023-10-18T04:40:35.231701+00:00   | 9458 Rebecca Valley Lake Williamfort, KY 77271       | 0           | NEW        | 2344      |
        | New Jeans      | 2023-10-18T04:40:35.231701+00:00   | 2671 Wilson Pass Apt. 048 Hessmouth, WI 95473        | 100         | APPROVED   | 6060      |
    Given the following items
        | Product ID | Name              | Price  | Amount   | Status        |
        | 233        | Ipad              | 699    | 2        | INSTOCK       |
        | 101        | Iphone 15         | 799    | 8        | LOWSTOCK      |     
        | 151        | Iphone 15 Plus    | 999    | 1        | NOSTOCK       |

Scenario: The server is running
    When I visit the "Home Page"
    Then I should see "Order RESTful Service" in the title
    And I should not see "404 Not Found"


Scenario: Create an Order
    When I visit the "Home Page"
    And I set the "Name" to "Micheal Potter"
    And I set the "Create Time" to "2022-10-18T04:40:35.231701+00:00"
    And I set the "Address" to "2671 Wilson Pass Apt. 048 Hessmouth, WI 95473"
    And I set the "Cost Amount" to "0"
    And I select "NEW" in the "Status" dropdown
    And I set the "User ID" to "1234"
    And I press the "Order-Create" button
    Then I should see the message "Success"
    When I copy the "ID" field
    And I press the "Order-Clear" button
    Then the "ID" field should be empty
    When I paste the "ID" field
    And I press the "Order-Retrieve" button
    Then I should see the message "Success"
    And I should see "Micheal Potter" in the "Name" field
    And I should see "2022-10-18T04:40:35.231701+00:00" in the "Create Time" field
    And I should see "2671 Wilson Pass Apt. 048 Hessmouth, WI 95473" in the "Address" field
    And I should see "0" in the "Cost Amount" field
    And I should see "NEW" in the "Status" dropdown
    And I should see "1234" in the "User ID" field


Scenario: List all orders
    When I visit the "Home Page"
    And I press the "Order-Clear" button
    And I press the "Order-Search" button
    Then I should see the message "Success"
    And I should see "Ariana Grande" in the results
    And I should see "Kanye West" in the results
    And I should see "Taylor Swift" in the results
    And I should not see "Maoqi Zhang" in the results


Scenario: Search orders status
    When I visit the "Home Page"
    And I press the "Order-Clear" button
    And I select "NEW" in the "Status" dropdown
    And I press the "Order-Search" button
    Then I should see the message "Success"
    And I should see "Ariana Grande" in the results
    And I should see "Kanye West" in the results
    And I should not see "Maoqi Zhang" in the results


Scenario: Search orders user_id
    When I visit the "Home Page"
    And I press the "Order-Clear" button
    And I set the "User ID" to "25"
    And I press the "Order-Search" button
    Then I should see the message "Success"
    And I should see "Ariana Grande" in the results
    And I should not see "Kanye West" in the results


Scenario: Search orders name
    When I visit the "Home Page"
    And I press the "Order-Clear" button
    And I set the "Name" to "New Jeans"
    And I press the "Order-Search" button
    Then I should see the message "Success"
    And I should see "APPROVED" in the results
    And I should not see "Kanye West" in the results
    And I should not see "Taylor Swift" in the results
    And I should not see "Ariana Grande" in the results
    

Scenario: Update an Order
    When I visit the "Home Page"
    And I press the "Order-Clear" button
    And I set the "Name" to "Ariana Grande"
    And I press the "Order-Search" button
    Then I should see the message "Success"
    And I should see "Ariana Grande" in the "Name" field
    And I should see "NEW" in the "Status" dropdown
    When I close the Modal
    WHEN I select "APPROVED" in the "Status" dropdown
    And I press the "Order-Update" button
    Then I should see the message "Success"
    When I set the "User ID" to "25"
    And I press the "Order-Search" button
    Then I should see "APPROVED" in the results
    And I should not see "NEW" in the results
    When I close the Modal
    Then I should see the message "Success"


Scenario: Retrieve an Order
    When I visit the "Home Page"
    And I set the "Name" to "Ariana Grande"
    And I press the "Order-Clear" button
    And I press the "Order-Search" button
    Then I should see the message "Success"
    When I close the Modal
    When I copy the "Id" field
    And I press the "Order-Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    When I paste the "Id" field
    And I press the "Order-Retrieve" button
    Then I should see the message "Success"
    And I should see "Ariana Grande" in the "Name" field


Scenario: Delete an Order
    When I visit the "Home Page"
    And I press the "Order-Clear" button
    And I set the "Name" to "Ariana Grande"
    And I press the "Order-Search" button
    Then I should see the message "Success"
    When I close the Modal
    When I copy the "Id" field
    And I press the "Order-Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    When I paste the "Id" field
    And I press the "Order-Delete" button
    Then I should see the message "Order has been Deleted!"
    And the "Name" field should be empty
    When I press the "Order-Clear" button
    And I press the "Order-Search" button
    Then I should not see "Ariana Grande" in the results


Scenario: Cancel an Order
    When I visit the "Home Page"
    And I press the "Order-Clear" button
    And I set the "Name" to "Ariana Grande"
    And I press the "Order-Search" button
    Then I should see the message "Success"
    When I close the Modal
    When I copy the "Id" field
    And I press the "Order-Clear" button
    Then the "Id" field should be empty
    And the "Name" field should be empty
    When I paste the "Id" field
    And I press the "Order-Cancel" button
    Then I should see the message "Order has been Canceled!"
    And the "Name" field should be empty
    When I press the "Order-Clear" button
    And I press the "Order-Search" button
    Then I should see "CANCELED" in the results


Scenario: Create an Item in an Order
    When I visit the "Home Page"
    And I press the "Order-Clear" button
    And I press the "Order-Search" button
    Then I should see the message "Success"
    When I close the Modal
    When I copy the "ID" field
    And I press the "Order-Clear" button
    Then the "ID" field should be empty
    When I paste the "Order ID" field
    And I set the "Product ID" to "1234"
    And I set the "Title" to "Ipad"
    And I set the "Price" to "799"
    And I set the "Amount" to "1"
    And I select "INSTOCK" in the "Item Status" dropdown
    And I press the "Item-Create" button
    Then I should see the message "Success"
    When I paste the "Order ID" field
    And I set the "Product ID" to "999"
    And I set the "Title" to "Ipad mini"
    And I set the "Price" to "599"
    And I set the "Amount" to "1"
    And I select "INSTOCK" in the "Item Status" dropdown
    And I press the "Item-Create" button
    Then I should see the message "Success"
    When I paste the "Order ID" field
    And I press the "Item-List" button
    Then I should see "Ipad" in the item list
    And I should see "Ipad mini" in the item list


Scenario: List Items in an Order
    When I visit the "Home Page"
    And I press the "Order-Clear" button
    And I press the "Order-Search" button
    Then I should see the message "Success"
    When I close the Modal
    When I copy the "ID" field
    And I press the "Order-Clear" button
    Then the "ID" field should be empty
    When I paste the "Order ID" field
    And I press the "Item-List" button
    When I close the Modal
    Then I should see the message "Success"
    

Scenario: Delete Items in an Order
    When I visit the "Home Page"
    And I press the "Order-Clear" button
    And I press the "Order-Search" button
    Then I should see the message "Success"
    When I copy the "ID" field
    When I close the Modal
    And I press the "Order-Clear" button
    Then the "ID" field should be empty
    When I paste the "Order ID" field
    And I set the "Product ID" to "1000"
    And I set the "Title" to "Iphone 15 PRO MAX"
    And I set the "Price" to "1199"
    And I set the "Amount" to "1"
    And I select "INSTOCK" in the "Item Status" dropdown
    And I press the "Item-Create" button
    Then I should see the message "Success"
    When I press the "Item-Delete" button
    And I paste the "Order ID" field
    And I press the "Item-List" button
    Then I should not see "Iphone 13 PRO MAX" in the item list


    
Scenario: Update Items in an Order
    When I visit the "Home Page"
    And I press the "Order-Clear" button
    And I press the "Order-Search" button
    Then I should see the message "Success"
    When I close the Modal
    When I copy the "ID" field
    And I press the "Order-Clear" button
    Then the "ID" field should be empty
    When I paste the "Order ID" field
    And I set the "Product ID" to "1000"
    And I set the "Title" to "Iphone 15 PRO"
    And I set the "Price" to "999"
    And I set the "Amount" to "1"
    And I select "INSTOCK" in the "Item Status" dropdown
    And I press the "Item-Create" button
    Then I should see the message "Success"
    When I select "NOSTOCK" in the "Item Status" dropdown
    And I press the "Item-Update" button
    And I press the "Item-List" button
    Then I should not see "INSTOCK" in the item list