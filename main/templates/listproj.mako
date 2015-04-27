<%!
from utils.views import commonheader, commonfooter
%>

${ commonheader(user) | n,unicode }

<link href="${ static('main/css/home.css') }" rel="stylesheet" type="text/css">
<script type="text/javascript" src="${ static('main/js/home.js') }"></script>

<div">

    <style type="text/css">

    .content {
        margin-top: 16px;
        border-top: 1px solid #e3e3e3;
        -webkit-box-shadow: 0px 1px 3px rgba(50, 50, 50, 0.1);
        -moz-box-shadow: 0px 1px 3px rgba(50, 50, 50, 0.1);
        box-shadow: 0px 1px 3px rgba(50, 50, 50, 0.1);
        background-color: #FFF
    }

    </style>

    <div class="content">
        <div class="container">
            <h3 class="muted">Project List</h3>
            <hr>
            % for project in projects:
            <h4><a href="${ project['proj_name']}">${ project['proj_name'] }</a></h4>
            <hr>
            % endfor

        </div>

    </div>

</div>

${ commonfooter() | n,unicode }