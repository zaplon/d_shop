/// <reference path="../jquery.d.ts" />
/// <reference path="../jquery_ui.d.ts" />

class SearchResult {
    images:string[];
    title:string;
    description:string;
    price:string;
    categories:string[];
    attributes:{}[];
    id: number;
    front_url: string;
    is_available: boolean;

    constructor(record) {
        this.images = record.images;
        this.title = record.title;
        this.categories = record.categories;
        this.description = record.description;
        this.price = record.stockrecords[0].price.toFixed(2) + 'zł';
        this.attributes = record.attribute_values;
        this.id = record.id;
        this.front_url = record.front_url;
        this.is_available = record.stockrecords[0].num_in_stock > 0;
    }
}

class SearchFilter {
    name:string;
    slug:string;
    options:{id: number, slug: string, text: string}[];

    constructor(name) {
        this.name = name;
        this.options = [];
        this.slug = name;
    }
}

class Search {
    params:{prices: [number, number], types: string[], category: string, sort: string,
        query: string, attribute_values: {}, sortDir: string};
    results:SearchResult[];
    filters:SearchFilter[];
    size: number;
    from: number;
    response:any;
    excludeFiters: string[];
    filtersOrder: string[];

    constructor() {
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
        this.excludeFiters =  ['Gwarancja'],
        this.filtersOrder = ['Kompatybilność', 'Kolor bazowy'],
        this.elasticQuery = {query: {bool: {must: {}, filter: {}}}, aggs: {}, sort: [], from: this.from, size: this.size};
        this.filters = [];
        this.results = [];
    }

    elasticQuery:{
        query: any, //filter: any, bool: {must: {}}
        aggs: {},
        from: number,
        size: number,
        sort: {}[]
    };
    completion(query){
        return $.post("/search/rest/", {'completion': true, 'query': query});
    };
    transformResponse(res, showAggregations) {
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
                    return b.key.split('_')[0] == f.name
                });
                if (matches.length == 0) {
                    me.filters.push(new SearchFilter(b.key.split('_')[0]));
                    var select = me.filters[me.filters.length - 1];
                }
                else
                    var select = matches[0];
                let name = b.key.split('_')[1];
                select.options.push({slug: name, id: b.id, text: name});
            });
        for (var i=0;i<me.filters.length;i++)
            if (me.excludeFiters.indexOf(me.filters[i]['name']) > -1)
                me.filters.splice(i,1);
        me.filters = me.filters.slice(0,6);
        me.filters.sort(function(a, b){
            if (me.filtersOrder.indexOf(a['name']) > -1 && me.filtersOrder.indexOf(b['name']) > -1)
                return me.filtersOrder.indexOf(a['name']) < me.filtersOrder.indexOf(b['name']) ? -1: 1;
            else if (me.filtersOrder.indexOf(a['name']) > -1)
                return -1;
            else if (me.filtersOrder.indexOf(b['name']) > -1)
                return 1;
            else
                return a < b ? -1 : 1;
        });
        return {products: me.results, filters: me.filters, prices: [res.aggregations.min_price.value, res.aggregations.max_price.value],
                count: res.hits.total};
    };
    getResults(showAggregations:boolean = false) {
        this.elasticQuery.query.bool = {must: []};
        if (!this.elasticQuery.query.bool.filter)
            this.elasticQuery.query.bool.filter = {};
        var me = this;
        if (this.params.prices[1] > 0) {
            if (!('range' in this.elasticQuery.query.bool.filter))
                this.elasticQuery.query.bool.filter.range = {};
            this.elasticQuery.query.bool.filter.range['stockrecords.price'] = {
                'gte': this.params.prices[0],
                'lte': this.params.prices[1]
            }
        }

        if (this.params.category.length > 0 && this.params.category[0]) {
            this.elasticQuery.query.bool.must.push(
                //{match: {type: 'Etu'}}
                {nested:{path:'categories', query:{bool:{must:{match:{'categories.ids': this.params.category }}}}}}
            )
        }

        if (this.params.query.length > 0) {
            this.elasticQuery.query.bool.must.push({match: {_all: this.params.query}});
        }

        var sort = [{}, {}];
        sort[1][this.params.sort] = this.params.sortDir;
        sort[0]['stockrecords.is_available'] = 'desc';

        this.elasticQuery.sort = sort;

        if (this.params.types.length > 0) {
            var subQuery = [];
            this.params.types.forEach(function (t) {
                if (t.length > 0) {
                    subQuery.push({match: {'type': t}});
                    this.elasticQuery.query.bool.must.push({bool: {should: subQuery}});
                }
            }, this);

            if (!$.isEmptyObject(this.params.attribute_values)) {
                var subQuery = [];
                for (var param in this.params.attribute_values){
                    if (typeof(this.params.attribute_values[param]) == "object" && this.params.attribute_values[param].length > 0) {
                        var bool = {bool: {should: []}};
                        this.params.attribute_values[param].forEach(function(p){
                             bool.bool.should.push({match: {'attribute_values.slug': param + '_' + p}});
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
                        //subQuery.push(bool);
                    }
                };
            }

            let me = this;
            if (showAggregations)
                this.elasticQuery.aggs = {
                    min_price: {
                        min: {field: "stockrecords.price"}
                    },
                    max_price: {
                        max: {field: "stockrecords.price"}
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
                url:  "/search/rest/",
                type: "POST",
                data: JSON.stringify(this.elasticQuery),
                contentType: "application/json; charset=utf-8",
                async: true,
                dataType: "json"
            });
        }
    }
}
let s = new Search();

//$(document).ready(function(){
//    $('.search-form input').autocomplete({
//      source: "/search/rest/",
//      minLength: 2,
//      select: function( event, ui ) {
//        window.location.href = '/szukaj/?q=' + ui.item.text;
//      }
//    }).data("ui-autocomplete")._renderItem = function( ul, item ) {
//      return $( "<li>" )
//        .append( "<div>" + item.text + "<br>" + "</div>" )
//        .appendTo( ul );
//    };
//});