from sqladmin import Admin


def setup_admin(app, engine):
    from app.api.admin.company import CompanyOfficialAdmin
    from app.api.admin.company import CompanyAdmin
    from app.api.admin.auth import UserAdmin, RegistrationTokenAdmin, PasswordRecoveryCodeAdmin
    from app.api.admin.products import ProductAdmin
    from app.api.admin.announcements import AnnouncementAdmin
    from app.api.admin.chats import ChatAdmin, ChatParticipantAdmin
    from app.api.admin.messages import MessageAdmin
    # from app.api.admin.purchases import DealAdmin, DealItemAdmin, DealDocumentAdmin, DealChangeAdmin

    admin = Admin(app, engine)

    # Регистрируем представления
    admin.add_view(UserAdmin)
    admin.add_view(RegistrationTokenAdmin)
    admin.add_view(PasswordRecoveryCodeAdmin)
    admin.add_view(CompanyAdmin)
    admin.add_view(CompanyOfficialAdmin)
    admin.add_view(ProductAdmin)
    admin.add_view(AnnouncementAdmin)
    admin.add_view(ChatAdmin)
    admin.add_view(ChatParticipantAdmin)
    admin.add_view(MessageAdmin)
    
    # Добавляем представления для системы заказов
    # admin.add_view(DealAdmin)
    # admin.add_view(DealItemAdmin)
    # admin.add_view(DealDocumentAdmin)
    # admin.add_view(DealChangeAdmin)

    return admin
