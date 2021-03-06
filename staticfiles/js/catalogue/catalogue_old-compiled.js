"use  strict";

var Api = function () {
    function Api(url) {
        this.url = url;
        this.loading = false;
        this.params = { limit: 0, attributes: '', offset: 0, categories: [] };
        this.count = 1;
    }
    Api.prototype.query = function (limit) {
        this.loading = true;
        var _this = this;
        this.params.limit = limit;
        if (this.params.offset >= this.count) return;
        if ('attributes' in this.params && this.params.attributes.length == 0) delete this.params.attributes;
        $.getJSON(this.url, this.params, function (res) {
            _this.renderResults(res);
            _this.appendResults = false;
            _this.count = res.count;
            history.pushState('', document.title, api.params.attributes);
            _this.loading = false;
        });
    };
    Api.prototype.watchResults = function () {
        if (api.productsEnd.visible() && !api.loading) {
            api.appendResults = true;
            api.params.offset += 6;
            api.query(6);
        }
    };
    Api.prototype.renderResults = function (res) {
        if (!this.appendResults) $('#products-container').html('');else this.productsEnd.remove();
        for (var r in res.results) {
            $.ajax({
                url: "/api/products/" + res.results[r].id + "/price/",
                async: false,
                type: 'GET',
                success: function (rr) {
                    res.results[r].price = rr;
                }
            });
            $.ajax({
                url: "/api/products/" + res.results[r].id + "/availability/",
                async: false,
                type: 'GET',
                success: function (rr) {
                    res.results[r].availability = rr;
                }
            });
            res.currentImage = 0;
            $('#products-container').append(Handlebars.templates['product'](res.results[r]));
        }

        var atts = [];
        if (this.attributes) {
            this.attributes.forEach(function (attribute, i) {
                atts.push([]);
                attribute.forEach(function (a, j) {
                    var aa = atts[i];
                    var f = aa.filter(function (at) {
                        return at.name == a.name;
                    });
                    if (f.length == 0) {
                        aa.push(a);
                        aa[aa.length - 1].ids = [a.id];
                    } else f[0].ids.push(a.id);
                });
            });
            $('#filters-list ul').html(Handlebars.templates['filters']({ attributes: atts }));
        }
        console.log(this.attributes);
        $('#products-container').append('<div id="products-end"></div>');
        this.productsEnd = $('#products-end');
        $(window).unbind('scroll', this.watchResults);
        $(window).bind('scroll', this.watchResults);
        this.products = res.results;
    };
    ;
    return Api;
}();
var api = new Api('/api/products/');
$(document).ready(function () {
    $('#products-container').delegate('.image', 'mouseover', function () {
        var parentId = $(this).parent().attr('data-id');
        var product = api.products.filter(function (p) {
            if (p.id == parentId) return true;
        })[0];
        var image = $(this).find('img');
        product.interval = window.setInterval(function () {
            if (product.currentImage >= product.images.length + 1) product.currentImage = 0;else product.currentImage += 1;
            image.attr('src', product.images[product.currentImage]);
        }, 1000);
    });
    $('#products-container').delegate('.image', 'mouseout', function () {
        var parentId = $(this).parent().attr('data-id');
        var product = api.products.filter(function (p) {
            if (p.id == parentId) return true;
        })[0];
        clearInterval(product.interval);
    });
    var categories = $('#product-categories').val();
    if (categories) api.params.categories = categories;
    $('#tree').treeview({
        enableLinks: true,
        data: JSON.parse($('#tree').attr('data')), expandIcon: 'fa fa-plus-square',
        collapseIcon: 'fa fa-minus-square' });
    $('#filters-list').delegate('li', 'click', function () {
        console.log('remove');
        var select = $('select[data-attribute="' + $(this).attr('data-attribute') + '"]');
        var ids = $(this).attr('data-ids');
        var values = $(select).selectpicker('val');
        if (typeof values == 'string') {
            $(select).selectpicker('val', '');
        } else if (typeof values == 'object') {
            for (var id in ids.split(',')) {
                values.splice(values.indexOf(ids[id]) - 1, 1);
            }
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
        api.params.offset = 0;
        api.count = 1;
        var selectedId = $(this).attr('data-attribute');
        var filterAttributes = [];
        $('#product-filters select').each(function (i, s) {
            var attr = $(s).attr('data-attribute');
            filterAttributes.push(attr);
            var val = $(s).val();
            if (typeof val == 'string' && val != '') {
                var selected = $(s).find('option:selected');
                val.split(',').forEach(function (a, i) {
                    attributes.push([{
                        id: a, name: $(selected).attr('name'),
                        attribute: attr
                    }]);
                });
            } else if (typeof val == 'object' && val !== null) {
                attributes.push([]);
                var a_length_1 = attributes.length - 1;
                val.forEach(function (v, i) {
                    v.split(',').forEach(function (a, i) {
                        attributes[a_length_1].push({
                            id: a, name: $(s).find('option[value="' + v + '"]').attr('name'),
                            attribute: $(s).attr('data-attribute')
                        });
                    });
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
        //odświeżanie filtrów
        $.getJSON('/api/available_attributes/', { attributes: JSON.stringify(api.attributes), filters: JSON.stringify(filterAttributes) }, function (res) {
            res.forEach(function (r) {
                if (r.id != selectedId) {
                    var s = $('select[data-attribute=' + r.name + ']');
                    var options = $(s).find('option');
                    options.each(function (i, o) {
                        var id = $(o).attr('data-id');
                        if ($.inArray(id, r['options']) == -1) $(o).attr('disabled', 'true');
                    });
                    $(s).selectpicker('refresh');
                }
            });
        });
        api.query(12);
    });
    api.query(12);
});

//# sourceMappingURL=catalogue_old-compiled.js.map