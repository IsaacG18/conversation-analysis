var clickState = false;
var clickTimeout;
$(document).ready(function(){
    $('.file-title').click(function(e){
        e.preventDefault();
        if (clickState === false){
            clickTimeout = setTimeout(()=>window.location=this.href, 250);
            clickState = true;
        }
        else {
            clearTimeout(clickTimeout);
            clickState = false;
            file = $(e.target).parent();
            renameInput = file.next(".file-rename-form")
            renameInput.removeClass('d-none');
            renameInput.children('.file-rename').focus();
            file.toggle();

        }
    })

    $('.file-rename-form').submit(function(e){
        e.preventDefault();
        $(this).children('.file-rename').blur();
    })

    $('.file-rename').blur(function(e){
        fileName = $(this).val();
        fileId = $(this).parent().attr('id').split("-")[2];
        renameSubmit($(this).parent(), fileName, fileId);
    })

    function renameSubmit(form, fileName, fileId){
        $.ajax({
            type: 'POST',
            url: "/rename_file",
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
            },
            data: {'fileName': fileName, 'fileId': fileId},
            success: function(response){
                console.log(response);
                $(form).prev(".file-title").children('small').html(fileName);
                $(form).prev(".file-title").toggle();
                $(form).addClass('d-none');
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