$(document).ready(function(){
    $('#suite-list .suite-item:first').addClass('active-suite'); // set the first suite active by default

    $('.suite-item').click(function(e) {
        suiteClick(targetGrabber(e));
    });

    $('.form-check-input').click(function(e){
        suiteCheck(e);
    })

    $('#back-btn').click(function() {
        file_slug = window.location.pathname.split('/').pop(); 
        $.get("/clear_duplicate_submission", {'file_slug': file_slug}, function(response) {
            // console.log(response);  // causes brocken pipe because of the immediate call of history.back()
          });
        history.back();
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
              <span class="keyword-risk" id="risk-{{ risk_word.id }}">${risk}</span>
            </div>
            </div>
            <div class="row align-items-center error-row" id="error-row-${keywordId}">
            </div>
            </div>
        </div>`
        });
        $('.keyword-item').remove();
        $('#keyword-list').append(toAppend);
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
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('AJAX Error:', textStatus, errorThrown);
            }
        })
    }

    function targetGrabber(e){
        return $(e.currentTarget);
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


})