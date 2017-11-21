[![Build Status](https://travis-ci.org/dennisja/yummy-recipes-api.svg?branch=master)](https://travis-ci.org/dennisja/yummy-recipes-api)
[![Coverage Status](https://coveralls.io/repos/github/dennisja/yummy-recipes-api/badge.svg?branch=master)](https://coveralls.io/github/dennisja/yummy-recipes-api?branch=master)
[![Maintainability](https://api.codeclimate.com/v1/badges/bef6f9c764c4a2b24ab7/maintainability)](https://codeclimate.com/github/dennisja/yummy-recipes-api/maintainability)

# yummy-recipes-api
This is the yummy recipes api
Yummy Recipes is a project inspired by the fact that keeping track of awesome food recipes is a need for many individuals who love to cook and eat good food. With it you will be able to create, save, share and keep track of those recipes, the one that matter.

## Requirements
- `Python 3.6+`
- `PostgreSQL`
- `Flask`

## Installation and Running
### Clone the repository
```
$ git clone https://github.com/dennisja/yummy-recipes-api.git
$ cd yummy-recipes-api
```
### Installing virtualenv
If you do not have virtualenv installed. Use the command below to install it
```
pip install virtualenv
```
### Create a virtual environment using virtualenv
For mac os or linux users
```
$ virtualenv venv
$ source venv/bin/activate
```
For windows users
- If you are using windows command prompt
```
virtualenv venv
cd venv/scripts && activate && cd ../..
```
- if you are using git bash
```
virtualenv venv
source venv/scripts/activate
```

### Install the project dependancies
```
pip install -r requirements.txt
```

## Set environment varibles
### For windows users
If you are using the in built windows command prompt
```
set YUMMY_TEST_DATABASE_URI=postgresql://postgres:mypassword@127.0.0.1:5432/test_yummy_recipes
set YUMMY_DATABASE_URI=postgresql://postgres:mypassword@127.0.0.1:5432/yummy_recipes
set YUMMY_SECRET_KEY="The secret key you prefer"
```
### For mac os or linux users or if you are using cygwin or git bash on windows
```
export YUMMY_TEST_DATABASE_URI=postgresql://postgres:mypassword@127.0.0.1:5432/test_yummy_recipes
export YUMMY_DATABASE_URI=postgresql://postgres:mypassword@127.0.0.1:5432/yummy_recipes
export YUMMY_SECRET_KEY="The secret key you prefer"
```

### Running database migrations
```
python migrate.py db init
python migrate.py db migrate
python migrate.py db upgrade
```

### Running the application locally
Make sure you are in the application root folder at the terminal and then run the command below
```
python run.py
```

## End points available
Method       | Path          | Role         | Access
------------ | ------------- | -------------| -------
POST |/yummy/api/v1.0/auth/register/ | Registers a user | PUBLIC
POST |/yummy/api/v1.0/auth/login/ | Log in a user | PUBLIC
PUT  |/yummy/api/v1.0/users/| Updates user details| PRIVATE
PATCH| /yummy/api/v1.0/users/| Changes user password| PRIVATE
GET| /yummy/api/v1.0/users/| Get details of all registered users| PRIVATE
GET| /yummy/api/v1.0/users/<id>| Get details of a particular user| PRIVATE
POST |/yummy/api/v1.0/recipe_categories/ | Helps user create a recipe category | PRIVATE
GET| /yummy/api/v1.0/search| search for registered users, recipes, and recipe categories| PRIVATE
PUT |/yummy/api/v1.0/recipe_categories/<int:category_id>| Helps a user edit existing category| PRIVATE
GET |/yummy/api/v1.0/recipe_categories/ | Used to fetch a user recipe categories | PRIVATE
GET |/yummy/api/v1.0/recipe_categories/<int:category_id> | Fetches recipe details of a single recipe  | PRIVATE
DELETE |/yummy/api/v1.0/recipe_categories/<int:category_id>| Helps a user delete a recipe category | PRIVATE
POST |/yummy/api/v1.0/recipes/ | Helps user add a new recipe | PRIVATE
PUT  |r/yummy/api/v1.0/recipes/<int:recipe_id> | Used to update recipe details | PRIVATE
PATCH| /yummy/api/v1.0/recipes/<int:recipe_id>| Helps user to publish a recipe| PRIVATE
DELETE |/yummy/api/v1.0/recipes/<int:recipe_id> | Helps user delete a recipe | PRIVATE
GET| /yummy/api/v1.0/recipes/| Get all recipes created by a user| PRIVATE
GET| /yummy/api/v1.0/recipes/<int:recipe_id> | Get details of a particular recipe created by a user| PRIVATE

