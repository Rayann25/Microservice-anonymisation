import streamlit as st
import tempfile
import os
from src.engine import RobustAnonymizationEngine

st.set_page_config(
    page_title="Passerelle Relation Client & LLM",
    page_icon="🛡️",
    layout="wide"
)

# Style CSS personnalisé pour coller pixel par pixel à ton design d'origine
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f8fafc;
    }
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    .main-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: #121826;
        padding: 15px 25px;
        border-radius: 12px;
        border: 1px solid #1f293d;
        margin-bottom: 25px;
    }
    .badge-mu {
        background: #7c3aed;
        color: white;
        padding: 6px 12px;
        border-radius: 8px;
        font-weight: bold;
        font-family: monospace;
    }
    .active-pill {
        background: rgba(124, 58, 237, 0.2);
        color: #a78bfa;
        border: 1px solid #7c3aed;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .custom-card {
        background: #121826;
        border: 1px solid #1f293d;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
    }
    .card-title {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.05em;
        margin-bottom: 12px;
        display: flex;
        justify-content: space-between;
    }
    .stButton>button {
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        width: 100%;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #6d28d9, #4338ca);
    }
    /* Style des onglets / radios */
    .stRadio > div {
        background-color: #121826;
        border: 1px solid #1f293d;
        padding: 6px;
        border-radius: 12px;
        display: inline-flex;
    }
    </style>
""", unsafe_allow_html=True)

@st.cache_resource
def get_engine():
    return RobustAnonymizationEngine()

# En-tête supérieur
st.markdown("""
    <div class="main-header">
        <div style="display: flex; align-items: center; gap: 15px;">
            <div class="badge-mu">μS</div>
            <div>
                <div style="font-size: 0.70rem; color: #94a3b8; letter-spacing: 0.1em; font-weight: bold;">MICROSERVICE</div>
                <div style="font-size: 1.1rem; font-weight: bold; color: #ffffff;">Passerelle Relation Client & LLM</div>
            </div>
        </div>
        <div>
            <span class="active-pill">● Actif</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sélecteur de mode (Flux Direct / Document PDF)
nav_mode = st.radio("Navigation", ["Flux Direct", "Document PDF"], horizontal=True, label_visibility="collapsed")

if "Flux" in nav_mode:
    col1, col2 = st.columns(2, gap="large")
    
    with col1:
        st.markdown("""
            <div class="custom-card" style="margin-bottom:0px; border-bottom:none; border-bottom-left-radius:0; border-bottom-right-radius:0; padding-bottom:5px;">
                <div class="card-title"><span>ENTRÉE SOURCE</span><span style="color:#64748b; font-weight:normal;">Effacer</span></div>
            </div>
        """, unsafe_allow_html=True)
        
        user_text = st.text_area("Entrée source", height=240, placeholder="Saisissez ou collez ici la communication...", label_visibility="collapsed")
        
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("Sécuriser le contenu"):
            if user_text.strip():
                try:
                    engine = get_engine()
                    res = engine.process_raw_text(user_text)
                    st.session_state["sanitized_text"] = res["sanitized_text"]
                    st.session_state["vault_data"] = res["encrypted_vault"]
                    st.success("Contenu sécurisé avec succès !")
                except Exception as e:
                    st.error(f"Erreur : {e}")
            else:
                st.warning("Veuillez saisir du texte.")

    with col2:
        st.markdown("""
            <div class="custom-card" style="margin-bottom:0px; border-bottom:none; border-bottom-left-radius:0; border-bottom-right-radius:0; padding-bottom:5px;">
                <div class="card-title"><span>SORTIE PROTÉGÉE</span><span style="color:#64748b; font-weight:normal;">Copier</span></div>
            </div>
        """, unsafe_allow_html=True)
        
        display_text = st.session_state.get("sanitized_text", "Le contenu neutralisé apparaîtra ici...")
        st.text_area("Sortie protégée", value=display_text, height=240, disabled=True, label_visibility="collapsed")
        
        st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
        if st.button("Restitution locale"):
            if "sanitized_text" in st.session_state and "vault_data" in st.session_state:
                try:
                    engine = get_engine()
                    rehydrated = engine.rehydrate_text(st.session_state["sanitized_text"], st.session_state["vault_data"])
                    st.info(f"Restitution : {rehydrated}")
                except Exception as e:
                    st.error(f"Erreur de restitution : {e}")
            else:
                st.warning("Aucun coffre actif en session.")

else:
    st.markdown("""
        <div class="custom-card">
            <div class="card-title"><span>TRAITEMENT DE DOCUMENT PDF (Biffure)</span></div>
        </div>
    """, unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Sélectionnez votre fichier PDF", type=["pdf"])
    if uploaded_file is not None:
        if st.button("Lancer la biffure souveraine du PDF"):
            try:
                engine = get_engine()
                pdf_bytes = uploaded_file.read()
                result = engine.process_pdf(pdf_bytes)
                st.success("Document PDF biffé et sécurisé avec succès !")
                with open(result["output_pdf"], "rb") as f:
                    st.download_button(
                        label="📥 Télécharger le PDF sécurisé",
                        data=f,
                        file_name="secured_document.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"Erreur lors du traitement du PDF : {e}")

# Pied de page (Footer identique à l'image)
st.markdown("""
    <div style="display: flex; justify-content: space-between; color: #64748b; font-size: 0.8rem; margin-top: 50px; border-top: 1px solid #1f293d; padding-top: 15px;">
        <span>Passerelle Cryptographique Souveraine</span>
        <span>Protocole AES-256-GCM</span>
    </div>
""", unsafe_allow_html=True)
