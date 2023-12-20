$(document).ready(function () {
    var startDate = document.getElementById('startDate').value;
    var endDate = document.getElementById('endDate').value;

    $(".date-fil").click(function () {
        startDate = document.getElementById('startDate').value;
        endDate = document.getElementById('endDate').value;
        var button = document.getElementsByClassName("existing");
        var filter_vals = []
        var pageSlug = window.location.pathname.split('/').pop(); 
        var clickedElement = this; 
        for (var i = 0; i < button.length; i++) {
            var buttonText = button[i].textContent || button[i].innerText;
            filter_vals.push(buttonText)
        }

        $.get('/filter/',
                {'filters': JSON.stringify(filter_vals), 'startDate':startDate, 'endDate':endDate ,'file_slug': pageSlug},
                function(data) {
                    var messageOutputDiv = document.getElementById("message_output");
                    messageOutputDiv.innerHTML = formatMessagesHTML(extractMessageDetails(data));
                });
    })



    $(".filter").click(function () {
        var button = document.getElementsByClassName("existing");
        var filter_vals = []
        var buttonValue = $(this).text();
        var pageSlug = window.location.pathname.split('/').pop(); 
        var clickedElement = this; 
        if (!$(this).hasClass("existing")) {
            for (var i = 0; i < button.length; i++) {
                var buttonText = button[i].textContent || button[i].innerText;
                filter_vals.push(buttonText)
            }

            filter_vals.push(buttonValue);

            $.get('/filter/',
            {'filters': JSON.stringify(filter_vals), 'startDate':startDate, 'endDate':endDate ,'file_slug': pageSlug},
                function(data) {
                    $(clickedElement).addClass("existing");
                    $(clickedElement).addClass("clicked");
                    var messageOutputDiv = document.getElementById("message_output");
                    messageOutputDiv.innerHTML = formatMessagesHTML(extractMessageDetails(data));
                });
        }else{
    
            for (var i = 0; i < button.length; i++) {
                var buttonText = button[i].textContent || button[i].innerText;
                if (buttonText != buttonValue){
                    filter_vals.push(buttonText)
                }
                    
            }
    
            $.get('/filter/',
            {'filters': JSON.stringify(filter_vals), 'startDate':startDate, 'endDate':endDate ,'file_slug': pageSlug},
                function(data) {
                    $(clickedElement).removeClass("existing");
                    $(clickedElement).removeClass("clicked");
                    var messageOutputDiv = document.getElementById("message_output");
                    messageOutputDiv.innerHTML = formatMessagesHTML(extractMessageDetails(data));
                });
        }
        
    });
});


function extractMessageDetails(data) {
    try {
        // Parse the "messages" property into an array of objects
        const messages = JSON.parse(data.messages);

        // Extract details from each message
        const messageDetailsList = messages.map(item => {
            return {
                sender: item.fields.sender,
                timestamp: item.fields.timestamp,
                display_content: item.fields.display_content
            };
        });

        return messageDetailsList;
    } catch (error) {
        console.error(`Error decoding JSON: ${error.message}`);
        return [];
    }
}

function formatMessagesHTML(messageDetails) {
    if (messageDetails.length > 0) {
        let html = '<div class="list-group">';
        console.log("here")
        messageDetails.forEach(message => {
            // Format timestamp using JavaScript Date object
            const formattedTimestamp = new Date(message.timestamp).toLocaleString('en-US', {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: 'numeric',
                minute: 'numeric',
                hour12: true
            });

            html += `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between">
                        <span class="sender"><small>${message.sender}:</small></span>
                        <small class="timestamp text-body-secondary">${formattedTimestamp}</small>
                    </div>
                    <small class="content">${message.display_content}</small>
                </div>`;
        });

        html += '</div>';
        return html;
    } else {
        return '<strong>There are no messages present.</strong>';
    }
}
var styles = `
  <style>
    /* Add your custom styles here */
    .clicked {
        color: var(--bs-btn-hover-color);
        background-color: var(--bs-btn-hover-bg);
        border-color: var(--bs-btn-hover-border-color);
    }
  </style>
`;
document.head.insertAdjacentHTML('beforeend', styles);
