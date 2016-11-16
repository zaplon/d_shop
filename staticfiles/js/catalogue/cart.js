"use strict";

var HIDDEN_CART_URLS = ['/basket/', '/checkout/', '/zamowienie/', '/koszyk/'];

class Cart {
    constructor(){
        this.quantity = 0;
        this.total = 0;
    }
    addToCart(id, quantity) {
        var data = {quantity: quantity, url: window.location.origin + '/api/products/' + id + '/'}
        $.post('/api/basket/add-product/', data, res => {
            //$('body').append(Handlebars.templates['add-to-cart']({}));
            //$("#message").alert();
            this.getCart();
            //$('.cd-cart .body ul').append(Handlebars.templates['cart-product'](res));
        });
    }
    deleteFromCart(line){
        $.ajax({
          type: 'DELETE',
          url: line,
          success: res => {
            this.getCart();
          }
        });
    }
    updateCard(line, quantity){
        $.ajax({
          type: 'PUT',
          url: line,
          dataType: 'json',
          data: {quantity: quantity},
          success: res => {
            this.getCart();
          }
        });
    }
    getCart(){
        var me = this;
        me.quantity = 0;
        $.get('/api/basket', res => {
                me.total = res.total_incl_tax;
                me.currency = res.currency;
            $.get(res.lines, res => {
                me.products = [];
                res.forEach(function(r, i){
                    var product = {line: r.url, quantity: r.quantity};
                    me.quantity += r.quantity;
                    product.price = r.price_incl_tax;
                    $.ajax({
                        url: r.product,
                        async: false,
                        success: res => {
                            product.title =  res.title;
                            product.image =  res.images.length > 0 ? res.images[0].original : '';
                            me.products.push(product);
                        }
                    })
                });
                if (me.quantity > 0) {
                    var cart = $('.cd-cart-container');
                    cart.removeClass('empty');
                    cart.removeClass('card-open');
                    cart.addClass('card');
                }
                else
                    $('.cd-cart-container').addClass('empty');
                $('#cart-total').html(me.total);
                $('#cart-count').html(me.quantity);
                var productsList = $('.cd-cart .body ul');
                productsList.html('');
                me.products.forEach(function(r){
                    productsList.append(Handlebars.templates['cart-product'](r));
                    $('select[data-line="'+r.line+'"]').val(r.quantity);
                })
            });
        })
    }
}

var showCart = true;
HIDDEN_CART_URLS.forEach(function(url){
 if (window.location.pathname.search(url) != -1)
    showCart = false
});
if (showCart){
    var cart = new Cart();
    cart.getCart();
}

$(document).ready(() => {
    $('#products-container').delegate('.add-to-cart', 'click', function (ev) {
        cart.addToCart(parseInt($(ev.target).attr('data-id')), 1);
    });
    $('.cd-cart-trigger').click(function(el){
        var container = $('.cd-cart-container');
        if (container.hasClass('cart-open'))
            $('.cd-cart-container').removeClass('cart-open');
        else
            $('.cd-cart-container').addClass('cart-open');
    });
    $('.cd-cart').delegate('.delete-item', 'click', function(ev){
        var line = $(ev.target).attr('data-line');
        cart.deleteFromCart(line);
    });
    $('.cd-cart').delegate('.product-quantity', 'change', function(ev){
        var line = $(ev.target).attr('data-line');
        var quantity = $(ev.target).val();
        cart.updateCard(line, quantity);
    });
    $('.delete-item').click(function(){

    });
});

// api/basket -> lines -> [0] product