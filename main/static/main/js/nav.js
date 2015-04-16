$(document).ready(function() {

    $('ul.nav>li>a').click(function(event) {

        $('ul.nav>li').removeClass('active');

        $(this).parent().addClass('active');

        $.get("fb", {}, function(data, textStatus) {
            $('#content').html(data);
        })

    })
})