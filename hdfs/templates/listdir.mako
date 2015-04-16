<%!
from utils.views import commonheader, commonfooter
%>

<%namespace name="sub" file="sub_header.mako"/>

${ commonheader(request) | n,unicode }

<div data-pjax>

    <div>
        ${ sub.showSubMenu('Hha', 'Designer', '')}
    </div>

        <div class="container" id="pjax-container">
            <div class="row" style="margin-top: 24px">
                <div class="col-lg-6">
                    <ol class="breadcrumb">
                      <li><a href="#">Home</a></li>
                      <li><a href="#">Library</a></li>
                    </ol>
                </div>

                <div class="col-lg-1">
                    <button class="btn btn-default">+</button>
                </div>
            </div>

        <table class="table table-striped">
            <thead>
                <tr>
                    <td width="1%">
                    <div class="bimCheckbox"></div>
                    </td>
                    <td><strong>Name</strong></td>
                    <td><strong>Owner</strong></td>
                    <td><strong>Date</strong></td>
                </tr>
            </thead>

            <tbody>
                <tr>
                    <td><div class="bimCheckbox"></div></td>
                    <td>haah.mako</td>
                    <td>eric</td>
                    <td>2011.12.11</td>
                </tr>
                <tr>
                    <td><div class="bimCheckbox"></div></td>
                    <td>haah.mako</td>
                    <td>eric</td>
                    <td>2011.12.11</td>
                </tr>
                <tr>
                    <td><div class="bimCheckbox"></div></td>
                    <td>haah.mako</td>
                    <td>eric</td>
                    <td>2011.12.11</td>
                </tr>
            </tbody>
        </table>


        <div class="pull-left" style="margin:20px 0;">
            <button type="button" class="btn btn-primary">Download</button>
            <button type="button" class="btn btn-danger">Delete</button>
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