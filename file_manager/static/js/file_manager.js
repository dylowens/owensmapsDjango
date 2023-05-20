$(document).ready(function() {
  $('#converterModal').on('show.bs.modal', function (event) {
    var button = $(event.relatedTarget);
    var fileId = button.data('fileid');
    var modal = $(this);
    modal.find('#file_id').val(fileId);
  });

  $('#converterForm').submit(function (event) {
    event.preventDefault();
    var form = $(this);
    var formData = new FormData(form[0]);

    $.ajax({
      url: convertUrl,
      type: 'POST',
      data: formData,
      processData: false,
      contentType: false,
      success: function (response) {
        if (response.status === 'success') {
          alert('File converted successfully.');
          location.reload();
        } else {
          alert('Error converting file: ' + response.message);
        }
      },
        error: function (jqXHR) {
        var response = jqXHR.responseJSON;
        var message = 'Error converting file.';
        if (response && response.traceback) {
            message += '\n\n' + response.traceback;
        }
        alert(message);
        }

    });
  });
});


var map = L.map('map').setView([0, 0], 2); // Set the view with coordinates [0, 0] and zoom level 2
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

