$(document).ready(function(){
    $('.delete-file').click(function(e){
        e.preventDefault();
        confirmDelete(e)
        })

    function confirmDelete(e) {
        var userConfirmed = window.confirm("Delete file?");
        if (userConfirmed) {
            deleteFileClick(e);
        }
    }

    function deleteFileClick(e){
        button = $(e.target).parent()
        fileId = button.attr("id").split("-")[1]
        console.log(fileId)
        $.ajax({
            type: 'POST',
            url: "/delete_file",
            datatype: 'json',
            headers: {
                'X-CSRFToken': $('input[name=csrfmiddlewaretoken]').val(),
            },
            data: {'fileId': fileId},
            success: function(data){
                console.log(data);
                $(`#file-item-${fileId}`).remove()
                if ($('.file-item').length===0){
                    $('#result-container').html("<strong>There are no files present.</strong>")
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error('AJAX Error:', textStatus, errorThrown);
            }
        })
    }
})