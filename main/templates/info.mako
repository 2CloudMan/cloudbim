<%!
from utils.views import commonheader, commonfooter
%>

<%namespace name="sub" file="sub_header.mako"/>

${ commonheader(user) | n,unicode }

<div class="container">

    <div>
       ${ sub.showSubMenu({'name': 'webform'}, 'worker', [], 'info' )}
    </div>

    <div class="card">
        <div class="container">

        </div>
    </div>

</div>

${ commonfooter() | n,unicode }
