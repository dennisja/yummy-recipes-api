""" This is the test recipes module
It has tests for testing functionality of recipes in the api
"""
import json

from tests import ApiBasicsTestCase


class RecipeTestCases(ApiBasicsTestCase):
    """ This class has tests for testing recipe functionality """

    def test_can_add_recipe(self):
        """ confirms that a user can add a recipe """
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # add recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # add recipe to a category
        response = self.create_recipe(self.sample_recipes[0], login_token)
        self.assertEqual(response.status_code, 201)
        self.assertIn("Successfully added recipe", response.data.decode())
        self.assertIn(self.sample_recipes[0]["steps"], response.data.decode())

    def test_cant_add_recipe_in_a_category_that_doesnot_exist(self):
        """ tests that a user cannot add a recipe in a category that doesnot exist """
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # add recipe to a category that does not exist
        response = self.create_recipe(self.sample_recipes[0], login_token)
        self.assertEqual(response.status_code, 404)
        self.assertIn(
            "Trying to add a recipe to a category that does not exist",
            response.data.decode())

    def test_cant_add_recipe_to_a_category_that_belongs_to_another_user(self):
        """ tests that a user cant add categories to a category that belongs to another user"""
        # register and login two users
        login_responses = [
            self.register_and_login_user(),
            self.register_and_login_user(self.user_details2,
                                         self.login_details2)
        ]
        login_tokens = [
            self.get_token_from_response(login_response)
            for login_response in login_responses
        ]

        # create a recipe category using 1 user
        self.create_recipe_category(self.sample_categories[0], login_tokens[0])
        # add recipe to the same category using another user
        response = self.create_recipe(self.sample_recipes[0], login_tokens[1])
        # test if addition fails
        self.assertEqual(response.status_code, 403)
        self.assertIn(
            "Trying to add a recipe to a category that does not belong to you",
            response.data.decode())

    def test_cant_add_recipe_in_a_category_with_a_recipe_of_same_name(self):
        """ tests whether a user cant add recipe with the same name in the same category """
        # register and login a user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)

        # create a recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # add two recipes in the same category with the same name
        response_one = self.create_recipe(self.sample_recipes[0], login_token)
        response_two = self.create_recipe(self.sample_recipes[0], login_token)
        # test if this fails
        self.assertEqual(response_two.status_code, 400)
        self.assertIn(
            "A recipe with the same name, by the same user already exists in the same category",
            response_two.data.decode())

    def test_cant_add_recipe_when_invalid_data_is_supplied(self):
        """ tests recipe addition fails if invalid data is supplied """
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # try adding recipe with data that violates validation rules
        self.sample_recipes[0]["name"] = "p"
        self.sample_recipes[0]["steps"] = "no"
        response = self.create_recipe(self.sample_recipes[0], login_token)
        # test if the addition fails
        self.assertEqual(response.status_code, 400)
        self.assertIn("Name must be a minimum of 3 characters",
                      response.data.decode())
        self.assertIn("Steps must be a minimum of 10 characters",
                      response.data.decode())

    def test_can_edit_recipe(self):
        """ tests whether a user can successfully add a recipe """
        # login and register user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # create recipe
        self.create_recipe(self.sample_recipes[0], login_token)
        # edit the recipe
        self.kwargs["data"] = json.dumps(self.sample_recipes[1])
        self.kwargs["headers"] = {"x-access-token": login_token}
        edit_response = self.test_client().put("/yummy/api/v1.0/recipes/1",
                                               **self.kwargs)
        # test if recipe is edited
        self.assertEqual(edit_response.status_code, 200)
        self.assertIn("Successfully edited recipe",
                      edit_response.data.decode())
        self.assertIn(self.sample_recipes[1]["steps"],
                      edit_response.data.decode())

    def test_can_change_recipe_category_to_a_category_that_doesnot_exist(self):
        """ Ensures that a user cannot change recipe category to an id of the recipe category that doesnot exist"""
        # login and register user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # create recipe
        self.create_recipe(self.sample_recipes[0], login_token)
        # try to edit recipe and use a category that does not exist
        self.sample_recipes[1]["category"] = 4
        self.kwargs["data"] = json.dumps(self.sample_recipes[1])
        self.kwargs["headers"] = {"x-access-token": login_token}
        edit_response = self.test_client().put("/yummy/api/v1.0/recipes/1",
                                               **self.kwargs)
        # test if editing fails
        self.assertEqual(edit_response.status_code, 404)
        self.assertIn(
            "Trying to move a recipe to a category that does not exist",
            edit_response.data.decode())

    def test_can_edit_recipe_category_to_a_category_that_doesnot_belong_to_you(
            self):
        """ Ensures that user cannot change recipe category to a category id that belongs to another user"""
        # register and login two users
        login_responses = [
            self.register_and_login_user(),
            self.register_and_login_user(self.user_details2,
                                         self.login_details2)
        ]
        login_tokens = [
            self.get_token_from_response(login_response)
            for login_response in login_responses
        ]

        # create two recipe categories with different users
        categories = [
            self.create_recipe_category(self.sample_categories[0],
                                        login_tokens[0]),
            self.create_recipe_category(self.sample_categories[1],
                                        login_tokens[1])
        ]
        # create recipe with one user
        recipe_response = self.create_recipe(self.sample_recipes[0],
                                             login_tokens[0])
        # edit recipe specifying category of the other user
        self.kwargs["headers"] = {"x-access-token": login_tokens[0]}
        self.sample_recipes[1]["category"] = 2
        self.kwargs["data"] = json.dumps(self.sample_recipes[1])
        edit_response = self.test_client().put("/yummy/api/v1.0/recipes/1",
                                               **self.kwargs)
        # test whether editing fails
        self.assertTrue(edit_response.status_code, 400)
        self.assertIn(
            "Trying to move a recipe to a category that does not belong to you",
            edit_response.data.decode())

    def test_can_only_edit_recipe_that_belongs_to_you(self):
        """ ensures that a user can only edit a recipe belonging to him/her """
        # register and login two users
        login_responses = [
            self.register_and_login_user(),
            self.register_and_login_user(self.user_details2,
                                         self.login_details2)
        ]
        login_tokens = [
            self.get_token_from_response(login_response)
            for login_response in login_responses
        ]
        # create a recipe category using 1 user
        self.create_recipe_category(self.sample_categories[0], login_tokens[0])
        # create recipe in that category using the same user
        self.create_recipe(self.sample_recipes[0], login_tokens[0])
        # try editing the recipe using the other user
        self.kwargs["headers"] = {"x-access-token": login_tokens[1]}
        self.kwargs["data"] = json.dumps(self.sample_recipes[1])
        edit_response = self.test_client().put("/yummy/api/v1.0/recipes/1",
                                               **self.kwargs)
        # test whether addition fails
        self.assertTrue(edit_response.status_code, 400)
        self.assertIn(
            "You are trying to modify a recipe that does not belong to you",
            edit_response.data.decode())

    def test_can_only_edit_recipe_that_exists(self):
        """ ensures that a user can only edit a recipe that exists """
        # register and login a user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # try editing a recipe in thet category that doesnot exist
        self.kwargs["headers"] = {"x-access-token": login_token}
        self.kwargs["data"] = json.dumps(self.sample_recipes[0])
        edit_response = self.test_client().put("/yummy/api/v1.0/recipes/1",
                                               **self.kwargs)
        # test if editing fails
        self.assertTrue(edit_response.status_code, 200)
        self.assertIn("Trying to access a recipe that does not exist",
                      edit_response.data.decode())

    def test_can_publish_recipe(self):
        """ ensures that user can publish a recipe """
        # register and login a user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # create a recipe in the category
        self.create_recipe(self.sample_recipes[0], login_token)
        # publish the recipe
        publish_response = self.test_client().patch(
            "/yummy/api/v1.0/recipes/1?action=publish",
            headers={
                "x-access-token": login_token
            })
        # test whether recipe is published
        self.assertTrue(publish_response.status_code, 200)
        self.assertIn("Published recipe", publish_response.data.decode())

    def test_can_publish_another_users_recipe(self):
        """ Ensures that a user cannot publish another users recipe"""
        # login two users
        login_responses = [
            self.register_and_login_user(),
            self.register_and_login_user(self.user_details2,
                                         self.login_details2)
        ]
        login_tokens = [
            self.get_token_from_response(login_response)
            for login_response in login_responses
        ]

        # create category using one user
        self.create_recipe_category(self.sample_categories[0], login_tokens[0])
        # add recipe to the same category using the same user
        self.create_recipe(self.sample_recipes[0], login_tokens[0])
        # try publishing recipe using the other user
        publish_response = self.test_client().patch(
            "/yummy/api/v1.0/recipes/1",
            headers={
                "x-access-token": login_tokens[1]
            })
        # test if publishing fails
        self.assertTrue(publish_response.status_code, 400)
        self.assertIn(
            "You are trying to modify a recipe that does not belong to you",
            publish_response.data.decode())

    def test_can_delete_recipe(self):
        """ ensures that user can delete a recipe """
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create a recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # create a recipe
        self.create_recipe(self.sample_recipes[0], login_token)
        # delete the recipe
        delete_response = self.test_client().delete(
            "/yummy/api/v1.0/recipes/1",
            headers={
                "x-access-token": login_token
            })
        # test to see whether deletion succeeds
        self.assertTrue(delete_response.status_code, 200)
        self.assertIn("Successfully deleted a recipe",
                      delete_response.data.decode())

    def test_can_only_delete_own_recipes(self):
        """ Ensure that a user can only delete his own recipes"""
        # register and login two users
        login_responses = [
            self.register_and_login_user(),
            self.register_and_login_user(self.user_details2,
                                         self.login_details2)
        ]
        login_tokens = [
            self.get_token_from_response(login_response)
            for login_response in login_responses
        ]
        # create a recipe category using 1 user
        self.create_recipe_category(self.sample_categories[0], login_tokens[0])
        # create recipe in that category using the same user
        self.create_recipe(self.sample_recipes[0], login_tokens[0])
        # try deleting that recipe using the other user
        delete_response = self.test_client().delete(
            "/yummy/api/v1.0/recipes/1",
            headers={
                "x-access-token": login_tokens[1]
            })
        # test if deletion fails
        self.assertEqual(delete_response.status_code, 403)
        self.assertIn(
            "You are trying to modify a recipe that does not belong to you",
            delete_response.data.decode())

    def test_can_get_all_user_recipes(self):
        """ tests whether a user can fetch all recipes """
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create a recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # create recipes in that category
        recipe_responses = [
            self.create_recipe(recipe, login_token)
            for recipe in self.sample_recipes if recipe["category"] == "1"
        ]
        # access the recipes in that category
        response = self.test_client().get(
            "/yummy/api/v1.0/recipes/",
            headers={
                "x-access-token": login_token
            })
        # test to see if your recipes are fetched
        self.assertTrue(response.status_code == 200)
        self.assertIn("recipes", response.data.decode())
        self.assertIn(self.sample_recipes[0]["steps"], response.data.decode())

    def test_can_get_single_recipe(self):
        """ tests whether a user can get a single recipe """
        # register and login user
        login_response = self.register_and_login_user()
        login_token = self.get_token_from_response(login_response)
        # create a recipe category
        self.create_recipe_category(self.sample_categories[0], login_token)
        # create a recipe
        self.create_recipe(self.sample_recipes[0], login_token)
        # access the recipe
        response = self.test_client().get(
            "/yummy/api/v1.0/recipes/1",
            headers={
                "x-access-token": login_token
            })
        # test if recipe can be accessed
        self.assertEqual(response.status_code, 200)
        self.assertIn("Recipe exists", response.data.decode())
        self.assertIn(self.sample_recipes[0]["steps"], response.data.decode())
