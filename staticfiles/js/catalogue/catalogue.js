"use  strict";
var Api = (function () {
    function Api(url) {
        this.url = url;
        this.params = { limit: 0, attributes: '' };
    }
    Api.prototype.query = function (limit) {
        var _this = this;
        this.params.limit = limit;
        if ('attributes' in this.params && this.params.attributes.length == 0)
            delete this.params.attributes;
        $.getJSON(this.url, this.params, function (res) {
            _this.renderResults(res);
            _this.appendResults = false;
            history.pushState('', document.title, api.params.attributes);
        });
    };
    Api.prototype.watchResults = function () {
        if (utils.isOnScreen(api.productsEnd, 0)) {
            console.log('read');
        }
    };
    Api.prototype.renderResults = function (res) {
        if (!this.appendResults)
            $('#products-container').html('');
        for (var r in res.results) {
            $('#products-container').append(Handlebars.templates['product'](res.results[r]));
        }
        $('#filters-list ul').html(Handlebars.templates['filters']({ attributes: this.attributes }));
        console.log(this.attributes);
        $('#products-container').append('<div id="products-end"></div>');
        this.productsEnd = $('#products-end');
        $(window).unbind('scroll', this.watchResults);
        $(window).bind('scroll', this.watchResults);
    };
    ;
    return Api;
}());
var api = new Api('/api/products/');
$(document).ready(function () {
    $('#filters-list').delegate('li', 'click', function () {
        console.log('remove');
        var select = $('select[data-attribute="' + $(this).attr('data-attribute') + '"]');
        var id = $(this).attr('data-id');
        var values = $(select).selectpicker('val');
        if (typeof(values) == 'string'){
            $(select).selectpicker('val', '');
        }
        else if (typeof(values) == 'object'){
            values.splice(values.indexOf(id)-1,1);
            $(select).selectpicker('val', values);
        }

        $(this).remove();
        $(select).selectpicker('refresh');
        $(select).trigger('change');
        api.query(12);
    });
    var productsEnd = $('#products-end');
    $('#product-filters select').change(function (e) {
        var attributes = [];
        $('#product-filters select').each(function (i, s) {
            var val = $(s).val();
            if (typeof (val) == 'string' && val != '') {
                var selected = $(s).find('option:selected');
                val.split(',').forEach(function(a, i){
                    attributes.push([{
                        id: parseInt(a), name: $(selected).attr('name'),
                        attribute: $(s).attr('data-attribute')
                    }]);
                })
            }
            else if (typeof (val) == 'object' && val !== null) {
                attributes.push([]);
                var a_length_1 = attributes.length - 1;
                val.forEach(function (v, i) {
                    v.split(',').forEach(function(a, i){
                        attributes[a_length_1].push({
                            id: parseInt(a), name: $(s).find('option[value="' + v + '"]').attr('name'),
                            attribute: $(s).attr('data-attribute')
                        });
                    })
                });
            }
        });
        api.attributes = attributes;
        var atts_ids = [];
        attributes.forEach(function (att, i) {
            atts_ids.push([]);
            att.forEach(function (a, j) {
                atts_ids[atts_ids.length - 1].push(a.id);
            });
            atts_ids[atts_ids.length - 1] = atts_ids[atts_ids.length - 1].join('.');
        });
        api.params.attributes = atts_ids.join(',');
        api.query(12);
    });
    api.query(12);
});