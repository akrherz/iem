/* global $ */
$(() => {
    $(".fdp").flatpickr({
        minDate: new Date(1947, 1, 1, 0, 0),
        dateFormat: "m/d/Y H:i",
        time_24hr: true,
        allowInput: true,
        enableTime: true
    });
});