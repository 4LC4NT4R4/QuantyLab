# quanty_sim/main.py

from typing import Union, Literal, overload
from .xas_quanty import XAS_sim
from .rixs_quanty import RIXS_sim


class Simulation:

    """
    Factory class to create spectroscopy simulations for Co²⁺ in different symmetries.

    Parameters
    ----------
    element : str, optional
        Chemical element. Only 'Co' is supported. Default is 'Co'.
    valence : str, optional
        Oxidation state. Only '2+' is supported. Default is '2+'.
    experiment : str, optional
        Type of spectroscopy experiment: 'xas' or 'rixs'. Default is 'xas'.
    symmetry : str, optional
        Local symmetry of the system: 'Oh' or 'D4h'. Default is 'Oh'.
    **kwargs : dict
        Additional keyword arguments passed to XAS_sim or RIXS_sim.

    Returns
    -------
    XAS_sim or RIXS_sim
        An instance of the corresponding simulation class.

    Raises
    ------
    ValueError
        If any of the input parameters are not among the allowed values.

    Example
    -------
    >>> sim = Simulation(element='Co', valence='2+', experiment='xas', symmetry='Oh')
    """


    ALLOWED_ELEMENTS = ["Co"]
    ALLOWED_VALENCES = ["2+"]
    ALLOWED_EXPERIMENTS = ["xas", "rixs"]
    ALLOWED_SYMMETRIES = ["Oh", "D4h"]

    # ------------------------------------------------------------------
    # SOBRECARGAS (OVERLOADS) - Isso é para a IDE entender!
    # ------------------------------------------------------------------
    
    # Dica 1: Se experiment for 'xas', retorna XAS_sim
    @overload
    def __new__(cls, element='Co', valence='2+', experiment: Literal['xas'] = 'xas', symmetry='Oh', **kwargs) -> XAS_sim: ...

    # Dica 2: Se experiment for 'rixs', retorna RIXS_sim
    @overload
    def __new__(cls, element='Co', valence='2+', experiment: Literal['rixs'] = 'rixs', symmetry='Oh', **kwargs) -> RIXS_sim: ...

    # Dica 3: Caso genérico (retorna um ou outro)
    @overload
    def __new__(cls, element='Co', valence='2+', experiment: str = 'xas', symmetry='Oh', **kwargs) -> Union[XAS_sim, RIXS_sim]: ...

    # ------------------------------------------------------------------
    # IMPLEMENTAÇÃO REAL
    # ------------------------------------------------------------------
    def __new__(cls, element='Co', valence='2+', experiment='xas', symmetry='Oh', **kwargs):
        
        # --- Validação de Inputs ---
        if element not in cls.ALLOWED_ELEMENTS:
            raise ValueError(f"Element '{element}' not supported. Allowed: {cls.ALLOWED_ELEMENTS}")
        
        if valence not in cls.ALLOWED_VALENCES:
            raise ValueError(f"Valence '{valence}' not supported. Allowed: {cls.ALLOWED_VALENCES}")
        
        experiment_lower = experiment.lower()
        if experiment_lower not in cls.ALLOWED_EXPERIMENTS:
            raise ValueError(f"Experiment '{experiment}' not supported. Allowed: {cls.ALLOWED_EXPERIMENTS}")
        
        if symmetry not in cls.ALLOWED_SYMMETRIES:
            raise ValueError(f"Symmetry '{symmetry}' not supported. Allowed: {cls.ALLOWED_SYMMETRIES}")

        # --- Instancia a simulação real ---
        if experiment_lower == 'xas':
            return XAS_sim(symmetry=symmetry, **kwargs)
        else:
            return RIXS_sim(symmetry=symmetry, **kwargs)


