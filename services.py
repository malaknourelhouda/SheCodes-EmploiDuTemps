from models import SessionLocal, Salle, Enseignant, Groupe, Module, Cours

def verifier_conflits_complets(salle_id, enseignant_id, groupe_id, jour, heure):
    db = SessionLocal()
    conflits = []

    # 1. Le professeur est-il déjà occupé ?
    if db.query(Cours).filter(Cours.enseignant_id == enseignant_id, Cours.jour == jour, Cours.heure == heure).first():
        conflits.append("L'enseignant est déjà occupé à ce créneau.")

    # 2. La salle est-elle déjà occupée ?
    if db.query(Cours).filter(Cours.salle_id == salle_id, Cours.jour == jour, Cours.heure == heure).first():
        conflits.append("La salle est déjà occupée à ce créneau.")

    # 3. Le groupe a-t-il déjà cours ?
    if db.query(Cours).filter(Cours.groupe_id == groupe_id, Cours.jour == jour, Cours.heure == heure).first():
        conflits.append("Le groupe a déjà un cours à ce créneau.")

    # 4. La salle est-elle assez grande ? (Capacité)
    salle = db.query(Salle).filter(Salle.id == salle_id).first()
    groupe = db.query(Groupe).filter(Groupe.id == groupe_id).first()
    if salle and groupe and salle.capacite < groupe.effectif:
        conflits.append(f"Capacité insuffisante : Salle ({salle.capacite}) < Groupe ({groupe.effectif}).")

    db.close()
    return conflits

def ajouter_cours(salle_id, enseignant_id, groupe_id, module_id, jour, heure):
    db = SessionLocal()
    nouveau_cours = Cours(
        salle_id=salle_id, enseignant_id=enseignant_id, groupe_id=groupe_id,
        module_id=module_id, jour=jour, heure=heure
    )
    db.add(nouveau_cours)
    db.commit()
    db.close()