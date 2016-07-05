/// <reference path="../jquery.d.ts" />
/// <reference path="../handlebars.d.ts" />


class Api{
    public params: {limit: number, attributes: any}
    constructor(public url: string) {
        this.params = {limit: 0, attributes: ''}
    }
    private _render_results(res){
        for (var r in res.results){
            $('#products-container').append(Handlebars.templates['product'](res.results[r]))
        }
    };
    public query(limit){
        this.params.limit = limit;
        if (this.params.attributes.length == 0)
            this.params.attributes = null;
        $.getJSON(this.url, this.params,
            res => {this._render_results(res)});
    };
}

var api = new Api('/api/products/');
$(document).ready(() => {
    $('#product-filters select').change((e) => {
        var attributes = [];
        $('#product-filters select').each((i, s) => {
            var val = $(s).val();
            if (parseInt(val) > 0)
                attributes.push(parseInt($(s).val()));
        });

        api.params.attributes = attributes.join(',');
        console.log(api.params);
        api.query(12);
    })
});
api.query(12);
