$(document).ready(function () {
    $(".chatgpt_quick_message").click(function () {
        var pageSlug = window.location.pathname.split('/').pop(); 
        $('#ChatGPT-results').replaceWith('<div id="ChatGPT-results">LOADING RESPONSE</div>');
        $.get('/quick_chat_message/',
                {'file_slug': pageSlug},
                function(data) {
                    $('#ChatGPT-results').replaceWith(data.results);
                });
    })
})