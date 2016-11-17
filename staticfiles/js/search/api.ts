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
    params: any;
    getResults(){
        $.getJSON("", function(){});
    }
}
