$(document).ready(function () {
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
                {'filters': JSON.stringify(filter_vals), 'file_slug': pageSlug},
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
                {'filters': JSON.stringify(filter_vals), 'file_slug': pageSlug},
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
                content: item.fields.content
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
        
        messageDetails.forEach(message => {
            html += `
                <div class="list-group-item">
                    <div class="d-flex justify-content-between">
                        <span class="sender"><small>${message.sender}:</small></span>
                        <small class="timestamp text-body-secondary">${message.timestamp}</small>
                    </div>
                    <small class="content">${message.content}</small>
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
