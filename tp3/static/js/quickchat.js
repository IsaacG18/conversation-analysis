$(document).ready(function () {
    $(".chatgpt_quick_message").click(function () {
        var pageSlug = window.location.pathname.split('/').pop(); 
        var query = document.getElementById('message_content').value;
        $('#ChatGPT-results').replaceWith('<div id="ChatGPT-results"><h3>ChatGPT response:</h3>LOADING RESPONSE</div>');
        $.get('/quick_chat_message/',
                {'query':query,'file_slug': pageSlug},
                function(data) {
                    $('#ChatGPT-results').replaceWith(data.results);
                });
    })
})