<script lang="ts">
  import L from "leaflet";

  const mapdiv = document.createElement("div");
  document.body.appendChild(mapdiv);
  mapdiv.id = "map";
  mapdiv.style.height = "0vh";
  mapdiv.style.width = "0vw";

  let loading = $state(true);

  const initialView = { center: [52, 19] as L.LatLngTuple, zoom: 7 };
  const map = L.map("map").setView(initialView.center, initialView.zoom);

  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution:
      '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
  }).addTo(map);

  const base_url = "http://localhost:8000";
  const voivodeships_url = `${base_url}/voivodeships`;
  const powiats_url = `${base_url}/powiats_in_voivodeship`;

  let currentMarkersLayer: L.GeoJSON | null = null;
  let resetButton: HTMLButtonElement | null = null;
  let powiatGeoJsonLayer: L.GeoJSON | null = null;
  let geoJsonLayer: L.GeoJSON | null = null;
  let sliderValue = 1; // Initial slider value
  let sliderContainer: HTMLDivElement | null = null;

  const osm = L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
    maxZoom: 19,
    attribution: "© OpenStreetMap",
  });

  const baseMaps = {
    OpenStreetMap: osm,
  };

  const layerControl = L.control.layers(baseMaps).addTo(map);

  // Helper function to calculate color based on temperature
  function getColorForTemperature(temp: number | null): string {
    if (temp === null) {
      return "gray"; // Gray for null values
    }

    const minTemp = -8; // Minimum temperature
    const maxTemp = 25; // Maximum temperature
    const clampedTemp = Math.max(minTemp, Math.min(maxTemp, temp)); // Clamp between -40 and 40

    const hue = ((maxTemp - clampedTemp) / (maxTemp - minTemp)) * 240; // 240 is blue, 0 is red
    return `hsl(${hue}, 100%, 50%)`;
  }

  // Update the fetchFeaturesAndAddMarkers function
  async function fetchFeaturesAndAddMarkers(
    url: string,
    id: string,
    map: L.Map,
  ): Promise<void> {
    try {
      const response = await fetch(`${url}/${id}`, {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch features: ${response.statusText}`);
      }

      let data;
      try {
        data = await response.json();
      } catch (jsonError) {
        throw new Error(`Failed to parse JSON: ${jsonError}`);
      }

      if (currentMarkersLayer) {
        map.removeLayer(currentMarkersLayer);
        layerControl.removeLayer(currentMarkersLayer); // Remove from layer control
      }

      // Convert GeoJSON features to Leaflet markers and add them to the map
      currentMarkersLayer = L.geoJSON(data, {
        pointToLayer: (feature, latlng) => {
          const meanTemp = parseFloat(getMeanValue(feature, sliderValue));
          const color = getColorForTemperature(
            isNaN(meanTemp) ? null : meanTemp,
          );

          const marker = L.circleMarker(latlng, {
            radius: 15,
            fillColor: color,
            color: "#000", // Border color
            weight: 1,
            opacity: 1,
            fillOpacity: 0.8,
          });

          const tooltipContent = `<b>${feature.properties?.name || "Marker"}</b><br>Avrg Temp: ${meanTemp || "N/A"}`;
          marker.bindTooltip(tooltipContent, { className: "custom-tooltip" });

          return marker;
        },
      });

      currentMarkersLayer.addTo(map);
      layerControl.addOverlay(currentMarkersLayer, "Markers"); // Add to layer control
      console.log("Markers added successfully");
    } catch (error) {
      console.error("Error fetching and adding markers:", error);
    }
  }

  // Helper function to get the correct mean value based on slider value
  function getMeanValue(feature: any, sliderValue: number): string {
    const meanKey = `mean${sliderValue}`;
    const value = feature.properties?.[meanKey];
    return value !== undefined ? parseFloat(value).toFixed(1) : "N/A"; // Round to 1 decimal place
  }

  function updateMarkerTooltips() {
    if (currentMarkersLayer) {
      currentMarkersLayer.eachLayer((layer) => {
        if (layer instanceof L.CircleMarker) {
          const feature = layer.feature;
          if (feature !== undefined) {
            // Get updated mean temperature for the selected month
            const meanTemp = parseFloat(getMeanValue(feature, sliderValue));
            const color = getColorForTemperature(
              isNaN(meanTemp) ? null : meanTemp,
            );

            // Update tooltip content
            const updatedTooltip = `<b>${feature.properties?.name || "Marker"}</b><br>Avrg Temp: ${meanTemp || "N/A"}`;
            layer.setTooltipContent(updatedTooltip);

            // Update marker color
            layer.setStyle({
              fillColor: color,
            });
          }
        }
      });
    }
  }

  async function fetchPowiatsAndAddToMap(
    url: string,
    id: string,
    map: L.Map,
  ): Promise<void> {
    try {
      const response = await fetch(`${url}/${id}`, {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch powiats: ${response.statusText}`);
      }

      let data;
      try {
        data = await response.json();
      } catch (jsonError) {
        throw new Error(`Failed to parse JSON: ${jsonError}`);
      }

      // Clear the existing powiat layer if it exists
      if (powiatGeoJsonLayer) {
        map.removeLayer(powiatGeoJsonLayer);
        layerControl.removeLayer(powiatGeoJsonLayer);
      }

      // Convert GeoJSON features to Leaflet polygons and add them to the map
      powiatGeoJsonLayer = L.geoJSON(data, {
        style: {
          color: "black",
          weight: 2,
          fillColor: "grey",
          fillOpacity: 0.3,
        },
        onEachFeature: async (feature, layer) => {
          const meanTemp = await fetchPowiatMeteoData(
            feature.properties?.national_c,
            sliderValue,
          );
          const tooltipContent = `Avg Temp: ${meanTemp || "N/A"}`;
          layer.bindTooltip(tooltipContent, {
            className: "custom-tooltip", // Optional: Add a class for custom styling
            permanent: false, // Optional: Tooltips will show on hover, not always visible
            offset: [0, -10], // Optional: Adjust the tooltip position
          });
        },
      });
    } catch (error) {
      console.error("Error fetching and adding powiats:", error);
    }
    if (powiatGeoJsonLayer) {
      powiatGeoJsonLayer.addTo(map);

      // Add powiats layer to layer control
      layerControl.addOverlay(powiatGeoJsonLayer, "Powiats");

      map.fitBounds(powiatGeoJsonLayer.getBounds(), {
        padding: [10, 10], // Add a small margin around the markers
      });
      updatePowiatColorsAndTooltips();
    }
  }

  // Helper function to fetch powiat mean temperatures for the selected month
  async function fetchPowiatMeteoData(
    teryt: string,
    sliderValue: number,
  ): Promise<number | null> {
    try {
      const response = await fetch(`${base_url}/powiat_meteo/${teryt}`, {
        method: "GET",
      });

      if (!response.ok) {
        throw new Error(
          `Failed to fetch powiat meteo data: ${response.statusText}`,
        );
      }

      let data;
      try {
        data = await response.json();
      } catch (jsonError) {
        throw new Error(`Failed to parse JSON: ${jsonError}`);
      }
      const meanKey = `mean${sliderValue}`;
      const meanTemp = data[meanKey];

      return meanTemp !== undefined ? parseFloat(meanTemp) : null;
    } catch (error) {
      console.error("Error fetching powiat meteo data:", error);
      return null;
    }
  }

  // Function to update the powiat colors and tooltips when the slider value changes
  // Function to update the powiat colors and tooltips when the slider value changes
  async function updatePowiatColorsAndTooltips() {
    if (powiatGeoJsonLayer) {
      powiatGeoJsonLayer.eachLayer(async (layer) => {
        if (layer instanceof L.Path) {
          const geoJsonLayerT = layer as L.Path & { feature: GeoJSON.Feature };
          if (geoJsonLayerT.feature) {
            const feature = geoJsonLayerT.feature;
            const teryt = feature.properties?.national_c; // Get the powiat TERYT

            // Use the pre-fetched PowiatMeteo data
            const meanTemp = await fetchPowiatMeteoData(teryt, sliderValue);
            // Update tooltip content
            const updatedTooltip = `Avrg Temp: ${meanTemp || "N/A"}`;
            layer.setTooltipContent(updatedTooltip);

            // Update powiat color only if we have a valid temperature
            if (meanTemp !== null) {
              const color = getColorForTemperature(meanTemp); // Get color for the temperature
              layer.setStyle({
                fillColor: color,
                fillOpacity: 0.4,
              });
            } else {
              layer.setStyle({
                fillColor: "gray",
                fillOpacity: 0.4,
              });
            }
          }
        }
      });
    }
  }

  // Reset Powiat layer
  function resetPowiatLayer() {
    if (powiatGeoJsonLayer) {
      map.removeLayer(powiatGeoJsonLayer);
      layerControl.removeLayer(powiatGeoJsonLayer); // Remove from layer control
      powiatGeoJsonLayer = null;
    }
  }

  // Reset map
  function showResetButton() {
    if (!resetButton) {
      resetButton = document.createElement("button");
      resetButton.textContent = "Reset View";
      resetButton.style.position = "absolute";
      resetButton.style.top = "20px";
      resetButton.style.left = "50px";
      resetButton.style.zIndex = "1000";
      resetButton.style.padding = "10px 15px";
      resetButton.style.background = "white";
      resetButton.style.border = "1px solid black";
      resetButton.style.borderRadius = "5px";
      resetButton.style.cursor = "pointer";

      resetButton.addEventListener("click", () => {
        resetMap();
        resetPowiatLayer(); // Clear powiat data
        hideResetButton();
        hideSlider();
      });

      document.body.appendChild(resetButton);
    }
  }

  function hideResetButton() {
    if (resetButton) {
      document.body.removeChild(resetButton);
      resetButton = null;
    }
  }

  function resetMap() {
    map.setView(initialView.center, initialView.zoom);
    if (currentMarkersLayer) {
      map.removeLayer(currentMarkersLayer);
      layerControl.removeLayer(currentMarkersLayer);
      currentMarkersLayer = null;
    }
    if (geoJsonLayer) {
      geoJsonLayer.eachLayer((layer) => {
        if (layer instanceof L.Path) {
          layer.setStyle({
            fillOpacity: 0.2,
            fillColor: "red",
            color: "red",
            weight: 4,
          });
        }
      });
    }
  }

  // Slider
  function showSlider() {
    if (!sliderContainer) {
      sliderContainer = document.createElement("div");
      Object.assign(sliderContainer.style, {
        position: "absolute",
        bottom: "10px",
        left: "20px",
        zIndex: "1000",
        textAlign: "center",
        backgroundColor: "rgba(255, 255, 255, 0.8)",
        padding: "10px",
        borderRadius: "5px",
        boxShadow: "0 2px 5px rgba(0, 0, 0, 0.3)"
      });

      const sliderLabelContainer = document.createElement("div");
      sliderLabelContainer.style.marginBottom = "10px";

      const label = document.createElement("label");
      label.textContent = "Month: ";

      const sliderValueDisplay = document.createElement("span");
      sliderValueDisplay.textContent = sliderValue.toString();

      sliderLabelContainer.appendChild(label);
      sliderLabelContainer.appendChild(sliderValueDisplay);

      const slider = document.createElement("input");
      Object.assign(slider, {
        type: "range",
        min: "1",
        max: "12",
        value: sliderValue.toString(),
        style: "width: 200px"
      });

      slider.addEventListener("input", (event) => {
        sliderValue = parseInt((event.target as HTMLInputElement).value);
        sliderValueDisplay.textContent = sliderValue.toString();
        updateMarkerTooltips();
        updatePowiatColorsAndTooltips();
      });

      sliderContainer.appendChild(sliderLabelContainer);
      sliderContainer.appendChild(slider);
      document.body.appendChild(sliderContainer);
    }
  }

  function hideSlider() {
    if (sliderContainer) {
      document.body.removeChild(sliderContainer);
      sliderContainer = null;
    }
  }

  fetch(voivodeships_url, { method: "GET" })
    .then((response) => {
      if (!response.ok) {
        throw new Error(`Failed to fetch voivodeships: ${response.statusText}`);
      }
      return response.text().then((text) => {
        try {
          return JSON.parse(text);
        } catch (jsonError) {
          throw new Error(`Failed to parse JSON: ${jsonError}`);
        }
      });
    })
    .then((data) => {
      geoJsonLayer = L.geoJSON(data, {
        style: { color: "red", weight: 4, fillColor: "red", fillOpacity: 0.2 },
        onEachFeature: (feature, layer) => {
          layer.on("click", () => {
            if (feature.properties && feature.properties.national_c) {
              geoJsonLayer?.eachLayer((otherLayer) => {
                if (otherLayer instanceof L.Path) {
                  if (otherLayer === layer) {
                    otherLayer.setStyle({
                      fillOpacity: 0,
                      color: "blue",
                      weight: 4,
                    });
                    otherLayer.bringToFront();
                  } else {
                    otherLayer.setStyle({
                      fillOpacity: 0.2,
                      fillColor: "red",
                      color: "red",
                      weight: 4,
                    });
                  }
                }
              });
              fetchPowiatsAndAddToMap(
                powiats_url,
                feature.properties.national_c,
                map,
              );
              fetchFeaturesAndAddMarkers(
                `${base_url}/meteo`,
                feature.properties.national_c,
                map,
              );
              showResetButton();
              showSlider(); // Show the slider when a feature is selected
            } else {
              console.error("Feature does not have a 'national_c' property");
            }
          });
        },
      });

      geoJsonLayer.addTo(map);
      layerControl.addOverlay(geoJsonLayer, "Voivodeships");

      loading = false;
      mapdiv.style.height = "100vh";
      mapdiv.style.width = "100vw";
      map.invalidateSize();
    });
</script>

{#if loading}
  <div class="loader-wrapper">
    <div class="loader"></div>
  </div>
{/if}

<style>
  .loader-wrapper {
    display: flex;
    justify-content: center;
    align-items: center;
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 9999;
  }

  .loader {
    width: 44.8px;
    height: 44.8px;
    position: relative;
    transform: rotate(45deg);
  }

  .loader:before,
  .loader:after {
    content: "";
    position: absolute;
    inset: 0;
    border-radius: 50% 50% 0 50%;
    background: #0000;
    background-image: radial-gradient(
      circle 11.2px at 50% 50%,
      #0000 94%,
      #ff4747
    );
  }

  .loader:after {
    animation: pulse-ytk0dhmd 1s infinite;
    transform: perspective(336px) translateZ(0px);
  }

  @keyframes pulse-ytk0dhmd {
    to {
      transform: perspective(336px) translateZ(168px);
      opacity: 0;
    }
  }
</style>
