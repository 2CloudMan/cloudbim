<%!
from utils.views import commonheader, commonfooter
%>
<%namespace name="slidebar" file="slidebar.mako" />

${ commonheader(user) | n,unicode }

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span3">
            ${ slidebar.slidebar('project')}
        </div>

        <div class="span9" >
            <div class="card" style="margin-top:0px!important">
                <div class="card-body">
                    <h3 class="muted">Project List</h3>
                    <hr>
                    % for project in projects:
                    <h4><a href="${ project['proj_name']}">${ project['proj_name'] }</a></h4>
                    <hr>
                    % endfor
                </div>
            </div>

        </div>
    </div>
</div>

${ commonfooter() | n,unicode }
