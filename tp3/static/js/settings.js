$(document).ready(function(){
    $('#suite-list .suite-item:first').addClass('active-suite'); // set the first suite active by default

    $('#new-suite-form').submit(function(e){
        e.preventDefault();
        if ($(this).valid() == true){
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
                    // insert new suite item
                    $(e.target).before(`
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
                    // add event listners
                    id = '#suite-item-' + response.suiteId;
                    $(id).click(function(e) {
                        suiteClick(targetGrabber(e));
                    });
                    btn = '#delete-' + response.suiteId;
                    $(btn).click(function(e){
                        deleteSuiteClick(e);
                    })
                    checkbox = '#checkbox-' + response.suiteId;
                    $(checkbox).click(function(e){
                        suiteCheck(e);
                    })
                    refreshSuiteFocusOnCreation($(`#suite-item-${suiteId}`));

                    alert(response.message);
                },
                error: function(jqXHR) {
                    var errorMessage = 'An error occurred';
                    if (jqXHR.responseJSON && jqXHR.responseJSON.message) {
                        errorMessage = jqXHR.responseJSON.message;
                    }
                    alert(errorMessage);
                }
            })
    }
    })

    $('#new-suite-form').validate({
        rules:{
            suite_input: "required",
        },
        messages: {
            suite_input: "Please input a suite name",
        },
        errorElement: "span",
        errorPlacement: function(error, element) {
            error_row = $('#suite-error-row');
            error.appendTo(error_row);

            setTimeout(function() {
                error.remove();
            }, 3000);
          },
          onfocusout: false,
          onkeyup: false,
    })


    $('.suite-item').click(function(e) {
        suiteClick(targetGrabber(e));
    });

    $('#new-keyword-form').validate({
        rules:{
            keyword: "required",
            risk_factor: {
                required: true,
                min: 0,
                max: 10,
            },
        },
        messages: {
            keyword: "Please input a keyword",
            risk_factor: "Please input a risk factor between 0 and 10"
        },
        errorClass: "invalid",
        errorElement: "span",
        errorPlacement: function(error, element) {
            error_row = $('#keyword-error-row');
            error.appendTo(error_row);

            setTimeout(function() {
                error.remove();
            }, 3000);
          },
          onfocusout: false,
          onkeyup: false,
    })

    $('#new-keyword-form').submit(function(e){
        e.preventDefault();
        if ($(this).valid() == true){
            if (checkIfSuiteExist()==true){
                var newKeyword = $('#new-keyword').val().toLowerCase()
                var newKeywordRisk = $('#new-keyword-risk').val()
                var activeSuiteName = getSuiteName($('.active-suite'));
                $.ajax({
                    type: 'POST',
                    url: "/create_keyword",
                    headers: {
                        'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
                    },
                    data: {'keyword': newKeyword, 'suite': activeSuiteName, 'risk': newKeywordRisk},
                    success: function(response){
                        keywordId = response.keywordId;
                        $('#new-keyword').val('');
                        $('#new-keyword-form').before(`<div class="list-group-item list-group-item-action keyword-item" id="keyword-item-${keywordId}">
                        <div class="row d-flex align-items-center justify-content-between">
                        <div class="col-8">
                                <a href="#" class="text-reset text-decoration-none">${newKeyword}</a>
                        </div>
                        <div class="col-1">
                        <input type="number" class="form-control keyword-risk"  value="${newKeywordRisk}" id="risk-${keywordId}">
                        </div>
                        <div class="col-3">
                        <button type="button" class="btn btn-danger btn-sm delete-keyword" value= "${keywordId}" id="delete-keyword-${keywordId}">Delete</button>
                        </div>
                        </div>
                        </div>
                        <div class="row align-items-center error-row" id="error-row-${keywordId}">
                        </div>
                    </div>`);
                    $(`#delete-keyword-${keywordId}`).click(function(e){
                        deleteKeywordClick(e);
                    })
                    $(`#risk-${keywordId}`).blur(function(e){
                        RiskFactorBlur(e);
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
    }}
    })



    $('.delete-suite').click(function(e){
        confirmDelete(e);
    })


    $('.delete-keyword').click(function(e){
        deleteKeywordClick(e);
    })

    $('.form-check-input').click(function(e){
        suiteCheck(e);
    })

    $('.keyword-risk').blur(function(e){
        RiskFactorBlur(e);
    })


    function displayKeywords(data){
        array = JSON.parse(data.objects);
        var toAppend = '';
        $.each(array, function(index, object) {
            var keyword = object.fields.keyword;
            var risk = object.fields.risk_factor;
            var keywordId = object.pk
            toAppend += 
            `<div class="list-group-item list-group-item-action keyword-item" id="keyword-item-${keywordId}">
            <div class="row d-flex align-items-center justify-content-between">
              <div class="col-8">
                    <a href="#" class="text-reset text-decoration-none">${keyword}</a>
              </div>
              <div class="col-1">
              <input type="number" class="form-control keyword-risk"  value="${risk}" id="risk-${keywordId}">
            </div>
            <div class="col-3">
              <button type="button" class="btn btn-danger btn-sm delete-keyword" value= "${keywordId}" id="delete-keyword-${keywordId}">Delete</button>
            </div>
            </div>
            <div class="row align-items-center error-row" id="error-row-${keywordId}">
            </div>
            </div>
        </div>`
        });
        $('.keyword-item').remove();
        $('#new-keyword-form').before(toAppend);
    }

    function refreshSuiteFocusOnCreation(suite){
        $('.active-suite').removeClass('active-suite');
        $(suite).addClass('active-suite');
        console.log(suite);
        $('.keyword-item').remove();
    }

    function refreshSuiteFocusOnDeletion(suite){
        if (suite.hasClass('active-suite')){
            suite.removeClass('active-suite');
            if ($('.suite-item').length>1){
                suite.remove();
                focusSuite = $('.suite-item:first');
                suiteClick(focusSuite);
                return;
            }else{
                $('.keyword-item').remove();
            }
        }
        suite.remove();
    }

    function suiteClick(suite){
        $('.active-suite').removeClass('active-suite');
        suite.addClass('active-suite')
        activeSuiteName = getSuiteName(suite);
        $.ajax({
            type: 'GET',
            url: "/select_suite",
            datatype: 'json',
            data: {'suite': activeSuiteName},
            success: function(data){
                displayKeywords(data);
                initialiseKeywordForm();
                $('.delete-keyword').click(function(e){
                    deleteKeywordClick(e);
                })
                $('.keyword-risk').blur(function(e){
                    RiskFactorBlur(e);
                })
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('AJAX Error:', textStatus, errorThrown);
            }
        })
    }

    function targetGrabber(e){
        return $(e.currentTarget);
    }



    function initialiseKeywordForm(){
        $('#new-keyword-risk-error').remove();
        $('#new-keyword-error').remove();
        $('#new-keyword').val('');
        $('#new-keyword-risk').val('0');
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
                refreshSuiteFocusOnDeletion($(`#suite-item-${suiteId}`));
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('AJAX Error:', textStatus, errorThrown);
            }
        })
    }

    function confirmDelete(e) {
        var userConfirmed = window.confirm("Deleting suite will remove all contained keywords. Are you sure you want to proceed?");
        if (userConfirmed) {
            deleteSuiteClick(e);
        }
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

    function validateRiskInput(input){
        if (input<0 || input>10){return false;}
        else return true;
    }

    function RiskFactorBlur(e){
        var risk = $(e.target).val();
        var keywordId = $(e.target).attr('id').split("-")[1];

        if (validateRiskInput(risk) == true){
            $(`#error-row-${keywordId}`).empty();
            $.ajax({
                type: 'POST',
                url: "/risk_update",
                headers: {
                    'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
                },
                data: {'keyword': keywordId, 'risk': risk},
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
            error_row = $(`#error-row-${keywordId}`);
            error_row.append('<span>Please input a number between 0 and 10</span>');
            }
    }


    function getSuiteName(suite){
        return suite.find('.form-check-label').text();
    }

    function checkIfSuiteExist(){
        console.log($('.active-suite'));
        if (!$('.active-suite').length) {
            $('#keyword-error-row').append(`<span>Please create a suite frist</span>`);
            return false;
        } else{
            $('#keyword-error-row').empty();
            return true;
        }
    }


})