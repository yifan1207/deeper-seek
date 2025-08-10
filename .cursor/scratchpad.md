# Background and Motivation
We want to incorporate a geospatial similarity heatmap into the game, inspired by the Google Earth Engine app. When a user clicks a point or searches for a city/place, we compute a world heatmap of similar embeddings and render it in the left geospatial panel. The query container on the right will act as the search UI for this feature.

# Key Challenges and Analysis
- Client-side Earth Engine (EE) initialization reliability and graceful fallback to Leaflet.
- Implementing true similarity in EE (embedding dot product) vs a lightweight fallback visualization.
- Providing a usable place search without adding new backend dependencies (use OSM Nominatim).
- UI overlays (legend, coordinates) without EE `ui.Panel` (we use HTML/CSS).
- Keeping multiplayer/game flow unaffected.

# High-level Task Breakdown
1) Phase 1 – EE integration and similarity core
   - Ensure `generateHeatmap(coords)` computes similarity using EE embeddings (already scaffolded).
   - Keep fallback `generateFallbackHeatmap` for when EE isn’t available.
   - Success: Clicking the EE map adds a similarity layer; no console errors.

2) Phase 2 – UI (legend + controls)
   - Add an HTML legend in `geospatial-container` with color bar and coordinate label.
   - Success: Legend appears when heatmap generated and shows last clicked/searched coords.

3) Phase 3 – Search integration via query container
   - Add a "Similarity Heatmap" button beside the existing Send Query.
   - Geocode input (city/place or "lat, lng") via Nominatim. On success, call heatmap.
   - Success: Entering a place runs heatmap; errors surfaced via notification.

4) Phase 4 – Enhancements (later)
   - Optional thumbnail panel, URL state, caching, multiplayer sync.

# Project Status Board
- [x] Phase 1 – Core EE similarity (existing code verified)
- [x] Phase 2 – Legend overlay
- [x] Phase 3 – Search button + geocoding wired
- [ ] Phase 4 – Enhancements

# Current Status / Progress Tracking
- Implemented legend UI and a new `Similarity Heatmap` button using the existing query textbox.
- Added geocoding (Nominatim) and coordinate parsing to trigger heatmap.
- Legend updates on click and search; fallback continues to work.

# Executor's Feedback or Assistance Requests
- If we need higher geocoding reliability or rate limits avoided, we may switch to Google Geocoding or Mapbox with an API key.
- Thumbnail similar to EE `ui.Thumbnail` isn’t directly available in our client; would require server or EE Apps context.

# Lessons
- Keep EE-specific UI (`ui.Panel`) out of our app; use plain HTML overlays.
- Handle both EE coords object `{lon, lat}` and Leaflet `{lat, lng}`.
