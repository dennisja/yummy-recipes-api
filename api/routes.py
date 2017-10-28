from api import app, models, db
from api.helpers import Secure, TokenError, TokenExpiredError
from api.validator import ValidationError, ValidateUser, ValidateRecipeCategory as ValidateCat, ValidateRecipe
from api.decorators import auth_token_required, json_data_required, user_must_own_recipe
from flask import make_response, jsonify, abort, request, url_for
from itsdangerous import BadSignature


@app.route("/yummy/api/v1.0/auth/register/", methods=["POST"])
def register_user():
    """ Registers a yummy recipes user """
    if not request.get_json():
        abort(400)

    request_data = request.get_json()
    # validate the user
    validation_errors = ValidateUser.validate_user_on_reg(request_data)

    # check if errors occurred
    if validation_errors:
        return jsonify({"errors": validation_errors}), 422

    # check if user already exists
    existing_user = models.User.query.filter_by(email=request_data["email"]).first()
    if existing_user:
        return jsonify({"errors": [f"Email address \'{request_data['email']}\' already in use"]}), 422

    # register the user
    user = models.User(request_data["email"], request_data["firstname"],
                       request_data["lastname"], request_data["password"])
    user.save_user()

    return jsonify(
        {"messages": ["You have been successfully registered and you can now login"], "data": user.user_details}), 201


@app.route("/yummy/api/v1.0/auth/login/", methods=["POST"])
def login_user():
    auth_details = request.authorization
    # check whether authorization details are supplied
    if not auth_details or not "username" in auth_details or not "password" in auth_details:
        return jsonify({"errors": ["Missing login credentials"]}), 400
    # validate sent details
    validation_errors = ValidateUser.validate_user_login(auth_details)
    if validation_errors:
        return jsonify({"errors": validation_errors}), 401, {
            "WWW-Authenticate": "Basic realm='Invalid login credentials'"}

    # check if a user exists
    user = models.User.query.filter_by(email=auth_details["username"]).first()
    if not user:
        raise models.UserNotFoundError(f"Email '{auth_details['username']}' is not yet registered")

    # if user password is correct
    if user.verify_password(auth_details["password"]):
        access_token = Secure.generate_auth_token(user.id)
        return jsonify({"message": "Successfully logged in", "token": access_token}), 200
        # generate and return the token

    return jsonify({"errors": ["Invalid email and password combination"]}), 401, {
        "WWW-Authenticate": "Basic realm='Invalid email and password combination'"}


# recipe category end points
@app.route("/yummy/api/v1.0/recipe_categories/", methods=["POST"])
@json_data_required
@auth_token_required
def add_recipe_category(user):
    """ Adds a recipe category """
    # validate submitted recipe category details
    recipe_errors = ValidateCat.validate_recipe(request.json)

    if recipe_errors:
        return jsonify({"errors": recipe_errors}), 400

    # check whether a recipe category name by the same already exists
    existing_recipe = models.RecipeCategory.query.filter_by(name=request.json.get("cat_name"), owner=user.id).first()

    if existing_recipe:
        return jsonify({"errors": ["The Recipe Category you are trying to add already exists"]}), 400

    # create the recipe category
    recipe = models.RecipeCategory(request.json.get("cat_name"), user.id)
    recipe.save_recipe_cat()

    return jsonify({"message": "Successfully created recipe category", "recipe_cat": recipe.recipe_cat_details}), 201, {
        "Location": recipe.recipe_cat_details.get("url")}


@app.route("/yummy/api/v1.0/recipe_categories/<int:category_id>", methods=["PUT"])
@json_data_required
@auth_token_required
def edit_recipe_category(user, category_id):
    """ Edits a recipe category """
    recipe_cat_errors = ValidateCat.validate_recipe(request.json)
    if recipe_cat_errors:
        return jsonify({"errors": recipe_cat_errors}), 400

    recipe_cat = models.RecipeCategory.query.filter_by(id=category_id).first()

    if not recipe_cat:
        return jsonify({"errors": ["The recipe you are trying to edit does not exist"]}), 404

    if recipe_cat.owner != user.id:
        return jsonify({"errors": ["The recipe category you are trying to edit doesnot belong to you"]}), 403

    existing_recipe_cat = models.RecipeCategory.query.filter_by(name=request.json.get("cat_name"),
                                                                owner=user.id).first()

    if existing_recipe_cat and existing_recipe_cat.id != category_id:
        return jsonify({"errors": ["The new recipe category name you are trying to use already exists"]}), 400

    if request.json.get("cat_name") == recipe_cat.name:
        return jsonify({"message": "Recipe category name is similar to the previous. No changes where made"}), 200

    # edit the recipe
    recipe_cat.name = request.json.get("cat_name")
    db.session.commit()

    return jsonify({"message": "Successfully edited recipe category", "recipe_cat": recipe_cat.recipe_cat_details}), 200


@app.route("/yummy/api/v1.0/recipe_categories/<int:category_id>", methods=["DELETE"])
@auth_token_required
def delete_recipe_category(user, category_id):
    """ Deletes a recipe category """
    # look for the recipe category
    recipe_cat = models.RecipeCategory.query.filter_by(id=category_id).first()
    if not recipe_cat:
        return jsonify({"errors": ["The recipe you are trying to delete does not exist"]}), 404

    # check if the user trying to delete the recipe is the owner of the recipe category
    if recipe_cat.owner != user.id:
        return jsonify({"errors": ["The recipe category you are trying to delete does not belong to you"]}), 403

    # delete the recipe category and all its recipes
    recipe_cat.delete_recipe_cat()
    # TODO: come back to delete all recipes in a recipe category
    return jsonify({"message": "Recipe Category successfully deleted"}), 200


@app.route("/yummy/api/v1.0/recipe_categories/", methods=["GET"])
@auth_token_required
def get_all_user_recipe_categories(user):
    """ Gets all user recipe categories """
    user_cats = models.RecipeCategory.query.filter_by(owner=user.id).all()
    if not user_cats:
        return jsonify({"errors": ["You have not added any recipe categories yet"]}), 404

    return jsonify(
        {"message": "Recipe Categories exists", "recipe_cats": [category.recipe_cat_details for category in user_cats]})


@app.route("/yummy/api/v1.0/recipe_categories/<int:category_id>", methods=["GET"])
@auth_token_required
def get_recipe_category(user, category_id):
    """ Gets a recipe categories """
    recipe_cat = user.recipe_categories.filter_by(id=category_id).first()

    if not recipe_cat:
        return jsonify({"errors": ["The recipe cat you are trying to access does not exist."]}), 404

    return jsonify({"recipe_cat": recipe_cat.recipe_cat_details, "message": "Recipe category exists"}), 200


@app.route("/yummy/api/v1.0/recipe_categories/<int:category_id>/recipes/", methods=["GET"])
@auth_token_required
def get_all_recipes_in_a_category(user, category_id):
    """ Gets user recipes in a particular category """
    recipe_cat = user.recipe_categories.filter_by(id=category_id).first()
    if not recipe_cat:
        abort(404)
    recipes = recipe_cat.recipes
    return jsonify({"message": "Category exists", "recipes": [recipe.recipe_details for recipe in recipes]}), 200


# recipe end points
@app.route("/yummy/api/v1.0/recipes/", methods=["POST"])
@json_data_required
@auth_token_required
def add_recipe(user):
    """ Adds a recipe """
    # validate recipe data
    recipe_errors = ValidateRecipe.validate_recipe(request.json)
    if recipe_errors:
        return jsonify({"errors": recipe_errors}), 400

    # check if the supplied recipe category exists
    recipe_cat = models.RecipeCategory.query.filter_by(id=request.json.get("category")).first()
    if not recipe_cat:
        return jsonify({"errors": ["Trying to add a recipe to a category that does not exist"]}), 404

    if recipe_cat.owner != user.id:
        return jsonify({"errors": ["Trying to add a recipe to a category that does not belong to you"]}), 403

    # check if a recipe with the same name exists in the same category and by the same user
    recipe_exists = models.Recipe.query.filter_by(name=request.json.get("name"), owner=user.id,
                                                  category_id=request.json.get("category")).first()
    if recipe_exists:
        return jsonify(
            {"errors": ["A recipe with the same name, by the same user already exists in the same category"],
             "existing_recipe": recipe_exists.recipe_details}), 400

    # add the recipe
    recipe_data = request.json
    recipe = models.Recipe(recipe_data.get("name"), recipe_data.get("steps"), recipe_data.get("ingredients"),
                           recipe_data.get("category"), user.id)
    recipe.save_recipe()
    return jsonify({"message": "Successfully added recipe", "recipe": recipe.recipe_details}), 201, {
        "Location": recipe.recipe_details["url"]}


@app.route("/yummy/api/v1.0/recipes/<int:recipe_id>", methods=["PUT"])
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
    # check if recipe exists
    if not str(recipe_id).isnumeric():
        return jsonify({"errors": ["Invalid recipe Id"]}), 400

    if not recipe:
        abort(404)

    # validate submitted data
    recipe_errors = ValidateRecipe.validate_recipe(request.json)
    if recipe_errors:
        return jsonify({"errors": recipe_errors}), 400

    # check if the supplied recipe category exists
    recipe_cat = models.RecipeCategory.query.filter_by(id=request.json.get("category")).first()
    if not recipe_cat:
        return jsonify({"errors": ["Trying to move a recipe to a category that does not exist"]}), 404

    if recipe_cat.owner != user.id:
        return jsonify({"errors": ["Trying to move a recipe to a category that does not belong to you"]}), 403

    # check whether the new name does not belong to any other recipe by the same user in the same category
    recipe_exists = models.Recipe.query.filter_by(name=request.json.get("name"), owner=user.id,
                                                  category_id=request.json.get("category")).first()

    if recipe_exists and recipe_exists.id != recipe_id:
        return jsonify(
            {"errors": ["A recipe with the same name, by the same user already exists in the same category"],
             "existing_recipe": recipe_exists.recipe_details}), 400

    # edit the recipe
    recipe.edit_recipe(request.json)

    return jsonify({"message": "Successfully edited recipe", "recipe": recipe.recipe_details}), 200


@app.route("/yummy/api/v1.0/recipes/<int:recipe_id>", methods=["PATCH"])
@auth_token_required
@user_must_own_recipe
def publish_recipe(user, recipe, recipe_id):
    """ Publishes or un publishes a recipe """
    # publish the recipe
    recipe.privacy = 0
    db.session.commit()
    return jsonify({"message": "Published recipe", "recipe": recipe.recipe_details})


@app.route("/yummy/api/v1.0/recipes/<int:recipe_id>", methods=["DELETE"])
@auth_token_required
@user_must_own_recipe
def delete_recipe(user, recipe, recipe_id):
    """ Deletes a single recipe """
    recipe.delete_recipe()
    return jsonify({"message": "Successfully deleted a recipe"})


@app.route("/yummy/api/v1.0/recipes/", methods=["GET"])
@auth_token_required
def get_all_user_recipes(user):
    """ Gets user recipes """
    return jsonify({"recipes": [recipe.recipe_details for recipe in user.recipes]}), 200


@app.route("/yummy/api/v1.0/recipes/<int:recipe_id>", methods=["GET"])
@auth_token_required
def get_recipe(user, recipe_id):
    """ Gets a single recipe """
    recipe = user.recipes.filter_by(id=recipe_id).first()

    if not recipe:
        return jsonify({"errors": ["the recipe you are trying to look for does not exist"]})

    return jsonify({"recipe": recipe.recipe_details, "message": "Recipe exists"}), 200


# user end points
@app.route("/yummy/api/v1.0/users/", methods=["PUT"])
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
    email_in_use = models.User.query.filter_by(email=user_data["email"]).first()

    if email_in_use and email_in_use.id != user.id:
        return jsonify({"errors": [f"The email \'{user_data['email']}\' is already in use"]}), 400

    user.email = user_data.get("email")
    user.firstname = user_data.get("firstname")
    user.lastname = user_data.get("lastname")

    db.session.commit()
    return jsonify({"message": "All changes where applied successfully"}), 200, {"Location": user.user_details["url"]}


@app.route("/yummy/api/v1.0/users/", methods=["PATCH"])
@json_data_required
@auth_token_required
def change_user_password(user):
    """ Changes a user password """
    # validate sent data
    password_errors = ValidateUser.validate_password_data(request.json)

    if password_errors:
        return jsonify({"errors": password_errors}), 400

    if not user.verify_password(request.json.get("current_password")):
        return jsonify({"errors": ["The current password supplied is wrong"]}), 403

    user.set_password(request.json.get("new_password"))
    db.session.commit()

    # change the password if no error has occurred
    return jsonify({"message": "Password Changed Successfully"}), 200


@app.route("/yummy/api/v1.0/users/", methods=["GET"])
def get_all_registered_users():
    """ Gets all the registered users """
    users = models.User.query.all()
    if not users:
        return jsonify({"errors": ["No user found"]}), 404

    return jsonify({"users": [current_user.user_details for current_user in users]}), 200


@app.route("/yummy/api/v1.0/users/<id>/", methods=["GET"])
def get_user(id):
    """ Gets user details """
    user_id = Secure.decrypt_user_id(id)
    if user_id:
        user = models.User.query.filter_by(id=user_id).first_or_404()
        return jsonify({"data": user.user_details})
    abort(400)


# error handlers
@app.errorhandler(404)
def not_found_error(error):
    """ Handles errors arising from absence of a resource """
    return make_response(jsonify({"errors": ["Resource Not found"]}), 404)


@app.errorhandler(400)
def bad_request(error):
    """ Handles Bad Request Errors """
    return make_response(jsonify({"errors": ["Request not Understood"]}), 400)


@app.errorhandler(401)
def invalid_authentication_details(error):
    """ Handles Invalid Login credential details """
    return make_response(jsonify({"errors": ["Invalid Login Credentials"]}), 401)


@app.errorhandler(403)
def permission_denied(error):
    """ Handles errors resulting from insufficient permissions to perform a task """
    return make_response(jsonify({"errors": ["You do not have enough permissions to perform this task"]}), 403)


@app.errorhandler(ValidationError)
def handle_validation_failure(error):
    """ Handles failure of validation of sent data, in case some keys are missing """
    return make_response(jsonify({"errors": [error.args[0]]}), 400)


@app.errorhandler(BadSignature)
def handle_invalid_user_ids(error):
    return make_response(jsonify({"errors": ["Request not understood"]}), 400)


@app.errorhandler(models.UserNotFoundError)
def handle_user_not_found_error(error):
    return make_response(jsonify({"errors": [error.args[0]]}), 404)


# handle token errors
@app.errorhandler(TokenExpiredError)
def handle_token_expiration_errors(error):
    return make_response(jsonify({"errors": [error.args[0]]}), 401)


@app.errorhandler(TokenError)
def handle_invalid_token(error):
    return make_response(jsonify({"errors": [error.args[0]]}), 401)
