/// <reference path="../jquery.d.ts" />
/// <reference path="../handlebars.d.ts" />

class Api {
    constructor(public url: string) {}
    private _render_results(res){
        for (var r in res){
            $('#products-container').html(Handlebars.templates['product']())
        }
    };
    public query(params: {}){
        $.getJSON(this.url,
            cs => {this._render_results(cs)});
    };
}

var api = new Api('/api/products/');
api.query();
