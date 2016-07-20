"use strict";
class Cart {
    addToCart(id, quantity) {
        data = {quantity: quantity, url: window.location.origin + '/api/products/' + id + '/'}
        $.post('/api/basket/add-product/', data, res => {
            $('body').append(Handlebars.templates['add-to-cart']({}));
            $("#message").alert();
        });
    }
}

var cart = new Cart();
$(document).ready(() => {
    $('#products-container').delegate('.add-to-cart', 'click', function (el) {
        cart.addToCart(parseInt($(el.target).attr('data-id')), 1);
    });
})