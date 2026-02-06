import reflex as rx
from ..services.supabase_client import supabase


class AuthState(rx.State):
    """Estado responsável pela autenticação via Supabase"""

    is_authenticated: bool = False
    login_email: str = ""
    login_password: str = ""
    login_error: str = ""
    _user_id: str = ""

    def set_login_email(self, email: str):
        self.login_email = email

    def set_login_password(self, password: str):
        self.login_password = password

    def attempt_login(self):
        """Tenta realizar login via Supabase Auth"""
        if not self.login_email or not self.login_password:
            self.login_error = "Preencha e-mail e senha."
            return

        if supabase is None:
            self.login_error = "Serviço indisponível. Verifique a configuração do Supabase."
            return

        try:
            response = supabase.auth.sign_in_with_password({
                "email": self.login_email,
                "password": self.login_password,
            })
            if response.user:
                self.is_authenticated = True
                self._user_id = response.user.id
                self.login_error = ""
                return rx.redirect("/")
            else:
                self.login_error = "Credenciais inválidas."
                self.is_authenticated = False
        except Exception as e:
            msg = str(e)
            if "Invalid login credentials" in msg:
                self.login_error = "E-mail ou senha incorretos."
            elif "Email not confirmed" in msg:
                self.login_error = "E-mail não confirmado. Verifique sua caixa de entrada."
            else:
                self.login_error = "Erro ao autenticar. Tente novamente."
            self.is_authenticated = False

    def logout(self):
        """Realiza logout"""
        if supabase:
            try:
                supabase.auth.sign_out()
            except Exception:
                pass
        self.is_authenticated = False
        self.login_email = ""
        self.login_password = ""
        self.login_error = ""
        self._user_id = ""
        return rx.redirect("/")

    def check_auth(self):
        """Verifica se o usuário está autenticado"""
        if not self.is_authenticated:
            return rx.redirect("/")
