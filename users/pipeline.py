from api.tasks import process_avatar_async

def get_avatar(backend, response, user=None, *args, **kwargs):
    if backend.name == 'google-oauth2':
        picture = response.get('picture')
        if picture:
            process_avatar_async.delay(user.id, picture)
    elif backend.name == 'github':
        avatar_url = response.get('avatar_url')
        if avatar_url:
            process_avatar_async.delay(user.id, avatar_url)