"""This is the routes module
It contains all end points of the application
"""
from flask import jsonify, abort, request, redirect
from sqlalchemy import or_

from api import app, models, db
from api.helpers import Secure, format_data
from api.validator import ValidateUser, ValidateRecipeCategory as ValidateCat, ValidateRecipe
from api.decorators import auth_token_required, json_data_required,\
                            user_must_own_recipe,user_must_own_recipe_category
from api import BASE_URL



@app.route("/")
def home_page():
    """ Redirects to the API documentation"""
    return redirect(
        "https://app.swaggerhub.com/api/dennisja/yummy_recipes/1.0.0")


# recipe category end point
@app.route(f"{BASE_URL}recipe_categories/", methods=["POST"])
@json_data_required
@auth_token_required
def add_recipe_category(user):
    """ Adds a recipe category """
    # validate submitted recipe category details
    recipe_cat_data = request.get_json()
    recipe_errors = ValidateCat.validate_recipe(recipe_cat_data)

    if recipe_errors:
        return jsonify({"errors": recipe_errors}), 400

    # check whether a recipe category name by the same already exists
    existing_recipe = models.RecipeCategory.query.filter_by(
        name=format_data(recipe_cat_data.get("cat_name")),
        owner=user.id).first()

    if existing_recipe:
        return jsonify({
            "errors":
            ["The Recipe Category you are trying to add already exists"]
        }), 400

    # create the recipe category
    recipe = models.RecipeCategory(
        format_data(recipe_cat_data.get("cat_name")), user.id)
    recipe.save_recipe_cat()

    return jsonify({
        "message": "Successfully created recipe category",
        "recipe_cat": recipe.recipe_cat_details
    }), 201, {
        "Location": recipe.recipe_cat_details.get("url")
    }


@app.route(
    f"{BASE_URL}recipe_categories/<int:category_id>", methods=["PUT"])
@json_data_required
@auth_token_required
@user_must_own_recipe_category
def edit_recipe_category(user, recipe_cat, category_id):
    """ Edits a recipe category """
    recipe_cat_data = request.get_json()
    recipe_cat_errors = ValidateCat.validate_recipe(recipe_cat_data)
    if recipe_cat_errors:
        return jsonify({"errors": recipe_cat_errors}), 400

    existing_recipe_cat = models.RecipeCategory.query.filter_by(
        name=format_data(recipe_cat_data.get("cat_name")),
        owner=user.id).first()

    if existing_recipe_cat and existing_recipe_cat.id != category_id:
        return jsonify({
            "errors": [
                "The new recipe category name you are trying to use already exists"
            ]
        }), 400

    if format_data(recipe_cat_data.get("cat_name")) == recipe_cat.name:
        return jsonify({
            "message":
            "Recipe category name is similar to the previous. No changes where made"
        }), 400

    # edit the recipe
    recipe_cat.name = format_data(recipe_cat_data.get("cat_name"))
    db.session.commit()

    return jsonify({
        "message": "Successfully edited recipe category",
        "recipe_cat": recipe_cat.recipe_cat_details
    }), 200


@app.route(
    f"{BASE_URL}recipe_categories/<int:category_id>", methods=["DELETE"])
@auth_token_required
@user_must_own_recipe_category
def delete_recipe_category(user, recipe_cat, category_id):
    """ Deletes a recipe category """
    # delete the recipe category and all its recipes
    recipe_cat.delete_recipe_cat()
    return jsonify({"message": "Recipe Category successfully deleted"}), 200


@app.route(f"{BASE_URL}recipe_categories/", methods=["GET"])
@auth_token_required
def get_all_user_recipe_categories(user):
    """ Gets all user recipe categories """
    user_cats = models.RecipeCategory.query.filter_by(owner=user.id).all()
    if not user_cats:
        return jsonify({
            "errors": ["You have not added any recipe categories yet"]
        }), 404

    return jsonify({
        "message":
        "Recipe Categories exists",
        "recipe_cats": [category.recipe_cat_details for category in user_cats]
    })


@app.route(
    f"{BASE_URL}recipe_categories/<int:category_id>", methods=["GET"])
@auth_token_required
def get_recipe_category(user, category_id):
    """ Gets a recipe categories """
    recipe_cat = user.recipe_categories.filter_by(id=category_id).first()

    if not recipe_cat:
        return jsonify({
            "errors":
            ["The recipe cat you are trying to access does not exist."]
        }), 404

    return jsonify({
        "recipe_cat": recipe_cat.recipe_cat_details,
        "message": "Recipe category exists"
    }), 200


@app.route(
    f"{BASE_URL}recipe_categories/<int:category_id>/recipes/",
    methods=["GET"])
@auth_token_required
def get_all_recipes_in_a_category(user, category_id):
    """ Gets user recipes in a particular category """
    recipe_cat = user.recipe_categories.filter_by(id=category_id).first()
    if not recipe_cat:
        abort(404)
    recipes = recipe_cat.recipes
    return jsonify({
        "message": "Category exists",
        "recipes": [recipe.recipe_details for recipe in recipes]
    }), 200


# recipe end points
@app.route(f"{BASE_URL}recipes/", methods=["POST"])
@json_data_required
@auth_token_required
def add_recipe(user):
    """ Adds a recipe """
    # validate recipe data
    recipe_data = request.get_json()
    recipe_errors = ValidateRecipe.validate_recipe(recipe_data)
    if recipe_errors:
        return jsonify({"errors": recipe_errors}), 400

    # check if the supplied recipe category exists
    recipe_cat = models.RecipeCategory.query.filter_by(
        id=format_data(recipe_data.get("category"))).first()
    if not recipe_cat:
        return jsonify({
            "errors":
            ["Trying to add a recipe to a category that does not exist"]
        }), 404

    if recipe_cat.owner != user.id:
        return jsonify({
            "errors": [
                "Trying to add a recipe to a category that does not belong to you"
            ]
        }), 403

    # check if a recipe with the same name exists in the same category and by the same user
    recipe_exists = models.Recipe.query.filter_by(
        name=format_data(recipe_data.get("name")),
        owner=user.id,
        category_id=recipe_data.get("category")).first()
    if recipe_exists:
        return jsonify({
            "errors": [
                "A recipe with the same name, by the same user already exists in the same category"
            ],
            "existing_recipe":
            recipe_exists.recipe_details
        }), 400

    # add the recipe
    recipe = models.Recipe(
        format_data(recipe_data.get("name")), recipe_data.get("steps"),
        recipe_data.get("ingredients"), recipe_data.get("category"), user.id)
    recipe.save_recipe()
    return jsonify({
        "message": "Successfully added recipe",
        "recipe": recipe.recipe_details
    }), 201, {
        "Location": recipe.recipe_details["url"]
    }


@app.route(f"{BASE_URL}recipes/<int:recipe_id>", methods=["PUT"])
@json_data_required
@auth_token_required
@user_must_own_recipe
def edit_a_recipe(user, recipe, recipe_id):
    """
    Edits a recipe
    :param user: Current user object, passed from a decorator
    :param recipe: Recipe object, passed from a decorator
    :param recipe_id: The recipe id
    :return:
    """

    recipe_data = request.get_json()
    # validate submitted data
    recipe_errors = ValidateRecipe.validate_recipe(recipe_data)
    if recipe_errors:
        return jsonify({"errors": recipe_errors}), 400

    # check if the supplied recipe category exists
    recipe_cat = models.RecipeCategory.query.filter_by(
        id=format_data(recipe_data.get("category"))).first()
    if not recipe_cat:
        return jsonify({
            "errors":
            ["Trying to move a recipe to a category that does not exist"]
        }), 404

    if recipe_cat.owner != user.id:
        return jsonify({
            "errors": [
                "Trying to move a recipe to a category that does not belong to you"
            ]
        }), 403
    ''' check whether the new name does not belong to any other recipe by
        the same user in the same category '''
    recipe_exists = models.Recipe.query.filter_by(
        name=format_data(recipe_data.get("name")),
        owner=user.id,
        category_id=recipe_data.get("category")).first()

    if recipe_exists and recipe_exists.id != recipe_id:
        return jsonify({
            "errors": [
                "A recipe with the same name, by the same user already exists in the same category"
            ],
            "existing_recipe":
            recipe_exists.recipe_details
        }), 400

    # edit the recipe
    recipe.edit_recipe(recipe_data)

    return jsonify({
        "message": "Successfully edited recipe",
        "recipe": recipe.recipe_details
    }), 200


@app.route(f"{BASE_URL}recipes/<int:recipe_id>", methods=["PATCH"])
@auth_token_required
@user_must_own_recipe
def publish_recipe(user, recipe, recipe_id):
    """ Publishes or un publishes a recipe """
    # publish the recipe
    recipe.privacy = 0
    db.session.commit()
    return jsonify({
        "message": "Published recipe",
        "recipe": recipe.recipe_details
    })


@app.route(f"{BASE_URL}recipes/<int:recipe_id>", methods=["DELETE"])
@auth_token_required
@user_must_own_recipe
def delete_recipe(user, recipe, recipe_id):
    """ Deletes a single recipe """
    recipe.delete_recipe()
    return jsonify({"message": "Successfully deleted a recipe"})


@app.route(f"{BASE_URL}recipes/", methods=["GET"])
@auth_token_required
def get_all_user_recipes(user):
    """ Gets user recipes """
    return jsonify({
        "recipes": [recipe.recipe_details for recipe in user.recipes]
    }), 200


@app.route(f"{BASE_URL}recipes/<int:recipe_id>", methods=["GET"])
@auth_token_required
def get_recipe(user, recipe_id):
    """ Gets a single recipe """
    recipe = user.recipes.filter_by(id=recipe_id).first()

    if not recipe:
        return jsonify({
            "errors": ["the recipe you are trying to look for does not exist"]
        })

    return jsonify({
        "recipe": recipe.recipe_details,
        "message": "Recipe exists"
    }), 200


# user end points
@app.route(f"{BASE_URL}users/", methods=["PUT"])
@json_data_required
@auth_token_required
def edit_user_details(user):
    """ Updates user details """
    # validate user data
    user_data = request.get_json()
    edit_errors = ValidateUser.validate_user_on_reg(user_data, action="edit")

    if edit_errors:
        return jsonify({"errors": edit_errors}), 400

    # check whether email user is changing to is already taken
    email_in_use = models.User.query.filter_by(
        email=user_data["email"]).first()

    if email_in_use and email_in_use.id != user.id:
        return jsonify({
            "errors":
            [f"The email \'{user_data['email']}\' is already in use"]
        }), 400

    user.email = user_data.get("email")
    user.firstname = user_data.get("firstname")
    user.lastname = user_data.get("lastname")

    db.session.commit()
    return jsonify({
        "message": "All changes where applied successfully"
    }), 200, {
        "Location": user.user_details["url"]
    }


@app.route(f"{BASE_URL}users/", methods=["PATCH"])
@json_data_required
@auth_token_required
def change_user_password(user):
    """ Changes a user password """
    # validate sent data
    password_errors = ValidateUser.validate_password_data(request.get_json())

    if password_errors:
        return jsonify({"errors": password_errors}), 400

    if not user.verify_password(request.get_json().get("current_password")):
        return jsonify({
            "errors": ["The current password supplied is wrong"]
        }), 403

    user.set_password(request.get_json().get("new_password"))
    db.session.commit()

    # change the password if no error has occurred
    return jsonify({"message": "Password Changed Successfully"}), 200


@app.route(f"{BASE_URL}users/", methods=["GET"])
def get_all_registered_users():
    """ Gets all the registered users """
    users = models.User.query.all()
    if not users:
        return jsonify({"errors": ["No user found"]}), 404

    return jsonify({
        "users": [current_user.user_details for current_user in users]
    }), 200


@app.route(f"{BASE_URL}users/<id>/", methods=["GET"])
def get_user(id):
    """ Gets user details """
    user_id = Secure.decrypt_user_id(id)
    if user_id:
        user = models.User.query.filter_by(id=user_id).first_or_404()
        return jsonify({"data": user.user_details})
    abort(400)


# search end point
@app.route(f"{BASE_URL}search")
def search():
    """ Provides functionality for searching for a recipes, categories and registered users"""
    if not request.args:
        return jsonify({
            "errors": [
                "Check that you have supplied all the required data and try again"
            ]
        }), 400

    if "q" not in request.args:
        return jsonify({
            "errors":
            ["Check that you have supplied the search term and try again"]
        }), 400

    search_term = request.args.get("q")
    search_terms = str(search_term).strip().split()

    if not search_terms:
        return jsonify({"errors": ["Search term is empty"]}), 400

    user_conditions = [
        models.User.firstname.like(f"%{term}%") for term in search_terms
    ] + [models.User.lastname.like(f"%{term}%") for term in search_terms
        ] + [models.User.email.like(f"%{term}%") for term in search_terms]
    recipe_conditions = [
        models.Recipe.name.like(f"%{term}%") for term in search_terms
    ] + [models.Recipe.steps.like(f"%{term}%") for term in search_terms] + [
        models.Recipe.ingredients.like(f"%{term}%") for term in search_terms
    ]
    category_conditions = [
        models.RecipeCategory.name.like(f"%{term}%") for term in search_terms
    ]

    page = int(request.args.get("page", 1))
    per_page = int(
        request.args.get("per_page", app.config.get("ITEMS_PER_PAGE")))
    max_per_page = app.config.get("MAX_ITEMS_PER_PAGE")
    if per_page > max_per_page:
        per_page = max_per_page

    users = models.User.query.filter(or_(*user_conditions)).paginate(
        page, per_page, False)
    recipes = models.Recipe.query.filter(or_(*recipe_conditions)).paginate(
        page, per_page, False)
    categories = models.RecipeCategory.query.filter(
        or_(*category_conditions)).paginate(page, per_page, False)

    response_body = {
        "users": [each_user.user_details for each_user in users.items],
        "recipes":
        [each_recipe.recipe_details for each_recipe in recipes.items],
        "categories":
        [each_cat.recipe_cat_details for each_cat in categories.items],
        "users_count":
        users.total,
        "recipes_count":
        recipes.total,
        "categories_count":
        categories.total,
        "total_results":
        users.total + recipes.total + categories.total,
        "search_term":
        search_term
    }
    if page > 1:
        response_body["previous_page"] = page - 1

    return jsonify(response_body), 200
