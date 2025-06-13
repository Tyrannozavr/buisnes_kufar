from sqladmin import Admin
from app.api.admin.admin import UserAdmin, RegistrationTokenAdmin, CompanyAdmin, CompanyOfficialAdmin


# class AdminView(ModelView, model=AdminModel):
#     name = "Admin"
#     icon = "fa-solid fa-user-shield"
#     column_list = [AdminModel.id, AdminModel.telegram_id, AdminModel.first_name, AdminModel.last_name, AdminModel.username]
#     column_searchable_list = [AdminModel.telegram_id, AdminModel.first_name, AdminModel.last_name, AdminModel.username]
#     column_filters = [AdminModel.is_active]
#     can_create = True
#     can_edit = True
#     can_delete = True
#     can_view_details = True



def setup_admin(app, engine):
    admin = Admin(app, engine)
    
    # Регистрируем представления
    admin.add_view(UserAdmin)
    admin.add_view(RegistrationTokenAdmin)
    admin.add_view(CompanyAdmin)
    admin.add_view(CompanyOfficialAdmin)
    
    return admin 