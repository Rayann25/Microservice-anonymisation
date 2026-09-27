import streamlit as st
from src.engine import RobustAnonymizationEngine

# Configuration de la page Streamlit (Mode sombre natif)
st.set_page_config(
    page_title="Zero-Knowledge Gateway",
    page_icon="🔒",
    layout="wide"
)

# Style personnalisé (Dark mode violet souverain)
st.markdown("""
    <style>
    .main {
        background-color: #0e1117;
        color: #f8fafc;
    }
    .stButton>button {
        background: linear-gradient(135deg, #7c3aed, #4f46e5);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #6d28d9, #4338ca);
    }
    </style>
""", unsafe_allow_html=True)

st.title("🔒 Zero-Knowledge Gateway")
st.markdown("### Passerelle souveraine de pseudonymisation bidirectionnelle & Traduction locale")

# Onglets principaux
tab1, tab2 = st.tabs(["💬 Anonymisation de Texte", "🌍 Traduction Hors-Ligne"])

with tab1:
    st.subheader("Traitement sécurisé des données textuelles")
    user_text = st.text_area("Entrez le texte sensible à pseudonymiser :", height=150, placeholder="Ex: Contrat avec Antoine Delaunay, SIRET 802 954 785 00027...")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Anonymiser et Sécuriser"):
            if user_text.strip():
                with st.spinner("Analyse sémantique GLiNER et validation arithmétique en cours..."):
                    sanitized, vault_id = RobustAnonymizationEngine.sanitize_text(user_text)
                    st.session_state["last_sanitized"] = sanitized
                    st.session_state["last_vault_id"] = vault_id
                st.success("Données pseudonymisées avec succès !")
                st.markdown(f"**Texte masqué envoyé au LLM :**")
                st.code(sanitized, language="text")
                st.info(f"🔑 ID du Coffre AES-256-GCM : `{vault_id}`")
            else:
                st.warning("Veuillez entrer du texte.")

    with col2:
        if "last_sanitized" in st.session_state:
            if st.button("🔄 Ré-hydrater (Restaurer les données)"):
                with st.spinner("Déchiffrement local du coffre..."):
                    rehydrated = RobustAnonymizationEngine.rehydrate_text(
                        st.session_state["last_sanitized"], 
                        st.session_state["last_vault_id"]
                    )
                st.success("Données restaurées avec succès !")
                st.markdown(f"**Texte original ré-hydraté :**")
                st.code(rehydrated, language="text")

with tab2:
    st.subheader("Traduction locale hors-ligne (MarianMT / Helsinki-NLP)")
    text_to_translate = st.text_area("Entrez le texte en français à traduire en anglais :", height=100)
    if st.button("🌐 Traduire localement sans cloud"):
        if text_to_translate.strip():
            with st.spinner("Chargement du modèle de traduction local..."):
                translated = RobustAnonymizationEngine.translate_locally(text_to_translate)
            st.success("Traduction effectuée en local !")
            st.code(translated, language="text")
        else:
            st.warning("Veuillez entrer du texte à traduire.")
