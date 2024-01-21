$(document).ready(function () {
    $("#search-bar").submit(function (e) {
        e.preventDefault();
        var query = document.getElementById('search-input').value;
        console.log(query);
        $.get(window.location.href,
                {'query': query},
                function(data) {
                    $('#results').replaceWith(data);
        });
    })
})