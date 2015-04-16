<%!
from utils.views import commonheader, commonfooter
%>

<%namespace name="sub" file="sub_header.mako"/>

${ commonheader(request) | n,unicode }

<div data-pjax>

    <div>
        ${ sub.showSubMenu('Hha', 'Designer', 'fb')}
    </div>

    <div class="container" id="pjax-container">
        <p>test</p>
    </div>

</div>
