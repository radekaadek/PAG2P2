<h1>Welcome to SvelteKit</h1>

<p>Visit <a href="https://svelte.dev/docs/kit">svelte.dev/docs/kit</a> to read the documentation</p>

<script lang="ts">
import L from "leaflet";

// add div with id="map" to your svelte component
const mapdiv = document.createElement("div");
document.body.appendChild(mapdiv);
mapdiv.id = "map";
// add height:180px to your svelte component
mapdiv.style.height = "180px";

const map = L.map("map").setView([51.505, -0.09], 13);

L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
	maxZoom: 19,
	attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

</script>

<style>
/*#map { height: 180px; }*/
</style>
