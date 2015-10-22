# NLP Pipeline

As previously discussed, one objective of this project is to have a "smart" 
analysis of "raw" food journal data. This is a possible pipeline for us to 
use to extract as much data as we can. See <this> page for definitions of
model objects. 

## Overview and Example

Consider the following raw entry.

"peach, hamburger, 3 apples, 12 oz coffee, hemp/chia/flax cereal."

We use Tag objects to create a mapping from text to a specific food in the 
database. The tag uses a "food_short" object 

For instance, we may get the following tags for this raw entry (with others)

{ pos=0, 
  text="peach",
  food_short="peach" }

{ pos=7, 
  text="hamburger", 
  food_short="hamburger", 
  food_description=.., }

{ pos=18, 
  text="3 apples", 
  food_short="apple", 
  food_description=..,
  count=3 }

{ pos=28, 
  text="12 oz coffee", 
  food_short="coffee", 
  food_description=..,
  size=12,
  size_units="oz" }

{ pos=42,
  text="hemp/chia/flax cereal",
  food_short=null,
  food_description=null }

In the last Tag, there is no food_short, because we were not able to
confidently infer the food item. The software has an interface for users to 
manually override this. 

## Step 1. Tokenize

"peach, hamburger, 3 apples, 12 oz coffee, hemp/chia/flax cereal."
... tokenize ...
see app.fplib.nlp.tokenize
["peach", "hamburger", "3 apples", "12 oz coffee", "hemp/chia/flax cereal"]

## Step 2. Parse out quantities and sizes 

{ pos=0, 
  text="peach" }

{ pos=7, 
  text="hamburger" }

{ pos=18, 
  text="3 apples", 
  count=3 }

{ pos=28, 
  text="12 oz coffee", 
  size=12,
  size_units="oz" }

{ pos=42,
  text="hemp/chia/flax cereal",
  food_short=null,
  food_description=null }

## Step 3. Find a relevant 'food_short'

We first check the text against the food_short table, so that users can create
preferences to their specific food (FoodDescription)

## Step 4. Find the actual food item

If we had a relevant food_short, use that. If not, search against 
food_descriptions table for a relevant item, and create a new food_short link

## Step 5. Apply calculations of size & count

this will probably happen at render time, TBD
