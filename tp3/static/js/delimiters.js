$(document).ready(function () {
    $('.delete-delim').click(function (e) {
        deleteDelimClick(e);
    })

    $('.delim-order').blur(function (e) {
        OrderBlur(e);
    })

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
        errorPlacement: function (error, element) {
            error_row = $('#delim-error-row');
            error.appendTo(error_row);

            setTimeout(function () {
                error.remove();
            }, 3000);
        },
        onfocusout: false,
        onkeyup: false,
    });

    $('#new-delim-form').submit(function (e) {
        e.preventDefault();
        if ($(this).valid() == true) {
            var newDelimName = $('#new-delim-name').val();
            var newDelimValue = $('#new-delim-value').val();
            var newDelimOrder = $('#new-delim-order').val();

            $.ajax({
                type: 'POST',
                url: "/create_delim",
                headers: {
                    'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
                },
                data: { 'name': newDelimName, 'value': newDelimValue, 'order': newDelimOrder },
                success: function (response) {
                    delimId = response.delimId;
                    $('#new-delim').val('');
                    $('tbody.delims').append(`
                        <tr class="delim-item" id="delim-item-{{ delim.id }}">
                            <td>
                                <div class="row align-items-center">
                                    <div class="col-4">
                                        <input type="number" class="form-control delim-order" value="${newDelimOrder}"
                                            id="delim-${delimId}" name="order">
                                    </div>
                                    <div class="col-8">
                                        <a href="#" class="text-reset text-decoration-none">${newDelimName}</a>
                                    </div>
                                    <div class="row align-items-center error-row" id="error-row-${delimId}">
                            </div>
                                </div>
                            </td>
                            <td class="col-6 text-center">
                                <input type="text" href="#" class="form-control delim-value" value="${newDelimValue}">
                            </td>
                            <td>
                                <div class="col-3">
                                    <button type="button" class="btn btn-danger btn-sm delete-delim" value="${delimId}" id="delete-delim-${delimId}">Delete</button>
                                </div>
                            </td>
                        </tr>
                    `);

                    $(`#delete-delim-${delimId}`).click(function (e) {
                        deleteDelimClick(e);
                    });

                    $(`#order-${delimId}`).blur(function (e) {
                        OrderBlur(e);
                    })
                    alert(response.message);
                },
                error: function (jqXHR) {
                    var errorMessage = 'An error occurred';
                    if (jqXHR.responseJSON && jqXHR.responseJSON.detail) {
                        errorMessage = jqXHR.responseJSON.detail;
                    }
                    alert(errorMessage);
                }
            });
        }
    });

    function deleteDelimClick(e) {
        delimId = $(e.target).val();
        $.ajax({
            type: 'GET',
            url: "/delete_delim",
            datatype: 'json',
            data: { 'delimId': delimId },
            success: function (data) {
                alert(data);
                id = '#delim-item-' + delimId;
                $(id).remove();
            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error('AJAX Error:', textStatus, errorThrown);
            }
        })
    }
    
    function validateOrderInput(input) {
        if (input < 0 || input > 5) { return false; }
        else return true;
    }
    
    function OrderBlur(e) {
        var order = $(e.target).val();
        var delimId = $(e.target).attr('id').split("-")[1];
    
        if (validateOrderInput(order) == true) {
            $(`#error-row-${delimId}`).empty();
            $.ajax({
                type: 'POST',
                url: "/order_update",
                headers: {
                    'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
                },
                data: { 'delim': delimId, 'order': order },
                success: function (response) {
                    console.log(response);
                },
                error: function (jqXHR) {
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
});

