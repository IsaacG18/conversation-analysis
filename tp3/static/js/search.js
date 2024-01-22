$(document).ready(function () {
    $("#search-button").click(function (e) {
        e.preventDefault();
        var query = document.getElementById('search-input').value;
        $.get(window.location.href,
                {'query': query},
                function(data) {
                    $('#results').replaceWith(data);
        });
    })
})