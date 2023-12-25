$(document).ready(function(){

    const newSuiteForm = $('#new-suite-form');
    const add_suite = $('#add-suite');
    var activeSuite = $('#suite-list div:first');
    var activeSuiteName = getSuiteName(activeSuite);

    $('#new-suite-form').submit(function(e){
        e.preventDefault();
        newSuiteName = $('#suite-name').val();
        $.ajax({
            type: 'POST',
            url: "/create_suite",
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
            },
            data: {'name': newSuiteName},
            success: function(response){
                $('#suite-name').val('');
                newSuiteForm.before(`
                <div class="list-group-item list-group-item-action suite-item">
                <div class="row d-flex align-items-center justify-content-between">
                    <div class="col-9 form-check">
                        <input class="form-check-input" type="checkbox" value="" id="flexCheckDefault">
                        <label class="form-check-label" for="flexCheckDefault">`
                        + newSuiteName +
                        `</label>
                  </div>
                  <div class="col-3">
                    <button type="button" class="btn btn-danger btn-sm">Delete</button>
                  </div>
                </div>
            </div>
                `)
                activeSuite = $('.suite-item:last');
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

    $('.suite-item').click(function(e){
        activeSuite = $(e.currentTarget);
        activeSuiteName = getSuiteName(activeSuite);
        $.ajax({
            type: 'GET',
            url: "/select_suite",
            datatype: 'json',
            data: {'suite': activeSuiteName},
            success: function(data){
                displayKeywords(data);
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('AJAX Error:', textStatus, errorThrown);
            }
        })
    })

    $('#new-keyword-form').submit(function(e){
        e.preventDefault();
        newKeyword = $('#new-keyword').val();
        $.ajax({
            type: 'POST',
            url: "/create_keyword",
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
            },
            data: {'keyword': newKeyword, 'suite': activeSuiteName},
            success: function(response){
                $('#new-keyword').val('');
                $('#new-keyword-form').before(`<div class="list-group-item list-group-item-action keyword-item">
                <div class="row d-flex align-items-center justify-content-between">
                  <div class="col-9">
                        <a href="#" class="text-reset text-decoration-none">`+newKeyword+`</a>
                  </div>
                  <div class="col-3">
                    <button type="button" class="btn btn-danger btn-sm">Delete</button>
                  </div>
                </div>
            </div>`);
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

    function displayKeywords(data){
        array = JSON.parse(data.objects);
        var toAppend = '';
        $.each(array, function(index, object) {
            var keyword = object.fields.keyword;
            toAppend += 
            `<div class="list-group-item list-group-item-action keyword-item">
            <div class="row d-flex align-items-center justify-content-between">
              <div class="col-9">
                    <a href="#" class="text-reset text-decoration-none">`+keyword+`</a>
              </div>
              <div class="col-3">
                <button type="button" class="btn btn-danger btn-sm">Delete</button>
              </div>
            </div>
        </div>`
        });
        $('.keyword-item').remove();
        $('#new-keyword-form').before(toAppend);
    }

    function getSuiteName(suite){
        return suite.find('.form-check-label').text();
    }

})