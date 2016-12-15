;(function() {
  window.onload = function() {
    var preloading = document.querySelector('.page-preloading');
    preloading.classList.add('loading-done');

    $('.scroll-to-top-btn').click(function(){
        $('body').animate({scrollTop:0}, '400', 'swing', function() {
        });
    });
  };
  $('.container').delegate('.ajax-form', 'click', function(ev){
    var name = this.attr('form-name');
    var formData = $('form[name="'+name+'"]').serialize();
    $.post('/pages/submit_form', {data: formData, name: name}, function(res){
      if (res.success){
        $('form[name="'+name+'"]').parent().html('<p class="form-success">Wiadomość przesłana poprawnie</p>');
      }
      else {
        $('form[name="'+name+'"]').parent().html(res.form);
      }
    });
  });
})();
