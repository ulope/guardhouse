window.addEvent("domready", function() {
    var messages = $('messages');
    if (messages) {
        messages.hide().reveal();
        messages.getElement(".close").addEvent("click", function(evt) {
            evt.stop();
            messages.dissolve();
        });
    }

    $$('.showlink').each(function(link){
        var content = link.getNext(".hidden");
        if (content) {
            content.hide();
            link.addEvent("click", function(evt) {
                evt.stop();
                content.reveal();
                link.hide();
            });
        }
    });
});