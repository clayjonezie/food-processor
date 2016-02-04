babel --presets react main.js -o out.js
browserify out.js -o bundle.js
cp bundle.js ../static/
