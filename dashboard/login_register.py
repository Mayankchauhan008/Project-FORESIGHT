# ============================================================
# PROJECT FORESIGHT - LOGIN / REGISTER
# CLEAN, ALIGNED, PROFESSIONAL UI
# ============================================================

from __future__ import annotations

import streamlit as st

from auth import (
    authenticate_user,
    login_user,
    register_user,
)


# ============================================================
# PAGE STYLE
# ============================================================

def apply_auth_style():

    st.markdown(
        """
        <style>

        /* ====================================================
           HIDE SIDEBAR BEFORE LOGIN
           ==================================================== */

        [data-testid="stSidebar"] {
            display: none !important;
        }

        /* ====================================================
           APPLICATION BACKGROUND
           ==================================================== */

        .stApp {
            background:
                radial-gradient(
                    circle at 8% 15%,
                    rgba(37, 99, 235, 0.15),
                    transparent 28%
                ),
                radial-gradient(
                    circle at 92% 85%,
                    rgba(14, 165, 233, 0.10),
                    transparent 30%
                ),
                #08101f;
        }

        /* ====================================================
           MAIN CONTENT
           ==================================================== */

        .block-container {
            max-width: 1180px !important;
            padding-top: 55px !important;
            padding-bottom: 55px !important;
        }

        /* ====================================================
           COLUMN SPACING
           ==================================================== */

        [data-testid="stHorizontalBlock"] {
            gap: 0 !important;
        }

        /* ====================================================
           LEFT COLUMN
           ==================================================== */

        [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:first-child {

            background:
                linear-gradient(
                    145deg,
                    #172554 0%,
                    #1d4ed8 48%,
                    #0f172a 100%
                );

            border-radius: 26px 0 0 26px;

            min-height: 650px;

            padding: 52px 48px !important;

            box-shadow:
                0 25px 70px
                rgba(0, 0, 0, 0.35);

            position: relative;

            overflow: hidden;
        }

        /* LEFT GLOW */

        [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:first-child::before {

            content: "";

            position: absolute;

            width: 270px;
            height: 270px;

            border-radius: 50%;

            background:
                rgba(96, 165, 250, 0.18);

            filter: blur(70px);

            top: -100px;
            left: -90px;
        }

        [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:first-child::after {

            content: "";

            position: absolute;

            width: 220px;
            height: 220px;

            border-radius: 50%;

            background:
                rgba(56, 189, 248, 0.12);

            filter: blur(70px);

            right: -70px;
            bottom: -80px;
        }

        /* ====================================================
           RIGHT COLUMN
           ==================================================== */

        [data-testid="stHorizontalBlock"]
        > [data-testid="column"]:nth-child(2) {

            background: #0f172a;

            border-radius: 0 26px 26px 0;

            min-height: 650px;

            padding: 52px 48px !important;

            display: flex;
            flex-direction: column;
            justify-content: center;

            box-shadow:
                0 25px 70px
                rgba(0, 0, 0, 0.35);
        }

        /* ====================================================
           BRAND LOGO
           ==================================================== */

        .brand-logo {

            width: 70px;
            height: 70px;

            display: flex;

            align-items: center;
            justify-content: center;

            background:
                rgba(255, 255, 255, 0.12);

            border:
                1px solid
                rgba(255, 255, 255, 0.20);

            border-radius: 18px;

            font-size: 34px;

            margin-bottom: 30px;

            position: relative;
            z-index: 5;

        }

        /* ====================================================
           BRAND TITLE
           ==================================================== */

        .brand-title {

            font-size: 46px;

            font-weight: 800;

            letter-spacing: -1.5px;

            line-height: 1.05;

            color: white;

            margin-bottom: 15px;

            position: relative;
            z-index: 5;

        }

        .brand-subtitle {

            max-width: 390px;

            font-size: 16px;

            line-height: 1.7;

            color: #dbeafe;

            margin-bottom: 30px;

            position: relative;
            z-index: 5;

        }

        /* ====================================================
           FEATURE CARDS
           ==================================================== */

        .feature-card {

            display: flex;

            align-items: center;

            padding: 13px 15px;

            margin-bottom: 12px;

            border-radius: 13px;

            background:
                rgba(255, 255, 255, 0.08);

            border:
                1px solid
                rgba(255, 255, 255, 0.10);

            position: relative;
            z-index: 5;

        }

        .feature-icon {

            width: 38px;
            height: 38px;

            display: flex;

            align-items: center;
            justify-content: center;

            border-radius: 10px;

            background:
                rgba(255, 255, 255, 0.10);

            font-size: 18px;

            margin-right: 13px;

        }

        .feature-text {

            color: #e2e8f0;

            font-size: 14px;

            font-weight: 500;

        }

        .brand-footer {

            margin-top: 32px;

            font-size: 12px;

            color: #bfdbfe;

            position: relative;
            z-index: 5;

        }

        /* ====================================================
           RIGHT SIDE TITLE
           ==================================================== */

        .login-title {

            font-size: 32px;

            font-weight: 800;

            color: #f8fafc;

            margin-bottom: 8px;

        }

        .login-subtitle {

            font-size: 14px;

            line-height: 1.6;

            color: #94a3b8;

            margin-bottom: 24px;

        }

        /* ====================================================
           LOGIN / REGISTER SWITCH
           ==================================================== */

        div[role="radiogroup"] {

            background: #111827;

            border:
                1px solid
                #263244;

            border-radius: 12px;

            padding: 4px;

            margin-bottom: 22px;

        }

        div[role="radiogroup"] label {

            padding: 8px 16px;

            border-radius: 9px;

        }

        /* ====================================================
           INPUT LABEL
           ==================================================== */

        div[data-testid="stTextInput"] label {

            color: #cbd5e1 !important;

            font-size: 13px !important;

            font-weight: 600 !important;

        }

        /* ====================================================
           INPUT BOX
           ==================================================== */

        div[data-testid="stTextInput"] input {

            min-height: 48px !important;

            background:
                #111827 !important;

            color:
                #f8fafc !important;

            border:
                1px solid
                #334155 !important;

            border-radius:
                11px !important;

        }

        div[data-testid="stTextInput"] input:focus {

            border-color:
                #3b82f6 !important;

            box-shadow:
                0 0 0 1px
                #3b82f6 !important;

        }

        /* ====================================================
           FORM
           ==================================================== */

        [data-testid="stForm"] {

            border:
                none !important;

            padding:
                0 !important;

            background:
                transparent !important;

        }

        /* ====================================================
           PRIMARY BUTTON
           ==================================================== */

        button[kind="primary"] {

            min-height:
                48px !important;

            border-radius:
                11px !important;

            font-size:
                14px !important;

            font-weight:
                700 !important;

            background:
                linear-gradient(
                    135deg,
                    #2563eb,
                    #0284c7
                ) !important;

            border:
                none !important;

            box-shadow:
                0 8px 18px
                rgba(37, 99, 235, 0.25);

        }

        button[kind="primary"]:hover {

            background:
                linear-gradient(
                    135deg,
                    #1d4ed8,
                    #0369a1
                ) !important;

        }

        /* ====================================================
           ALERT
           ==================================================== */

        div[data-testid="stAlert"] {

            border-radius:
                11px;

        }

        /* ====================================================
           SECURITY NOTE
           ==================================================== */

        .security-note {

            text-align:
                center;

            color:
                #64748b;

            font-size:
                12px;

            margin-top:
                20px;

        }

        /* ====================================================
           MOBILE
           ==================================================== */

        @media (max-width: 850px) {

            [data-testid="stHorizontalBlock"] {
                display: block !important;
            }

            [data-testid="stHorizontalBlock"]
            > [data-testid="column"]:first-child {

                border-radius:
                    24px 24px 0 0;

                min-height:
                    auto;

            }

            [data-testid="stHorizontalBlock"]
            > [data-testid="column"]:nth-child(2) {

                border-radius:
                    0 0 24px 24px;

                min-height:
                    auto;

            }

            .brand-title {
                font-size:
                    38px;
            }

        }

        </style>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# LOGIN / REGISTER PAGE
# ============================================================

def render_auth_page():

     # Switch back to Login on the next rerun
    if st.session_state.pop("switch_to_login", False):
        st.session_state["auth_mode"] = "Login"
        
    apply_auth_style()

    # ========================================================
    # MAIN TWO-COLUMN LAYOUT
    # ========================================================

    left, right = st.columns(
        [1, 1],
        gap=None,
    )

    # ========================================================
    # LEFT BRAND PANEL
    # ========================================================

    with left:

        st.markdown(
            '<div class="brand-logo">🛒</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="brand-title">'
            'FORESIGHT'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="brand-subtitle">'
            'Retail AI Intelligence Platform '
            'for smarter business decisions.'
            '</div>',
            unsafe_allow_html=True,
        )

        # Feature 1
        st.markdown(
            '<div class="feature-card">'
            '<div class="feature-icon">📊</div>'
            '<div class="feature-text">'
            'Sales Analytics'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Feature 2
        st.markdown(
            '<div class="feature-card">'
            '<div class="feature-icon">🔮</div>'
            '<div class="feature-text">'
            'Demand Forecasting'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Feature 3
        st.markdown(
            '<div class="feature-card">'
            '<div class="feature-icon">📦</div>'
            '<div class="feature-text">'
            'Inventory Intelligence'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        # Feature 4
        st.markdown(
            '<div class="feature-card">'
            '<div class="feature-icon">🚨</div>'
            '<div class="feature-text">'
            'Product Risk Detection'
            '</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="brand-footer">'
            'AI-powered retail decision support'
            '</div>',
            unsafe_allow_html=True,
        )

    # ========================================================
    # RIGHT LOGIN PANEL
    # ========================================================

    with right:

        st.markdown(
            '<div class="login-title">'
            'Welcome back'
            '</div>',
            unsafe_allow_html=True,
        )

        st.markdown(
            '<div class="login-subtitle">'
            'Sign in to access your FORESIGHT dashboard.'
            '</div>',
            unsafe_allow_html=True,
        )

        # ----------------------------------------------------
        # LOGIN / REGISTER
        # ----------------------------------------------------

        mode = st.radio(
            "Account",
            [
                "Login",
                "Register",
            ],
            horizontal=True,
            label_visibility="collapsed",
            key="auth_mode",
        )

        # ====================================================
        # LOGIN
        # ====================================================

        if mode == "Login":

            with st.form(
                "login_form",
                clear_on_submit=False,
            ):

                email = st.text_input(
                    "Email",
                    placeholder="Enter your email",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Enter your password",
                )

                submitted = st.form_submit_button(
                    "Sign In",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:

                success, message, user = authenticate_user(
                    email,
                    password,
                )

                if success and user:

                    login_user(user)

                    st.success(
                        f"Welcome, {user.get('name', 'User')}!"
                    )

                    st.rerun()

                else:

                    st.error(message)

        # ====================================================
        # REGISTER
        # ====================================================

        else:

            with st.form(
                "register_form",
                clear_on_submit=True,
            ):

                name = st.text_input(
                    "Full Name",
                    placeholder="Enter your full name",
                )

                email = st.text_input(
                    "Email",
                    placeholder="Enter your email",
                )

                password = st.text_input(
                    "Password",
                    type="password",
                    placeholder="Minimum 6 characters",
                )

                confirm_password = st.text_input(
                    "Confirm Password",
                    type="password",
                    placeholder="Repeat your password",
                )

                submitted = st.form_submit_button(
                    "Create Account",
                    type="primary",
                    use_container_width=True,
                )

            if submitted:

                if not name.strip():

                    st.error(
                        "Please enter your full name."
                    )

                elif not email.strip():

                    st.error(
                        "Please enter your email."
                    )

                elif len(password) < 6:

                    st.error(
                        "Password must contain at least 6 characters."
                    )

                elif password != confirm_password:

                    st.error(
                        "Passwords do not match."
                    )

                else:

                    success, message = register_user(
                        name,
                        email,
                        password,
                    )

                    if success:

                        st.success(
                            message
                        )

                        # st.session_state[
                        #     "auth_mode"
                        # ] = "Login"

                        st.rerun()

                    else:

                        st.error(message)

        st.markdown(
            '<div class="security-note">'
            '🔒 Your account is protected with secure '
            'password hashing.'
            '</div>',
            unsafe_allow_html=True,
        )