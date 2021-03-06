function limit(text) {
    return text.length > 75 ? text.substr(0, 97) + '...' : text;
}

var viewModel = {
    formatCurrency: function (value) {
        return parseFloat(value).toFixed(2).replace('.', ',') + "zł";
    },
    showFilters: function () {
        var filters = $('#product-filters-container');
        if (filters.hasClass('hidden-sm-down')) {
            filters.removeClass('hidden-sm-down');
            $('#show-filters').html('Ukryj filtry');
        }
        else {
            filters.addClass('hidden-sm-down');
            $('#show-filters').html('Pokaż filtry');
        }
    },
    showCategories: function () {
        var cats = $('#mobile-tree');
        if (cats.hasClass('hidden-sm-down')) {
            cats.removeClass('hidden-sm-down');
            //$('#show-categories').html('Ukryj filtry');
        }
        else {
            cats.addClass('hidden-sm-down');
            //$('#show-categories').html('Pokaż filtry');
        }
    },
    filters: ko.observableArray([]),
    products: ko.observableArray([]),
    hasFilters: ko.observable(false),
    priceRange: {range: {}, min: ko.observable(0), max: ko.observable(0)},
    selectedType: ko.observable(),
    categories: $('#variables input[name="categories"]').val().split('.'),
    productClasses: JSON.stringify($('#variables input[name="product_classes"]').val().split(',')),
    filterNames: JSON.parse($('#variables input[name="filters"]').val()),
    sortOptions: typeof(sortOptions) != "undefined" ? sortOptions : [{
        name: 'Ceną rosnąco',
        id: 0,
        value: 'price'
    }, {name: 'Ceną malejąco', id: 1, value: '-price'}],
    selectedSortOption: typeof(selectedSortOption) != "undefined" ? selectedSortOption : 0,
    limit: 12,
    firstLoad: true,
    offset: 0,
    loading: false,
    count: 0,
    productsEnd: $('#products-end'),
    setOptionDisable: function (option, item) {
        if (item)
            ko.applyBindingsToNode(option, {disable: item.disable}, item);
    },
    removeFilter: function (value, event) {
        var newOptions = [];
        var filter = viewModel.filters()[parseInt($(event.target).attr('data-index'))];
        var options = filter.selectedOptions();
        for (var o in options) {
            if (options[o] != value)
                newOptions.push(filter.selectedOptions()[o]);
        }
        filter.selectedOptions(newOptions);
        var filters = false;
        viewModel.filters().forEach(function(f){
            if (f.selectedOptions().length > 0)
                var filters = true;
        });
        viewModel.hasFilters(true);    
        viewModel.loadData(filters);
    },
    clearFilters: function() {
        this.filters().forEach(function(f){
            f.selectedOptions([]);
        });
        $('.selectpicker').selectpicker('refresh');
        this.hasFilters(false);
    },
    watchScroll: function () {
        if (viewModel.productsEnd.visible() && !viewModel.loading) {
            //console.log('scroll');
            s.elasticQuery.from += 12;
            if (viewModel.offset < viewModel.count)
                viewModel.loadData(false, true);
        }
    },
    loadData: function (ev, dontRefreshFilters, filterPrices) {
        viewModel.loading = true;
        var params = {};
        if (viewModel.priceRange.range.start > 0)
            params.start = viewModel.priceRange.range.start;
        if (viewModel.priceRange.range.end > 0)
            params.end = viewModel.priceRange.range.end;
        if (dontRefreshFilters)
            params.dont_refresh_filters = true;
        else
            s.elasticQuery.from = 0;
        //$.getJSON("/api/products/", params , function(data){

        if (viewModel.selectedSortOption == 0) {
            s.params.sort = 'stockrecords.price';
            s.params.sortDir = 'asc';
        }
        if (viewModel.selectedSortOption == 1) {
            s.params.sort = 'stockrecords.price';
            s.params.sortDir = 'desc';
        }
        if (viewModel.selectedSortOption == -1) {
            s.params.sort = '_score';
            s.params.sortDir = 'desc';
        }
        s.params.from = viewModel.offset;
        s.params.limit = viewModel.limit;
        s.params.category = viewModel.categories.length > 0 ? viewModel.categories[viewModel.categories.length - 1] : '';
        s.params.attribute_values = s.baseAttributes;
        s.params.types = JSON.parse(viewModel.productClasses);
        if (viewModel.priceRange.range.start > 0)
            s.params.prices[0] = viewModel.priceRange.range.start;
        if (viewModel.priceRange.range.end > 0)
            s.params.prices[1] = viewModel.priceRange.range.end;
        this.filters().forEach(function (f) {
            if (f.selectedOptions)
                s.params.attribute_values[f.name] = f.selectedOptions();
        });
        s.getResults(!dontRefreshFilters).done(function (data) {
            data = s.transformResponse(data, !dontRefreshFilters);
            $(window).unbind('scroll', viewModel.watchScroll);
            $(window).bind('scroll', viewModel.watchScroll);
            s.from += viewModel.limit;
            viewModel.loading = false;
            if (dontRefreshFilters) {
                viewModel.products(viewModel.products().concat(data));
                return true;
            }
            data = {
                results: {
                    products: data.products, filters: data.filters, prices: {
                        min: data.prices[0], max: data.prices[1],
                        range: {start: data.prices[0], end: data.prices[1]}
                    }
                }, count: data.count
            };
            viewModel.count = data.count;
            viewModel.products(data.results.products);
            if (viewModel.firstLoad)
                viewModel.priceRange = data.results.prices;
            if (viewModel.firstLoad || filterPrices) {
                $('#price-from').html(viewModel.priceRange.min.toFixed(0));
                $('#price-to').html(viewModel.priceRange.max.toFixed(0));
                if (viewModel.firstLoad) {
                    viewModel.priceSlider.setAttribute('min', viewModel.priceRange.min);
                    viewModel.priceSlider.setAttribute('max', viewModel.priceRange.max);
                }
                viewModel.priceSlider.setValue([viewModel.priceRange.range.start, viewModel.priceRange.range.end]);
            }
            var filters = viewModel.filters();
            if (filters.length == 0) {
                data.results.filters.forEach(function (f) {
                    f.selectedOptions = ko.observableArray([]);
                    f.options.forEach(function (option) {
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
                    //if (!(ev && $(ev.target) && dataFilter.name == $(ev.target).attr('title'))){
                    var filters = viewModel.filters().filter(function (f) {
                        return f.slug == dataFilter.slug
                    });
                    if (filters.length == 0)
                        return;
                    var filter = filters[0];
                    filter.options.forEach(function (option) {

                        if (!dataFilter.options.find(function (o) {
                                return o.slug == option.slug
                            })) {
                            //option.disable(true);
                        }
                        else
                            option.disable(false);
                    });
                    //}
                    //filter.options.sort(function(a,b){ return a > b  });
                });
                $('.selectpicker').selectpicker('refresh');
            }
            viewModel.firstLoad = false;
        });
        //me.response = {results: me.results, filters: me.filters, prices: {min: res.aggregations.min_price, hits: res.hits,
        //max: res.aggregations.max_price, start: res.aggregations.min_price, end: res.aggregations.min_price}}
    },
    selectionChanged: function (event) {
        viewModel.loadData(event);
        viewModel.hasFilters(false);
        viewModel.filters().forEach(function(f){
            if (f.selectedOptions().length > 0)
                viewModel.hasFilters(true);
        });
    }
};
ko.applyBindings(viewModel);
viewModel.priceSlider = new Slider("#price-slider", {value: [10, 20]});
$(document).ready(function () {

    //viewModel.loadData();
    //viewModel.slider = $("#price-slider").bootstrapSlider();
    //viewModel.slider.on('change', function(oldVal, newVal){
    //   console.log('change');
    //    console.log(newVal);
    //    viewModel.loadData();
    //});
    viewModel.priceSlider.on('slideStop', function (value) {
        console.log(value);
        viewModel.priceRange.range.start = parseFloat(value[0]);
        viewModel.priceRange.range.end = parseFloat(value[1]);
        viewModel.loadData(false, false, true);
    });

    $('#products-container').delegate('.image', 'mouseover', function () {
        var parentId = $(this).parent().attr('data-id');
        var product = viewModel.products().filter(function (p) {
            if (p.id == parentId) return true;
        })[0];
        var image = $(this).find('img');

        var changeImage = function () {
            if (isNaN(product.currentImage))
                product.currentImage = 0;
            if (product.currentImage >= product.images.length - 1)
                product.currentImage = 0;
            else
                product.currentImage += 1;
            image.attr('src', product.images[product.currentImage].original);
        };
        changeImage();
        product.interval = window.setInterval(function () {
            changeImage();
        }, 750);
    });
    $('#products-container').delegate('.image', 'mouseout', function () {
        var parentId = $(this).parent().attr('data-id');
        var product = viewModel.products().filter(function (p) {
            if (p.id == parentId) return true;
        })[0];
        clearInterval(product.interval);
    });
    var categories = $('#product-categories').val();
    if ($('#tree').length > 0)
        $('#tree').treeview({
            enableLinks: true,
            data: JSON.parse($('#tree').attr('data')), expandIcon: 'fa fa-plus-square-o',
            collapseIcon: 'fa fa-minus-square-o'
        });
    if ($('#mobile-tree').length > 0)
        $('#mobile-tree').treeview({
            enableLinks: true,
            data: JSON.parse($('#mobile-tree').attr('data')), expandIcon: 'fa fa-plus-square-o',
            collapseIcon: 'fa fa-minus-square-o'
        });

});
