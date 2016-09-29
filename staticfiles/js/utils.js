;(function() {
  window.onload = function() {
    var preloading = document.querySelector('.page-preloading');
    preloading.classList.add('loading-done');

    $('.scroll-to-top-btn').click(function(){
        $('body').animate({scrollTop:0}, '400', 'swing', function() {
        });
    });
  };
})();
