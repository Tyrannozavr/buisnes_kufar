from sqladmin import Admin




def setup_admin(app, engine):
    from app.api.admin.company import CompanyOfficialAdmin
    from app.api.admin.company import CompanyAdmin
    from app.api.admin.auth import UserAdmin, RegistrationTokenAdmin
    from app.api.admin.products import ProductAdmin
    admin = Admin(app, engine)

    # Регистрируем представления
    admin.add_view(UserAdmin)
    admin.add_view(RegistrationTokenAdmin)
    admin.add_view(CompanyAdmin)
    admin.add_view(CompanyOfficialAdmin)
    admin.add_view(ProductAdmin)

    return admin
