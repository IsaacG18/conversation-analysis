$(document).ready(function () {
    $(".filter").mouseenter(function () {
        var buttonValue = "." + classify($(this).text());
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
            buttonValue = buttonValue.split("(")[0];
            $(`.risk${buttonValue}`).addClass("bold");
            buttonValue = buttonValue.toUpperCase();
            $(`.risk${buttonValue}`).addClass("bold");
        }
    }).mouseleave(function () {
        // Handle mouseleave event here
        var buttonValue = "." + classify($(this).text());
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
            buttonValue = buttonValue.split("(")[0];
            $(`.risk${buttonValue}`).removeClass("bold");
            buttonValue = buttonValue.toUpperCase();
            $(`.risk${buttonValue}`).removeClass("bold");
            };
        }
    )
})


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

function classify(inputString) {
    const resultString = inputString.replace(/ /g, '_');
    return resultString;
  }