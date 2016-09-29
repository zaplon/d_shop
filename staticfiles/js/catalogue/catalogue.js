function limit(text){
    return text.length > 75 ? text.substr(0,97) + '...' : text;
}

var viewModel = {
    filters : ko.observableArray([]),
    products : ko.observableArray([]),
    priceRange : ko.observableArray([]),
    categories: $('#variables input[name="categories"]').val(),
    filterNames: JSON.parse($('#variables input[name="filters"]').val()),
    limit: 12,
    offset: 0,
    loading: false,
    count: 0,
    productsEnd: $('#products-end'),
    setOptionDisable: function(option, item) {
            ko.applyBindingsToNode(option, {disable: item.disable}, item);
    },
    removeFilter: function(value, event){
        var newOptions = [];
        var filter = viewModel.filters()[parseInt($(event.target).attr('data-index'))];
        var options = filter.selectedOptions();
        for (var o in options){
            if (options[o] != value)
                newOptions.push(filter.selectedOptions()[o]);
        }
        filter.selectedOptions(newOptions);
        viewModel.loadData();
    },
    watchScroll: function(){
      if (viewModel.productsEnd.visible() && !viewModel.loading) {
          viewModel.offset += 12;
          if (viewModel.offset < viewModel.count)
            viewModel.loadData(true);
      }
    },
    loadData: function(dontRefreshFilters){
        viewModel.loading = true;
        var params = {filters: JSON.stringify(viewModel.filterNames), attributes: [], categories: viewModel.categories,
            limit: viewModel.limit, offset: viewModel.offset};
        this.filters().forEach(function(f){
            var a = [];
            if (f.selectedOptions)
                f.selectedOptions().forEach(function(o){
                    a.push(f.options.filter(function(option){ return o == option.slug;  })[0].slug);
                });
            if (a.length > 0)
                params.attributes.push(a.join('.'));
        });
        params.attributes = params.attributes.join(',');
        if (dontRefreshFilters)
            params.dont_refresh_filters = true;
        $.getJSON("/api/products/", params , function(data){
            viewModel.count = data.count;
            viewModel.loading = false;
            if (dontRefreshFilters){
                viewModel.products(viewModel.products().concat(data.results.products));
                return true;
            }
            viewModel.products(data.results.products);
            viewModel.priceRange(data.results.prices);
            var filters = viewModel.filters();
            if (filters.length == 0){
                data.results.filters.forEach(function(f){
                    f.selectedOptions = ko.observableArray([]);
                    f.options.forEach(function(option){
                        option.disable = ko.observable(false);
                    });
                });
                viewModel.filters(data.results.filters);
                $('.selectpicker').selectpicker();
            }
            else {
                data.results.filters.forEach(function (dataFilter, i) {
                    //if (filters.length > 0)
                    //    f.selectedOptions = filters[i].selectedOptions;  //f.options.filter(function(o){ return $.inArray(o, data.filters[i]); });
                    //else
                    //    f.selectedOptions = [];
                    //if (!f.name)
                    //    f.name = filters[i].name;
                    var filter = viewModel.filters()[i];
                    filter.options.forEach(function (option) {
                        if (!dataFilter.options.find(function (o) {
                                return o.slug == option.slug
                            })) {
                            option.disable(true);
                        }
                        else
                            option.disable(false);
                    });
                });
                $('.selectpicker').selectpicker('refresh');
            }
        });
        $(window).unbind('scroll', viewModel.watchScroll);
        $(window).bind('scroll', viewModel.watchScroll);
    },
    selectionChanged: function(event) {
        viewModel.loadData();
    }
};
ko.applyBindings(viewModel);

$(document).ready(function () {

    viewModel.loadData();

    $('#products-container').delegate('.image', 'mouseover', function () {
        var parentId = $(this).parent().attr('data-id');
        var product = viewModel.products().filter(function (p) {
            if (p.id == parentId) return true;
        })[0];
        var image = $(this).find('img');
        product.interval = window.setInterval(function () {
            if (isNaN(product.currentImage))
                product.currentImage = 0;
            if (product.currentImage >= product.images.length)
                product.currentImage = 0;
            else
                product.currentImage += 1;
            image.attr('src', product.images[product.currentImage].original);
        }, 1000);
    });
    $('#products-container').delegate('.image', 'mouseout', function () {
        var parentId = $(this).parent().attr('data-id');
        var product = viewModel.products().filter(function (p) {
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
});
