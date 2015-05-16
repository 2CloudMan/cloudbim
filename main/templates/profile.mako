<%!
from utils.views import commonheader, commonfooter
%>
<%namespace name="slidebar" file="slidebar.mako" />

${ commonheader(user) | n,unicode }

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span3">
            ${ slidebar.slidebar('profile')}
        </div>

        <div class="span9">

        </div>
    </div>
</div>

${ commonfooter() | n,unicode }