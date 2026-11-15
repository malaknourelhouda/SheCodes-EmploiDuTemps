import streamlit as st
import pandas as pd
from models import init_db, SessionLocal, Salle, Enseignant, Groupe, Module, Cours
from services import verifier_conflits_complets, ajouter_cours

st.set_page_config(page_title="SheCodes EDT Pro", layout="wide")
init_db()

st.title("📅 Gestion des Emplois du Temps - Version Pro")

# --- INITIALISATION DES DONNÉES DE DÉMONSTRATION (SEED) ---
db = SessionLocal()
if db.query(Salle).count() == 0:
    db.add_all([
        Salle(nom="Amphi A", capacite=150, type_salle="Amphi"),
        Salle(nom="Salle TD 1", capacite=30, type_salle="TD"),
        Salle(nom="Labo Info", capacite=20, type_salle="TP")
    ])
    db.add_all([Enseignant(nom="M. Dupont"), Enseignant(nom="Mme. Martin")])
    db.add_all([Groupe(nom="G1", effectif=25), Groupe(nom="G2", effectif=15)])
    db.add_all([Module(nom="DevOps"), Module(nom="Algorithmique")])
    db.commit()

# Récupération des données pour les menus
salles = db.query(Salle).all()
profs = db.query(Enseignant).all()
groupes = db.query(Groupe).all()
modules = db.query(Module).all()
db.close()

# --- INTERFACE ---
tab1, tab2, tab3 = st.tabs(["📅 Emploi du temps", "⚙️ Référentiels", "📊 Statistiques"])

with tab1:
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Ajouter un cours")
        with st.form("form_cours"):
            salle = st.selectbox("Salle", salles, format_func=lambda x: f"{x.nom} (Cap: {x.capacite})")
            prof = st.selectbox("Enseignant", profs, format_func=lambda x: x.nom)
            groupe = st.selectbox("Groupe", groupes, format_func=lambda x: f"{x.nom} (Eff: {x.effectif})")
            module = st.selectbox("Module", modules, format_func=lambda x: x.nom)
            jour = st.selectbox("Jour", ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi"])
            heure = st.selectbox("Heure", ["08:00-10:00", "10:00-12:00", "14:00-16:00", "16:00-18:00"])
            
            submit = st.form_submit_button("Vérifier et Ajouter")
            
            if submit:
                conflits = verifier_conflits_complets(salle.id, prof.id, groupe.id, jour, heure)
                if conflits:
                    for c in conflits:
                        st.error(f"❌ {c}")
                else:
                    ajouter_cours(salle.id, prof.id, groupe.id, module.id, jour, heure)
                    st.success("✅ Cours ajouté sans conflit !")
                    st.rerun()

    with col2:
        st.subheader("Planning actuel")
        # On affiche le planning sous forme de tableau
        db = SessionLocal()
        query = db.query(Cours, Salle, Enseignant, Groupe, Module)\
                  .join(Salle, Cours.salle_id == Salle.id)\
                  .join(Enseignant, Cours.enseignant_id == Enseignant.id)\
                  .join(Groupe, Cours.groupe_id == Groupe.id)\
                  .join(Module, Cours.module_id == Module.id).all()
        
        data = []
        for c, s, e, g, m in query:
            data.append({"Jour": c.jour, "Heure": c.heure, "Module": m.nom, "Enseignant": e.nom, "Groupe": g.nom, "Salle": s.nom})
        db.close()
        
        if data:
            st.dataframe(pd.DataFrame(data), use_container_width=True)
        else:
            st.info("Aucun cours planifié pour le moment.")

with tab2:
    st.subheader("Importer des données via CSV")
    uploaded_file = st.file_uploader("Choisir un fichier CSV (colonnes: nom, capacite, type_salle)", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        db = SessionLocal()
        for _, row in df.iterrows():
            try:
                db.add(Salle(nom=row['nom'], capacite=int(row['capacite']), type_salle=row['type_salle']))
                db.commit()
            except:
                db.rollback()
        db.close()
        st.success("Importation terminée !")
        st.rerun()

with tab3:
    st.subheader("Occupation des salles")
    db = SessionLocal()
    query = db.query(Salle.nom, db.query(Cours).filter(Cours.salle_id == Salle.id).count())\
              if False else None # placeholder
    
    # Requête simple pour le graphique
    from sqlalchemy import func
    stats = db.query(Salle.nom, func.count(Cours.id)).outerjoin(Cours).group_by(Salle.nom).all()
    db.close()
    
    df_stats = pd.DataFrame(stats, columns=["Salle", "Nombre de cours"])
    st.bar_chart(df_stats.set_index("Salle"))