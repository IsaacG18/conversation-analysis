$(document).ready(function(){
    // Validation rules for the new delimiter form
    $('#new-delim-form').validate({
        rules: {
            name: "required",
            value: "required",
            order: {
                required: true,
                min: 0,
                max: 5,
            },
        },
        messages: {
            name: "Please input a delimiter name",
            value: "Please input a delimiter value",
            order: "Please input an order between 0 and 5"
        },
        errorClass: "invalid",
        errorElement: "span",
        errorPlacement: function(error, element) {
            // Display validation errors in the designated row
            error_row = $('#delim-error-row');
            error.appendTo(error_row);

            // Remove error message after 3 seconds
            setTimeout(function() {
                error.remove();
            }, 3000);
        },
        onfocusout: false,
        onkeyup: false,
    });

    // Handle form submission for new delimiter creation
    $('#new-delim-form').submit(function(e){
        e.preventDefault();
        if ($(this).valid() == true){
            
                var newDelimName = $('#new-delim-name').val();
                var newDelimValue = $('#new-delim-value').val();
                var newDelimOrder = $('#new-delim-order').val();
                
                $.ajax({
                    type: 'POST',
                    url: "/create_delim",
                    headers: {
                        'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
                    },
                    data: {'name': newDelimName, 'value': newDelimValue, 'order': newDelimOrder},
                    success: function(response){
                        delimId = response.delimId;
                        $('#new-delim').val('');
                        
                        // Insert new delimiter item
                        $('#new-delim-form').before(`
                            <div class="list-group-item list-group-item-action delim-item" id="delim-item-${delimId}">
                                <div class="row d-flex align-items-center justify-content-between">
                                    <div class="col-8">
                                        <a href="#" class="text-reset text-decoration-none">${newDelimName}</a>
                                    </div>
                                    <div class="col-8">
                                        <a href="#" class="text-reset text-decoration-none">${newDelimValue}</a>
                                    </div>
                                    <div class="col-1">
                                        <input type="number" class="form-control delim-order"  value="${newDelimOrder}" id="order-${delimId}">
                                    </div>
                                    <div class="col-3">
                                        <button type="button" class="btn btn-danger btn-sm delete-delim" value="${delimId}" id="delete-delim-${delimId}">Delete</button>
                                    </div>
                                </div>
                            </div>
                            <div class="row align-items-center error-row" id="error-row-${delimId}">
                            </div>
                        `);

                        // Add event listener for delete button
                        $(`#delete-delim-${delimId}`).click(function(e){
                            deleteDelimClick(e);
                        });
                    }
                });
            
        }
    });

    $('.delete-delim').click(function(e){
        deleteDelmClick(e);
    })

    $('.delim-order').blur(function(e){
        OrderBlur(e);
    })

    function deleteDelimClick(e){
        delimId = $(e.target).val();
        $.ajax({
            type: 'GET',
            url: "/delete_delim",
            datatype: 'json',
            data: {'delimId': delimId},
            success: function(data){
                alert(data);
                id = '#delim-item-' + delimId;
                $(id).remove();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('AJAX Error:', textStatus, errorThrown);
            }
        })
    }


    function validateOrderInput(input){
        if (input<0 || input>5){return false;}
        else return true;
    }

    function OrderBlur(e){
        var order = $(e.target).val();
        var delimId = $(e.target).attr('id').split("-")[1];

        if (validateOrderInput(order) == true){
            $(`#error-row-${delimId}`).empty();
            $.ajax({
                type: 'POST',
                url: "/order_update",
                headers: {
                    'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
                },
                data: {'delim': delimId, 'order': order},
                success: function(response){
                    console.log(response);
                },
                error: function(jqXHR) {
                    var errorMessage = 'An error occurre';
                    if (jqXHR.responseJSON && jqXHR.responseJSON.detail) {
                        errorMessage = jqXHR.responseJSON.detail;
                    }
                    alert(errorMessage);
                }
            })
        }
        else {
            error_row = $(`#error-row-${delimId}`);
            error_row.append('<span>Please input a number between 0 and 5</span>');
            }
    }

})


