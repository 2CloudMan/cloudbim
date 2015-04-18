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
                <button class="btn btn-default" data-toggle="modal" data-target="#uploadFileModal">+</button>
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
            % for file in files:
                <tr>
                    <td><div class="bimCheckbox"></div></td>
                    <td>${file.get("name")}</td>
                    <td>${file.get("role_slug")}</td>
                    <td>${file.get("ctime")}</td>
                </tr>
            % endfor
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

        <!-- 上传模块 -->
        <div class="modal fade" id="uploadFileModal" tabindex="-1" role="dialog" aria-labelledby="myModalLabel" aria-hidden="true">
          <div class="modal-dialog">
            <div class="modal-content">
              <div class="modal-header">
                <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
                <h4 class="modal-title" id="myModalLabel">上传至: /home/haha</h4>
              </div>

              <div class="modal-body">

              <div id="drag-and-drop-zone" class="uploader">
                  <div>Drag &amp; Drop Images Here</div>
                  <div class="or">-or-</div>
                  <div class="browser">
                    <label>
                      <span>Click to open the file Browser</span>
                      <input type="file" name="files[]" multiple="multiple" title="Click to add Files">
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
        url: '',
        dataType: 'json',
        allowedTypes: '*',
        extraData:{ 'dest' : ''},
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

</div>
