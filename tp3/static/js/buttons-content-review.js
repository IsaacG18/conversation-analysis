$(document).ready(function () {
    document.querySelectorAll(".filter-button").forEach(personButton => {
        personButton.addEventListener("click", () => personButton.classList.toggle("filter-button--selected"));
    });

    $('.risk-button').click(function (e) {
        var clickedElement = $(e.target);
        riskButtonClick(clickedElement);
    })
});

function riskButtonClick(clickedElement) {
    if (clickedElement.hasClass('low')) {
        clickedElement.toggleClass("risk-button-low--selected");
    } else if (clickedElement.hasClass('medium')) {
        clickedElement.toggleClass("risk-button-medium--selected");
    } else {
        clickedElement.toggleClass("risk-button-high--selected");
    }
}
