<%!
from utils.lib.django_mako import static
%>

<html lang="en">
    <head>
        <title>CloudBIM</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <!-- Bootplus -->
        <link href="${ static('ext/css/bootplus.min.css') }" rel="stylesheet" media="screen">
        <link href="${ static('ext/css/bootplus-responsive.min.css') }" rel="stylesheet" media="screen">
        <link href="${ static('ext/css/font-awesome.min.css') }" rel="stylesheet" media="screen">
        <!--[if IE 7]>
        <link rel="stylesheet" href="${ static('css/bootplus-ie7.min.css') }">
        <![endif]-->

        <link href="${ static('css/cloudbim.css') }" rel="stylesheet">

        <script src="${ static('ext/js/jquery-2.1.1.js') }"></script>
        <script src="${ static('ext/js/bootstrap.min.js') }"></script>

        <script src="${ static('ext/js/jquery.pjax.js') }"></script>
        <script src="${ static('ext/js/dmuploader.min.js') }"></script>
        <script src="${ static('ext/js/fileuploader.js') }"></script>
        <script src="${ static('ext/js/jquery.rowselector.js') }"></script>
        <script src="${ static('ext/js/knockout-min.js')}" type='text/javascript'></script>
        <script src="${ static('ext/js/knockout.mapping-2.3.2.js')}" type='text/javascript'></script>

        <script src="${ static('js/cloudbim.js') }"></script>

    </head>
<body>

    <div class="navbar navbar-inverse navbar-fixed-top">
        <div class="navbar-inner">
            <div class="container-fluid">
                <a class="brand" href="#">CloudBIM</a>
                % if user:
                <p class="navbar-text navbar-right">Signed in as <a href="#" class="navbar-link">${user.name}</a></p>
                % endif
            </div>

        </div>
    </div>









