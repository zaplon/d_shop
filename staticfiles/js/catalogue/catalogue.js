var viewModel = {
    filters : ko.observableArray([]),
    products : ko.observableArray([]),
    categories: $('#variables input[name="categories"]').val(),
    filterNames: JSON.parse($('#variables input[name="filters"]').val())
};
ko.applyBindings(viewModel);

$(document).ready(function () {

    params = {filters: JSON.stringify(viewModel.filterNames)};
    $.getJSON("/api/products/", params , function(data) {
        data.filters.forEach(function(f, i){
            f.selectedOptions = f.options.filter(function(o){ return o.id == 1 });
        });
        viewModel.filters(data.filters);
        $('.selectpicker').selectpicker();
    });

    $('#products-container').delegate('.image', 'mouseover', function () {
        var parentId = $(this).parent().attr('data-id');
        var product = api.products.filter(function (p) {
            if (p.id == parentId) return true;
        })[0];
        var image = $(this).find('img');
        product.interval = window.setInterval(function () {
            if (product.currentImage >= product.images.length + 1)
                product.currentImage = 0;
            else
                product.currentImage += 1;
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
    $('#tree').treeview({
        enableLinks: true,
        data: JSON.parse($('#tree').attr('data')), expandIcon: 'fa fa-plus-square',
        collapseIcon: 'fa fa-minus-square'
    });
})
