$(document).ready(function () {
    $(".chatgpt_new_message").click(function () {
        var message_content = document.getElementById('message_content').value;
        if (message_content.trim() == ""){return;}
        var pageSlug = window.location.pathname.split('/').pop(); 
        $.get('/message/',
                {'message_content':message_content,'chatgpt_slug': pageSlug},
                function(data) {
                    $('.results').replaceWith(data.results);
                });
    })

})