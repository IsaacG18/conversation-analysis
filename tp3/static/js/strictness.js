$('.form-range').on("input", function (e) {
    var level = $(e.target).val();
    var attr = $(this).attr('id').split("-")[0];
    $.ajax({
        type: 'POST',
        url: "settings/strictness",
        headers: {
            'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
        },
        data: { 'attr': attr, 'level': level },
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
})