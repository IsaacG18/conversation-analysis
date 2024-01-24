var clickStateDelim = false; // Logging if the item has been clicked in a short time frame
var clickTimeoutDelim;

$(document).ready(function() {
    // Click event for delim value
    $('.delim-item').click(function(e) {
        e.preventDefault();
        if (clickStateDelim === false) {
            // If it's a single click, wait for 250 milliseconds
            clickTimeoutDelim = setTimeout(() => window.location = this.href, 250);
            clickStateDelim = true;
        } else { // Double click
            clearTimeout(clickTimeoutDelim);
            clickStateDelim = false;

            // Extract delim name and value
            delimName = $(e.target).closest('.delim-item').find('.col-10 a').text();
            delimValue = $(e.target).closest('.delim-item').find('.text-center a').text();

            // Identify the clicked delim item
            delimItem = $(e.target).closest('.delim-item');

            // Extract delim ID
            delimId = delimItem.attr('id').split("-")[2];

            // Update rename form
            $(`#delim-rename-${delimId}`).attr('value', delimName);
            $(`#delim-value-${delimId}`).attr('value', delimValue);

            // Show rename form and hide delim item
            renameInputDelim = delimItem.next(".delim-rename-form");
            renameInputDelim.removeClass('d-none');
            renameInputDelim.children('.delim-rename').focus();
            delimItem.toggle();
        }
    });

    // Submit event for delim rename form
    $('.delim-rename-form').submit(function(e) {
        e.preventDefault();
        $(this).children('.delim-rename').blur();
    });

    // Blur event for delim rename input
    $('.delim-rename').blur(function(e) {
        delimName = $(this).val();
        delimValue = $(this).closest('.delim-rename-form').find('.delim-value').val();
        delimId = $(this).attr('id').split("-")[2];
        renameSubmitDelim($(`#delim-rename-form-${delimId}`), delimName, delimValue, delimId);
    });

    // Function to handle AJAX submission for renaming delim value
    function renameSubmitDelim(form, delimName, delimValue, delimId) {
        $.ajax({
            type: 'POST',
            url: "/change_delim",
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
            },
            data: {'delimName': delimName, 'delimValue': delimValue, 'delimId': delimId},
            success: function(response) {
                console.log(response.message);
                $(form).prev(".delim-item").find('.col-10 a').html(response.delimName);
                $(form).prev(".delim-item").find('.text-center a').html(response.delimValue);
                $(form).prev(".delim-item").toggle();
                $(form).addClass('d-none');
            },
            error: function(jqXHR) {
                var errorMessage = 'An error occurred';
                if (jqXHR.responseJSON && jqXHR.responseJSON.message) {
                    errorMessage = jqXHR.responseJSON.message;
                }
                alert(errorMessage);
            }
        });
    }
});
