<%def name="showSubMenu(curr_proj, curr_role, roleList, app)">
    <style type="text/css">
        body {
            padding-top:100px !important;
        }
    </style>
    <script type="text/javascript" src="${ static('main/js/nav.js') }"></script>
    <div class="navbar navbar-default navbar-fixed-top sub-nav" style="top:50px!important">
        <div class="container">

          <p class="navbar-text">${curr_proj['name']}</p>

          <div class="btn-group">
              <button type="button" class="btn btn-default dropdown-toggle navbar-btn" data-toggle="dropdown" aria-expanded="false">
                ${curr_role} <span class="caret"></span>
              </button>
              <ul class="dropdown-menu" role="menu">
                % for role in roleList:
                <li><a href="/project/${curr_proj['slug']}/${role['slug']}/${app}/view">${role['name']}</a></li>
                % endfor
              </ul>
          </div>
          <ul class="nav navbar-nav navbar-right">
            <li
            % if app == 'fb':
            class="active"
            % endif
            ><a href="/project/${curr_proj['name']}/${curr_role}/fb/view/">FileSystem</a></li>
            <li
            % if app == 'tb':
            class="active"
            % endif
            ><a href="/project/${curr_proj['name']}/${curr_role}/tb">Table</a></li>
            <li
            % if app == 'log':
            class="active"
            % endif
            ><a href="/project/${curr_proj['name']}/${curr_role}/log">Log</a></li>
            <li
            % if app == 'info':
            class="active"
            % endif
            ><a href="/project/${curr_proj['name']}/${curr_role}/info">Detail</a></li>
          </ul>

        </div>
    </div>
</%def>