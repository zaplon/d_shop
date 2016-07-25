"use strict";

var HIDDEN_CART_URLS = ['/basket/', '/checkout/'];

class Cart {
    constructor(){
        this.quantity = 0;
        this.total = 0;
    }
    addToCart(id, quantity) {
        var data = {quantity: quantity, url: window.location.origin + '/api/products/' + id + '/'}
        $.post('/api/basket/add-product/', data, res => {
            //$('body').append(Handlebars.templates['add-to-cart']({}));
            $("#message").alert();
            this.getCart();
            //$('.cd-cart .body ul').append(Handlebars.templates['cart-product'](res));
        });
    }
    deleteFromCart(id){

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
                    var product = {};
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
                if (me.quantity > 0)
                    $('.cd-cart-container').removeClass('empty');
                $('#cart-total').html(me.total);
                $('#cart-count').html(me.quantity);
                var productsList = $('.cd-cart .body ul');
                me.products.forEach(function(r){
                    productsList.append(Handlebars.templates['cart-product'](r));
                })
            });
        })
    }
}

if (HIDDEN_CART_URLS.join('|').search(window.location.pathname) == -1) {
    var cart = new Cart();
    cart.getCart();
}
$(document).ready(() => {
    $('#products-container').delegate('.add-to-cart', 'click', function (el) {
        cart.addToCart(parseInt($(el.target).attr('data-id')), 1);
    });
    $('.cd-cart-trigger').click(function(el){
        var container = $('.cd-cart-container');
        if (container.hasClass('cart-open'))
            $('.cd-cart-container').removeClass('cart-open');
        else
            $('.cd-cart-container').addClass('cart-open');
    });
    $('.delete-item').click(function(){
        var id = $(this).attr('data-id');
        cart.deleteFromCart(id);
    });
});

// api/basket -> lines -> [0] product