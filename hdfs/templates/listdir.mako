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
        <div class="row">
            <div class="col col-lg-6">
            <ul class="nav nav-pills hueBreadcrumbBar">
                <li data-bind="css:{'disabled': breadcrumbs().length == 1}"><a href="" class="upLink" data-bind="click: folderUp"><span class="glyphicon glyphicon-arrow-left"></span></a></li>
                <li>
                    <ul class="hueBreadcrumb" data-bind="foreach: breadcrumbs" style="padding-right:40px; padding-top: 12px">
                        <li data-bind="visible: label == '/'"><a href="" data-bind="click: show"><span class="divider" data-bind="text: label"></span></a></li>
                        <li data-bind="visible: label != '/'"><a href="" data-bind="text: label" click:show></a><span class="divider">/</span></li>
                    </ul>
                </li>
            </ul>
            </div>
            <div class="col col-lg-2" style="padding:12px 0">
            <button class="btn btn-default" data-toggle="modal" data-target="#uploadFileModal">+f</button>
            <button class="btn btn-default" data-toggle="modal" data-target="#createDirModal">+d</button>
            </div>
        </div>

        <table class="table table-striped">
            <thead>
                <tr>
                    <td width="1%">
                    <span class="bimCheckbox" data-bind="click: selectAll, css: {'glyphicon glyphicon-ok' : allSelected}"><span>
                    </td>
                    <td><strong>Name</strong></td>
                    <td><strong>Size</strong></td>
                    <td><strong>Owner</strong></td>
                    <td><strong>Date</strong></td>
                </tr>
            </thead>


            <tbody id="files" data-bind="template: {name: 'fileTemplate', foreach: files}"></tbody>
        </table>


        <div class="pull-left" style="margin:20px 0;">
            <button type="button" class="btn btn-primary" data-bind="enable : selectedFiles().length == 1 && !selectedFile().isdir">Download</button>
            <button type="button" class="btn btn-danger" data-toggle="modal" data-target="#deleteModal" data-bind="enable : selectedFiles().length > 0">Delete</button>
        </div>


        <div>
            <nav>
              <ul class="pagination pull-right">
                <li data-bind="css: { 'disabled': (page().number === page().previous_page_number || page().num_pages <= 1)}">
                  <a href="#" aria-label="First">
                    <span class="glyphicon glyphicon-fast-backward"></span>
                  </a>
                </li>
                <li data-bind="css: { 'disabled': (page().number === page().previous_page_number || page().num_pages <= 1)}">
                  <a href="#" aria-label="Previous">
                    <span class="glyphicon glyphicon-backward"></span>
                  </a>
                </li>
                <li data-bind="css: { 'disabled': (page().number === page().num_pages)}">
                  <a href="#" aria-label="Next">
                    <span class="glyphicon glyphicon-forward"></span>
                  </a>
                </li>
                <li data-bind="css: { 'disabled': (page().number === page().num_pages)}">
                  <a href="#" aria-label="Last">
                    <span class="glyphicon glyphicon-fast-forward"></span>
                  </a>
                </li>
              </ul>
            </nav>

            <div class="form-inline pagination-input-form inline pull-right" style="margin: 20px 10px;">
              <span>${_('Page')}</span>
              <input type="text" style="width: 40px" data-bind="value: page().number, valueUpdate: 'afterkeydown', event: { change: skipTo }" class="pagination-input" />
              <input type="hidden" id="current_page" data-bind="value: page().number" />
              of <span data-bind="text: page().num_pages"></span>
            </div>
        </div>


        <!-- 上传模块 -->
        <div class="modal fade" id="uploadFileModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <h4 class="modal-title" id="myModalLabel">上传至: ${path}</h4>
              </div>

              <div class="modal-body">

              <div id="drag-and-drop-zone" class="uploader">
                  <div>Drag &amp; Drop Images Here</div>
                  <div class="or">-or-</div>
                  <div class="browser">
                    <label>
                      <span>Click to open the file Browser</span>
                      <input type="file" name="files" multiple="multiple" title="Click to add Files">
                    </label>
                  </div>
              </div>

              <div id="fileList">
                <!-- Files will be places here -->
              </div>

              </div>
              <div class="modal-footer">
              </div>
            </div>
          </div>
        </div>

        <!-- 新建目录模块 -->
        <div class="modal fade" id="createDirModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <h4 class="modal-title" id="myModalLabel">创建目录</h4>
              </div>

              <div class="modal-body">

              <form action="">
                <label for="dirName">目录名</label>
                <input type="text" class="form-control" id="dirName" placeholder="">
                <button type="submit" class="btn btn-default" style="margin-top: 10px">submit</button>
              </form>

              </div>
              <div class="modal-footer">
              </div>
            </div>
          </div>
        </div>

        <!-- 删除模块 -->
        <div class="modal fade" id="deleteModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <h4 class="modal-title" id="myModalLabel">确定删除这些文件吗?</h4>
              </div>

              <div class="modal-body">

              <form id="deleteForm" action="">
                <button type="cancel" class="btn btn-default" style="margin-top: 10px">取消</button>
                <button type="submit" class="btn btn-default btn-danger" style="margin-top: 10px">确定</button>
              </form>

              </div>
              <div class="modal-footer">
              </div>
            </div>
          </div>
        </div>



    <script type="text/javascript">

      //-- Some functions to work with our UI
      function add_log(message)
      {
        console.log(new Date().getTime() + '-' + message)
      }

      function add_file(id, file)
      {
        var template = '' +
          '<div class="file" id="uploadFile' + id + '">' +
            '<div class="info">' +
              '#1 - <span class="filename" title="Size: ' + file.size + 'bytes - Mimetype: ' + file.type + '">' + file.name + '</span><br /><small>Status: <span class="status">Waiting</span></small>' +
            '</div>' +
            '<div class="bar">' +
              '<div class="bar-progress" style="width:0%"></div>' +
            '</div>' +
          '</div>';

          $('#fileList').prepend(template);
      }

      function update_file_status(id, status, message)
      {
        $('#uploadFile' + id).find('span.status').html(message).addClass(status);
      }

      function update_file_progress(id, percent)
      {
        $('#uploadFile' + id).find('div.bar-progress').width(percent);
      }

      // Upload Plugin itself
      $('#drag-and-drop-zone').dmUploader({
        url: '/project/webform/worker/fb/upload/files',
        dataType: 'json',
        allowedTypes: '*',
        extraData:{ 'dest' : '/worker/'},
        onInit: function(){
          add_log('Penguin initialized :)');
        },
        onBeforeUpload: function(id){
          add_log('Starting the upload of #' + id);

          update_file_status(id, 'uploading', 'Uploading...');
        },
        onNewFile: function(id, file){
          add_log('New file added to queue #' + id);

          add_file(id, file);
        },
        onComplete: function(){
          add_log('All pending tranfers finished');
        },
        onUploadProgress: function(id, percent){
          var percentStr = percent + '%';

          //update_file_progress(id, percentStr);
        },
        onUploadSuccess: function(id, data){
          add_log('Upload of file #' + id + ' completed');

          add_log('Server Response for file #' + id + ': ' + JSON.stringify(data));

          update_file_status(id, 'success', 'Upload Complete');

          update_file_progress(id, '100%');
        },
        onUploadError: function(id, message){
          add_log('Failed to Upload file #' + id + ': ' + message);

          update_file_status(id, 'error', message);
        },
        onFileTypeError: function(file){
          add_log('File \'' + file.name + '\' cannot be added: must be an image');

        },
        onFileSizeError: function(file){
          add_log('File \'' + file.name + '\' cannot be added: size excess limit');
        },
        onFallbackMode: function(message){
          alert('Browser not supported(do something else here!): ' + message);
        }
      });
    </script>

     <script id="fileTemplate" type="text/html">
        <tr data-bind="click: $root.viewFile">
            <td data-bind="click: handleSelect">
                <span class="bimCheckbox" data-bind="css: {'glyphicon glyphicon-ok' : selected}"></span>
            </td>
            <td>
                <span data-bind="text: name"></span>
            </td>
            <td>
                <span data-bind="text: human_size"></span>
            </td>
             <td>
                <span data-bind="text: owner"></span>
            </td>
             <td>
                <span data-bind="text: ctime"></span>
            </td>
        </tr>
    </script>


    <script type="text/javascript">

      var File = function(file) {

        return {

            name: file.name,
            owner: file.owner,
            path: file.path,
            raw_path: file.raw_path,
            isdir: file.isdir,
            human_size: file.human_size,
            project: file.project,
            role:  file.role,
            ctime: file.ctime,
            atime: file.atime,
            selected: ko.observable(false),
            handleSelect: function (row, e) {
              e.preventDefault();
              e.stopPropagation();
              this.selected(! this.selected());
              viewModel.allSelected(false);
            }
        };
      }

      var Breadcrumb = function(breadcrumb) {
        return {
            url: breadcrumb.url,
            label: breadcrumb.label,
            show: function() {
                console.log("show called");
                //self.targetPath('/project/${curr_proj}/${curr_role}/fb/view${url}');
                location.href = '/project/${curr_proj}/${curr_role}/fb/view' + this.url;
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
          return {
          }
      };

      var FileBrowserModel = function(files, page, breadcrumbs, currentDirPath) {

        console.log('set up ko');
        var self = this;

        self.page = ko.observable(new Page(page));
        self.recordsPerPage = ko.observable(30);
        self.targetPageNum = ko.observable(1);
        self.targetPath = ko.observable('/project/${curr_proj}/${curr_role}/fb/view${path}')

        self.files = ko.observableArray(ko.utils.arrayMap(files, function(file){
            new File(file);
        }));

        self.breadcrumbs = ko.observableArray(ko.utils.arrayMap(breadcrumbs, function(breadcrumbs){
            return Breadcrumb(breadcrumb);
        }));

        self.isLoading = ko.observable(false);
        self.allSelected = ko.observable(false);
        self.selectedFiles = ko.computed(function () {
            return ko.utils.arrayFilter(self.files(), function (file) {
              return file.selected();
            });
        }, self);

        self.selectedFile = ko.computed(function () {
            return self.selectedFiles()[0];
        }, self);

        self.selectAll = function() {

            console.log('selectAll');
            self.allSelected(! self.allSelected());

            ko.utils.arrayForEach(self.files(), function (file) {
                if (file.name != "." && file.name != "..") {

                }

                file.selected(self.allSelected());
            });
            return true;
        }

        self.folderUp = function() {
            self.targetPath('/project/${curr_proj}/${curr_role}/fb/view'+self.breadcrumbs()[self.breadcrumbs().length - 2].url);

            location.href = self.targetPath();

        }


        self.updateFileList = function (files, page, breadcrumbs, currentDirPath) {
            //$(".tooltip").hide();

            //self.isCurrentDirSentryManaged(isSentryManaged);

            self.page(new Page(page));

            self.files(ko.utils.arrayMap(files, function (file) {
              return new File(file);
            }));
            //if (self.sortBy() == "name"){
            //  self.files.sort(self.fileNameSorting);
            //}

            self.breadcrumbs(ko.utils.arrayMap(breadcrumbs, function (breadcrumb) {
              return new Breadcrumb(breadcrumb);
            }));

            //self.currentPath(currentDirPath);

            //$('.uploader').trigger('fb:updatePath', {dest:self.currentPath()});

            self.isLoading(false);

            //$("*[rel='tooltip']").tooltip({ placement:"left" });

            $(window).scrollTop(0);

            //resetActionbar();
        };

        self.retrieveData = function () {
            self.isLoading(true);

            $.getJSON(self.targetPath() + "?pagesize=" + self.recordsPerPage() + "&pagenum=" + self.targetPageNum() + "&format=json", function (data) {
              if (data.error){
                $(document).trigger("error", data.error);
                self.isLoading(false);
                return false;
              }

              if (data.type != null && data.type == "file") {
                location.href = data.url;
                return false;
              }

              self.updateFileList(data.files, data.page, data.breadcrumbs, data.current_dir_path);


            });
        };

        self.viewFile = function (file) {
            if (file.isdir) {
              // Reset page number so that we don't hit a page that doesn't exist
              self.targetPageNum(1);
              self.targetPath('/project/${curr_proj}/${curr_role}/fb/view'+ file.path);
              location.href = self.targetPath();
            } else {
              ;
            }
        };

        self.goToPage = function(pageNumber) {

            console.log('Skip To Page:' +  pageNumber);

            self.targetPageNum(pageNumber);
            if (location.hash.indexOf("!!") > -1){
              location.hash =  location.hash.substring(0, location.hash.indexOf("!!")) + "!!" + pageNumber;
            } else {
              location.hash += "!!" + pageNumber;
            }
        }

        self.skipTo = function() {

            var doc = document,
            old_page = doc.querySelector('#current_page').value,
            page = doc.querySelector('.pagination-input');

            if (! isNaN(page.value) && (page.value > 0 && page.value <= self.page().num_pages)) {
              self.goToPage(page.value);
            } else {
              page.value = old_page;
            }
        };

        self.deleteSelected = function () {
           var paths = [];

            $(self.selectedFiles()).each(function (index, file) {
              paths.push(file.path);
            });

            hiddenFields($("#deleteForm"), 'path', paths);

            $("#deleteForm").attr("action", "/filebrowser/rmtree" + "?" +
              "next=/");

            $("#deleteModal").modal({
              keyboard:true,
              show:true
            });
        };

        // Place all values into hidden fields under parent element.
        // Looks for managed hidden fields and handles sizing appropriately.
        var hiddenFields = function (parentEl, name, values) {
            parentEl = $(parentEl);
            parentEl.find("input.hidden-field").remove();

            $(values).each(function (index, value) {
            var field = $("<input type='hidden' />");
            field.attr("name", name);
            field.attr("class", "hidden-field")
            field.val(value);
            parentEl.append(field);
            });
        };


      }

      var viewModel = new FileBrowserModel([], null, [], "/");
      ko.applyBindings(viewModel);



      $(document).ready(function() {
        viewModel.retrieveData();
      });

    </script>

</div>

