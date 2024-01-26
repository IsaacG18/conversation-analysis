$(document).ready(function () {
    var startDate = document.getElementById('startDate').value;
    var endDate = document.getElementById('endDate').value;
    var risk = []

    $(".date-fil").click(function () {
        startDate = document.getElementById('startDate').value;
        endDate = document.getElementById('endDate').value;
        var button = document.getElementsByClassName("existing");
        var filter_vals = []
        var pageSlug = window.location.pathname.split('/').pop(); 
        for (var i = 0; i < button.length; i++) {
            var buttonText = button[i].textContent || button[i].innerText;
            filter_vals.push(removeNumberedSuffix(buttonText))
        }

        $.get('/filter/',
                {'filters': JSON.stringify(filter_vals), 'startDate':startDate, 'endDate':endDate ,'file_slug': pageSlug,"risk":JSON.stringify(risk)},
                function(data) {
                    $('.results').replaceWith(data.results);
                });
    })

    $(".risk").click(function () {
        var button = document.getElementsByClassName("existing");
        var filter_vals = []
        var risk_value  = $(this).value
        var pageSlug = window.location.pathname.split('/').pop(); 
        for (var i = 0; i < button.length; i++) {
            var buttonText = button[i].textContent || button[i].innerText;
            filter_vals.push(removeNumberedSuffix(buttonText))
        }
        if(!$(this).hasClass("existing")){
            let index = risk.indexOf(risk_value);
            if (index !== -1) {
                risk.splice(index, 1);
            }
        }else{
            risk.push(risk_value)
        }

        $.get('/filter/',
                {'filters': JSON.stringify(filter_vals), 'startDate':startDate, 'endDate':endDate ,'file_slug': pageSlug, "risk":JSON.stringify(risk)},
                function(data) {
                    $('.results').replaceWith(data.results);
                    $(clickedElement).addClass("existing");
                    $(clickedElement).addClass("clicked");
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
                filter_vals.push(removeNumberedSuffix(buttonText))
            }

            filter_vals.push(removeNumberedSuffix(buttonValue));

            $.get('/filter/',
            {'filters': JSON.stringify(filter_vals), 'startDate':startDate, 'endDate':endDate ,'file_slug': pageSlug,"risk":JSON.stringify(risk)},
                function(data) {
                    $(clickedElement).addClass("existing");
                    $(clickedElement).addClass("clicked");
                    $('.results').replaceWith(data.results);
                });
        }else{
    
            for (var i = 0; i < button.length; i++) {
                var buttonText = button[i].textContent || button[i].innerText;
                if (buttonText != buttonValue){
                    filter_vals.push(removeNumberedSuffix(buttonText))
                }
                    
            }
    
            $.get('/filter/',
            {'filters': JSON.stringify(filter_vals), 'startDate':startDate, 'endDate':endDate ,'file_slug': pageSlug, "risk":JSON.stringify(risk)},
                function(data) {
                    $(clickedElement).removeClass("existing");
                    $(clickedElement).removeClass("clicked");
                    $('.results').replaceWith(data.results);
                });
        }
        
    });
});

function removeNumberedSuffix(input) {
    return input.replace(/\(\d+\)$/, '');
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
