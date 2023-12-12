$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#order_id").val(res.id);
        $("#order_name").val(res.name);
        $("#order_create_time").val(res.create_time);
        $("#order_address").val(res.address);
        $("#order_cost_amount").val(res.cost_amount);
        $("#order_status").val(res.status);
        $("#order_user_id").val(res.user_id);
    }

    // Updates the form with data from the response for the item section
    function update_item_form_data(res) {
        $("#order_item_id").val(res.id);
        $("#order_product_id").val(res.product_id);
        $("#order_title").val(res.title);
        $("#order_price").val(res.price);
        $("#order_amount").val(res.amount);
        $("#order_item_status").val(res.status);
        $("#order_order_id").val(res.order_id);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#order_name").val("");
        $("#order_create_time").val("");
        $("#order_address").val("");
        $("#order_cost_amount").val("");
        $("#order_status").val("");
        $("#order_user_id").val("");
    }

    // Clears all item form fields
    function clear_item_form_data() {
        $("#order_item_id").val("");
        $("#order_product_id").val("");
        $("#order_title").val("");
        $("#order_price").val("");
        $("#order_amount").val("");
        $("#order_order_id").val("");
        $("#order_item_status").val("");
    }
    

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create an Order
    // ****************************************

    $("#order-create-btn").click(function () {

        let name = $("#order_name").val();
        let create_time = $("#order_create_time").val();
        let address = $("#order_address").val();
        let cost_amount = $("#order_cost_amount").val();
        let status = $("#order_status").val();
        let user_id = $("#order_user_id").val();
        

        let data = {
            "name": name,
            "create_time": create_time,
            "address": address,
            "cost_amount": parseInt(cost_amount, 10),
            "status": status,
            "user_id": parseInt(user_id, 10),
            "items" : []
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/orders",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });

    

    // ****************************************
    // Update an Order
    // ****************************************

    $("#order-update-btn").click(function () {

        let id =  $("#order_id").val();
        let name = $("#order_name").val();
        let create_time = $("#order_create_time").val();
        let address = $("#order_name").val();
        let cost_amount = $("#order_cost_amount").val();
        let status = $("#order_status").val();
        let user_id = $("#order_user_id").val();

        let data = {
            "name": name,
            "create_time": create_time,
            "address": address,
            "cost_amount": cost_amount,
            "status": status,
            "user_id": user_id
        };

        $("#flash_message").empty();

        let ajax = $.ajax({
                type: "PUT",
                url: `/orders/${id}`,
                contentType: "application/json",
                data: JSON.stringify(data)
            })

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Retrieve an Order
    // ****************************************

    $("#order-retrieve-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            clear_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Order
    // ****************************************

    $("#order-delete-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/orders/${order_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Order has been Deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Cancel an Order
    // ****************************************

    $("#order-cancel-btn").click(function () {

        let order_id = $("#order_id").val();

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/orders/${order_id}/cancel`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Order has been Canceled!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });

    // ****************************************
    // Clear the form
    // ****************************************

    $("#order-clear-btn").click(function () {
        $("#order_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });

    // ****************************************
    // Search for an Order
    // ****************************************

    $("#order-search-btn").click(function () {

        let name = $("#order_name").val();
        let status = $("#order_status").val();
        let user_id = $("#order_user_id").val();


        let queryString = ""

        if (name) {
            queryString += 'name=' + name
        }
        if (status) {
            if (queryString.length > 0) {
                queryString += '&status=' + status
            } else {
                queryString += 'status=' + status
            }
        }
        if (user_id) {
            if (queryString.length > 0) {
                queryString += '&user_id=' + user_id
            } else {
                queryString += 'user_id=' + user_id
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders?${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Create Time</th>'
            table += '<th class="col-md-2">Address</th>'
            table += '<th class="col-md-2">Cost Amount</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '<th class="col-md-2">User ID</th>'
            table += '</tr></thead><tbody>'
            let firstOrder = "";
            for(let i = 0; i < res.length; i++) {
                let order = res[i];
                table +=  `<tr id="row_${i}"><td>${order.id}</td><td>${order.name}</td><td>${order.create_time}</td><td>${order.address}</td><td>${order.cost_amount}</td><td>${order.status}</td><td>${order.user_id}</td></tr>`;
                if (i == 0) {
                    firstOrder = order;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstOrder != "") {
                update_form_data(firstOrder)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Create an Item
    // ****************************************

    $("#item-create-btn").click(function () {
        let order_id = $("#order_order_id").val();
        let title = $("#order_title").val();
        let product_id = $("#order_product_id").val();
        let price = $("#order_price").val();
        let amount = $("#order_amount").val();
        let status = $("#order_item_status").val();

        if ( !order_id || !title || !product_id || !amount || !status || !price) {
            flash_message("Missing required fields")
            return
        }

        let data = {
            "order_id": parseInt(order_id, 10),
            "title": title,
            "amount": parseInt(amount, 10),
            "price": parseFloat(price),
            "product_id": parseInt(product_id, 10),
            "status": status
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/orders/" + order_id + "/items",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function (res) {
            update_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });
    });

    // ****************************************
    // List Items
    // ****************************************

    $("#item-list-btn").click(function () {

        let order_id = $("#order_order_id").val();

        if (!order_id || order_id == "") {
            clear_item_form_data();
            flash_message("Order ID is required for List Operation")
            return
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}/items`,
            contentType: "application/json",
            data: ''
        })


        ajax.done(function (res) {
            $("#list_item_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-1">Item ID</th>'
            table += '<th class="col-md-2">Product ID</th>'
            table += '<th class="col-md-3">Name</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '<th class="col-md-2">Quantity</th>'
            table += '<th class="col-md-2">Order ID</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '</tr></thead><tbody>'
            let firstItem = "";
            for (let i = 0; i < res.length; i++) {
                let item = res[i];
                table += `<tr id="row_${i}"><td>${item.id}</td><td>${item.product_id}</td><td>${item.title}</td><td>${item.price}</td><td>${item.amount}</td><td>${item.order_id}</td><td>${item.status}</td></tr>`;
                if (i == 0) {
                    firstItem = item;
                }
            }
            table += '</tbody></table>';
            $("#list_item_results").append(table);

            // copy the first result to the form
            if (firstItem != "") {
                update_item_form_data(firstItem)
            }
            else{
                $("#order_item_id").val("");
                clear_item_form_data();
            }

            flash_message("Success")
        });

        ajax.fail(function (res) {
            $("#list_item_results").empty();
            $("#order_item_id").val("");
            clear_item_form_data();
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Clear the item form
    // ****************************************

    $("#item-clear-btn").click(function () {
        $("#order_item_id").val("");
        $("#order_order_id").val("");
        $("#flash_message").empty();
        clear_item_form_data()
    });


    // ****************************************
    // Retrieve an Item
    // ****************************************

    $("#item-retrieve-btn").click(function () {

        let item_id = $("#order_item_id").val();
        let order_id = $("#order_order_id").val();

        if (!order_id) {
            flash_message("Order ID is required for Retrieving Item")
            return
        }

        if (!item_id) {
            flash_message("Item ID is required for Retrieve Operation")
            return
        }
        
        var ajax = $.ajax({
            type: "GET",
            url: `/orders/${order_id}/items/${item_id}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function (res) {
            update_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            clear_item_form_data()
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Update an Item
    // ****************************************

    $("#item-update-btn").click(function () {

        let order_id = $("#order_order_id").val();
        let item_id = $("#order_item_id").val();

        if (!order_id) {
            flash_message("Order ID is required for Updating Item")
            return
        }

        if (!item_id) {
            flash_message("Item ID is required for Update Operation")
            return
        }

        let title = $("#order_title").val();
        let product_id = $("#order_product_id").val();
        let price = $("#order_price").val();
        let amount = $("#order_amount").val();
        let status = $("#order_item_status").val();

        if ( !order_id || !title || !product_id || !amount || !status || !price) {
            flash_message("Missing required fields")
            return
        }

        let data = {
            "order_id": parseInt(order_id, 10),
            "title": title,
            "amount": parseInt(amount, 10),
            "price": parseFloat(price),
            "product_id": parseInt(product_id, 10),
            "status": status
        };


        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "PUT",
            url: `/orders/${order_id}/items/${item_id}`,
            contentType: "application/json",
            data: JSON.stringify(data)
        })

        ajax.done(function (res) {
            update_item_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function (res) {
            flash_message(res.responseJSON.message)
        });

    });

    // ****************************************
    // Delete an Item
    // ****************************************

    $("#item-delete-btn").click(function () {
        let order_id = $("#order_order_id").val();
        let item_id = $("#order_item_id").val();

        if (!order_id) {
            flash_message("Order ID is required for Deleting Item")
            return
        }

        if (!item_id) {
            flash_message("Item ID is required for Delete Operation")
            return
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `/orders/${order_id}/items/${item_id}`,
            contentType: "application/json"
        })

        ajax.done(function (res) {
            // remove the order from the form and table
            clear_item_form_data();
            flash_message("Item has been Deleted!")
        });

        ajax.fail(function (res) {
            clear_item_form_data();
            flash_message(res.responseJSON.message)
        });
    });

})
