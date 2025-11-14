from scoreboard.models import CTFConfig

def ctf_config(request):
    """Context processor para tener el config del CTF disponible en todos los templates"""
    config = CTFConfig.get_config()
    return {
        'ctf_config': config,
        'ctf_name': config.name if config else 'CTF Platform',
    }
