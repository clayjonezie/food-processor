# Journal Parsing

This document describes the process of taking a user's submitted journal
entry and turning it into a tagged entry. This is a high-level overview,
where `nlp-pipeline.md` provides a more detailed description of individual
methods. The goal of this analysis is to find data we can precompute.

Another document, to be written, will describe journal rendering, which could also
have results that can be precomputed or cached to reduce the page render time.

When the user submits a new entry, `nlp.tag_raw_entry` is used to create a number
of tags, which are added to the database.

## nlp.tag_raw_entry

This method gathers a list of tokens, and iterates through them. At this point,
a token should represent one tag, or one food. For each token, 
we lemmatize all words in the token. We then check if any word in the token
is a quantity and assign this to the tag. By default, quantity is 1. 

We then have to find the 'best' FoodDescription object for the token. This
is currently computed in `models.FoodShort.get_food`. It might fit better
elsewhere, but the `FoodShort` model represents the mapping of a short form 
food (like the tokens being processed here) and a FoodDescription. 

## FoodShort.get_food

This takes in a fresh token, and gets the FoodShort model object via
`models.FoodShort.get_or_create` for that token. This allows us to look up a 
users preference, and cached FoodDescription model objects. 

## FoodShort.get_or_create

This method is worth discussing because upon creation of a new FoodShort 
model object, we associate with it a `best_fd` property, which is used as the
associated FoodDescription when the user has no preference. This takes a 
considerable amount of time. If the search for a `best_fd` fails, none is
associated.

The search for a best_fd happens in `fplib.nlp.nearby_food_descriptions`

## fplib.nlp.nearby_food_descriptions

This works by querying the long_desc property of FoodDescription for anything
"like" the token, meaning an exact 'string contains'. *This could be improved
on using some other text matching, but at an overhead cost.* Then, we rank each
of these matches. The ranking uses a few metrics, one of which includes a 
Google query that is not yet cached. See implementation for details. 

