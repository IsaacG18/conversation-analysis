$(document).ready(function () {
    $(".search-chats").click(function () {
        var query = document.getElementById('search-input').value;
        var page_slug = window.location.pathname.split('/').pop(); 
        $.get("search_chats",
                {'query': query, "page_slug":page_slug},
                function(data) {
                    $('#search_results').replaceWith(data.results);
        });
    })
})