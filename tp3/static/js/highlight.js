$(document).ready(function () {
    convertLocationsToLinks();
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
                convertLocationsToLinks();
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
                convertLocationsToLinks();
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
function convertLocationsToLinks() {
    var locationElements = document.querySelectorAll('.GPE');
    locationElements.forEach(function (locationElement) {
        var locationName = locationElement.textContent;
        if (!locationElement.querySelector('a')) {
            var encodedLocation = encodeURIComponent(locationName);
            var googleMapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodedLocation}`;
            locationElement.innerHTML = convertToLink(locationName, googleMapsUrl);
        }
    });
}

function convertToLink(text, url) {
    return `<a href="${url}" target="_blank" class="location-link">${text}</a>`;
}

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