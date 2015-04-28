<%def name="showSubMenu(curr_proj, curr_role, roleList, app)">

    <script type="text/javascript" src="${ static('main/js/nav.js') }"></script>
    <div class="navbar sub-nav" ">
        <div class="container">
          <div class="navbar-inner">
              <a class="brand" href="#">${curr_proj['name']}</a>
              <div class="btn-group">
                  <a type="button" class="btn dropdown-toggle" data-toggle="dropdown" href="#">
                    ${curr_role} <span class="caret"></span>
                  </a>
                  <ul class="dropdown-menu" role="menu">
                    % for role in roleList:
                    <li>
                    % if app == 'fb':
                    <a href="/project/${curr_proj['slug']}/${role['slug']}/${app}/view">${role['name']}/</a></li>
                    % else:
                    <a href="/project/${curr_proj['slug']}/${role['slug']}/${app}">${role['name']}</a></li>
                    % endif
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
    </div>
</%def>