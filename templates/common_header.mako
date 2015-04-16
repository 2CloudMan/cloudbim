<%!
from utils.lib.django_mako import static
%>

<html lang="en">
    <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <link rel="icon" href="../../favicon.ico">

        <title>CloudBIM</title>

        <link href="${ static('ext/css/bootstrap.min.css') }" rel="stylesheet">
        <link href="${ static('css/cloudbim.css') }" rel="stylesheet">

        <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
        <!--[if lt IE 9]>
          <script src="http://cdn.bootcss.com/html5shiv/3.7.2/html5shiv.min.js"></script>
          <script src="http://cdn.bootcss.com/respond.js/1.4.2/respond.min.js"></script>
        <![endif]-->

        <script src="${ static('ext/js/jquery-2.1.1.js') }"></script>
        <script src="${ static('ext/js/bootstrap.min.js') }"></script>
        <script src="${ static('ext/js/jquery.pjax.js') }"></script>
        <script src="${ static('ext/js/dmuploader.min.js') }"></script>

        <script src="${ static('js/cloudbim.js') }"></script>

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



    <%def name="showSubMenu(projectName, roleList, app)">
    <style type="text/css">
        body {
            padding-top:100px !important;
        }
    </style>
    <script type="text/javascript" src="${ static('main/js/nav.js') }"></script>
    <div class="navbar navbar-default navbar-fixed-top sub-nav" style="top:50px!important">
        <div class="container">

          <p class="navbar-text">ProjectName</p>

          <div class="btn-group">
              <button type="button" class="btn btn-default dropdown-toggle navbar-btn" data-toggle="dropdown" aria-expanded="false">
                RoleA <span class="caret"></span>
              </button>
              <ul class="dropdown-menu" role="menu">
                <li><a href="#">RoleA</a></li>
                <li><a href="#">RoleB</a></li>
                <li><a href="#">RoleC</a></li>
                <li class="divider"></li>
                <li><a href="#">other Roles</a></li>
              </ul>
          </div>
          <ul class="nav navbar-nav navbar-right">
            <li><a href="fb">FileSystem</a></li>
            <li><a data-pjax href="table">Table</a></li>
            <li><a data-pjax href="log">Log</a></li>
            <li class="active"><a href="#">Detail</a></li>
          </ul>

        </div>
    </div>
</%def>

