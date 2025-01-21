<script lang="ts">
import L from "leaflet";

const mapdiv = document.createElement("div");
document.body.appendChild(mapdiv);
mapdiv.id = "map";
mapdiv.style.height = "100vh";
mapdiv.style.width = "100vw";

const map = L.map("map").setView([52, 21], 7);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
	maxZoom: 19,
	attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

// request voivodeships from server
const base_url = "http://0.0.0.0:8000";
const voivodeships_url = `${base_url}/voivodeships`;
const powiats_url = `${base_url}/powiats`;

const osm = L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap'
});
const osmHOT = L.tileLayer('https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors, Tiles style by Humanitarian OpenStreetMap Team hosted by OpenStreetMap France'});
const baseMaps = {
    "OpenStreetMap": osm,
    "OpenStreetMap.HOT": osmHOT
};

const layerControl = L.control.layers(baseMaps).addTo(map);

fetch(voivodeships_url, {
	method: "GET",
})
	.then((response) => response.json())
	.then((data) => {
    const d = L.geoJSON(data, { style: { color: 'red', weight: 4 } });
    // Add the layer to the map directly
    d.addTo(map); // 'map' is your Leaflet map instance

    // Add the layer to the layer control
    layerControl.addOverlay(d, "Voivodeships");
    
	});

fetch(powiats_url, {
	method: "GET",
})
	.then((response) => response.json())
	.then((data) => {
    const d = L.geoJSON(data, { style: { color: 'blue', weight: 4 } });
    layerControl.addOverlay(d, "Powiaty");
    
	});

</script>

<style>
</style>
