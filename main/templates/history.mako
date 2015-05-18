<%!
from utils.views import commonheader, commonfooter
%>
<%namespace name="slidebar" file="slidebar.mako" />

${ commonheader(user) | n,unicode }

<div class="container-fluid">
    <div class="row-fluid">
        <div class="span3">
            ${ slidebar.slidebar('history')}
        </div>

        <div class="span9">
            <div class="card" style="margin-top:0px!important">
                <div class="card-heading simple">

                      <div class="input-append">
                        <input type="text" class="span12 search-query" data-bind="value: query">
                        <button class="btn" data-bind="click: search">Search</button>
                      </div>

                    <div class="btn-group pull-right">
                      <a id="selected-type" class="btn dropdown-toggle" data-toggle="dropdown" href="#">
                        File
                        <span class="caret"></span>
                      </a>
                      <ul class="dropdown-menu">
                        <li><a class="file-type" href="#">File</a></li>
                        <li><a class="db-type" href="#">DB</a></li>
                      </ul>
                    </div>
                </div>

                <div class="card-body">
                    <table class="table table-log">
                        <thead>
                            <th width="15%">Date</th>
                            <th>FilePath</th>
                            <th width="15%">Op</th>
                        </thead>
                        <tbody data-bind="foreach: records">
                            <tr>
                            <td data-bind="text: op_time"></td>
                            <td data-bind="text: target"></td>
                            <td data-bind="text: op"></td>
                            </tr>
                        </tbody>
                        <tfoot>
                        </tfoot>
                    </table>

                    <div>
                        <div class="pagination pull-right">
                          <ul>
                            <li data-bind="css: { 'disabled': (page().number === page().previous_page_number || page().num_pages <= 1)}">
                              <a href="#" aria-label="First">
                                <i class="fa fa-fast-backward"></i>
                              </a>
                            </li>
                            <li data-bind="css: { 'disabled': (page().number === page().previous_page_number || page().num_pages <= 1)}">
                              <a href="#" aria-label="Previous">
                               <i class="fa fa-backward"></i>
                              </a>
                            </li>
                            <li data-bind="css: { 'disabled': (page().number === page().num_pages)}">
                              <a href="#" aria-label="Next">
                                <i class="fa fa-forward"></i>
                              </a>
                            </li>
                            <li data-bind="css: { 'disabled': (page().number === page().num_pages)}">
                              <a href="#" aria-label="Last">
                                <i class="fa fa-fast-forward"></i>
                              </a>
                            </li>
                          </ul>
                        </div>

                        <div class="form-inline pagination-input-form inline pull-right" style="margin: 20px 10px;">
                          <span>${_('Page')}</span>
                          <input type="text" style="width: 40px" data-bind="value: page().number, valueUpdate: 'afterkeydown', event: { change: skipTo }" class="pagination-input" />
                          <input type="hidden" id="current_page" data-bind="value: page().number" />
                          of <span data-bind="text: page().num_pages"></span>
                        </div>
                    </div>
                </div>
            </div>

        </div>
    </div>
</div>

<script type="text/javascript">

    console.log('Setup KO');

    var OpRecord = function(record) {
        if(record != null) {
            return {
                op_time: record.time,
                op: record.op,
                target: record.target,
                //target_type: record.target_type
            }
        }

    }
    var Page = function (page) {
          if (page != null) {
            return {
              number: page.number,
              num_pages: page.num_pages,
              previous_page_number: page.previous_page_number,
              next_page_number: page.next_page_number,
              start_index: page.start_index,
              end_index: page.end_index,
              total_count: page.total_count
            }
          }

          return {}
    };

    var LogModal = function(records, page, type) {
        var self = this;

        self.records = ko.observableArray(ko.utils.arrayMap(records, function(record) {
            return new OpRecord(record);
        }));

        self.curr_type = ko.observable(type)
        self.page = ko.observable(new Page(page));
        self.targetPageNum = ko.observable(1);
        self.targetPageSize = ko.observable(30);
        self.targetType = ko.observable('fileinfo')
        self.query = ko.observable('');

        self.resumeDefault = function() {
            self.targetPageNum(1);
            self.query('');
        }

        self.retrieveData = function() {

            location.hash = "#" + self.targetType();
            if (self.targetPageNum() != 1) {
                location.hash += ('/' + self.targetPageNum());
            }
            if (self.query() != '') {
                location.hash += ("!!" + self.query());
            }

            $.getJSON('/profile/history',{
                format:'json',
                pagesize: self.targetPageSize(),
                pageNum: self.targetPageNum(),
                targetType: self.targetType(),
                query :self.query(),
            },
            function(data){

                console.log(data);

                if(data.err){
                    //TODO: dosomething
                    return;
                }

                self.updateRecords(data.records, data.page, data.type);
            });
        }

        self.updateRecords =function(records, page, type) {
            self.records(ko.utils.arrayMap(records, function(record){
                return new OpRecord(record);
            }));

            self.page(new Page(page))

            self.curr_type(type);
        };


        self.skipTo = function() {
            var doc = document,
            old_page = doc.querySelector('#current_page').value,
            page = doc.querySelector('.pagination-input');

            if (! isNaN(page.value) && (page.value > 0 && page.value <= self.page().num_pages)) {
              self.goToPage(page.value);
            } else {
              page.value = old_page;
            }
        }

        self.goToPage = function(num) {
            self.targetPageNum(num);
        }

        self.changeType = function() {

        }

        self.search = function() {

            var queryStr =  self.query().trim
            if (queryStr != '') {
                self.retrieveData();
            }
        }
    }

    var viewModal = new LogModal([], null, 'fileinfo');
    ko.applyBindings(viewModal);

    $(document).ready(function(){
        if (viewModal) {
            viewModal.retrieveData();
        }

        $('a.file-type').click(function(event) {

            event.preventDefault();

            if (viewModal) {
                viewModal.resumeDefault();
                viewModal.targetType('fileinfo');
                viewModal.retrieveData();
            }

            $('#selected-type').html("File<span class=\"caret\"></span>");


        })

        $('a.db-type').click(function(event) {
            event.preventDefault();

            if (viewModal) {
                viewModal.resumeDefault();
                viewModal.targetType('dbinfo');
                viewModal.retrieveData();

            }


            $('#selected-type').html("DB<span class=\"caret\"></span>");
        })

    });


</script>
${ commonfooter() | n,unicode }