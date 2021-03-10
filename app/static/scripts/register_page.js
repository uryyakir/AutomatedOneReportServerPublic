document.addEventListener("DOMContentLoaded", function() {
    const button = $(document.querySelector('.btn'));
    const form   = document.querySelector('.form');
    const usernameSelector = $("#username");
    const passwordSelector = $("#password");
    const confirmSelector = $("#confirm")

    console.log("there");
    document.addEventListener('keyup', event => {
        if ((passwordSelector.val() === confirmSelector.val()) && (confirmSelector.val() !== "") && (usernameSelector.val() != "")) {
            button.css("pointer-events", "auto");
            button.css("background-color", "#4CAF50")
        }
        else {
            button.css("pointer-events", "none");
            button.css("background-color", "")
        }
    });
});
