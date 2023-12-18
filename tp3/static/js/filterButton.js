$(document).ready(function () {
    $(".filter").click(function () {
        var buttonValue = $(this).text();
        var pageSlug = window.location.pathname.split('/').pop();  // Extract the last part of the path
        console.log(pageSlug)
        console.log(buttonValue)
        $.get('/filter/',
            {'filter_button': buttonValue, 'file_slug': pageSlug},
            function(data) {
                console.log(data);
            })
    });
});