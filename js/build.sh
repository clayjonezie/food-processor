babel --presets react main.js -o main_out.js
babel --presets react plan.js -o plan_out.js
browserify plan_out.js main_out.js -o bundle.js
cp bundle.js ../static/
