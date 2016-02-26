babel --presets react main.js -o main_out.js
babel --presets react plan.js -o plan_out.js
babel --presets react food.js -o food_out.js
browserify main_out.js plan_out.js food_out.js -o bundle.js
cp bundle.js ../static/
