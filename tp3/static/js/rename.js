var clickState = false; // logging if the item has been clicked in a short time frame
var clickTimeout;
$(document).ready(function(){
    $('.file-title').click(function(e){
        e.preventDefault();
        if (clickState === false){
            clickTimeout = setTimeout(()=>window.location=this.href, 250); // wait for 250 microseconds if it's a single click
            clickState = true;
        }
        else { // double click
            clearTimeout(clickTimeout);
            clickState = false;

            fileName = $(e.target).text().split("."); // split file name from suffix
            suffix = fileName.pop();
            editable = fileName.join("");

            if ($(e.target).is("small")){  // in case <small></small> is clicked
                file = $(e.target).parent();
            }
            else file = $(e.target);

            fileId = file.attr('id').split("-")[2]; // update rename form
            $(`#file-rename-${fileId}`).attr('value', editable);
            $(`#suffix-${fileId}`).text(`.${suffix}`);

            renameInput = file.next(".file-rename-form") // show rename form
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
        fileId = $(this).attr('id').split("-")[2];
        renameSubmit($(`#file-rename-form-${fileId}`), fileName, fileId);
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
                console.log(response.message);
                $(form).prev(".file-title").children('small').html(response.fileName);
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