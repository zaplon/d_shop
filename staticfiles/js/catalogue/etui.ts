/// <reference path="../jquery.d.ts" />
/// <reference path="../handlebars.d.ts" />
/// <reference path="../utils.ts" />



class Api {
    public params:{limit: number, attributes: any}
    public productsEnd:any
    public appendResults:boolean
    public attributes: any
    constructor(public url:string) {
        this.params = {limit: 0, attributes: ''}
    }

    public query(limit) {
        this.params.limit = limit;
        if ('attributes' in this.params && this.params.attributes.length == 0)
            delete this.params.attributes;
        $.getJSON(this.url, this.params,
            res => {
                this.renderResults(res);
                this.appendResults = false;
                history.pushState('', document.title, api.params.attributes);
            });
    };

    private watchResults() {
        if (utils.isOnScreen(api.productsEnd, 0)) {
            console.log('read');
            //api.appendResults = true;
            //api.query(4);
        }
    }

    private renderResults(res) {
        if (!this.appendResults)
            $('#products-container').html('');
        for (var r in res.results) {
            $('#products-container').append(Handlebars.templates['product'](res.results[r]));
        }
        $('#filters-list ul').html(Handlebars.templates['filters']({attributes: this.attributes}));
        console.log(this.attributes);
        $('#products-container').append('<div id="products-end"></div>');
        this.productsEnd = $('#products-end');
        $(window).unbind('scroll', this.watchResults);
        $(window).bind('scroll', this.watchResults);
    };
}

var api = new Api('/api/products/');
$(document).ready(() => {
    $('#filters-list').delegate('li', 'click', function(){
        console.log('remove');
        let select = $('select[data-attribute="'+$(this).attr('data-attribute')+'"]');
        //let values = $(select).selectpicker('val');
        //if (typeof(values) == 'string'){
        //    $(select).selectpicker('val', '');
        //}
        //else if (typeof(values) == 'object'){
        //
        //}
        $(this).remove();

    });
    var productsEnd = $('#products-end');
    $('#product-filters select').change((e) => {
        var attributes = [];
        $('#product-filters select').each((i, s) => {
            var val = $(s).val();
            if (typeof(val) == 'string' && val != ''){
                let selected = $(s).find('option:selected');
                attributes.push([{id: parseInt($(s).val()), name: $(selected).attr('name'),
                    attribute: $(s).attr('data-attribute')}]);
            }
            else if (typeof(val) == 'object' && val !== null){
                attributes.push([]);
                let a_length = attributes.length - 1;
                val.forEach(function(v, i){
                    attributes[a_length].push({id: parseInt(v), name: $(s).find('option[value="'+v+'"]').attr('name'),
                        attribute: $(s).attr('data-attribute')})
                })
            }
        });
        api.attributes = attributes;
        let atts_ids = [];
        attributes.forEach(function(att, i){
            atts_ids.push([])
            att.forEach(function(a, j){
                atts_ids[atts_ids.length-1].push(a.id)
            });
            atts_ids[atts_ids.length-1] = atts_ids[atts_ids.length-1].join('.');
        });
        api.params.attributes = atts_ids.join(',');
        api.query(12);
    })
    api.query(12);
});
