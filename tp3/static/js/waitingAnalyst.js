$(document).ready(function () {
    $("#proceed-btn").click(function (e) {
        var image = document.getElementById('loadingImage');
        document.getElementById('waiting_file').innerHTML = "File Processing";
        image.style.display = '';
    })
})

