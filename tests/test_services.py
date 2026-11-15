import pytest
from models import SessionLocal, Salle, Enseignant, Groupe, Module, Cours, init_db
from services import verifier_conflits_complets

# On initialise la base (crée les tables si elles n'existent pas)
init_db()

@pytest.fixture(autouse=True)
def setup_and_teardown():
    """Fixture qui nettoie la base AVANT et APRES chaque test."""
    db = SessionLocal()
    # Nettoyage total
    db.query(Cours).delete()
    db.query(Salle).delete()
    db.query(Enseignant).delete()
    db.query(Groupe).delete()
    db.query(Module).delete()
    db.commit()
    
    # Création de données de base pour les tests
    db.add_all([
        Salle(id=1, nom="Amphi", capacite=100, type_salle="Amphi"),
        Salle(id=2, nom="TD1", capacite=30, type_salle="TD"),
        Salle(id=3, nom="Labo", capacite=20, type_salle="TP"),
        Enseignant(id=1, nom="Prof1"),
        Enseignant(id=2, nom="Prof2"),
        Groupe(id=1, nom="G1", effectif=20),
        Groupe(id=2, nom="G2", effectif=20),
        Module(id=1, nom="DevOps"),
        Module(id=2, nom="Maths")
    ])
    db.commit()
    db.close()
    
    yield  # C'est ici que le test s'exécute
    
    # Nettoyage après le test
    db = SessionLocal()
    db.query(Cours).delete()
    db.commit()
    db.close()

def test_pas_de_conflit():
    """Vérifie qu'un créneau vide n'a pas de conflit."""
    conflits = verifier_conflits_complets(salle_id=1, enseignant_id=1, groupe_id=1, jour="Lundi", heure="08:00-10:00")
    assert len(conflits) == 0

def test_conflit_salle():
    """Vérifie qu'on détecte bien une salle occupée."""
    db = SessionLocal()
    db.add(Cours(salle_id=1, enseignant_id=1, groupe_id=1, module_id=1, jour="Mardi", heure="10:00-12:00"))
    db.commit()
    db.close()
    
    # On essaie d'ajouter un autre cours dans la même salle, même jour, même heure
    conflits = verifier_conflits_complets(salle_id=1, enseignant_id=2, groupe_id=2, jour="Mardi", heure="10:00-12:00")
    assert any("salle" in c.lower() and "occup" in c.lower() for c in conflits)

def test_conflit_enseignant():
    """Vérifie qu'on détecte bien un enseignant occupé."""
    db = SessionLocal()
    db.add(Cours(salle_id=2, enseignant_id=1, groupe_id=2, module_id=1, jour="Mercredi", heure="14:00-16:00"))
    db.commit()
    db.close()
    
    conflits = verifier_conflits_complets(salle_id=1, enseignant_id=1, groupe_id=1, jour="Mercredi", heure="14:00-16:00")
    assert any("enseignant" in c.lower() and "occup" in c.lower() for c in conflits)

def test_conflit_groupe():
    """Vérifie qu'on détecte bien un groupe occupé."""
    db = SessionLocal()
    db.add(Cours(salle_id=3, enseignant_id=2, groupe_id=1, module_id=2, jour="Jeudi", heure="08:00-10:00"))
    db.commit()
    db.close()
    
    conflits = verifier_conflits_complets(salle_id=1, enseignant_id=1, groupe_id=1, jour="Jeudi", heure="08:00-10:00")
    assert any("groupe" in c.lower() and ("déjà" in c.lower() or "occup" in c.lower()) for c in conflits)

def test_conflit_capacite():
    """Vérifie qu'on détecte une salle trop petite."""
    db = SessionLocal()
    # On crée une petite salle et un grand groupe
    db.add(Salle(id=99, nom="Petite", capacite=10, type_salle="TD"))
    db.add(Groupe(id=99, nom="Grand", effectif=50))
    db.commit()
    db.close()
    
    conflits = verifier_conflits_complets(salle_id=99, enseignant_id=1, groupe_id=99, jour="Vendredi", heure="16:00-18:00")
    assert any("Capacité insuffisante" in c for c in conflits)