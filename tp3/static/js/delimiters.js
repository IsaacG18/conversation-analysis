$(document).ready(function () {
    $('.delete-delim').click(function (e) {
        deleteDelimClick(e);
    })

    $('.delim-order').blur(function (e) {
        OrderBlur(e);
    })

    $('.delim-value').blur(function (e) {
        ValueBlur(e);
    })

    $('#new-delim-form').validate({
        rules: {
            name: "required",
            value: "required",
            order: {
                required: true,
                min: 1,
                max: 5,
            },
        },
        messages: {
            name: "Please input a delimiter name",
            value: "Please input a delimiter value",
            order: "Please input an order between 1 and 5"
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

        if ($(this).valid()) {
            var newDelimName = $('#new-delim-name').val();
            var newDelimValue = $('#new-delim-value').val();
            var newDelimOrder = $('#new-delim-order').val();

            if (getOrders().includes(newDelimOrder)) {
                handleCreateDelimError('Order already exists. Please choose a different order.');
                return;
            }
            if (/^[a-zA-Z0-9]+$/.test(newDelimValue)) {
                handleCreateDelimError('Delimiter must be a symbol. Please choose a different delimiter.');
                return;
            }

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
                    <tr class="delim-item" id="delim-item-${delimId}">
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
                                <input type="text" href="#" class="form-control delim-value" value="${newDelimValue}" id="delim-${delimId}" name="value">
                                <div class="row align-items-center value-error-row" id="value-error-row-${delimId}" style="color: red;font-size: 12px;">
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
                    });
                    $(`#value-${delimId}`).blur(function (e) {
                        ValueBlur(e);
                    });
                    alert(response.message);
                },
                error: function (jqXHR) {
                    handleCreateDelimError(jqXHR.responseJSON && jqXHR.responseJSON.detail || 'An error occurred');
                }
            });
        }
    });

    function handleCreateDelimError(errorMessage) {
        alert(errorMessage);
    }

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
                $(id).remove()

            },
            error: function (jqXHR, textStatus, errorThrown) {
                console.error('AJAX Error:', textStatus, errorThrown);
            }
        })
    }

    function validateOrderInput(input) {
        if (input < 1 || input > 5) { return false; }
        else return true;
    }

    var oldOrders = [];

    function getOrders() {
        var existingOrders = [];
        $('.delim-order').each(function () {
            existingOrders.push(($(this).val()));
        });
        return existingOrders;
    }

    $('.delim-order').focus(function (e) {
        oldOrders = getOrders();
    });

    function OrderBlur(e) {
        var order = $(e.target).val();
        var delimId = $(e.target).attr('id').split("-")[1];

        if (oldOrders.includes(order)) {
            error_row = $(`#error-row-${delimId}`);
            error_row.append('<span>Order must be unique.</span>');
        } else {
            if (validateOrderInput(order)) {
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
                        var errorMessage = 'An error occurred';
                        if (jqXHR.responseJSON && jqXHR.responseJSON.detail) {
                            errorMessage = jqXHR.responseJSON.detail;
                        }
                        alert(errorMessage);
                    }
                });
            } else {
                error_row = $(`#error-row-${delimId}`);
                error_row.append('<span>Please input a number between 1 and 5</span>');
            }
        }
    }


    function ValueBlur(e) {
        var value = $(e.target).val();
        var delimId = $(e.target).attr('id').split("-")[1];

        if (/^[a-zA-Z0-9]+$/.test(value)) {
            error_row = $(`#value-error-row-${delimId}`);
            error_row.append('<span>Please choose an non-alphanumerical symbol</span>');
        }
        else{
        $(`#value-error-row-${delimId}`).empty();
        $.ajax({
            type: 'POST',
            url: "/value_update",
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
            },
            data: { 'delim': delimId, 'value': value },
            success: function (response) {
                console.log(response);
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
}


});