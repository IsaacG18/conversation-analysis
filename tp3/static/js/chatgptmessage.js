$(document).ready(function () {
    $(".chatgpt_new_message").click(function () {
        var message_content = document.getElementById('message_content').value;
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

})

function formatMediaString(content) {
    var formattedString = `
        <div class="media">
            <img src="/static/pictures/user.png" class="mr-3 rounded-circle" alt="User Image" style="width: 60px; height: 60px;">
            <div class="media-body">
                <h5 class="mt-0">User</h5>
                ${content}
            </div>
        </div>
        <hr>
    `;

    return formattedString;
}