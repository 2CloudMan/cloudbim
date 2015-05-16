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
                    <form class="form-search">
                      <div class="input-append">
                        <input type="text" class="span12 search-query">
                        <button type="submit" class="btn">Search</button>
                      </div>
                    </form>
                </div>

                <div class="card-body">
                    <table class="table table-log">
                        <thead>
                            <th width="15%">Date</th>
                            <th width="1%">T</th>
                            <th>FilePath</th>
                            <th width="15%">Op</th>
                        </thead>
                        <tbody data-bind="foreach: records">
                            <tr data-bind="text: date"></tr>
                            <tr data-bind="text: target_type"></tr>
                            <tr data-bind="text: target_path"></tr>
                            <tr data-bind="text: op"></tr>
                        </tbody>
                        <tfoot>
                        </tfoot>
                    </table>
                </div>


            </div>

        </div>
    </div>
</div>

<script type="text/javascript">

    console.log('Setup KO');

    var FileOpRecord = function(record) {
        if(record != null) {
            return {
                op_time: record.op_time,
                operation: record.operation,
                target_path: record.target_path,
                target_type: record.target_type
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

    var FileOpModal = function(records, page) {
        var self = this;

        self.records = ko.observableArray(ko.utils.arrayMap(records, function(record) {
            return new FileOpRecord(record);
        }));

        self.page = ko.observable(new Page(page));
        self.targetPageNum = ko.observable(1);
        self.targetPageSize = ko.observable(30);
        self.query = ko.observable('');

        self.retrieveData() = function() {
            $.getJSON('/profie/history',{
                format:json,
                pagesize: self.targetPageSize,
                pageNum: self.targetPageNum,
                query = self.query(),
            }
            function(data){

                if(data.err){
                    //TODO: dosomething
                    return;
                }

                self.updateRecords(data.records, data.page);
            });
        }

        self.updateRecords =function(records, page) {
            self.records(ko.utils.arrayMap(records, function(record){
                return new FileOpRecord(record);
            }));

            self.page(nenw Page(page))
        };
    }

    var viewModal = new FileOpModal([], null);
    ko.applyBinding(viewModal);

    $(document).ready(function(){
        if viewModal {
            viewModal.retrieveData();
        }

    });


</script>
${ commonfooter() | n,unicode }