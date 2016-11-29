/// <reference path="../jquery.d.ts" />

// {
//   "query": { 
//     "bool": { 
//       "must": [
//         { "match": { "title":   "Search"        }}, 
//         { "match": { "content": "Elasticsearch" }}  
//       ],
//       "filter": [ 
//         { "term":  { "status": "published" }}, 
//         { "range": { "publish_date": { "gte": "2015-01-01" }}} 
//       ]
//     }
//   }
// }


class SearchResult {
    images:string[];
    title:string;
    description:string;
    price:number;
    categories:string[];
    attributes:{}[];

    constructor(record) {
        this.images = record.images;
        this.title = record.title;
        this.categories = record.categories;
        this.description = record.description;
        this.price = record.stockrecords[0].price;
        this.attributes = record.attribute_values;
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
    params:{prices: [number, number], types: string[], categories: string[], sort: string, scroll: number,
        query: string, attribute_values: string[], sortDir: string};
    results:SearchResult[];
    filters:SearchFilter[];
    response:any;

    constructor() {
        this.params = {
            prices: [0, 0],
            types: [''],
            categories: [''],
            sort: 'stockRecords.price',
            sortDir: 'asc',
            scroll: 0,
            query: '',
            attribute_values: []
        };
        this.elasticQuery = {query: {filter: {}, bool: {must: {}}}, aggs: {}};
        this.filters = [];
        this.results = [];
    }

    elasticQuery:{
        query: any, //filter: any, bool: {must: {}}
        aggs: {},
        sort: {}
    };

    transformResponse(res){
        res.hits.hits.forEach(function (r) {
            me.results.push(new SearchResult(r._source));
        });
        if (!showAggregations)
            return me.results;
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
        return me.results;
    }
    
    getResults(showAggregations:boolean = false) {
        this.elasticQuery.query.bool = {must: []};
        if (this.params.prices[1] > 0) {
            if (!('range' in this.elasticQuery.query.filter))
                this.elasticQuery.query.filter.range = {};
            this.elasticQuery.query.filter.range['stockrecords.price'] = {
                'gte': this.params.prices[0],
                'lte': this.params.prices[1]
            }
        }
        
        if (this.params.query.length > 0) {
            this.elasticQuery.query.bool.must.push({match: {_all: this.params.query}});
        }
        
        var sort = {};
        sort[this.params.sort] = this.params.sortDir;
        this.elasticQuery.sort = [sort];
        
        if (this.params.types.length > 0){
            var subQuery = [];
            this.params.types.forEach(function(t){
                subQuery.push({match: {'type': t}});
            }
            this.elasticQuery.query.bool.must.push({bool: {should: subQuery });
        }
        
        if (this.params.attribute_values.length > 0) {
            var subQuery = [];
            this.params.attribute_values.forEach(function(param){
                if (typeof(param) == "object"){
                    var bool = {bool: should: []};
                    for (var p in params)
                        bool.push({ match: {'attribute_values.slug': p } } })
                }
                subQuery.push(bool);
            });
            this.elasticQuery.query.bool.must.push({
                nested: {
                    path: "attribute_values",
                    score_mode: "max",
                    query: {
                        bool: {
                            must: subQuery
                        }
                    }
                }
            });
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
                        field: "type"
                    }
                },
                attributes: {
                    nested: {
                        path: "attribute_values"
                    },
                    aggs: {
                        attributes: {
                            terms: {
                                field: "attribute_values.slug"
                            }
                        }
                    }
                }
            };
        return $.ajax({
            url: "http://localhost:9200/_search/",
            type: "POST",
            data: JSON.stringify(this.elasticQuery),
            contentType: "application/json; charset=utf-8",
            async: true,
            dataType: "json"
        });
    }
}

let s = new Search();
