<%!
from utils.views import commonheader, commonfooter, subheader
%>

<%namespace name="sub" file="sub_header.mako"/>

${ commonheader(user) | n,unicode }

<div class="container">

    <div>
       ${ subheader(project, curr_role, roles, 'info' ) | n,unicode }
    </div>

    <div class="card">
        <div class="container">
            <div class="card-heading">
                <h4>Project Info</h4>
            </div>

        </div>
    </div>

</div>

${ commonfooter() | n,unicode }
