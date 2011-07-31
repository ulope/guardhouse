window.addEvent("domready", function() {
    var messages = $('messages');
    if (messages) {
        messages.hide().reveal();
        messages.getElement(".close").addEvent("click", function(evt) {
            evt.stop();
            messages.dissolve();
        });
    }
});