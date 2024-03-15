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

    $(".risk-level").click(function () {
        var clickedElement = this; 
            var button = document.getElementsByClassName("existing");
            var filter_vals = []
            var risk_value  = parseInt($(this).val())
            
            var pageSlug = window.location.pathname.split('/').pop(); 
            for (var i = 0; i < button.length; i++) {
                var buttonText = button[i].textContent || button[i].innerText;
                filter_vals.push(removeNumberedSuffix(buttonText))
            }
            if($(this).hasClass("clicked")){
                let index = risk.indexOf(risk_value);
                if (index !== -1) {
                    risk.splice(index, 1);
                }
                $.get('/filter/',
                    {'filters': JSON.stringify(filter_vals), 'startDate':startDate, 'endDate':endDate ,'file_slug': pageSlug, "risk":JSON.stringify(risk)},
                    function(data) {
                        $('.results').replaceWith(data.results);
                        $(clickedElement).removeClass("clicked");
                    });
            }else{
                risk.push(risk_value)
                $.get('/filter/',
                    {'filters': JSON.stringify(filter_vals), 'startDate':startDate, 'endDate':endDate ,'file_slug': pageSlug, "risk":JSON.stringify(risk)},
                    function(data) {
                        $('.results').replaceWith(data.results);
                        $(clickedElement).addClass("clicked");
                    });
            }
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
    $(".restort_filters").click(function () {
        var button = document.getElementsByClassName(".filter");
        var filter_vals = []
        var pageSlug = window.location.pathname.split('/').pop(); 
        for (var i = 0; i < button.length; i++) {
            if (button[i].classList.contains("clicked")) {
                button[i].classList.remove("existing")
                button[i].classList.remove("clicked");
                if (button[i].classList.contains('risk-button')) {
                    risk_remove(button[i])
                }
                if (button[i].classList.contains('filter-button--selected')) {
                    button[i].classList.remove("filter-button--selected")
                }
            }
        }
        var risk_levels = document.getElementsByClassName("risk-level");
        for (var i = 0; i < risk_levels.length; i++) {
            if (risk_levels[i].classList.contains("clicked")) {
                risk_levels[i].classList.remove("clicked");
                risk_remove(risk_levels[i])
            }
        }
        risk = []
        document.getElementById('startDate').value = '';
        document.getElementById('endDate').value = '';
        startDate = null
        endDate = null
        console.log(JSON.stringify(filter_vals), startDate, endDate, pageSlug, JSON.stringify(risk))
        $.get('/filter/',
        {'filters': JSON.stringify(filter_vals), 'startDate':startDate, 'endDate':endDate ,'file_slug': pageSlug,"risk":JSON.stringify(risk)},
            function(data) {
                $('.results').replaceWith(data.results);
            });
    });
});
function removeNumberedSuffix(input) {
    return input.replace(/\(\d+\)$/, '');
}

function risk_remove(button){
    if (button.classList.contains('low')) {
        button.classList.remove("risk-button-low--selected");
    } else if (button.classList.contains('medium')) {
        button.classList.remove("risk-button-medium--selected");
    } else {
        button.classList.remove("risk-button-high--selected");
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
