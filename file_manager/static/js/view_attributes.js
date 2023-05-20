    // Attribute modal  
    // Declare fileId outside of the modal event handlers so it can be accessed by both
    var fileId;

    // Capture the fileId when the modal is about to be shown
    $('#attributeModal').on('show.bs.modal', function (event) {
        var button = $(event.relatedTarget); 
        fileId = button.data('fileid'); 
    });

    // Load the data when the modal has been shown
    $('#attributeModal').on('shown.bs.modal', function (event) {
        table.innerHTML = '';  // Clear the table here
        var modal = $(this);
        var attributesUrl = `/file_manager/file_attributes/${fileId}`;  // Construct the URL here
        $.ajax({
            url: attributesUrl,  // Use the URL here
            type: 'GET',
            success: function(response) {
                var data = response.data;
                var table = document.getElementById('attributesTable');
                table.innerHTML = '';  // Clear the table first
                if (data.length > 0) {
                    var headers = Object.keys(data[0]);
                    var thead = document.createElement('thead');
                    var tr = document.createElement('tr');
                    for (var j = 0; j < headers.length; j++) {
                        var th = document.createElement('th');
                        th.textContent = headers[j];
                        tr.appendChild(th);
                    }
                    thead.appendChild(tr);
                    table.appendChild(thead);
                    var tbody = document.createElement('tbody');
                    for (var i = 0; i < data.length; i++) {
                        var tr = document.createElement('tr');
                        for (var j = 0; j < headers.length; j++) {
                            var td = document.createElement('td');
                            td.textContent = data[i][headers[j]];
                            tr.appendChild(td);
                        }
                        tbody.appendChild(tr);
                    }
                    table.appendChild(tbody);
                }
            },
            error: function(jqXHR, textStatus, errorThrown) {
                console.error(textStatus, errorThrown);
            }

        });
    });

    // Clear the table when the modal is hidden
    $('#attributeModal').on('hide.bs.modal', function (event) {
        var table = document.getElementById('attributesTable');
        table.innerHTML = '';  // Clear the table
        console.log('Table cleared')
    });


