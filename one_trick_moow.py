import streamlit as st
import pandas as pd
import io
import base64

# Configuration de la page
st.set_page_config(
    page_title="One trick MOOW",
    page_icon="🐮",
    layout="wide",
)

# Fonction pour charger les données depuis un fichier CSV/Excel
def load_data(file):
    try:
        if file.name.endswith('.csv'):
            df = pd.read_csv(file, sep=None, engine='python')
        elif file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(file)
        else:
            st.error("Format de fichier non supporté. Veuillez charger un fichier CSV ou Excel.")
            return None
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement du fichier : {e}")
        return None

# Fonction pour générer des liens de téléchargement
def get_download_link(df, filename):
    csv_buffer = io.BytesIO()
    excel_buffer = io.BytesIO()
    
    df.to_csv(csv_buffer, index=False)
    df.to_excel(excel_buffer, index=False)
    
    csv_b64 = base64.b64encode(csv_buffer.getvalue()).decode()
    excel_b64 = base64.b64encode(excel_buffer.getvalue()).decode()
    
    csv_link = f'<a href="data:file/csv;base64,{csv_b64}" download="{filename}.csv">Télécharger en CSV</a>'
    excel_link = f'<a href="data:file/excel;base64,{excel_b64}" download="{filename}.xlsx">Télécharger en Excel</a>'
    
    return csv_link, excel_link

# Titre principal de l'application
st.title("One Trick MOOW")

# Création des onglets pour chaque consortium
tabs = st.tabs(["Consortium MOOW Pro", "Consortium MOOW Sup"])

# Fonction pour traiter un onglet (pour éviter la redondance)
def process_tab(consortium_name, file_key, pays_key, status_key, etab_key):
    st.header(consortium_name)
    data_file = st.file_uploader("Téléchargez le fichier de données", type=["csv", "xlsx", "xls"], key=file_key)
    
    if data_file is not None:
        df = load_data(data_file)
        if df is not None:
            # Affichage du nombre total d'enregistrements chargés
            total_records = len(df)
            st.write(f"Nombre total d'enregistrements chargés : {total_records}")
            
            # Variable pour suivre les enregistrements après filtrage
            filtered_df = df.copy()
            
            # Filtrage par pays (colonne 'pays_accueil') avec "Tous les Pays" en option initiale
            if "pays_accueil" in df.columns:
                pays_options = sorted(df["pays_accueil"].dropna().unique().tolist())
                pays_options = ["Tous les Pays"] + pays_options
                selected_pays = st.selectbox("Sélectionnez le pays", options=pays_options, key=pays_key)
                if selected_pays != "Tous les Pays":
                    filtered_df = filtered_df[filtered_df["pays_accueil"] == selected_pays]
                    # Affichage du nombre après filtrage par pays
                    st.write(f"Nombre d'enregistrements pour le pays '{selected_pays}' : {len(filtered_df)}")
            else:
                st.warning("La colonne 'pays_accueil' est absente du fichier.")
            
            # Filtrage par statut participant (colonne 'statut_participant') avec option "Tous"
            if "statut_participant" in df.columns:
                status_options = sorted(df["statut_participant"].dropna().unique().tolist())
                status_options = ["Tous"] + status_options
                selected_status = st.selectbox("Sélectionnez le statut participant", options=status_options, key=status_key)
                if selected_status != "Tous":
                    filtered_df = filtered_df[filtered_df["statut_participant"] == selected_status]
                    # Affichage du nombre après filtrage par statut
                    st.write(f"Nombre d'enregistrements pour le statut '{selected_status}' : {len(filtered_df)}")
            else:
                st.warning("La colonne 'statut_participant' est absente du fichier.")
            
            # Filtrage par établissement
            # On vérifie la présence de la colonne EPLEFPA ou etablissement et on utilise celle disponible
            if "EPLEFPA" in df.columns:
                etab_col = "EPLEFPA"
            elif "etablissement" in df.columns:
                etab_col = "etablissement"
            else:
                st.error("Aucune colonne 'EPLEFPA' ni 'etablissement' n'a été trouvée dans le fichier.")
                return
            
            etab_values = sorted(filtered_df[etab_col].dropna().unique().tolist())
            etab_options = ["Tous"] + etab_values
            selected_etab = st.selectbox("Sélectionnez l'établissement", options=etab_options, key=etab_key)
            if selected_etab != "Tous":
                filtered_df = filtered_df[filtered_df[etab_col] == selected_etab]
                # Affichage du nombre après filtrage par établissement
                st.write(f"Nombre d'enregistrements pour l'établissement '{selected_etab}' : {len(filtered_df)}")
            
            # Affichage du nombre total après tous les filtrages
            st.write(f"Nombre total d'enregistrements après filtrage : {len(filtered_df)}")
            
            # Vérification des colonnes requises pour l'affichage
            required_columns = ["pays_accueil", etab_col, "demandeur_siret", "statut_participant"]
            missing_cols = [col for col in required_columns if col not in filtered_df.columns]
            if missing_cols:
                st.error(f"Les colonnes suivantes sont manquantes : {', '.join(missing_cols)}")
            else:
                # Préparation du tableau final
                display_df = filtered_df[required_columns].copy()
                display_df.columns = ["Pays", "Etablissement", "SIRET", "Statut participant"]
                st.dataframe(display_df)
                
                # Génération des liens de téléchargement
                filename = f"{consortium_name.replace(' ', '_')}_{selected_pays if selected_pays != 'Tous les Pays' else 'TousLesPays'}_{selected_status if selected_status != 'Tous' else 'TousStatuts'}_{selected_etab if selected_etab != 'Tous' else 'TousEtablissements'}"
                csv_link, excel_link = get_download_link(display_df, filename)
                st.markdown(f"{csv_link} | {excel_link}", unsafe_allow_html=True)
    else:
        st.info(f"Veuillez télécharger un fichier de données pour le {consortium_name}.")

# Traitement des onglets
with tabs[0]:
    process_tab("Consortium MOOW Pro", "pro_file", "pays_pro", "status_pro", "etab_pro")

with tabs[1]:
    process_tab("Consortium MOOW Sup", "sup_file", "pays_sup", "status_sup", "etab_sup")

st.markdown("---")
st.markdown("© 2025 - Paradigme Heuristique de Décryptage Cognitif d'impact de MOOW")
