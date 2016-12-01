/// <reference path="../jquery.d.ts" />
var SearchResult = (function () {
    function SearchResult(record) {
        this.images = record.images;
        this.title = record.title;
        this.categories = record.categories;
        this.description = record.description;
        this.price = record.stockrecords[0].price.toFixed(2) + 'zł';
        this.attributes = record.attribute_values;
        this.id = record.id;
        this.front_url = record.front_url;
        this.is_available = true;
    }
    return SearchResult;
}());
var SearchFilter = (function () {
    function SearchFilter(name) {
        this.name = name;
        this.options = [];
        this.slug = name;
    }
    return SearchFilter;
}());
var Search = (function () {
    function Search() {
        this.params = {
            prices: [0, 0],
            types: [''],
            category: '',
            sort: 'stockRecords.price',
            sortDir: 'desc',
            query: '',
            attribute_values: {}
        };
        this.from = 0,
            this.size = 12,
            this.elasticQuery = { query: { bool: { must: {}, filter: {} } }, aggs: {}, sort: [], from: this.from, size: this.size };
        this.filters = [];
        this.results = [];
    }
    Search.prototype.transformResponse = function (res, showAggregations) {
        var me = this;
        me.results = [];
        res.hits.hits.forEach(function (r) {
            me.results.push(new SearchResult(r._source));
        });
        if (!showAggregations)
            return me.results;
        me.filters = [];
        if (me.filters.length == 0)
            res.aggregations.attributes.attributes.buckets.forEach(function (b) {
                var matches = me.filters.filter(function (f) {
                    return b.key.split('_')[0] == f.name;
                });
                if (matches.length == 0) {
                    me.filters.push(new SearchFilter(b.key.split('_')[0]));
                    var select = me.filters[me.filters.length - 1];
                }
                else
                    var select = matches[0];
                var name = b.key.split('_')[1];
                select.options.push({ slug: name, id: b.id, text: name });
            });
        me.filters = me.filters.slice(0, 6);
        return { products: me.results, filters: me.filters, prices: [res.aggregations.min_price.value, res.aggregations.max_price.value],
            count: res.hits.total };
    };
    ;
    Search.prototype.getResults = function (showAggregations) {
        if (showAggregations === void 0) { showAggregations = false; }
        this.elasticQuery.query.bool = { must: [] };
        if (!this.elasticQuery.query.bool.filter)
            this.elasticQuery.query.bool.filter = {};
        var me = this;
        if (this.params.prices[1] > 0) {
            if (!('range' in this.elasticQuery.query.bool.filter))
                this.elasticQuery.query.bool.filter.range = {};
            this.elasticQuery.query.bool.filter.range['stockrecords.price'] = {
                'gte': this.params.prices[0],
                'lte': this.params.prices[1]
            };
        }
        if (this.params.category.length > 0 && this.params.category[0]) {
            this.elasticQuery.query.bool.must.push(
            //{match: {type: 'Etu'}}
            { nested: { path: 'categories', query: { bool: { must: { match: { 'categories.ids': this.params.category } } } } } });
        }
        if (this.params.query.length > 0) {
            this.elasticQuery.query.bool.must.push({ match: { _all: this.params.query } });
        }
        var sort = {};
        sort[this.params.sort] = this.params.sortDir;
        this.elasticQuery.sort = [sort];
        if (this.params.types.length > 0) {
            var subQuery = [];
            this.params.types.forEach(function (t) {
                if (t.length > 0) {
                    subQuery.push({ match: { 'type': t } });
                    this.elasticQuery.query.bool.must.push({ bool: { should: subQuery } });
                }
            }, this);
            if (!$.isEmptyObject(this.params.attribute_values)) {
                var subQuery = [];
                for (var param in this.params.attribute_values) {
                    if (typeof (this.params.attribute_values[param]) == "object" && this.params.attribute_values[param].length > 0) {
                        var bool = { bool: { should: [] } };
                        this.params.attribute_values[param].forEach(function (p) {
                            bool.bool.should.push({ match: { 'attribute_values.slug': param + '_' + p } });
                        });
                        this.elasticQuery.query.bool.must.push({
                            nested: {
                                path: "attribute_values",
                                //score_mode: "max",
                                query: {
                                    bool: {
                                        must: bool
                                    }
                                }
                            }
                        });
                    }
                }
                ;
            }
            var me_1 = this;
            if (showAggregations)
                this.elasticQuery.aggs = {
                    min_price: {
                        min: { field: "stockrecords.price" }
                    },
                    max_price: {
                        max: { field: "stockrecords.price" }
                    },
                    types: {
                        terms: {
                            field: "type",
                            size: 3000
                        }
                    },
                    attributes: {
                        nested: {
                            path: "attribute_values"
                        },
                        aggs: {
                            attributes: {
                                terms: {
                                    field: "attribute_values.slug",
                                    size: 3000
                                }
                            }
                        }
                    }
                };
            if (!('range' in this.elasticQuery.query.bool.filter))
                delete this.elasticQuery.query.bool.filter;
            console.log(this.elasticQuery);
            return $.ajax({
                url: 'https://obudowynatelefon.pl:9200/_search/',
                type: "POST",
                data: JSON.stringify(this.elasticQuery),
                contentType: "application/json; charset=utf-8",
                async: true,
                dataType: "json"
            });
        }
    };
    return Search;
}());
var s = new Search();
//# sourceMappingURL=api.js.map