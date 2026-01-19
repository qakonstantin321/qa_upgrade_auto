from src.main.ui.pages.base_page import BasePage


class EditProfilePage(BasePage):
    @property
    def edit_profile_panel_text(self):
        return self.page.get_by_text("✏️ Edit Profile")

    @property
    def save_changes_button(self):
        return self.page.get_by_role("button", name="💾 Save Changes")

    def name_input(self, name: str):
        return self.page.locator("input[placeholder='Enter new name']").fill(name)

    def url(self):
        return "/edit-profile"

    def edit_profile_name(self, name: str):
        self.name_input(name)
        self.save_changes_button.click()
        return self
