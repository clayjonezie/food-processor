# Entry Methods

The entire purpose of this project is to decrese the time it takes to create detailed food logs. 
This document will evaluate different approaches. 

An entry is a set of foods, each of which needs to these three things to accurately calculate the nutrition data. 

- The food item, which has to be in our nutrient database
- A quantity
- A measure ("cup shredded", "small", "slice", "oz")

## Entry Approaches

- Static input and NL parsing
  - + Quick initial entry
  - - Inacurate
  - - Slows down entry when something is wrong, requires user to double check
  - + Would be aided by having an existing data set of food logs so we can weight the NL parsing by useage
  - - Ambiguity may be inevitable
  - - Difficult to do realtime
  
- Discrete entry fields 
  - - Doesn't add anything to existing solutions
  - + Provides instant verification, 100% confidence it's correct
