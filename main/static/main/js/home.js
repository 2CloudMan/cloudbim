$(document).ready(function(){
  $("a.list-group-item").on('click', function(event){
    $('a.list-group-item').removeClass('active');
    $(this).addClass('active')
  });

  )
});