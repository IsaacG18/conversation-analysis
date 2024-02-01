$(document).ready(function () {
    $(".chatgpt_new_message").click(function () {
        var startDate = document.getElementById('startDate').value;
        var endDate = document.getElementById('endDate').value;
        var pageSlug = window.location.pathname.split('/').pop(); 
        $.get('/chatgpt_new_message/',
                {'startDate':startDate, 'endDate':endDate ,'file_slug': pageSlug},
                function(data) {
                    $('.results').replaceWith(data.results);
                });
    })

})