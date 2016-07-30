/// <reference path="jquery.d.ts" />

class Utils{
    public isOnScreen(element, offset)
    {
        var curPos = element.offset();
        var curTop = curPos.top;
        if (offset)
            curTop -= offset;
        return (curTop < window.scrollY) ? true : false;
    }
    public fixedTopSpy()
    {
        var me = this;
        $( window ).scroll(function(){
            var div = $('#fixed-top-spy');
            var mark = $('#fixed-top-spy-mark');
            if (!div)
                return;
            if (me.isOnScreen(mark, $('#navbar-header').height())) {
                if (!div.hasClass('fixed-top'))
                    div.addClass('fixed-top');

            }else {
                if (div.hasClass('fixed-top'))
                    div.removeClass('fixed-top');
            }
        })
    }
}

var utils = new Utils();
$(document).ready(() => {
    //utils.fixedTopSpy();
});