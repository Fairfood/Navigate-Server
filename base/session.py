from asgiref.local import Local

_active = Local()


def set_to_local(key, value):
    """Sets attribute to Thread Local Storage."""
    setattr(_active, key, value)
    return True


def get_from_local(key, default=None):
    """Gets attribute from Thread Local Storage."""
    return getattr(_active, key, default)


def get_current_user():
    """Returns the currently authenticated user when called while processing an
    API.

    Otherwise, returns None.
    """
    from django.contrib.auth import get_user_model

    UserModel = get_user_model()

    user = get_from_local("user", None)
    current_user = UserModel.objects.filter(
        id=get_from_local("user_id")
    ).first()
    if user and user == current_user:
        return user
    user = current_user
    set_to_local("user", user)
    return user


def get_current_entity():
    """Returns the currently authenticated entity when called while processing
    an API.

    Otherwise, returns None.
    """
    from iam.nodes import Node

    entity = get_from_local("node", None)
    current_entity = Node.objects.filter(
        id=get_from_local("node_id")
    ).first()
    if entity and entity == current_entity:
        return entity
    entity = current_entity
    set_to_local("node", entity)
    return entity
