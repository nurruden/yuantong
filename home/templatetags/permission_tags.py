from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """Lookup a key in a dictionary"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def has_edit_others_permission(permissions):
    """Check if user has edit_others permission (supports both edit_others and edit-others keys)"""
    if isinstance(permissions, dict):
        return permissions.get('edit_others', False) or permissions.get('edit-others', False)
    return False
