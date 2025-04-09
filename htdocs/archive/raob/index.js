/* global $ */
$(() => {
    $(".fdp").flatpickr({
        minDate: new Date(1947, 1, 1, 0, 0),
        dateFormat: "Y-m-d H:i",
        time_24hr: true,
        allowInput: true,
        enableTime: true
    });
});