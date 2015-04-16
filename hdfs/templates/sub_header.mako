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
            <li class="active"><a href="fb/view/">FileSystem</a></li>
            <li><a href="table">Table</a></li>
            <li><a href="log">Log</a></li>
            <li><a href="info">Detail</a></li>
          </ul>

        </div>
    </div>
</%def>