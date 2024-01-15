$(document).ready(function () {
    $("#search-button").click(function (e) {
        e.preventDefault();
        console.log("detected");
        var query = document.getElementById('search-input').value;
        console.log(query);
        $.get(window.location.href,
                {'query': query},
                function(data) {
                    console.log(data);
                    $('#results').replaceWith(data);
        });
    })
})