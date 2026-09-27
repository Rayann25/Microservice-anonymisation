import streamlit as st
import os
from src.engine import RobustAnonymizationEngine

st.set_page_config(
    page_title="Microservice — Passerelle Souveraine LLM",
    page_icon="🔒",
    layout="centered"
)

STORAGE_DIR = os.path.abspath("./storage_vault")
os.makedirs(STORAGE_DIR, exist_ok=True)

# CSS STRICT : forçage noir et blanc sur tous les sélecteurs de saisie
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    /* Fond global */
    .stApp, html, body {
        background-color: #070709 !important;
        color: #f4f4f5 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
    }
    
    #MainMenu, footer, header {visibility: hidden !important;}

    /* FORÇAGE ZONE DE TEXTE SOMBRE + TEXTE BLANC NET */
    .stTextArea,
    .stTextArea > div,
    .stTextArea > div > div,
    div[data-baseweb="textarea"],
    div[data-baseweb="base-input"],
    div[data-baseweb="textarea"] > textarea,
    textarea {
        background-color: #09090d !important;
        background: #09090d !important;
        color: #ffffff !important;
        -webkit-text-fill-color: #ffffff !important;
        border-color: #27272a !important;
        caret-color: #a855f7 !important;
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        font-size: 0.82rem !important;
        line-height: 1.5 !important;
    }

    textarea:focus {
        border-color: #9333ea !important;
        box-shadow: 0 0 0 1px #9333ea !important;
    }

    textarea::placeholder {
        color: #71717a !important;
        -webkit-text-fill-color: #71717a !important;
    }

    /* Cartes conteneurs */
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        background-color: #0d0d12 !important;
        border: 1px solid rgba(168, 85, 247, 0.25) !important;
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.08) !important;
        border-radius: 1rem !important;
        padding: 1.25rem !important;
    }

    /* Onglets de navigation */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #0d0d12 !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 0.75rem !important;
        padding: 4px !important;
        gap: 6px !important;
        justify-content: center !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #a1a1aa !important;
        border-radius: 0.5rem !important;
        font-weight: 500 !important;
        font-size: 0.75rem !important;
        padding: 6px 20px !important;
        border: none !important;
        background: transparent !important;
    }
    .stTabs [aria-selected="true"] {
        background: #9333ea !important;
        color: #ffffff !important;
        font-weight: 600 !important;
        box-shadow: 0 0 15px rgba(147, 51, 234, 0.4) !important;
    }
    .stTabs [data-baseweb="tab-highlight"] {
        display: none !important;
    }

    /* Boutons */
    button[kind="primary"] {
        background: linear-gradient(to right, #9333ea, #4f46e5) !important;
        color: #ffffff !important;
        border: none !important;
        border-radius: 0.75rem !important;
        font-weight: 600 !important;
        font-size: 0.8rem !important;
        padding: 0.5rem 1rem !important;
        box-shadow: 0 0 18px rgba(168, 85, 247, 0.25) !important;
    }
    button[kind="secondary"] {
        background-color: #18181b !important;
        color: #d4d4d8 !important;
        border: 1px solid #27272a !important;
        border-radius: 0.75rem !important;
        font-weight: 500 !important;
        font-size: 0.8rem !important;
        padding: 0.5rem 1rem !important;
    }
    button[kind="secondary"]:hover {
        border-color: #a855f7 !important;
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# En-tête Microservice
st.markdown("""
    <div style="border-bottom: 1px solid rgba(255,255,255,0.08); background-color: rgba(11,11,14,0.9); backdrop-filter: blur(12px); padding: 12px 0; margin-bottom: 2rem;">
        <div style="max-width: 56rem; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; padding: 0 1rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div style="width: 2rem; height: 2rem; border-radius: 0.5rem; background: linear-gradient(to top right, #9333ea, #6366f1); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.875rem; box-shadow: 0 0 15px rgba(168,85,247,0.4);">
                    μS
                </div>
                <div>
                    <div style="font-size: 0.65rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: #a1a1aa;">Microservice</div>
                    <div style="font-size: 0.875rem; font-weight: 600; color: white;">Passerelle Relation Client & LLM</div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem; background-color: #121217; padding: 0.35rem 0.75rem; border-radius: 9999px; border: 1px solid rgba(255,255,255,0.08);">
                <span style="width: 0.5rem; height: 0.5rem; border-radius: 50%; background-color: #a855f7; display: inline-block;"></span>
                <span style="font-size: 0.75rem; font-weight: 500; color: #d4d4d8;">Actif</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

tab_text, tab_pdf = st.tabs(["Flux Direct", "Document PDF"])

# ==========================================
# ONGLET 1 : FLUX DIRECT
# ==========================================
with tab_text:
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        with st.container(border=True):
            col_t, col_c = st.columns([2, 1])
            with col_t:
                st.markdown('<span style="font-size: 0.70rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #a1a1aa;">Entrée Source</span>', unsafe_allow_html=True)
            with col_c:
                if st.button("Effacer", key="clearBtn", type="secondary", use_container_width=True):
                    st.session_state["raw_text"] = ""
                    st.session_state["sanitized_text"] = ""
                    st.session_state["encrypted_vault"] = ""
                    st.session_state["entities_count"] = 0
                    st.session_state["restored_text"] = ""
                    st.rerun()

            raw_input = st.text_area(
                "Entrée source",
                value=st.session_state.get("raw_text", ""),
                placeholder="Saisissez ou collez ici la communication...",
                height=180,
                label_visibility="collapsed"
            )
            st.session_state["raw_text"] = raw_input

            if st.button("Sécuriser le contenu", key="procBtn", type="primary", use_container_width=True):
                if raw_input.strip():
                    with st.spinner("Traitement en cours..."):
                        res = RobustAnonymizationEngine.process_raw_text(raw_input)
                        st.session_state["sanitized_text"] = res["sanitized_text"]
                        st.session_state["encrypted_vault"] = res["encrypted_vault"]
                        st.session_state["entities_count"] = res["entities_count"]
                        st.session_state["restored_text"] = ""
                    st.rerun()

    with col2:
        with st.container(border=True):
            count = st.session_state.get('entities_count', 0)
            badge_html = f'<span style="font-size: 0.65rem; background: rgba(168,85,247,0.15); color: #c084fc; padding: 2px 8px; border-radius: 9999px; border: 1px solid rgba(168,85,247,0.3);">{count} entité(s)</span>' if count else ""
            
            st.markdown(f'''
                <div style="display: flex; justify-content: space-between; align-items: center; height: 38px; margin-bottom: 8px;">
                    <span style="font-size: 0.70rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #c084fc;">Sortie Protégée</span>
                    {badge_html}
                </div>
            ''', unsafe_allow_html=True)

            sanitized_output = st.session_state.get("sanitized_text", "")
            
            if sanitized_output:
                st.markdown(f"""
                    <div style="height: 180px; font-size: 0.80rem; padding: 0.875rem; border-radius: 0.75rem; background-color: #09090d; border: 1px solid #27272a; color: #ffffff; overflow-y: auto; white-space: pre-wrap; font-family: 'JetBrains Mono', monospace; line-height: 1.5; margin-bottom: 1rem;">{sanitized_output}</div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div style="height: 180px; font-size: 0.80rem; padding: 0.875rem; border-radius: 0.75rem; background-color: #09090d; border: 1px solid #27272a; color: #52525b; font-style: italic; overflow-y: auto; line-height: 1.5; margin-bottom: 1rem;">Le contenu neutralisé apparaîtra ici...</div>
                """, unsafe_allow_html=True)

            if st.button("Restitution locale", key="restBtn", type="secondary", use_container_width=True):
                if st.session_state.get("encrypted_vault") and st.session_state.get("sanitized_text"):
                    with st.spinner("Déchiffrement..."):
                        restored = RobustAnonymizationEngine.rehydrate_text(
                            st.session_state["sanitized_text"],
                            st.session_state["encrypted_vault"]
                        )
                        st.session_state["restored_text"] = restored
                        st.rerun()

    if st.session_state.get("restored_text"):
        st.markdown(f"""
            <div style="background-color: #0D0D12; border-radius: 1rem; padding: 1.25rem; border: 1px solid rgba(16,185,129,0.25); box-shadow: 0 0 20px rgba(16,185,129,0.06); margin-top: 1.5rem;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="width: 0.4rem; height: 0.4rem; border-radius: 50%; background-color: #10b981;"></span>
                        <span style="font-size: 0.70rem; font-weight: 600; color: #34d399; text-transform: uppercase; letter-spacing: 0.05em;">Contenu Reconstitué</span>
                    </div>
                    <span style="font-size: 0.65rem; color: #71717a;">Validation d'intégrité terminée</span>
                </div>
                <div style="font-size: 0.80rem; padding: 1rem; border-radius: 0.75rem; background-color: #09090d; border: 1px solid #27272a; color: #ffffff; white-space: pre-wrap; line-height: 1.5;">{st.session_state["restored_text"]}</div>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# ONGLET 2 : DOCUMENT PDF
# ==========================================
with tab_pdf:
    with st.container(border=True):
        st.markdown('<span style="font-size: 0.75rem; font-weight: 600; color: #a1a1aa; text-transform: uppercase;">Sélectionner un fichier PDF</span>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader("Sélectionner un fichier PDF", type=["pdf"], label_visibility="collapsed")

        if uploaded_file is not None:
            temp_input = os.path.join(STORAGE_DIR, f"raw_{uploaded_file.name}")
            output_name = f"sanitized_{uploaded_file.name}"
            temp_output = os.path.join(STORAGE_DIR, output_name)

            if not os.path.exists(temp_output):
                with st.spinner("Biffure vectorielle sans rétention..."):
                    with open(temp_input, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    RobustAnonymizationEngine.process_pdf(temp_input, temp_output)

            st.markdown(f"""
                <div style="border: 1px solid #27272a; border-radius: 0.75rem; padding: 1rem; background-color: #09090d; margin-top: 1rem; margin-bottom: 1rem;">
                    <div style="font-size: 0.8rem; font-weight: 600; color: #ffffff;">{uploaded_file.name}</div>
                    <div style="font-size: 0.7rem; color: #34d399; margin-top: 0.2rem;">● Prêt pour transmission</div>
                </div>
            """, unsafe_allow_html=True)

            with open(temp_output, "rb") as f:
                st.download_button(
                    label="Télécharger le document sécurisé",
                    data=f,
                    file_name=output_name,
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )

# Pied de page
st.markdown("""
    <div style="border-top: 1px solid rgba(255,255,255,0.06); padding: 1.5rem 0; margin-top: 3rem;">
        <div style="max-width: 56rem; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; font-size: 0.7rem; color: #71717a; padding: 0 1rem;">
            <span>Passerelle Cryptographique Souveraine</span>
            <span>Protocole AES-256-GCM</span>
        </div>
    </div>
""", unsafe_allow_html=True)
