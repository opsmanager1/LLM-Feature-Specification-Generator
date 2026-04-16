from sqladmin import ModelView

from app.modules.auth.models import RefreshToken, User
from app.modules.feature_spec.models import FeatureSpecRun, PromptTemplate


class UserAdmin(ModelView, model=User):
    name = "User"
    name_plural = "Users"
    icon = "fa-solid fa-user"

    column_list = [
        User.id,
        User.username,
        User.email,
        User.is_active,
        User.is_superuser,
        User.is_verified,
        User.created_at,
    ]
    column_searchable_list = [User.username, User.email]
    column_filters = [User.is_active, User.is_superuser, User.is_verified, User.created_at]
    column_sortable_list = [User.id, User.username, User.email, User.created_at]

    column_exclude_list = [User.hashed_password]
    form_excluded_columns = [User.hashed_password, User.created_at]
    can_create = False
    can_delete = False


class RefreshTokenAdmin(ModelView, model=RefreshToken):
    name = "Refresh Token"
    name_plural = "Refresh Tokens"
    icon = "fa-solid fa-key"

    column_list = [
        RefreshToken.id,
        RefreshToken.user_id,
        RefreshToken.expires_at,
        RefreshToken.created_at,
        RefreshToken.revoked_at,
    ]
    column_searchable_list = [RefreshToken.user_id]
    column_filters = [RefreshToken.expires_at, RefreshToken.created_at, RefreshToken.revoked_at]
    column_sortable_list = [RefreshToken.id, RefreshToken.user_id, RefreshToken.expires_at]

    column_exclude_list = [RefreshToken.token_hash]
    form_excluded_columns = [RefreshToken.token_hash, RefreshToken.created_at]
    can_create = False
    can_edit = False


class PromptTemplateAdmin(ModelView, model=PromptTemplate):
    name = "Prompt Template"
    name_plural = "Prompt Templates"
    icon = "fa-solid fa-file-lines"

    column_list = [
        PromptTemplate.id,
        PromptTemplate.is_active,
        PromptTemplate.updated_at,
        PromptTemplate.feature_to_feature_summary,
    ]
    column_searchable_list = [PromptTemplate.feature_to_feature_summary]
    column_filters = [PromptTemplate.is_active, PromptTemplate.updated_at]
    column_sortable_list = [PromptTemplate.id, PromptTemplate.updated_at]

    can_create = False
    can_delete = False


class FeatureSpecRunAdmin(ModelView, model=FeatureSpecRun):
    name = "Feature Spec Run"
    name_plural = "Feature Spec Runs"
    icon = "fa-solid fa-wand-magic-sparkles"

    column_list = [
        FeatureSpecRun.id,
        FeatureSpecRun.user_id,
        FeatureSpecRun.status,
        FeatureSpecRun.feature_idea,
        FeatureSpecRun.created_at,
        FeatureSpecRun.updated_at,
    ]
    column_searchable_list = [FeatureSpecRun.feature_idea, FeatureSpecRun.status]
    column_filters = [FeatureSpecRun.status, FeatureSpecRun.created_at, FeatureSpecRun.updated_at]
    column_sortable_list = [
        FeatureSpecRun.id,
        FeatureSpecRun.user_id,
        FeatureSpecRun.status,
        FeatureSpecRun.created_at,
    ]

    can_create = False
    can_delete = False
