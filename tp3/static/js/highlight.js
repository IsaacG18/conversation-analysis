$(document).ready(function () {
    $(".filter").mouseenter(function () {
        var buttonValue = $(this).text();
        buttonValue = "." + buttonValue;

        if ($(this).hasClass("person-button")) {
            var personElements = document.querySelectorAll('.PERSON');
            personElements.forEach(function (personElement) {
                var nestedDiv = personElement.querySelector(buttonValue);
                if (nestedDiv) {
                    nestedDiv.classList.add("green-text");
                }
            });
        } else if ($(this).hasClass("location-button")) {
            var locationElements = document.querySelectorAll('.GPE');
            locationElements.forEach(function (locationElement) {
                var nestedDiv = locationElement.querySelector(buttonValue);
                if (nestedDiv) {
                    nestedDiv.classList.add("yellow-background");
                }
            });
        } else if ($(this).hasClass("risk-button")) {
            var riskElements = document.querySelectorAll('.risk');
            riskElements.forEach(function (riskElement) {
                var nestedDiv = riskElement.querySelector(buttonValue);
                if (nestedDiv) {
                    nestedDiv.classList.add("bold");
                }
            });
        }
    }).mouseleave(function () {
        // Handle mouseleave event here
        var buttonValue = $(this).text();
        buttonValue = "." + buttonValue;

        if ($(this).hasClass("person-button")) {
            var personElements = document.querySelectorAll('.PERSON');
            personElements.forEach(function (personElement) {
                var nestedDiv = personElement.querySelector(buttonValue);
                if (nestedDiv) {
                    nestedDiv.classList.remove("green-text");
                }
            });
        } else if ($(this).hasClass("location-button")) {
            var locationElements = document.querySelectorAll('.GPE');
            locationElements.forEach(function (locationElement) {
                var nestedDiv = locationElement.querySelector(buttonValue);
                if (nestedDiv) {
                    nestedDiv.classList.remove("yellow-background");
                }
            });
        } else if ($(this).hasClass("risk-button")) {
            var riskElements = document.querySelectorAll('.risk');
            riskElements.forEach(function (riskElement) {
                var nestedDiv = riskElement.querySelector(buttonValue);
                if (nestedDiv) {
                    nestedDiv.classList.remove("bold");
                }
            });
        }
    });
});


style = ""

var styles = `
  <style>
    .green-text {
        color: green;
    }
    .bold {
        font-weight: bold;
    }
    .yellow-background{
        background-color: yellow;
    }
  </style>
`;
document.head.insertAdjacentHTML('beforeend', styles);