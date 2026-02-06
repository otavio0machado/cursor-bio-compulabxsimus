import logging
import reflex as rx
from ..services.supabase_client import supabase

logger = logging.getLogger(__name__)


class AuthState(rx.State):
    """Estado responsável pela autenticação via Supabase"""

    is_authenticated: bool = False
    login_email: str = ""
    login_password: str = ""
    login_error: str = ""
    _user_id: str = ""
    _session_checked: bool = False
    show_forgot_password: bool = False
    forgot_password_email: str = ""
    forgot_password_message: str = ""
    forgot_password_error: str = ""

    def set_login_email(self, email: str):
        self.login_email = email

    def set_login_password(self, password: str):
        self.login_password = password

    def set_forgot_password_email(self, email: str):
        self.forgot_password_email = email

    def toggle_forgot_password(self):
        self.show_forgot_password = not self.show_forgot_password
        self.forgot_password_message = ""
        self.forgot_password_error = ""

    def restore_session(self):
        """Tenta restaurar sessão existente do Supabase no carregamento da página"""
        if self._session_checked:
            return
        self._session_checked = True

        if supabase is None:
            return

        try:
            session = supabase.auth.get_session()
            if session and session.user:
                self.is_authenticated = True
                self._user_id = session.user.id
                logger.info(f"Sessão restaurada para usuário {session.user.email}")
        except Exception as e:
            logger.debug(f"Nenhuma sessão ativa para restaurar: {e}")

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

    def send_password_reset(self):
        """Envia e-mail de recuperação de senha via Supabase"""
        if not self.forgot_password_email:
            self.forgot_password_error = "Informe o e-mail cadastrado."
            return

        if supabase is None:
            self.forgot_password_error = "Serviço indisponível."
            return

        try:
            supabase.auth.reset_password_email(self.forgot_password_email)
            self.forgot_password_message = "E-mail de recuperação enviado! Verifique sua caixa de entrada."
            self.forgot_password_error = ""
        except Exception as e:
            logger.error(f"Erro ao enviar reset de senha: {e}")
            self.forgot_password_error = "Erro ao enviar e-mail. Verifique o endereço e tente novamente."

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
        self._session_checked = False
        return rx.redirect("/")

    def check_auth(self):
        """Verifica se o usuário está autenticado"""
        if not self.is_authenticated:
            return rx.redirect("/")
