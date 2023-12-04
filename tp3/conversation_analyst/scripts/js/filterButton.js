console.log("data");
$(document).ready(function () {
    $(".filter").click(function () {
        var buttonValue = $(this).val();
        var pageSlug = window.location.pathname.split('/').pop();  // Extract the last part of the path

        $.ajax({
            type: "POST",
            url: `/json_content/${pageSlug}/`,  // Use the correct URL for your Django app
            data: {value: buttonValue},
            dataType: "json",
            success: function (data) {
                // Handle the JSON response here
                console.log(data);
            },
            error: function (error) {
                console.error("AJAX request failed:", error);
            }
        });
    });
});
