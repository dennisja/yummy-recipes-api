"""
This module has tests for RecipeCategories functionality in the api
"""
import json

from tests import ApiBasicsTestCase


class CategoryTestCases(ApiBasicsTestCase):
    """ This class has tests for recipe categories """

    def test_adding_recipe_category(self):
        """ Tests adding a recipe category """
        # register and login a user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Successfully created recipe category",
                      response.data.decode())

    def test_existing_recipe_category(self):
        """ tests whether a user cant add a category with the same name """
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        self.test_client().post("/yummy/api/v1.0/recipe_categories/",
                                **self.kwargs)
        again_response = self.test_client().post(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        self.assertEqual(again_response.status_code, 400)
        self.assertIn(
            "The Recipe Category you are trying to add already exists",
            again_response.data.decode())

    def test_invalid_data(self):
        """ tests whether a user cant add category if invalid data is sent """
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        self.sample_categories[0]["cat_name"] = "h"
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().post(
            "/yummy/api/v1.0/recipe_categories/", **self.kwargs)
        self.assertEqual(response.status_code, 400)
        self.assertIn("Category Name must be a minimum of 3 characters",
                      response.data.decode())

    def test_edit_recipe_category(self):
        """ tests if a user cant successfully edit a recipe category """
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        self.test_client().post("/yummy/api/v1.0/recipe_categories/",
                                **self.kwargs)

        # change category details
        self.sample_categories[0]["cat_name"] = "New Recipe Edited"
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn("Successfully edited recipe category",
                      edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 200)

    def test_edit_other_category(self):
        """ Register and login two users """
        login_responses = [
            self.register_and_login_user(),
            self.register_and_login_user(self.user_details2,
                                         self.login_details2)
        ]
        login_tokens = [
            self.get_token_from_response(login_response)
            for login_response in login_responses
        ]

        # create category using the first user
        self.kwargs["data"] = json.dumps({"cat_name": "This is new"})
        self.kwargs["headers"] = {"x-access-token": login_tokens[0]}
        self.test_client().post("/yummy/api/v1.0/recipe_categories/",
                                **self.kwargs)
        # try editing category details using the second user
        self.sample_categories[0]["cat_name"] = "New Recipe Edited"
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_tokens[1]}
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn(
            "The recipe category you are trying to modify does not belong to you",
            edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 403)

    def test_edit_onlogout(self):
        """ tests if a user can only edit a category if logged in """
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        self.test_client().post("/yummy/api/v1.0/recipe_categories/",
                                **self.kwargs)

        # change category name to the same name
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs.pop("headers")
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn("The access token is required",
                      edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 401)

    def test_different_names(self):
        """ tests if category isn't edited if new name is same as current name """
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        self.test_client().post("/yummy/api/v1.0/recipe_categories/",
                                **self.kwargs)

        # change category name to the same name
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn(
            "The new recipe category name you are trying to use already exists",
            edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 400)

    def test_absent_category(self):
        """ tests if a user cant add a category that already exists """
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        self.test_client().post("/yummy/api/v1.0/recipe_categories/",
                                **self.kwargs)

        # change category details
        self.sample_categories[0]["cat_name"] = "New Recipe Edited"
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        edit_response = self.test_client().put(
            "/yummy/api/v1.0/recipe_categories/2", **self.kwargs)
        self.assertIn(
            "The recipe category you are trying to modify does not exist",
            edit_response.data.decode())
        self.assertEqual(edit_response.status_code, 404)

    def test_delete_category(self):
        """ tests to see if a user can succesfully delete a category """
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create category
        self.kwargs["data"] = json.dumps(self.sample_categories[0])
        self.kwargs["headers"] = {"x-access-token": login_token}
        self.test_client().post("/yummy/api/v1.0/recipe_categories/",
                                **self.kwargs)

        # delete the category
        self.kwargs.pop("data")
        delete_response = self.test_client().delete(
            "/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertEqual(delete_response.status_code, 200)
        self.assertIn("Recipe Category successfully deleted",
                      delete_response.data.decode())

    def test_delete_other_category(self):
        """ test whether a user can only delete his/her own category """
        # register and login a user
        login_responses = [
            self.register_and_login_user(),
            self.register_and_login_user(self.user_details2,
                                         self.login_details2)
        ]
        login_tokens = [
            self.get_token_from_response(login_response)
            for login_response in login_responses
        ]

        # create category using the first user
        self.kwargs["data"] = json.dumps({"cat_name": "This is new"})
        self.kwargs["headers"] = {"x-access-token": login_tokens[0]}
        self.test_client().post("/yummy/api/v1.0/recipe_categories/",
                                **self.kwargs)
        # try deleting category  using the second user
        self.kwargs.pop("data")
        self.kwargs["headers"] = {"x-access-token": login_tokens[1]}
        delete_response = self.test_client().delete(
            "/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertIn(
            "The recipe category you are trying to modify does not belong to you",
            delete_response.data.decode())
        self.assertEqual(delete_response.status_code, 403)

    def test_delete_absent_category(self):
        """ tests whether a user cannot delete a category of another user"""
        # register and login a user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # delete a category that does not exist
        self.kwargs["headers"] = {"x-access-token": login_token}
        delete_response = self.test_client().delete(
            "/yummy/api/v1.0/recipe_categories/1", **self.kwargs)
        self.assertEqual(delete_response.status_code, 404)
        self.assertIn(
            "The recipe category you are trying to modify does not exist",
            delete_response.data.decode())

    def test_get_categories(self):
        """ tests whether a user can get his own categories """
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create some recipe categories
        responses = [
            self.create_recipe_category(recipe_cat, login_token)
            for recipe_cat in self.sample_categories
        ]

        # fetch all the categories
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().get("/yummy/api/v1.0/recipe_categories/",
                                          **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Recipe Categories exists", response.data.decode())

    def test_recipes_per_category(self):
        """ tests whether a user can get  all recipes in a category """
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create a recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)

        # add recipes to the recipe category
        add_recipe_responses = [
            self.create_recipe(recipe, login_token)
            for recipe in self.sample_recipes
        ]
        # fetch the recipes is the category
        self.kwargs["headers"] = {"x-access-token": login_token}
        response = self.test_client().get(
            "/yummy/api/v1.0/recipe_categories/1/recipes/", **self.kwargs)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Category exists", response.data.decode())
        self.assertIn(self.sample_recipes[0]["steps"], response.data.decode())

    def test_can_get_recipe_category(self):
        """ test whther a user can get a recipe category """
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create a recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        response = self.test_client().get(
            "/yummy/api/v1.0/recipe_categories/1",
            headers={
                "x-access-token": login_token
            })
        self.assertIn("Recipe category exists", response.data.decode())
        self.assertIn(self.sample_categories[0]["cat_name"],
                      response.data.decode())
        self.assertEqual(response.status_code, 200)
