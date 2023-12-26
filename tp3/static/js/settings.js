$(document).ready(function(){

    const newSuiteForm = $('#new-suite-form');
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
                var suiteId = response.suiteId;
                $('#suite-name').val('');
                newSuiteForm.before(`
                <div class="list-group-item list-group-item-action suite-item" id="suite-item-${suiteId}">
                <div class="row d-flex align-items-center justify-content-between">
                <div class="col-9 form-check" id="suite-check-${suiteId}">
                        <input class="form-check-input" type="checkbox" value="${suiteId}" id="checkbox-${suiteId}">
                        <label class="form-check-label" for="checkbox-${suiteId}">${newSuiteName}</label>
                  </div>
                  <div class="col-3">
                    <button type="button" class="btn btn-danger btn-sm delete-suite" id = "delete-${suiteId}" value="${suiteId}">Delete</button>
                  </div>
                </div>
            </div>
                `)
                id = '#suite-item-' + response.suiteId;
                $(id).click(function(e) {
                    suiteClick(e);
                });
                btn = '#delete-' + response.suiteId;
                $(btn).click(function(e){
                    deleteSuiteClick(e);
                })
                checkbox = '#checkbox-' + response.suiteId;
                $(checkbox).click(function(e){
                    suiteCheck(e);
                })

                activeSuite = $('.suite-item:last');
                alert(response.message);
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

    $('.suite-item').click(function(e) {
        suiteClick(e);
    });

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
                keywordId = response.keywordId;
                $('#new-keyword').val('');
                $('#new-keyword-form').before(`<div class="list-group-item list-group-item-action keyword-item" id="keyword-item-${keywordId}">
                <div class="row d-flex align-items-center justify-content-between">
                  <div class="col-9">
                        <a href="#" class="text-reset text-decoration-none">${newKeyword}</a>
                  </div>
                  <div class="col-3">
                  <button type="button" class="btn btn-danger btn-sm delete-keyword" value= "${keywordId}" id="delete-keyword-${keywordId}">Delete</button>
                  </div>
                </div>
            </div>`);
            $('.delete-keyword').click(function(e){
                deleteKeywordClick(e);
            })
                alert(response.message);
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


    $('.delete-suite').click(function(e){
        deleteSuiteClick(e);
    })


    $('.delete-keyword').click(function(e){
        deleteKeywordClick(e);
    })

    $('.form-check-input').click(function(e){
        suiteCheck(e);
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
                    <a href="#" class="text-reset text-decoration-none">${keyword}</a>
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

    function suiteClick(e){
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
    }

    function deleteSuiteClick(e){
        suiteId = $(e.target).val();
        $.ajax({
            type: 'GET',
            url: "/delete_suite",
            datatype: 'json',
            data: {'suiteId': suiteId},
            success: function(data){
                alert(data);
                id = '#suite-item-' + suiteId;
                $(id).remove();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('AJAX Error:', textStatus, errorThrown);
            }
        })
    }

    function deleteKeywordClick(e){
        keywordId = $(e.target).val();
        $.ajax({
            type: 'GET',
            url: "/delete_keyword",
            datatype: 'json',
            data: {'keywordId': keywordId},
            success: function(data){
                alert(data);
                id = '#keyword-item-' + keywordId;
                $(id).remove();
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('AJAX Error:', textStatus, errorThrown);
            }
        })
    }

    function suiteCheck(e){
        var suiteId = $(e.target).val();
        var isChecked = $(e.target).is(':checked');
        console.log(`${suiteId} ${isChecked}`)
        $.ajax({
            type: 'POST',
            url: "/check_suite",
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
            },
            data: {'suiteId': suiteId, 'value': isChecked},
            success: function(response){
                console.log(response);
            },
            error: function(jqXHR) {
                var errorMessage = 'An error occurred';
                if (jqXHR.responseJSON && jqXHR.responseJSON.detail) {
                    errorMessage = jqXHR.responseJSON.detail;
                }
                alert(errorMessage);
            }
        })
    }

    function getSuiteName(suite){
        return suite.find('.form-check-label').text();
    }

    function initialiseCheckbox(){
        
    }
})