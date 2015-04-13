<%!
from utils.views import commonheader, commonfooter
%>

${ commonheader() | n,unicode }

<link href="${ static('main/css/home.css') }" rel="stylesheet" type="text/css">
<script type="text/javascript" src="${ static('main/js/home.js') }"></script>

<div class="container-fluid">
    <div class="row">
        <div class="col-sm-3 col-md-2 sidebar">
            <a href="#">
                <img id="avatar" class="img-responsive img-rounded" src="${ static('main/images/default_avatar.png') }"/>
            </a>

            <h4 class="username">${ user['name'] }</h4>

            <ul class="nav nav-sidebar">

            </ul>
        </div>

        <div class="col-sm-9 col-sm-offset-3 col-md-10 col-md-offset-2 main">
            <h1 class="page-header">项目列表</h1>
            <div class="list-group proj-list">
                % for project in projects:
                    <a class="list-group-item" href="/project/${ project['proj_name'] }">
                        <h4 class="list-group-item-heading">${ project['proj_name'] }</h4>
                         <p class="list-group-item-text">项目详情...</p>
                    </a>
                % endfor
            </div>

            <nav>
              <ul class="pagination pull-right">
                <li>
                  <a href="#" aria-label="Previous">
                    <span aria-hidden="true">&laquo;</span>
                  </a>
                </li>
                <li><a href="#">1</a></li>
                <li><a href="#">2</a></li>
                <li><a href="#">3</a></li>
                <li><a href="#">4</a></li>
                <li><a href="#">5</a></li>
                <li>
                  <a href="#" aria-label="Next">
                    <span aria-hidden="true">&raquo;</span>
                  </a>
                </li>
              </ul>
            </nav>
        </div>
    </div>
</div>

${ commonfooter() | n,unicode }