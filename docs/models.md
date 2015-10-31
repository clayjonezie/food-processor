- RawEntry: content,  at, user, tags
- User: email, password hash
- FoodShort:name, common_long_id (need to make this a user preference)
- FoodDescription: food group, long description, short description, common name, other food data
- NutrientDefinition: nutrient, description, 
- NutrientData: nutrient, food, value, 
- Tag: raw_entry, position, text, food_short, food_description, count, size, size_units

See app/models.py for more information
