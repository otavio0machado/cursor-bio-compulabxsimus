import reflex as rx
from typing import Optional
from ..config import Config

class AuthState(rx.State):
    """Estado responsável pela autenticação e controle de acesso"""
    
    # Autenticação - Login único
    is_authenticated: bool = False
    login_email: str = ""
    login_password: str = ""
    login_error: str = ""

    # Credenciais validas (definidas via variaveis de ambiente)
    def _credentials_configured(self) -> bool:
        return bool(Config.AUTH_EMAIL and Config.AUTH_PASSWORD)
    
    def set_login_email(self, email: str):
        self.login_email = email
        
    def set_login_password(self, password: str):
        self.login_password = password
        
    def attempt_login(self):
        """Tenta realizar login com as credenciais fornecidas"""
        if not self._credentials_configured():
            self.login_error = "Login indisponivel. Configure AUTH_EMAIL e AUTH_PASSWORD."
            self.is_authenticated = False
            return
        if self.login_email == Config.AUTH_EMAIL and self.login_password == Config.AUTH_PASSWORD:
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
