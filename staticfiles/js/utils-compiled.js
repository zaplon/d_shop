/// <reference path="jquery.d.ts" />
var Utils = function () {
    function Utils() {}
    Utils.prototype.isOnScreen = function (element, offset) {
        var curPos = element.offset();
        var curTop = curPos.top;
        if (offset) curTop -= offset;
        return curTop < window.scrollY ? true : false;
    };
    Utils.prototype.fixedTopSpy = function () {
        var me = this;
        $(window).scroll(function () {
            var div = $('#fixed-top-spy');
            var mark = $('#fixed-top-spy-mark');
            if (!div) return;
            if (me.isOnScreen(mark, $('#navbar-header').height())) {
                if (!div.hasClass('fixed-top')) div.addClass('fixed-top');
            } else {
                if (div.hasClass('fixed-top')) div.removeClass('fixed-top');
            }
        });
    };
    return Utils;
}();
var utils = new Utils();
$(document).ready(function () {
    //utils.fixedTopSpy();
});
//# sourceMappingURL=utils.js.map

//# sourceMappingURL=utils-compiled.js.map