import time
import allure
import pytest

from unittest import TestCase
from ddt import ddt, data, unpack

from utils.ConfigureProperties import ConfigureProperties
from utils.ManageFiles import ManageFiles
from utils.OpenBrowser import OpenBrowser
from utils.ScreenShot import ScreenShot
from helpers.data_processing.DataFormatter import DataFormatter
from helpers.elements.ButtonsClick import ButtonsClick
from helpers.data_processing.UserData import UserData
from pages.homepage.GuestView import GuestView
from pages.homepage.Home import Home
from pages.homepage.SignIn import SignIn
from pages.profile_settings.Emails import Emails
from pages.profile_settings.PublicProfile import PublicProfile
from pages.repository.Creation import Creation
from pages.repository.General import General
from pages.search.SearchResults import SearchResults
from pages.stars_list.View import View
from pages.stars_list.ListProperties import ListProperties


@allure.severity(allure.severity_level.NORMAL)
@ddt
class TestGitHub(TestCase):
    manage_files = ManageFiles()

    @classmethod
    def setUpClass(cls):
        cls.driver = OpenBrowser.create_driver()
        cls.properties = ConfigureProperties.get_properties("app-config.properties")
        cls.manage_files.read_from_csv("constants", "dictionary")
        cls.home = Home(cls.driver)
        cls.public_profile = PublicProfile(cls.driver)
        cls.screenshot = ScreenShot()
        cls.repository_general = General(cls.driver)
        cls.stars_list_view = View(cls.driver)
        cls.user_data = UserData()
        cls.buttons_click = ButtonsClick(cls.driver)
        cls.list_properties = ListProperties(cls.driver)
        cls.search_results = SearchResults(cls.driver)
        cls.sign_in = SignIn(cls.driver)
        cls.guest_view = GuestView(cls.driver)

    @allure.title("Signing the user into GitHub")
    @allure.description("A test for signing the user into GitHub website successfully using securely store credentials")
    @pytest.mark.dependency(name="sign_in")
    @allure.severity(allure.severity_level.BLOCKER)
    def test_a_sign_in(self):
        self.driver.get(self.manage_files.get_constant_value("WEBSITE"))
        self.guest_view.click_on_header_menu("Sign in")
        user_email = self.properties["EMAIL"].data
        self.sign_in.enter_credentials("login_field", user_email)
        self.sign_in.enter_credentials("password", self.properties["PASSWORD"].data)
        self.sign_in.click_on_signin_button("Sign in")
        self.sign_in.do_manual_verification(self.manage_files.get_constant_value("WEBSITE"))
        self.home.click_on_profile("avatar-small")
        self.home.select_from_dropdown_list("Settings")
        self.public_profile.click_on_account_menu("Access settings", "Emails")
        emails = Emails(self.driver)
        actual_email = emails.get_account_email(user_email)
        user_name = emails.get_account_name()
        self.user_data.set_value("user_name", user_name)
        self.assertEqual(user_email, actual_email)
        pass

    @allure.title("Changing the user profile image")
    @allure.description("A test for changing the user profile image and validating it is successfully updated")
    @pytest.mark.dependency(name="profile_image")
    @data(*manage_files.read_from_csv("input-data", "unpack"))
    @unpack
    def test_b_profile_image(self, test_case_id, repository_name, repository_description, list_name,
                             list_description, new_list_name, search_term):
        self.user_data.set_data(test_case_id, repository_name, repository_description, list_name,
                                list_description, new_list_name, search_term)
        self.public_profile.reset_tries_count()
        self.public_profile.click_on_account_menu("Profile settings", "Public profile")
        upload_result = None
        time.sleep(5)
        while upload_result is None and self.public_profile.get_tries_count() < 2:
            self.screenshot.take_screenshot(
                self.manage_files.get_constant_value("PROFILE_IMAGE_BEFORE") + "_" +
                self.user_data.get_value("test_case_id") + "_" + str(self.public_profile.get_tries_count()), "png")
            self.screenshot.attach_image_to_allure()
            self.public_profile.click_on_edit_profile("avatar rounded-2 avatar-user")
            self.public_profile.upload_profile_image("avatar-image-" + self.user_data.get_value("test_case_id"), "jpg")
            self.public_profile.submit_image()
            upload_result = self.public_profile.check_action_image_alert("profile picture has been updated")
        self.screenshot.take_screenshot(
            self.manage_files.get_constant_value("PROFILE_IMAGE_AFTER") + "_" +
            self.user_data.get_value("test_case_id"), "png")
        self.screenshot.attach_image_to_allure()
        self.assertTrue(upload_result)
        pass

    @allure.title("Creating a public repository")
    @allure.description("A test for creating a repository with a public visibility and a description")
    @pytest.mark.dependency(name="create_repository")
    @data(*manage_files.read_from_csv("input-data", "unpack"))
    @unpack
    def test_c_create_repository(self, test_case_id, repository_name, repository_description, list_name,
                                 list_description, new_list_name, search_term):
        self.user_data.set_data(test_case_id, repository_name, repository_description, list_name,
                                list_description, new_list_name, search_term)
        self.home.click_on_website_icon(self.manage_files.get_constant_value("WEBSITE"))
        self.home.determine_repository_visibility("public", False)
        self.home.click_on_action_button("Create a new repository")
        repository_creation = Creation(self.driver)
        exp_repo_name = self.user_data.get_value("repository_name")
        repository_creation.fill_fields_with_data(exp_repo_name, "repository_name")
        repository_creation.fill_fields_with_data(self.user_data.get_value("repository_description"),
                                                  "repository_description")
        repository_creation.manage_visibility_option("public", True)
        time.sleep(5)
        repository_creation.click_on_create_button("Create repository")
        actual_repo_name = self.repository_general.get_repository_name(exp_repo_name)
        self.assertEqual(exp_repo_name, actual_repo_name)
        pass

    @allure.title("Configuring the repository visibility")
    @allure.description("A test for changing the repository visibility setting from public to private")
    @pytest.mark.dependency(name="repository_settings", depends=["create_repository"])
    def test_d_repository_settings(self):
        exp_value = "private"
        self.repository_general.click_on_settings("settings-tab")
        self.repository_general.click_on_repository_config("Change visibility")
        self.repository_general.click_on_dropdown_option(exp_value)
        index = 0
        while index < 3:
            self.repository_general.click_on_confirmation_button("Button-label")
            index += 1
        actual_value = self.repository_general.get_visibility_value(exp_value)
        self.assertEqual(exp_value, actual_value)
        pass

    @allure.title("Un/starring the repository")
    @allure.description("A test for marking the repository with a star and then removing it")
    @pytest.mark.dependency(name="repository_star", depends=["create_repository"])
    @data(*manage_files.read_from_csv("input-data", "unpack"))
    @unpack
    def test_e_repository_star(self, test_case_id, repository_name, repository_description, list_name,
                               list_description, new_list_name, search_term):
        self.user_data.set_data(test_case_id, repository_name, repository_description, list_name,
                                list_description, new_list_name, search_term)
        self.home.click_on_profile("avatar-small")
        self.home.select_from_dropdown_list("Your stars")
        stars_before = self.stars_list_view.get_stars_number()
        self.stars_list_view.click_on_tab("Repositories")
        self.stars_list_view.star_repository(
            self.user_data.get_value("user_name"), self.user_data.get_value("repository_name"), "Star this repository"
        )
        self.driver.refresh()
        is_starred = self.repository_general.check_repository_star()
        self.assertTrue(is_starred)
        self.stars_list_view.click_on_tab("Stars")
        stars_after = self.stars_list_view.get_stars_number()
        self.assertEqual(stars_before + 1, stars_after)

        self.repository_general.click_on_repository_star("Unstar this repository", "List Star")
        self.driver.refresh()
        self.driver.refresh()  # first one alone results in a 500 page not found
        stars_after = self.stars_list_view.get_stars_number()
        self.assertEqual(stars_before, stars_after)
        pass

    @allure.title("Creating a stars list")
    @allure.description("A test for creating a stars list with a name and description")
    @pytest.mark.dependency(name="list_creation")
    @data(*manage_files.read_from_csv("input-data", "unpack"))
    @unpack
    def test_f_list_creation(self, test_case_id, repository_name, repository_description, list_name,
                             list_description, new_list_name, search_term):
        self.user_data.set_data(test_case_id, repository_name, repository_description, list_name,
                                list_description, new_list_name, search_term)
        self.home.scroll_to_the_top()
        self.home.click_on_profile("avatar-small")
        self.home.select_from_dropdown_list("Your stars")
        lists_before = self.stars_list_view.get_lists_number() + 1
        self.stars_list_view.click_on_create_list()
        exp_name = self.user_data.get_value("list_name")
        exp_description = self.user_data.get_value("list_description")
        self.list_properties.fill_list_name(exp_name)
        self.list_properties.fill_list_description(exp_description)
        self.list_properties.click_on_list_action("Button-label", "Create")
        self.list_properties.check_action_completion("Create list")
        self.buttons_click.click_hyperlinked_buttons("Stars")
        time.sleep(10)
        self.driver.refresh()
        lists_after = self.stars_list_view.get_lists_number()
        self.assertEqual(lists_before, lists_after)
        pass

    @allure.title("Renaming the stars list")
    @allure.description("A test for renaming the stars list by editing the list name")
    @pytest.mark.dependency(name="list_renaming", depends=["list_creation"])
    @data(*manage_files.read_from_csv("input-data", "unpack"))
    @unpack
    def test_g_list_renaming(self, test_case_id, repository_name, repository_description, list_name,
                             list_description, new_list_name, search_term):
        self.user_data.set_data(test_case_id, repository_name, repository_description, list_name,
                                list_description, new_list_name, search_term)
        self.buttons_click.click_hyperlinked_buttons("Stars")
        self.list_properties.click_on_user_list(self.user_data.get_value('user_name'),
                                                self.user_data.get_value('list_name'))
        self.list_properties.click_on_edit_list()
        self.list_properties.fill_list_name("")
        exp_name = self.user_data.get_value("new_list_name")
        self.list_properties.fill_list_name(exp_name)
        time.sleep(10)
        self.list_properties.click_on_list_action("Button-content", "Save list")
        self.list_properties.check_action_completion("Edit list")
        actual_name = self.list_properties.get_list_name()
        self.assertEqual(exp_name, actual_name)
        pass

    @allure.title("Searching for a term")
    @allure.description("A test for searching for a specific term and getting the results that match into a csv file")
    @pytest.mark.dependency(name="search_repositories")
    @data(*manage_files.read_from_csv("input-data", "unpack"))
    @unpack
    def test_h_search_repositories(self, test_case_id, repository_name, repository_description, list_name,
                                   list_description, new_list_name, search_term):
        self.user_data.set_data(test_case_id, repository_name, repository_description, list_name,
                                list_description, new_list_name, search_term)
        self.buttons_click.click_hyperlinked_buttons("Explore")
        search_term = self.user_data.get_value("search_term")
        self.search_results.search_for_term(search_term)
        self.search_results.hit_search()
        self.search_results.check_search_completion(search_term.capitalize())
        exp_result = self.search_results.star_valid_results(search_term, self.user_data.get_value("test_case_id"))
        actual_result = self.search_results.read_search_results_file(self.user_data.get_value("test_case_id"))
        self.assertEqual(exp_result, actual_result)
        pass

    @allure.title("Sorting the search results")
    @allure.description("A test for sorting the csv file that has the search results that matched the search term")
    @pytest.mark.dependency(name="list_sorting", depends=["search_repositories"])
    @data(*manage_files.read_from_csv("input-data", "unpack"))
    @unpack
    def test_i_list_sorting(self, test_case_id, repository_name, repository_description, list_name,
                            list_description, new_list_name, search_term):
        self.user_data.set_data(test_case_id, repository_name, repository_description, list_name,
                                list_description, new_list_name, search_term)
        exp_result = self.search_results.get_stars_list(self.user_data.get_value("test_case_id"))
        actual_result = DataFormatter.sort_list_by_stars(exp_result, self.user_data.get_value("test_case_id"))
        self.assertEqual(len(exp_result), len(actual_result))
        pass

    @allure.title("Deleting the repository")
    @allure.description("A test for deleting the created repositories by going through the repository settings")
    @pytest.mark.dependency(name="delete_repository", depends=["create_repository"])
    @data(*manage_files.read_from_csv("input-data", "unpack"))
    @unpack
    def test_j_delete_repository(self, test_case_id, repository_name, repository_description, list_name,
                                 list_description, new_list_name, search_term):
        self.user_data.set_data(test_case_id, repository_name, repository_description, list_name,
                                list_description, new_list_name, search_term)
        repo_action = "Delete this repository"
        repo_name = self.user_data.get_value("repository_name")
        get_expected = True
        count = 2
        while count > 0:
            count -= 1
            self.home.click_on_profile("avatar-small")
            self.home.select_from_dropdown_list("Your repositories")
            number_of_repos = self.stars_list_view.get_repositories_number()
            if get_expected:
                exp_result = number_of_repos - 1
                self.stars_list_view.click_on_specific_repository(repo_name)
                self.repository_general.click_on_settings("settings-tab")
                self.repository_general.click_on_repository_config(repo_action)
                confirmation_term = self.repository_general.get_confirmation_term(repo_name)
                self.repository_general.write_on_text_box(confirmation_term)
                action_hyperlink = "/" + self.user_data.get_value("user_name") + "/" + \
                                   self.user_data.get_value("repository_name")
                self.repository_general.click_on_delete_confirmation(action_hyperlink)
                get_expected = False
        self.assertEqual(exp_result, number_of_repos)
        pass

    @allure.title("Removing the user profile image")
    @allure.description("A test for removing the user profile image successfully")
    @pytest.mark.dependency(name="remove_profile_image", depends=["profile_image"])
    def test_k_remove_profile_image(self):
        self.home.click_on_profile("avatar-small")
        self.home.select_from_dropdown_list("Settings")
        self.public_profile.click_on_account_menu("Profile settings", "Public profile")
        self.public_profile.click_on_edit_profile("avatar rounded-2 avatar-user")
        self.public_profile.click_on_remove_image()
        self.public_profile.accept_alert_if_exist()
        remove_result = self.public_profile.check_action_image_alert("profile picture has been reset")
        self.assertTrue(remove_result)
        pass

    @allure.title("Deleting the stars list")
    @allure.description("A test for deleting the stars list by going through the edit settings")
    @pytest.mark.dependency(name="delete_list", depends=["list_creation"])
    @data(*manage_files.read_from_csv("input-data", "unpack"))
    @unpack
    def test_l_delete_list(self, test_case_id, repository_name, repository_description, list_name,
                           list_description, new_list_name, search_term):
        self.user_data.set_data(test_case_id, repository_name, repository_description, list_name,
                                list_description, new_list_name, search_term)
        self.home.click_on_profile("avatar-small")
        self.home.select_from_dropdown_list("Your stars")
        lists_before = self.stars_list_view.get_lists_number() - 1
        self.list_properties.click_on_user_list(self.user_data.get_value('user_name'),
                                                self.user_data.get_value('new_list_name'))
        self.list_properties.click_on_edit_list()
        time.sleep(10)
        self.list_properties.click_on_list_action("Button-content", "Delete list")
        time.sleep(10)
        self.list_properties.confirm_deletion()
        self.list_properties.check_action_completion("Edit list")
        lists_after = self.stars_list_view.get_lists_number()
        self.assertEqual(lists_before, lists_after)
        pass

    @allure.title("Signing out the user")
    @allure.description("A test for signing the user out and validating the user is on the guest view page")
    @pytest.mark.dependency(name="sign_out", depends=["sign_in"])
    def test_m_sign_out(self):
        self.home.click_on_profile("avatar-small")
        self.home.click_on_action_button("Sign out")
        sign_in_exist = self.guest_view.check_sign_in_button("Sign in")
        self.assertTrue(sign_in_exist)
        pass

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()
        cls.driver.quit()
