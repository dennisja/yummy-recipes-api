from tests import ApiBasicsTestCase


class SearchTestCases(ApiBasicsTestCase):
    def test_can_search_recipes_users_and_categories(self):
        """ Test if can search for recipes, recipe categories and users """
        # login and register two users
        login_responses = [
            self.register_and_login_user(),
            self.register_and_login_user(self.user_details2,
                                         self.login_details2)
        ]
        login_tokens = [
            self.get_token_from_response(login_response)
            for login_response in login_responses
        ]
        # create some recipe categories
        category_reponses = [
            self.create_recipe_category(cat, login_tokens[0])
            for cat in self.sample_categories
        ]
        # create some recipes
        recipe_responses = [
            self.create_recipe(recipe, login_tokens[0])
            for recipe in self.sample_recipes
        ]

        # test to see if search is successful
        response = self.test_client().get(
            "/yummy/api/v1.0/search?q=a&page=1",
            headers={
                "x-access-token": login_tokens[0]
            })
        self.assertEqual(response.status_code, 200)
        self.assertIn("recipes", response.data.decode())
        self.assertIn("recipe_categories", response.data.decode())
        self.assertIn("users", response.data.decode())
        self.assertIn(self.user_details1["email"], response.data.decode())
        self.assertIn(self.sample_categories[0]["cat_name"],
                      response.data.decode())
        self.assertIn(self.sample_recipes[0]["name"], response.data.decode())

    def test_search_fails_when_q_param_is_missing(self):
        """ Test if search fails with missing q param """
        # login and register two users
        login_responses = [
            self.register_and_login_user(),
            self.register_and_login_user(self.user_details2,
                                         self.login_details2)
        ]
        login_tokens = [
            self.get_token_from_response(login_response)
            for login_response in login_responses
        ]
        # create some recipe categories
        category_reponses = [
            self.create_recipe_category(cat, login_tokens[0])
            for cat in self.sample_categories
        ]
        # create some recipes
        recipe_responses = [
            self.create_recipe(recipe, login_tokens[0])
            for recipe in self.sample_recipes
        ]

        # test to see if search is successful
        response = self.test_client().get("/yummy/api/v1.0/search?page=1", headers={
            "x-access-token":login_tokens[0]
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Check that you have supplied the search term and try again",
            response.data.decode())

    def test_search_fails_when_all_get_param_are_missing(self):
        """ Test if search fails if all parameters in the query string are missing """
        # login and register two users
        login_responses = [
            self.register_and_login_user(),
            self.register_and_login_user(self.user_details2,
                                         self.login_details2)
        ]
        login_tokens = [
            self.get_token_from_response(login_response)
            for login_response in login_responses
        ]
        # create some recipe categories
        category_reponses = [
            self.create_recipe_category(cat, login_tokens[0])
            for cat in self.sample_categories
        ]
        # create some recipes
        recipe_responses = [
            self.create_recipe(recipe, login_tokens[0])
            for recipe in self.sample_recipes
        ]

        # test to see if search is successful
        response = self.test_client().get("/yummy/api/v1.0/search", headers={
            "x-access-token": login_tokens[0]
        })
        self.assertEqual(response.status_code, 400)
        self.assertIn(
            "Check that you have supplied all the required data and try again",
            response.data.decode())
