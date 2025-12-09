# quanty_sim/__init__.py

# Expõe as classes principais para quem importar o pacote
from .main import Simulation
from .xas_quanty import XAS_sim
from .rixs_quanty import RIXS_sim
from .readers import xas_sim, rixs_sim, emap_sim

# Define o que é exportado quando alguém faz "from quanty_sim import *"
__all__ = [
    'Simulation',
    'XAS_sim',
    'RIXS_sim',
    'xas_sim',
    'rixs_sim',
    'emap_sim'
]