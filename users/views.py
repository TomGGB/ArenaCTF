from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import get_user_model

User = get_user_model()

@login_required
def profile(request):
    """Vista de perfil del usuario"""
    user = request.user
    
    if request.method == 'POST':
        # Obtener datos del formulario
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        
        # Actualizar datos
        user.first_name = first_name
        user.last_name = last_name
        
        # Cambiar contraseña si se proporcionó
        new_password = request.POST.get('new_password', '').strip()
        confirm_password = request.POST.get('confirm_password', '').strip()
        
        if new_password:
            if new_password == confirm_password:
                if len(new_password) >= 8:
                    user.set_password(new_password)
                    messages.success(request, 'Contraseña actualizada exitosamente. Por favor, inicia sesión nuevamente.')
                    user.save()
                    return redirect('login')
                else:
                    messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
                    return render(request, 'users/profile.html', {'user': user})
            else:
                messages.error(request, 'Las contraseñas no coinciden.')
                return render(request, 'users/profile.html', {'user': user})
        
        user.save()
        messages.success(request, 'Perfil actualizado exitosamente.')
        return redirect('users:profile')
    
    return render(request, 'users/profile.html', {'user': user})
