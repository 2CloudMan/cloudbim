<%def name="slidebar(app)">
    <div class="sidebar-nav">
        <ul class="nav nav-list">
            <li class="nav-header">Personal Panel</li>
            %if app == 'profile':
            <li class="active"><a href="/profile">Profile</a></li>
            %else:
            <li><a href="/profile">Profile</a></li>
            %endif

            %if app == 'project':
            <li class="active"><a href="/project">Project</a></li>
            %else:
            <li><a href="/project">Project</a></li>
            %endif

            %if app == 'history':
            <li class="active"><a href="/history">History</a></li>
            %else:
            <li><a href="/history">History</a></li>
            %endif


        </ul>
    </div>
</%def>

