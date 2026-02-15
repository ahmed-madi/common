import frappe
import secrets
from frappe.utils import get_url
from common.api.utils.jwt import prepare_token
from common.api.utils.response import build_success_response, build_error_response


@frappe.whitelist(allow_guest=True)
def get_providers():
    """
    Get list of enabled social login providers.

    Returns:
     List of enabled social login providers with their configuration
    """
    try:
        providers = frappe.get_all(
            "Social Login Key",
            filters={"enable_social_login": 1},
            fields=["name", "provider_name", "icon", "client_id"],
        )

        provider_list = []
        for provider in providers:
            provider_list.append(
                {
                    "name": provider.name,
                    "provider_name": provider.provider_name,
                    "icon": provider.icon,
                }
            )

        return build_success_response(
            status_code=200,
            message="Social login providers retrieved successfully",
            data={"providers": provider_list},
        )

    except Exception as e:
        frappe.log_error(
            title="Get Social Providers Failed",
            message=f"Error retrieving social login providers: {str(e)}\n\n{frappe.get_traceback()}",
        )
        return build_error_response(
            status_code=500,
            message="Failed to retrieve social login providers",
            error=str(e),
        )


@frappe.whitelist(allow_guest=True)
def get_oauth_url(provider):
    """
    Generate OAuth authorization URL for mobile apps.

    Args:
     provider: Name of the social login provider (e.g., 'microsoft', 'google')

    Returns:
     OAuth authorization URL and state token for CSRF protection
    """
    try:
        # Get the social login key configuration
        social_login_key = frappe.get_doc("Social Login Key", provider)

        if not social_login_key.enable_social_login:
            return build_error_response(
                status_code=400,
                message=f"Social login is not enabled for {provider}",
                error="Provider not enabled",
            )

        # Generate state token for CSRF protection
        state = secrets.token_urlsafe(32)

        # Store state in cache for validation (expires in 10 minutes)
        frappe.cache().set_value(
            f"oauth_state_{state}",
            {"provider": provider, "timestamp": frappe.utils.now()},
            expires_in_sec=600,
        )

        # Get the OAuth provider configuration
        oauth_provider = social_login_key.provider_name.lower()

        # Build authorization URL based on provider
        if oauth_provider == "microsoft":
            # Microsoft OAuth 2.0 endpoint
            tenant_id = social_login_key.get("tenant_id") or "common"
            auth_url = (
                f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/authorize"
            )
            scope = "openid profile email User.Read"
        elif oauth_provider == "google":
            # Google OAuth 2.0 endpoint
            auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
            scope = "openid profile email"
        elif oauth_provider == "facebook":
            # Facebook OAuth endpoint
            auth_url = "https://www.facebook.com/v12.0/dialog/oauth"
            scope = "email public_profile"
        else:
            # Generic OAuth 2.0 (use custom base_url if configured)
            auth_url = (
                social_login_key.get("base_url") or social_login_key.authorize_url
            )
            scope = social_login_key.get("scope") or "openid profile email"

        # Get redirect URI from social login key or use default
        redirect_uri = (
            social_login_key.redirect_url
            or f"{get_url()}/api/method/frappe.integrations.oauth2_logins.login_via_oauth2"
        )

        # Build the authorization URL with parameters
        import urllib.parse

        params = {
            "client_id": social_login_key.client_id,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": scope,
            "state": state,
        }

        # Add response_mode for Microsoft
        if oauth_provider == "microsoft":
            params["response_mode"] = "query"

        authorization_url = f"{auth_url}?{urllib.parse.urlencode(params)}"

        return build_success_response(
            status_code=200,
            message="OAuth URL generated successfully",
            data={
                "authorization_url": authorization_url,
                "state": state,
                "provider": provider,
                "redirect_uri": redirect_uri,
            },
        )

    except frappe.DoesNotExistError:
        return build_error_response(
            status_code=404,
            message=f"Social login provider '{provider}' not found",
            error="Provider not configured",
        )
    except Exception as e:
        frappe.log_error(
            title="Get OAuth URL Failed",
            message=f"Error generating OAuth URL for {provider}: {str(e)}\n\n{frappe.get_traceback()}",
        )
        return build_error_response(
            status_code=500, message="Failed to generate OAuth URL", error=str(e)
        )


@frappe.whitelist(allow_guest=True)
def handle_oauth_callback(code, state, provider=None):
    """
    Handle OAuth callback and exchange authorization code for access tokens.

    Args:
     code: Authorization code from OAuth provider
     state: State token for CSRF validation
     provider: Optional provider name (can be extracted from state)

    Returns:
     JWT access and refresh tokens for the authenticated user
    """
    try:
        # Validate state token (CSRF protection)
        cached_state = frappe.cache().get_value(f"oauth_state_{state}")

        if not cached_state:
            return build_error_response(
                status_code=400,
                message="Invalid or expired state token",
                error="CSRF validation failed",
            )

        # Get provider from cached state if not provided
        if not provider:
            provider = cached_state.get("provider")

        # Clear the state from cache (one-time use)
        frappe.cache().delete_value(f"oauth_state_{state}")

        # Get social login key configuration
        social_login_key = frappe.get_doc("Social Login Key", provider)

        # Exchange authorization code for access token
        import requests

        oauth_provider = social_login_key.provider_name.lower()

        # Get token endpoint based on provider
        if oauth_provider == "microsoft":
            tenant_id = social_login_key.get("tenant_id") or "common"
            token_url = (
                f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
            )
        elif oauth_provider == "google":
            token_url = "https://oauth2.googleapis.com/token"
        elif oauth_provider == "facebook":
            token_url = "https://graph.facebook.com/v12.0/oauth/access_token"
        else:
            token_url = (
                social_login_key.get("access_token_url")
                or social_login_key.base_url + "/token"
            )

        # Get redirect URI
        redirect_uri = (
            social_login_key.redirect_url
            or f"{get_url()}/api/method/frappe.integrations.oauth2_logins.login_via_oauth2"
        )

        # Exchange code for token
        token_data = {
            "client_id": social_login_key.client_id,
            "client_secret": social_login_key.get_password("client_secret"),
            "code": code,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        token_response = requests.post(token_url, data=token_data)

        if token_response.status_code != 200:
            frappe.log_error(
                title="OAuth Token Exchange Failed",
                message=f"Failed to exchange code for token: {token_response.text}",
            )
            return build_error_response(
                status_code=400,
                message="Failed to authenticate with OAuth provider",
                error=token_response.text,
            )

        token_info = token_response.json()
        access_token = token_info.get("access_token")

        # Get user info from OAuth provider
        if oauth_provider == "microsoft":
            user_info_url = "https://graph.microsoft.com/v1.0/me"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = requests.get(user_info_url, headers=headers)
            user_data = user_response.json()

            email = user_data.get("mail") or user_data.get("userPrincipalName")

        elif oauth_provider == "google":
            user_info_url = "https://www.googleapis.com/oauth2/v2/userinfo"
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = requests.get(user_info_url, headers=headers)
            user_data = user_response.json()

            email = user_data.get("email")

        elif oauth_provider == "facebook":
            user_info_url = f"https://graph.facebook.com/me?fields=id,email&access_token={access_token}"
            user_response = requests.get(user_info_url)
            user_data = user_response.json()

            email = user_data.get("email")
        else:
            # Generic OAuth - try to get user info from standard endpoint
            user_info_url = (
                social_login_key.get("api_endpoint")
                or social_login_key.base_url + "/userinfo"
            )
            headers = {"Authorization": f"Bearer {access_token}"}
            user_response = requests.get(user_info_url, headers=headers)
            user_data = user_response.json()

            email = user_data.get("email")

        if not email:
            return build_error_response(
                status_code=400,
                message="Email not provided by OAuth provider",
                error="Email is required",
            )

        # Check if user exists - DO NOT create new users (login only, no signup)
        user = frappe.db.exists("User", email)

        if not user:
            # User does not exist - reject login attempt
            frappe.log_error(
                title="Social Login Failed - User Not Found",
                message=f"User with email {email} attempted to login via {provider} but does not exist in the system",
            )
            return build_error_response(
                status_code=404,
                message="User account not found. Please contact your administrator.",
                error="User does not exist",
            )

        # Get existing user
        user_doc = frappe.get_doc("User", user)

        # Check if user is enabled
        if not user_doc.enabled:
            return build_error_response(
                status_code=403,
                message="User account is disabled",
                error="Account disabled",
            )

        # Check if user has an employee record (matching existing login logic)
        if user != "Administrator":
            employee = frappe.db.get_value("Employee", {"user_id": user}, "name")
            if not employee:
                frappe.log_error(
                    title="Social Login Failed - Employee Not Found",
                    message=f"User {user} authenticated via {provider} but has no employee record",
                )
                return build_error_response(
                    status_code=409,
                    message="Invalid employee account",
                    error="No employee record found for this user",
                )

        # Generate JWT tokens using existing infrastructure
        tokens = prepare_token(user_doc)
        frappe.db.commit()

        # Return user data and tokens
        data = {
            "user": user_doc.name,
            "email": user_doc.email,
            "language": user_doc.language,
            "full_name": user_doc.full_name,
            "access_token": tokens["access_token"],
            "refresh_token": tokens["refresh_token"],
        }

        return build_success_response(
            status_code=200, message="Login successful", data=data
        )

    except frappe.DoesNotExistError:
        return build_error_response(
            status_code=404,
            message=f"Social login provider '{provider}' not found",
            error="Provider not configured",
        )
    except Exception as e:
        frappe.log_error(
            title="OAuth Callback Failed",
            message=f"Error handling OAuth callback: {str(e)}\n\n{frappe.get_traceback()}",
        )
        return build_error_response(
            status_code=500, message="Failed to complete social login", error=str(e)
        )
