import reflex as rx
from typing import Optional

class AuthState(rx.State):
    """Estado responsável pela autenticação e controle de acesso"""
    
    # Autenticação - Login único
    is_authenticated: bool = False
    login_email: str = ""
    login_password: str = ""
    login_error: str = ""
    
    # Credenciais válidas (login único)
    _valid_email: str = "evandrotorresmachado@gmail.com"
    _valid_password: str = "eva123"
    
    def set_login_email(self, email: str):
        self.login_email = email
        
    def set_login_password(self, password: str):
        self.login_password = password
        
    def attempt_login(self):
        """Tenta realizar login com as credenciais fornecidas"""
        if self.login_email == self._valid_email and self.login_password == self._valid_password:
            self.is_authenticated = True
            self.login_error = ""
            return rx.redirect("/")
        else:
            self.login_error = "Credenciais inválidas. Tente novamente."
            self.is_authenticated = False
            
    def logout(self):
        """Realiza logout do usuário"""
        self.is_authenticated = False
        self.login_email = ""
        self.login_password = ""
        self.login_error = ""
        return rx.redirect("/login")

    def check_auth(self):
        """Verifica se o usuário está autenticado e redireciona se não estiver"""
        if not self.is_authenticated:
            return rx.redirect("/")
