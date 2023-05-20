var map = L.map('map').setView([0, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var selectedLayers = {}; // Store the selected layers

// Add event listeners to checkboxes
document.querySelectorAll("input[type='checkbox'][name='selected_files']").forEach(function (checkbox) {
  checkbox.addEventListener('change', function () {
    var fileId = this.value;
    var fileUrl = this.getAttribute('data-filename');

    if (this.checked) {
      // Request the GeoJSON data from the Django view
      fetch('/converter_to_geojson/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify({ file_url: fileUrl })
      })
        .then(response => response.json())
        .then(data => {
          if (data.error) {
            console.error(data.error);
            return;
          }

          var geojsonData = JSON.parse(data.geojson_data);
          var layer = L.geoJSON(geojsonData).addTo(map);
          selectedLayers[fileId] = layer; // Store the layer for later removal

          // Zoom to the extent of the selected file
          var bounds = layer.getBounds();
          map.fitBounds(bounds);
        })
        .catch(error => console.error('Error fetching GeoJSON data:', error));
    } else {
      // Remove the selected file's geometry from the map
      if (selectedLayers[fileId]) {
        map.removeLayer(selectedLayers[fileId]);
        delete selectedLayers[fileId];
      }
    }
  });
});

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Check if this cookie string begins with the name we want
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

