from django.contrib import admin


class ReadOnlyFieldsAdmin(admin.ModelAdmin):
    readonly_fields: tuple = (
        'id',
        'created_at',
        'updated_at',
    )