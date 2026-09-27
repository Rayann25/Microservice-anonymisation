import streamlit as st
import os
import tempfile
from src.engine import RobustAnonymizationEngine

# Configuration de la page Streamlit (Mode sombre et titre)
st.set_page_config(
    page_title="Microservice — Passerelle Souveraine LLM",
    page_icon="🔒",
    layout="centered"
)

# Dossier de stockage temporaire pour les PDF
STORAGE_DIR = os.path.abspath("./storage_vault")
os.makedirs(STORAGE_DIR, exist_ok=True)

# Injection du design CSS personnalisé (Tailwind-like & Thème Violet Sombre)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    .stApp {
        background-color: #070709;
        color: #f4f4f5;
        font-family: 'Plus Jakarta Sans', sans-serif;
    }
    
    /* Masquer les éléments par défaut de Streamlit pour un look application web pure */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .code-font {
        font-family: 'JetBrains Mono', monospace;
    }

    .glow-border {
        border: 1px solid rgba(168, 85, 247, 0.22);
        box-shadow: 0 0 25px rgba(168, 85, 247, 0.06);
        background-color: #0D0D12;
        border-radius: 1rem;
        padding: 1.25rem;
    }

    /* Style des boutons personnalisés */
    .stButton > button {
        background: linear-gradient(to right, #9333ea, #4f46e5);
        color: white;
        font-weight: 600;
        font-size: 0.75rem;
        border-radius: 0.75rem;
        border: none;
        padding: 0.6rem 1rem;
        width: 100%;
        box-shadow: 0 0 20px rgba(168, 85, 247, 0.25);
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        opacity: 0.95;
    }

    /* Style des onglets Streamlit pour matcher le design original */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0d0d12;
        padding: 4px;
        border-radius: 0.75rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
        justify-content: center;
    }
    .stTabs [data-baseweb="tab"] {
        height: 38px;
        color: #a1a1aa;
        font-weight: 500;
        font-size: 0.75rem;
        border-radius: 0.5rem;
        border: none;
        padding: 0 24px;
    }
    .stTabs [aria-selected="true"] {
        background: #9333ea !important;
        color: white !important;
        font-weight: 600;
    }
    </style>
""", unsafe_allow_html=True)

# --- HEADER ---
st.markdown("""
    <div style="border-bottom: 1px solid rgba(255,255,255,0.08); background-color: rgba(11,11,14,0.8); backdrop-filter: blur(12px); padding: 12px 0; margin-bottom: 2rem;">
        <div style="max-width: 56rem; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; padding: 0 1.5rem;">
            <div style="display: flex; align-items: center; gap: 0.75rem;">
                <div style="width: 2rem; height: 2rem; border-radius: 0.5rem; background: linear-gradient(to top right, #9333ea, #6366f1); display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; font-size: 0.875rem; box-shadow: 0 0 15px rgba(168,85,247,0.4);">
                    μS
                </div>
                <div>
                    <div style="font-size: 0.65rem; font-weight: 600; letter-spacing: 0.05em; text-transform: uppercase; color: #a1a1aa;">Microservice</div>
                    <div style="font-size: 0.875rem; font-weight: 500; color: white;">Passerelle Relation Client & LLM</div>
                </div>
            </div>
            <div style="display: flex; align-items: center; gap: 0.5rem; background-color: rgba(24,24,27,0.8); padding: 0.35rem 0.75rem; border-radius: 9999px; border: 1px solid rgba(255,255,255,0.08);">
                <span style="width: 0.5rem; height: 0.5rem; border-radius: 50%; background-color: #a855f7; display: inline-block;"></span>
                <span style="font-size: 0.75rem; font-weight: 500; color: #d4d4d8;">Actif</span>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# --- NAVIGATION PAR ONGLETS ---
tab_text, tab_pdf = st.tabs(["Flux Direct", "Document PDF"])

# ==========================================
# ONGLET 1 : FLUX DIRECT (TEXTE)
# ==========================================
with tab_text:
    col1, col2 = st.columns(2, gap="medium")

    with col1:
        st.markdown('<div class="glow-border">', unsafe_allow_html=True)
        col_title, col_clear = st.columns([4, 1])
        with col_title:
            st.markdown('<span style="font-size: 0.70rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #a1a1aa;">Entrée Source</span>', unsafe_allow_html=True)
        with col_clear:
            if st.button("Effacer", key="clearTextBtn"):
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

        if st.button("Sécuriser le contenu", key="processTextBtn"):
            if raw_input.strip():
                with st.spinner("Traitement en cours..."):
                    res = RobustAnonymizationEngine.process_raw_text(raw_input)
                    st.session_state["sanitized_text"] = res["sanitized_text"]
                    st.session_state["encrypted_vault"] = res["encrypted_vault"]
                    st.session_state["entities_count"] = res["entities_count"]
                    st.session_state["restored_text"] = ""
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="glow-border">', unsafe_allow_html=True)
        col_out_title, col_copy = st.columns([4, 1])
        with col_out_title:
            entities_badge = f" • {st.session_state.get('entities_count', 0)} entité(s)" if st.session_state.get('entities_count') else ""
            st.markdown(f'<span style="font-size: 0.70rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #c084fc;">Sortie Protégée{entities_badge}</span>', unsafe_allow_html=True)
        with col_copy:
            # Note: Le bouton copier natif Streamlit ou texte brut
            pass

        sanitized_output = st.session_state.get("sanitized_text", "")
        display_box = sanitized_output if sanitized_output else "Le contenu neutralisé apparaîtra ici..."
        
        st.markdown(f"""
            <div class="code-font" style="height: 188px; font-size: 0.75rem; padding: 0.875rem; border-radius: 0.75rem; background-color: rgba(9,9,11,0.6); border: 1px solid rgba(255,255,255,0.08); color: {'#d4d4d8' if sanitized_output else '#52525b'}; overflow-y: auto; white-space: pre-wrap; line-height: 1.5; margin-bottom: 1rem;">
{display_box}
            </div>
        """, unsafe_allow_html=True)

        if st.button("Restitution locale", key="triggerRestoreBtn"):
            if st.session_state.get("encrypted_vault") and st.session_state.get("sanitized_text"):
                with st.spinner("Restauration..."):
                    restored = RobustAnonymizationEngine.rehydrate_text(
                        st.session_state["sanitized_text"],
                        st.session_state["encrypted_vault"]
                    )
                    st.session_state["restored_text"] = restored
            else:
                st.warning("Aucun contenu sécurisé en mémoire.")
        st.markdown('</div>', unsafe_allow_html=True)

    # Bloc de contenu restitué (si actif)
    if st.session_state.get("restored_text"):
        st.markdown(f"""
            <div style="background-color: #0D0D12; border-radius: 1rem; padding: 1.25rem; border: 1px solid rgba(16,185,129,0.2); box-shadow: 0 0 20px rgba(16,185,129,0.04); margin-top: 1.5rem;">
                <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem;">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="width: 0.375rem; height: 0.375rem; border-radius: 50%; background-color: #10b981;"></span>
                        <span style="font-size: 0.70rem; font-weight: 600; color: #34d399; text-transform: uppercase; letter-spacing: 0.05em;">Contenu Reconstitué</span>
                    </div>
                    <span style="font-size: 0.65rem; color: #71717a;">Validation d'intégrité terminée</span>
                </div>
                <div style="font-size: 0.75rem; padding: 1rem; border-radius: 0.75rem; background-color: rgba(9,9,11,0.8); border: 1px solid rgba(255,255,255,0.06); color: #e4e4e7; white-space: pre-wrap; line-height: 1.5;">
{st.session_state["restored_text"]}
                </div>
            </div>
        """, unsafe_allow_html=True)


# ==========================================
# ONGLET 2 : DOCUMENT PDF
# ==========================================
with tab_pdf:
    st.markdown('<div class="glow-border" style="padding: 2rem;">', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Sélectionner ou glisser un fichier PDF", type=["pdf"], label_visibility="collapsed")

    if uploaded_file is not None:
        file_bytes = uploaded_file.read()
        
        with st.spinner("Génération du document sécurisé (Biffure vectorielle sans rétention)..."):
            temp_input = os.path.join(STORAGE_DIR, f"raw_{uploaded_file.name}")
            output_name = f"sanitized_{uploaded_file.name}"
            temp_output = os.path.join(STORAGE_DIR, output_name)

            with open(temp_input, "wb") as f:
                f.write(file_bytes)

            try:
                RobustAnonymizationEngine.process_pdf(temp_input, temp_output)
                st.session_state["pdf_output_path"] = temp_output
                st.session_state["pdf_filename"] = output_name
            except Exception as e:
                st.error(f"Erreur de traitement PDF : {str(e)}")

        if "pdf_output_path" in st.session_state and os.path.exists(st.session_state["pdf_output_path"]):
            st.markdown(f"""
                <div style="border: 1px solid rgba(255,255,255,0.08); border-radius: 0.75rem; padding: 1.25rem; background-color: rgba(9,9,11,0.6); margin-top: 1rem;">
                    <div style="display: flex; align-items: center; justify-content: space-between;">
                        <div style="display: flex; align-items: center; gap: 0.75rem;">
                            <div style="width: 2.25rem; height: 2.25rem; border-radius: 0.5rem; background-color: rgba(168,85,247,0.1); border: 1px solid rgba(168,85,247,0.2); display: flex; align-items: center; justify-content: center; font-size: 0.65rem; font-weight: bold; color: #c084fc;">
                                PDF
                            </div>
                            <div>
                                <div style="font-size: 0.75rem; font-weight: 600; color: #e4e4e7;">{uploaded_file.name}</div>
                                <div style="font-size: 0.65rem; color: #34d399; display: flex; align-items: center; gap: 0.35rem; margin-top: 0.15rem;">
                                    <span style="width: 0.375rem; height: 0.375rem; border-radius: 50%; background-color: #34d399;"></span>
                                    <span>Prêt pour transmission</span>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            with open(st.session_state["pdf_output_path"], "rb") as pdf_file:
                st.download_button(
                    label="Télécharger le PDF sécurisé",
                    data=pdf_file,
                    file_name=st.session_state["pdf_filename"],
                    mime="application/pdf",
                    key="download_pdf_btn"
                )

            if st.button("Supprimer / Réinitialiser", key="reset_pdf_btn"):
                for p in [st.session_state["pdf_output_path"], os.path.join(STORAGE_DIR, f"raw_{uploaded_file.name}")]:
                    if os.path.exists(p):
                        try:
                            os.remove(p)
                        except OSError:
                            pass
                for key in ["pdf_output_path", "pdf_filename"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

# --- FOOTER ---
st.markdown("""
    <div style="border-top: 1px solid rgba(255,255,255,0.05); padding: 1.5rem 0; margin-top: 3rem; background-color: #070709;">
        <div style="max-width: 56rem; margin: 0 auto; display: flex; align-items: center; justify-content: space-between; font-size: 0.7rem; color: #71717a; padding: 0 1.5rem;">
            <span>Passerelle Cryptographique Souveraine</span>
            <span>Protocole AES-256-GCM</span>
        </div>
    </div>
""", unsafe_allow_html=True)
