$(document).ready(function(){

    const newSuiteForm = $('#new-suite-form');
    const add_suite = $('#add-suite');

    $('#new-suite-form').submit(function(e){
        e.preventDefault();
        suite = $('#suite-name').val();
        $.ajax({
            type: 'POST',
            url: "/create_suite",
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
            },
            data: {'name': suite},
            success: function(response){
                $('#suite-name').val('');
                newSuiteForm.before(`
                <div class="list-group-item list-group-item-action">
                <div class="row d-flex align-items-center justify-content-between">
                    <div class="col-9 form-check">
                        <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                        <label class="form-check-label" for="flexCheckDefault">`
                        + suite +
                        `</label>
                  </div>
                  <div class="col-3">
                    <button type="button" class="btn btn-danger btn-sm">Delete</button>
                  </div>
                </div>
            </div>
                `)
                alert(response);
            },
            error: function(jqXHR) {
                var errorMessage = 'An error occurred';
                if (jqXHR.responseJSON && jqXHR.responseJSON.detail) {
                    errorMessage = jqXHR.responseJSON.detail;
                }
                alert(errorMessage);
            }
        })
    })


})