// Backend Messages
$(document).ready(function() {
    $('.flashes li').each(function(index, flash) {
        setTimeout(function() {
            $(flash).hide();
        }, 5000);
    });
});