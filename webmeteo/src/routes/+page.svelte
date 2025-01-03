<script lang="ts">
import L from "leaflet";

// add div with id="map" to your svelte component
const mapdiv = document.createElement("div");
document.body.appendChild(mapdiv);
mapdiv.id = "map";
// add height:180px to your svelte component
mapdiv.style.height = "100vh";
mapdiv.style.width = "100vw";

const map = L.map("map").setView([52, 21], 7);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
	maxZoom: 19,
	attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

// request voivodeships from server
const base_url = "http://0.0.0.0:8000";
const url = `${base_url}/voivodeships`;

fetch(url, {
	method: "GET",
})
	.then((response) => response.json())
	.then((data) => {
    console.log(data);
		L.geoJSON(data).addTo(map);
	});

</script>

<style>
</style>
