$(document).ready(function () {
    $(".chatgpt_new_message_form").submit(function (e) {
        e.preventDefault();
        var message_content = document.getElementById('message_content').value;
        if (message_content.trim() == ""){
            return;
        }
        document.getElementById('message_content').value = ""
        document.getElementById('loading_message').innerHTML = "Loading Response"
        if (message_content.trim() == ""){return;}
        var pageSlug = window.location.pathname.split('/').pop(); 
        var formattedResult = formatMediaString(message_content);
        $(".chat-messages.results").append(formattedResult);
        $.get('/message/',
                {'message_content':message_content,'chatgpt_slug': pageSlug},
                function(data) {
                    $('.results').replaceWith(data.results);
                    document.getElementById('loading_message').innerHTML = ""
                });
    })
    $(".gpt_prompt").click(function () {
        document.getElementById('loading_message').innerHTML = "Loading Response"
        var message_content =  $(this).text();
        var pageSlug = window.location.pathname.split('/').pop(); 
        var formattedResult = formatMediaString(message_content);
        $(".chat-messages.results").append(formattedResult);
        $.get('/message/',
                {'message_content':message_content,'chatgpt_slug': pageSlug},
                function(data) {
                    $('.results').replaceWith(data.results);
                    document.getElementById('loading_message').innerHTML = ""
                });
    })

})

function formatMediaString(content) {
        var formattedString = `
            <div class="media outgoing">
                            <div class="media-content">
                            <div class="media-details">
                                <img src="/static/pictures/user.png" class="mr-3 rounded-circle" alt="User Image">
                                <p>${content}</p>
                            </div>
                            </div>
                        </div>
        `;
    
        return formattedString;
    }