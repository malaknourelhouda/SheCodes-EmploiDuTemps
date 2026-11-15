from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# Connexion à la base de données
DATABASE_URL = f"postgresql+psycopg2://{os.getenv('DB_USER', 'admin')}:{os.getenv('DB_PASSWORD', 'admin123')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '5432')}/{os.getenv('DB_NAME', 'edt_db')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- LES TABLES (Le référentiel) ---
class Salle(Base):
    __tablename__ = "salles"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, index=True)
    capacite = Column(Integer)
    type_salle = Column(String) # Amphi, TD, TP

class Enseignant(Base):
    __tablename__ = "enseignants"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, index=True)

class Groupe(Base):
    __tablename__ = "groupes"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, index=True)
    effectif = Column(Integer, default=30)

class Module(Base):
    __tablename__ = "modules"
    id = Column(Integer, primary_key=True, index=True)
    nom = Column(String, unique=True, index=True)
    volume_horaire = Column(Integer, default=0)

# --- LA TABLE CENTRALE (Les séances) ---
class Cours(Base):
    __tablename__ = "cours"
    id = Column(Integer, primary_key=True, index=True)
    salle_id = Column(Integer, ForeignKey("salles.id"))
    enseignant_id = Column(Integer, ForeignKey("enseignants.id"))
    groupe_id = Column(Integer, ForeignKey("groupes.id"))
    module_id = Column(Integer, ForeignKey("modules.id"))
    jour = Column(String)
    heure = Column(String)

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()