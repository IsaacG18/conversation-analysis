var clickState = false; // logging if the item has been clicked in a short time frame
var clickTimeout;
$(document).ready(function(){
    $('.chat-title').on( "dblclick", function(e){
        e.preventDefault();

        chatName = $(e.target).text(); // split chat name from suffix

        if ($(e.target).is("a")){  // in case <small></small> is clicked
            chat = $(e.target).parent();
        }
        else chat = $(e.target);

        chatId = chat.attr('id').split("-")[2]; // update rename form
        $(`#chat-rename-${chatId}`).attr('value', chatName);

        renameInput = chat.next(".chat-rename-form") // show rename form
        renameInput.removeClass('d-none');
        renameInput.children('.chat-rename').focus();
        chat.toggle();
    })

    $('.chat-rename-form').submit(function(e){
        e.preventDefault();
        $(this).children('.chat-rename').blur();
    })

    $('.chat-rename').blur(function(e){
        chatName = $(this).val();
        chatId = $(this).attr('id').split("-")[2];
        renameSubmit($(`#chat-rename-form-${chatId}`), chatName, chatId);
    })

    function renameSubmit(form, chatName, chatId){
        $.ajax({
            type: 'POST',
            url: "/rename_chat",
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
            },
            data: {'chatName': chatName, 'chatId': chatId},
            success: function(response){
                console.log(response.message);
                titleObject = $(form).prev(".chat-title");
                if (titleObject.hasClass('convo')){
                    titleObject.html(response.chatName);
                }
                else {
                    titleObject.children('a').html(response.chatName);
                }
                $(form).addClass('d-none');
                titleObject.toggle();
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