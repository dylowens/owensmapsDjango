var map = L.map('map').setView([0, 0], 2);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
}).addTo(map);

var selectedLayers = {}; // Store the selected layers

// Add event listeners to checkboxes
document.querySelectorAll("input[type='checkbox'][name='selected_files']").forEach(function (checkbox) {
  checkbox.addEventListener('change', function () {
    var fileId = this.value;
    var fileName = this.getAttribute('data-filename');

    if (this.checked) {
      // Add the selected file's geometry to the map
      fetch(fileName)
        .then(response => response.json())
        .then(data => {
          var layer = L.geoJSON(data).addTo(map);
          selectedLayers[fileId] = layer; // Store the layer for later removal

          // Zoom to the extent of the selected file
          var bounds = layer.getBounds();
          map.fitBounds(bounds);
        })
        .catch(error => console.error('Error fetching GeoJSON file:', error));
    } else {
      // Remove the selected file's geometry from the map
      if (selectedLayers[fileId]) {
        map.removeLayer(selectedLayers[fileId]);
        delete selectedLayers[fileId];
      }
    }
  });
});
