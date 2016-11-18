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

class Search {
    params: {prices: [0, 0], productClasses: string[], categories: string[], sorting: string};
    results: {images: string[], title: string, content: string, price: number}[];
    elasticQuery: {
        query: { filter: any }
    }
    getResults() {
        if (this.params.prices[1] > 0) {
            if (!('range' in this.elasticQuery.query.filter))
                this.elasticQuery.query.filter.range = {}    
            this.elasticQuery.query.filter.range['price'] = {
                'gte': this.params.prices[0],
                'lte': this.params.prices[1]}
        }
        //$.getJSON("", this.elasticQuery, function(res){});
    }
}
