<%!
from utils.lib.django_mako import static
%>

<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="icon" href="../../favicon.ico">

        <title>Starter Template for Bootstrap</title>

        <!-- Bootstrap core CSS -->
        <link href="${ static('ext/css/bootstrap.min.css') }" rel="stylesheet">
        <!-- Custom styles for this template -->
        <link href="${ static('css/cloudbim.css') }" rel="stylesheet">

        <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
        <!--[if lt IE 9]>
          <script src="http://cdn.bootcss.com/html5shiv/3.7.2/html5shiv.min.js"></script>
          <script src="http://cdn.bootcss.com/respond.js/1.4.2/respond.min.js"></script>
        <![endif]-->

         <!-- Bootstrap core JavaScript
        ================================================== -->
        <script src="http://cdn.bootcss.com/jquery/1.11.2/jquery.min.js"></script>
        <script src="http://cdn.bootcss.com/bootstrap/3.3.4/js/bootstrap.min.js"></script>
    </head>
<body>

    <nav class="nav navbar-inverse navbar-fixed-top">
        <div class="container-fluid">
            <div class="navbar-header">
                <a class="navbar-brand" href="#">
                    CloudBIM
                </a>
            </div>
            % if user:
            <p class="navbar-text navbar-right">Signed in as <a href="#" class="navbar-link">${user.name}</a></p>
            % endif
        </div>
    </nav>