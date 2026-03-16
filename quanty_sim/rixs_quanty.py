#!/usr/bin/env python
# coding: utf-8

# Libraries
import os
import subprocess
import shutil
import copy
import math
import pandas as pd
import re
from io import StringIO
from pathlib import Path

# Importação para lidar com recursos do pacote
import importlib.resources

# Importação do Jinja
from jinja2 import Environment, PackageLoader, select_autoescape

# Nome do pacote onde estão os templates e o código
PACKAGE_NAME = 'quanty_sim'

# Configuração do Jinja2 para carregar templates do pacote
try:
    env = Environment(
        loader=PackageLoader(PACKAGE_NAME, 'Templates'),
        autoescape=False
    )
except ImportError:
    # Fallback para desenvolvimento local sem instalação
    print("⚠️ Aviso: Carregando Templates via sistema de arquivos (fallback).")
    from jinja2 import FileSystemLoader
    TEMPLATES_DIR = Path(__file__).parent / "Templates"
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=False)

# RIXS Simulation Class
class RIXS_sim:
    def __init__(self, symmetry='Oh', IncidentEnergy=None, filename='filename'):
        self.IncidentEnergy = IncidentEnergy
        self.filename = filename
        self.symmetry = symmetry
        self.CrystalField = {}
        self.LMCT = {}
        self.MLCT = {}
        self._set_symmetry(self.symmetry)


        self.Parameters = {
            "Experiment": {
                "Temperature": 10,
                "Linear": False,
                "Isotropic": True,
                "NConfigurations": 1,
                "SynchronizeHamiltonian": True,
                "NPsis": 120,
                "NPsisAuto": 'true',
            },
        
            "Energy": {
                    "Emin1": 768.0,
                    "Emax1": 808.0,
                    "NPoints1": 93,
                    "Gaussian1": 0.0,
                    "Gamma1": 0.43,
                
                    "Emin2": -7.0,
                    "Emax2": 33.0,
                    "NPoints2": 2000,
                    "Gaussian2": 0.0,
                    "Gamma2": 0.1
                },
        
            "Fields": {
                "Bx_i": 0.0, "By_i": 0.0, "Bz_i": 0.0,
                "Bx_m": 0.0, "By_m": 0.0, "Bz_m": 0.0,
                "Bx_f": 0.0, "By_f": 0.0, "Bz_f": 0.0,
                "Hx_i": 0.0, "Hy_i": 0.0, "Hz_i": 0.0,
                "Hx_m": 0.0, "Hy_m": 0.0, "Hz_m": 0.0,
                "Hx_f": 0.0, "Hy_f": 0.0, "Hz_f": 0.0,
            },
        
            "Geometry": {
                "WaveVectorIn": "{0, 0, 1}",
                "EhIn": "{0, 1, 0}",
                "EvIn": "{1, 0, 0}",
                "WaveVectorOut": "{0, 0, 1}",
                "EhOut": "{0, 1, 0}",
                "EvOut": "{1, 0, 0}"
            }
        }


        self.ScaleFactors={
            'Fk':0.8,
            'Gk':0.8,
            'zeta': 1.0

        }


        # Termos do Hamiltoniano
        self.HamiltonianTerms = {
            'AtomicTerm': 'true',
            'CrystalFieldTerm': 'false',
            'LmctLigandsHybridizationTerm': 'false',
            'MlctLigandsHybridizationTerm': 'false',
            'MagneticFieldTerm': 'false',
            'ExchangeFieldTerm': 'false'}

        self.InitialHamiltonian = {'U_3d_3d_i': 0.0, 'F2_3d_3d_i': 11.6047,
                                'F4_3d_3d_i': 7.2094, 'zeta_3d_i': 0.066}

        self.MiddleHamiltonian = {'U_3d_3d_m': 0.0, 'F2_3d_3d_m': 12.3956, 'F4_3d_3d_m': 7.7077,
                             'U_2p_3d_m' : 0.0,'F2_2p_3d_m' : 7.2601,'G1_2p_3d_m' : 5.3971,
                             'G3_2p_3d_m' : 3.0687, 'zeta_3d_m': 0.083, 'zeta_2p_m': 9.7475}

        self.FinalHamiltonian = {'U_3d_3d_f': 0.0, 'F2_3d_3d_f': 11.6047,
                                'F4_3d_3d_f': 7.2094, 'zeta_3d_f': 0.066}



        self.Electrons = {
            'NBosons': 0,
            'NFermions': 16,
            'NElectrons_2p': 6,
            'NElectrons_3d': 7,
            'IndexDn_2p' : '{0, 2, 4}',
            'IndexUp_2p' : '{1, 3, 5}',
            'IndexDn_3d' : '{6, 8, 10, 12, 14}',
            'IndexUp_3d' : '{7, 9, 11, 13, 15}',
            'NElectron_L1': 10,
            'IndexDn_L1' : '{16, 18, 20, 22, 24}',
            'IndexUp_L1' : '{17, 19, 21, 23, 25}',
            'NElectron_L2': 0,
            'IndexDn_L2' : '{16, 18, 20, 22, 24}',
            'IndexUp_L2' : '{17, 19, 21, 23, 25}'

        }


        self._defaults = {
            'Parameters': copy.deepcopy(self.Parameters),
            'ScaleFactors': copy.deepcopy(self.ScaleFactors),
            'CrystalField': copy.deepcopy(self.CrystalField),
            'LMCT': copy.deepcopy(self.LMCT),
            'MLCT': copy.deepcopy(self.MLCT),
            'HamiltonianTerms': copy.deepcopy(self.HamiltonianTerms),
            'InitialHamiltonian': copy.deepcopy(self.InitialHamiltonian),
            'MiddleHamiltonian': copy.deepcopy(self.MiddleHamiltonian),
            'FinalHamiltonian': copy.deepcopy(self.FinalHamiltonian),
            'Electrons': copy.deepcopy(self.Electrons)
        }
        self._verify()



    # def _set_symmetry(self, symmetry):
    #     self.symmetry = symmetry


    #     # Define o template automaticamente com base na simetria
    #     if symmetry == 'Oh':
    #         self.template_path = 'quanty_sim/Templates/Co2+_Oh_RIXS_2p3d.lua'
    #     elif symmetry == 'D4h':
    #         self.template_path = 'quanty_sim/Templates/Co2+_D4h_RIXS_2p3d.lua'
    #     else:
    #         raise ValueError(f"Simetria '{symmetry}' não reconhecida. Use 'Oh' ou 'D4h'.")



    #     if self.symmetry == 'Oh':
    #         self.CrystalField = {
    #             'tenDq_3d_i': 1.0,
    #             'tenDq_3d_m': 1.0,
    #             'tenDq_3d_f': 1.0,
    #         }
    
    #         self.LMCT = {
    #             'Delta_3d_L1_i': 0.0, 'Delta_3d_L1_m': 0.0, 'Delta_3d_L1_f': 0.0,
    #             'Dq_L1_i': 0.0, 'Vt2g_3d_L1_i': 0.0,
    #             'Dq_L1_m': 0.0, 'Vt2g_3d_L1_m': 0.0,
    #             'Dq_L1_f': 0.0, 'Vt2g_3d_L1_f': 0.0,
    #             'Veg_3d_L1_i': 0.0, 'Veg_3d_L1_m': 0.0, 'Veg_3d_L1_f': 0.0
    #         }
            
    
    #         self.MLCT = {
    #             'Delta_3d_L2_i': 0.0, 'Delta_3d_L2_m': 0.0, 'Delta_3d_L2_f': 0.0,
    #             'Dq_L2_i': 0.0, 'Vt2g_3d_L2_i': 0.0, 'Veg_3d_L2_i': 0.0,
    #             'Dq_L2_m': 0.0, 'Vt2g_3d_L2_m': 0.0, 'Veg_3d_L2_m': 0.0,
    #             'Dq_L2_f': 0.0, 'Vt2g_3d_L2_f': 0.0, 'Veg_3d_L2_f': 0.0
    #         }
    
    
        
        
    #     elif self.symmetry == 'D4h':
    #         self.CrystalField = {
    #             'tenDq_3d_i': 1.0, 'Ds_3d_i': 0.0, 'Dt_3d_i': 0.0,
    #             'tenDq_3d_m': 1.0, 'Ds_3d_m': 0.0, 'Dt_3d_m': 0.0,
    #             'tenDq_3d_f': 1.0, 'Ds_3d_f': 0.0, 'Dt_3d_f': 0.0
    #         }
            
    
    #         self.LMCT = {
    #             'Delta_3d_L1_i': 0.0, 'Delta_3d_L1_m': 0.0, 'Delta_3d_L1_f': 0.0,
    #             'Dq_L1_i': 0.0, 'Ds_L1_i': 0.0, 'Dt_L1_i': 0.0,
    #             'Dq_L1_m': 0.0, 'Ds_L1_m': 0.0, 'Dt_L1_m': 0.0,
    #             'Dq_L1_f': 0.0, 'Ds_L1_f': 0.0, 'Dt_L1_f': 0.0,
    #             'Va1g_3d_L1_i': 0.0, 'Va1g_3d_L1_m': 0.0, 'Va1g_3d_L1_f': 0.0,
    #             'Vb1g_3d_L1_i': 0.0, 'Vb1g_3d_L1_m': 0.0, 'Vb1g_3d_L1_f': 0.0,
    #             'Vb2g_3d_L1_i': 0.0, 'Vb2g_3d_L1_m': 0.0, 'Vb2g_3d_L1_f': 0.0,
    #             'Veg_3d_L1_i': 0.0, 'Veg_3d_L1_m': 0.0, 'Veg_3d_L1_f': 0.0
    #         }
    
    #         self.MLCT = {
    #             'Delta_3d_L2_i': 0.0, 'Delta_3d_L2_m': 0.0, 'Delta_3d_L2_f': 0.0,
    #             'Dq_L2_i': 0.0, 'Ds_L2_i': 0.0, 'Dt_L2_i': 0.0,
    #             'Dq_L2_m': 0.0, 'Ds_L2_m': 0.0, 'Dt_L2_m': 0.0,
    #             'Dq_L2_f': 0.0, 'Ds_L2_f': 0.0, 'Dt_L2_f': 0.0,
    #             'Va1g_3d_L2_i': 0.0, 'Va1g_3d_L2_m': 0.0, 'Va1g_3d_L2_f': 0.0,
    #             'Vb1g_3d_L2_i': 0.0, 'Vb1g_3d_L2_m': 0.0, 'Vb1g_3d_L2_f': 0.0,
    #             'Vb2g_3d_L2_i': 0.0, 'Vb2g_3d_L2_m': 0.0, 'Vb2g_3d_L2_f': 0.0,
    #             'Veg_3d_L2_i': 0.0, 'Veg_3d_L2_m': 0.0, 'Veg_3d_L2_f': 0.0
    #         }
        
        
    #     else:
    #         raise ValueError(f"Unsupported crystal symmetry: {self.symmetry}")

    def _set_symmetry(self, symmetry):
        self.symmetry = symmetry

        # Define o template automaticamente com base na simetria
        if symmetry == 'Oh':
            # note: armazenamos tanto template_path (possível caminho) quanto template_name (basename)
            self.template_path = 'quanty_sim/Templates/Co2+_Oh_RIXS_2p3d.lua'
            self.template_name = Path(self.template_path).name  # 'Co2+_Oh_RIXS_2p3d.lua'
        elif symmetry == 'D4h':
            self.template_path = 'quanty_sim/Templates/Co2+_D4h_RIXS_2p3d.lua'
            self.template_name = Path(self.template_path).name
        else:
            raise ValueError(f"Simetria '{symmetry}' não reconhecida. Use 'Oh' ou 'D4h'.")

        # agora configuramos os parâmetros específicos por simetria (mantive seu conteúdo)
        if self.symmetry == 'Oh':
            self.CrystalField = {
                'tenDq_3d_i': 1.0,
                'tenDq_3d_m': 1.0,
                'tenDq_3d_f': 1.0,
            }
            self.LMCT = {
                'Delta_3d_L1_i': 0.0, 'Delta_3d_L1_m': 0.0, 'Delta_3d_L1_f': 0.0,
                'Dq_L1_i': 0.0, 'Vt2g_3d_L1_i': 0.0,
                'Dq_L1_m': 0.0, 'Vt2g_3d_L1_m': 0.0,
                'Dq_L1_f': 0.0, 'Vt2g_3d_L1_f': 0.0,
                'Veg_3d_L1_i': 0.0, 'Veg_3d_L1_m': 0.0, 'Veg_3d_L1_f': 0.0
            }
            self.MLCT = {
                'Delta_3d_L2_i': 0.0, 'Delta_3d_L2_m': 0.0, 'Delta_3d_L2_f': 0.0,
                'Dq_L2_i': 0.0, 'Vt2g_3d_L2_i': 0.0, 'Veg_3d_L2_i': 0.0,
                'Dq_L2_m': 0.0, 'Vt2g_3d_L2_m': 0.0, 'Veg_3d_L2_m': 0.0,
                'Dq_L2_f': 0.0, 'Vt2g_3d_L2_f': 0.0, 'Veg_3d_L2_f': 0.0
            }

        elif self.symmetry == 'D4h':
            self.CrystalField = {
                'tenDq_3d_i': 1.0, 'Ds_3d_i': 0.0, 'Dt_3d_i': 0.0,
                'tenDq_3d_m': 1.0, 'Ds_3d_m': 0.0, 'Dt_3d_m': 0.0,
                'tenDq_3d_f': 1.0, 'Ds_3d_f': 0.0, 'Dt_3d_f': 0.0
            }
            self.LMCT = {
                'Delta_3d_L1_i': 0.0, 'Delta_3d_L1_m': 0.0, 'Delta_3d_L1_f': 0.0,
                'Dq_L1_i': 0.0, 'Ds_L1_i': 0.0, 'Dt_L1_i': 0.0,
                'Dq_L1_m': 0.0, 'Ds_L1_m': 0.0, 'Dt_L1_m': 0.0,
                'Dq_L1_f': 0.0, 'Ds_L1_f': 0.0, 'Dt_L1_f': 0.0,
                'Va1g_3d_L1_i': 0.0, 'Va1g_3d_L1_m': 0.0, 'Va1g_3d_L1_f': 0.0,
                'Vb1g_3d_L1_i': 0.0, 'Vb1g_3d_L1_m': 0.0, 'Vb1g_3d_L1_f': 0.0,
                'Vb2g_3d_L1_i': 0.0, 'Vb2g_3d_L1_m': 0.0, 'Vb2g_3d_L1_f': 0.0,
                'Veg_3d_L1_i': 0.0, 'Veg_3d_L1_m': 0.0, 'Veg_3d_L1_f': 0.0
            }
            self.MLCT = {
                'Delta_3d_L2_i': 0.0, 'Delta_3d_L2_m': 0.0, 'Delta_3d_L2_f': 0.0,
                'Dq_L2_i': 0.0, 'Ds_L2_i': 0.0, 'Dt_L2_i': 0.0,
                'Dq_L2_m': 0.0, 'Ds_L2_m': 0.0, 'Dt_L2_m': 0.0,
                'Dq_L2_f': 0.0, 'Ds_L2_f': 0.0, 'Dt_L2_f': 0.0,
                'Va1g_3d_L2_i': 0.0, 'Va1g_3d_L2_m': 0.0, 'Va1g_3d_L2_f': 0.0,
                'Vb1g_3d_L2_i': 0.0, 'Vb1g_3d_L2_m': 0.0, 'Vb1g_3d_L2_f': 0.0,
                'Vb2g_3d_L2_i': 0.0, 'Vb2g_3d_L2_m': 0.0, 'Vb2g_3d_L2_f': 0.0,
                'Veg_3d_L2_i': 0.0, 'Veg_3d_L2_m': 0.0, 'Veg_3d_L2_f': 0.0
            }

        else:
            raise ValueError(f"Unsupported crystal symmetry: {self.symmetry}")

    def _synchronize_hamiltonians(self):
        if self.Parameters["Experiment"].get("SynchronizeHamiltonian", False):
            # Synchronize with Initial Hamiltonian
            for key, value in self.InitialHamiltonian.items():
                # Tenta encontrar o equivalente "f" a partir do sufixo "_i"
                if key.endswith("_i"):
                    corresponding_key = key.replace("_i", "_f")
                    if corresponding_key in self.FinalHamiltonian:
                        self.FinalHamiltonian[corresponding_key] = value
                    # Now also synchronize with Middle Hamiltonian
                    corresponding_key_middle = key.replace("_i", "_m")
                    if corresponding_key_middle in self.MiddleHamiltonian:
                        self.MiddleHamiltonian[corresponding_key_middle] = value


    def get_modified_parameters(self):
        modified = {}
    
        for name, current_dict in [
            ('Parameters', self.Parameters),
            ('ScaleFactors', self.ScaleFactors),
            ('CrystalField', self.CrystalField),
            ('LMCT', self.LMCT),
            ('MLCT', self.MLCT),
            ('HamiltonianTerms', self.HamiltonianTerms),
            ('InitialHamiltonian', self.InitialHamiltonian),
            ('MiddleHamiltonian', self.MiddleHamiltonian),
            ('FinalHamiltonian', self.FinalHamiltonian),
            ('Electrons', self.Electrons)
        ]:
            default_dict = self._defaults[name]
            changes = {
                k: v for k, v in current_dict.items()
                if default_dict.get(k) != v
            }
            if changes:
                modified[name] = changes
    
        return modified



    def _verify(self):
    
        # Incident energy mode
        if self.IncidentEnergy is not None:
            self.Parameters['Energy']['Emin1'] = self.IncidentEnergy
            self.Parameters['Energy']['Emax1'] = self.IncidentEnergy + 0.0001
            self.Parameters['Energy']['NPoints1'] = 1
        else:
            print(f"Problem with IncidentEnergy = {self.IncidentEnergy}")
    
        # Spectra types
        SpecTypes = []
    
        if self.Parameters['Experiment'].get('Isotropic', False):
            SpecTypes.append("Isotropic")
    
        if self.Parameters['Experiment'].get('Linear', False):
            SpecTypes.append("Linear")
    
        if not SpecTypes:
            raise ValueError("At least one spectra type must be enabled.")
    
        lua_list = ", ".join(f'"{t}"' for t in SpecTypes)
        self.Parameters['Experiment']['SpectraToCalculate'] = f'{{{lua_list}}}'

        if self.HamiltonianTerms['LmctLigandsHybridizationTerm'] == 'true' or self.HamiltonianTerms['MlctLigandsHybridizationTerm'] == 'true':
            self.Parameters['Experiment']['NConfigurations'] = 2

        if self.Parameters['Fields']['Bz_i'] != 0.0 or self.Parameters['Fields']['Bz_f'] != 0.0:
            self.HamiltonianTerms['MagneticFieldTerm'] = 'true'



    def _verify_hamiltonians(self, raise_on_missing=True):
        """Verifica se os Hamiltonianos inicial, intermediário e final possuem todas as chaves necessárias."""
        required_inicial_keys = {'U_3d_3d_i', 'F2_3d_3d_i', 'F4_3d_3d_i', 'zeta_3d_i'}
        required_middle_keys = {
            'U_3d_3d_m', 'F2_3d_3d_m', 'F4_3d_3d_m', 'U_2p_3d_m', 'F2_2p_3d_m',
            'G1_2p_3d_m', 'G3_2p_3d_m', 'zeta_3d_m', 'zeta_2p_m'}
        required_final_keys = {'U_3d_3d_f', 'F2_3d_3d_f', 'F4_3d_3d_f', 'zeta_3d_f'}
    
        actual = {
            'InitialHamiltonian': set(self.InitialHamiltonian.keys()),
            'MiddleHamiltonian': set(self.MiddleHamiltonian.keys()),
            'FinalHamiltonian': set(self.FinalHamiltonian.keys())
        }
    
        required = {
            'InitialHamiltonian': required_inicial_keys,
            'MiddleHamiltonian': required_middle_keys,
            'FinalHamiltonian': required_final_keys
        }
    
        report = {}
        for name in ['InitialHamiltonian', 'MiddleHamiltonian', 'FinalHamiltonian']:
            missing = required[name] - actual[name]
            extra = actual[name] - required[name]
            report[name] = {'missing': missing, 'extra': extra}
            if missing and raise_on_missing:
                raise ValueError(f"⚠️ Missing keys in {name}: {missing}")
            if extra:
                print(f"🔸 Warning: Unrecognized keys in {name}: {extra}")
    
        return report




    def info(self):
        """Exibe os parâmetros da simulação organizados em seções e com até 5 colunas por linha."""

        self._verify()
        self._verify_hamiltonians()
    
        def print_dict_section(title, dictionary):
            print(f"\n🔹 {title}:")
            items = list(dictionary.items())
            for i in range(0, len(items), 5):
                row = items[i:i+5]
                print("  ", end="")
                print(" | ".join(f"{k} = {v}" for k, v in row))
    
        print("📘 Simulação - Parâmetros Atuais")
        
        print_dict_section("Experimento", self.Parameters['Experiment'])
        print_dict_section("Geometria", self.Parameters['Geometry'])
        print_dict_section("Energia", self.Parameters['Energy'])
        print_dict_section("Campos", self.Parameters['Fields'])
        print_dict_section("Fatores de escala", self.ScaleFactors)
        print_dict_section("Campo cristalino", self.CrystalField)
        print_dict_section("LMCT", self.LMCT)
        print_dict_section("MLCT", self.MLCT)
        print_dict_section("Termos do Hamiltoniano", self.HamiltonianTerms)
        print_dict_section("Hamiltoniano Inicial", self.InitialHamiltonian)
        print_dict_section("Hamiltoniano do Meio", self.MiddleHamiltonian)
        print_dict_section("Hamiltoniano Final", self.FinalHamiltonian)
        print_dict_section("Elétrons", self.Electrons)


    # def generate_lua_script(self, template_path=None, output_filename="rixs_output/input.lua"):
    #     self._verify()
    #     self._verify_hamiltonians()
        
    #     if template_path is None:
    #         # Usa o nome do template definido em _set_symmetry
    #         template_path = getattr(self, "template_name", None)
            
    #     if template_path is None:
    #          raise ValueError("Nenhum template especificado e nenhum padrão definido.")

    #     # Carrega o template usando o env global (configurado com PackageLoader)
    #     try:
    #         template = env.get_template(template_path)
    #     except Exception as e:
    #         raise FileNotFoundError(f"Erro ao carregar o template '{template_path}': {e}")

    #     context = {
    #         "Parameters": self.Parameters,
    #         "ScaleFactors": self.ScaleFactors,
    #         "CrystalField": self.CrystalField,
    #         "LMCT": self.LMCT,
    #         "MLCT": self.MLCT,
    #         "HamiltonianTerms": self.HamiltonianTerms,
    #         "InitialHamiltonian": self.InitialHamiltonian,
    #         "MiddleHamiltonian": self.MiddleHamiltonian,
    #         "FinalHamiltonian": self.FinalHamiltonian,
    #         "Electrons": self.Electrons,
    #         "filename": self.filename,
    #     }

    #     rendered_script = template.render(context)

    #     # Pathlib para criação de diretórios e arquivos
    #     output_path = Path(output_filename)
    #     output_path.parent.mkdir(parents=True, exist_ok=True)

    #     with open(output_path, 'w') as f:
    #         f.write(rendered_script)


    def generate_lua_script(self, template_path=None, output_filename="rixs_output/input.lua"):
        self._verify()
        self._verify_hamiltonians()

        # Resolve o template solicitado (parâmetro) ou o padrão definido no objeto
        if template_path is None:
            # tenta primeiro template_name (basename), depois template_path (possível caminho completo)
            template_candidate = getattr(self, "template_name", None) or getattr(self, "template_path", None)
        else:
            template_candidate = template_path

        if not template_candidate:
            raise ValueError("Nenhum template especificado e nenhum padrão definido.")

        # Se for um ficheiro local existente, carrega diretamente do ficheiro
        template_file = Path(template_candidate)
        try:
            if template_file.exists():
                template_text = template_file.read_text(encoding='utf8')
                template = env.from_string(template_text)
            else:
                # tenta carregar pelo nome (compatível com PackageLoader)
                template = env.get_template(Path(template_candidate).name)
        except Exception as e:
            raise FileNotFoundError(f"Erro ao carregar o template '{template_candidate}': {e}")

        context = {
            "Parameters": self.Parameters,
            "ScaleFactors": self.ScaleFactors,
            "CrystalField": self.CrystalField,
            "LMCT": self.LMCT,
            "MLCT": self.MLCT,
            "HamiltonianTerms": self.HamiltonianTerms,
            "InitialHamiltonian": self.InitialHamiltonian,
            "MiddleHamiltonian": self.MiddleHamiltonian,
            "FinalHamiltonian": self.FinalHamiltonian,
            "Electrons": self.Electrons,
            "filename": self.filename,
        }

        rendered_script = template.render(context)

        # Pathlib para criação de diretórios e arquivos
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf8') as f:
            f.write(rendered_script)


    # def run_quanty(self, input_filename='input.lua', input_dir=None, output_dir='rixs_output', print_output=True):
        

    #     quanty_exec = getattr(self, "quanty_path", None)

    #     if not quanty_exec:
    #         raise FileNotFoundError("❌ Erro: O executável do Quanty não foi encontrado.")

    #     # 2. Configura caminhos
    #     if input_dir is None:
    #         input_dir = 'rixs_output'
            
    #     input_dir_path = Path(input_dir)
    #     output_dir_path = Path(output_dir)
        
    #     fname = input_filename
    #     if not fname.endswith('.lua'): fname += '.lua'

    #     input_file_path = input_dir_path / fname
        
    #     if not input_file_path.exists():
    #         raise FileNotFoundError(f"O arquivo de entrada '{input_file_path}' não foi encontrado.")
            
    #     output_dir_path.mkdir(parents=True, exist_ok=True)
        
    #     # --- CORREÇÃO AQUI ---
    #     destination_input = output_dir_path / fname
        
    #     # Só copia se os caminhos forem diferentes
    #     if input_file_path.resolve() != destination_input.resolve():
    #         shutil.copy(input_file_path, destination_input)

    #     try:
    #         result = subprocess.run(
    #             [quanty_exec, fname],
    #             capture_output=True,
    #             text=True,
    #             cwd=str(output_dir_path),
    #             timeout=300
    #         )

    #         if print_output:
    #             print("🔹 Saída do Quanty:")
    #             print(result.stdout)
    #             if result.stderr:
    #                 print("🔻 Erros do Quanty:")
    #                 print(result.stderr)
            
    #         # Chama o parser
    #         self._parse_quanty_output(result.stdout)
            
    #     except subprocess.TimeoutExpired:
    #         print(f"⚠️ Timeout ao rodar {fname}.")
    #     except Exception as e:
    #          print(f"❌ Erro na execução: {e}")

    # def _parse_quanty_output(self, stdout):
    #     match = re.search(r"Analysis of the initial Hamiltonian:(.*?)(?:\n\n|\Z)", stdout, flags=re.S)
    #     if match:
    #         table_text = match.group(1).strip()
    #         lines = [line for line in table_text.splitlines() if not line.startswith("=") and line.strip()]
    #         table_clean = "\n".join(lines)
    #         try:
    #             self.output = pd.read_csv(StringIO(table_clean), sep=r'\s+')
    #         except Exception as e:
    #             print(f"Erro ao ler tabela de output: {e}")
    #     else:
    #          print("Aviso: Tabela 'Analysis of the initial Hamiltonian' não encontrada no output.")


    def run_quanty(self, input_filename='input.lua', input_dir='rixs_output', output_dir='rixs_output', print_output=True):
        # -----------------------------------------
        # 1. Determina o executável do Quanty
        # -----------------------------------------
        quanty_exec = getattr(self, "quanty_path", None)

        if not quanty_exec:
            try:
                # Procura no pacote
                exe_resource = importlib.resources.files(PACKAGE_NAME) / 'quanty_win' / 'Quanty' 
                if not exe_resource.exists():
                     exe_resource = importlib.resources.files(PACKAGE_NAME) / 'quanty_win' / 'Quanty.exe'
                
                if exe_resource.exists():
                    with importlib.resources.as_file(exe_resource) as exe_path:
                        quanty_exec = str(exe_path)
            except Exception:
                pass

        if not quanty_exec or not os.path.exists(quanty_exec):
             quanty_exec = shutil.which("Quanty") or shutil.which("quanty")

        if not quanty_exec:
            raise FileNotFoundError("❌ Erro: O executável do Quanty não foi encontrado.")

        # -----------------------------------------
        # 2. Execução
        # -----------------------------------------
        input_dir_path = Path(input_dir or ".")
        output_dir_path = Path(output_dir or ".")
        
        fname = input_filename or self.filename
        if not fname.endswith('.lua'): fname += '.lua'
        
        input_file_path = input_dir_path / fname
        
        if not input_file_path.exists():
            raise FileNotFoundError(f"Arquivo Lua não encontrado: {input_file_path}")
            
        output_dir_path.mkdir(parents=True, exist_ok=True)
        
        # --- CORREÇÃO AQUI ---
        destination_input = output_dir_path / fname
        
        # Só copia se os caminhos forem diferentes (evita SameFileError)
        # .resolve() garante que estamos comparando caminhos absolutos reais
        if input_file_path.resolve() != destination_input.resolve():
            shutil.copy(input_file_path, destination_input)
        
        try:
            result = subprocess.run(
                [quanty_exec, fname],
                capture_output=True,
                text=True,
                cwd=str(output_dir_path), 
                timeout=300)

            if print_output:
                print("🔹 Saída do Quanty:")
                print(result.stdout)
                if result.stderr:
                    print("🔻 Erros do Quanty:")
                    print(result.stderr)
            
            self._parse_quanty_output(result.stdout)

        except subprocess.TimeoutExpired:
            print(f"⚠️ Timeout ao rodar {fname}.")
        except Exception as e:
             print(f"❌ Erro na execução: {e}")

    def _parse_quanty_output(self, stdout):
        """Método auxiliar para limpar o código principal"""
        match = re.search(r"Analysis of the initial Hamiltonian:(.*?)(?:\n\n|\Z)", stdout, flags=re.S)
        if match:
            table_text = match.group(1).strip()
            lines = [line for line in table_text.splitlines() if not line.startswith("=") and line.strip()]
            table_clean = "\n".join(lines)
            try:
                self.output = pd.read_csv(StringIO(table_clean), sep=r'\s+')
            except Exception as e:
                 print(f"Erro ao ler tabela de output: {e}")
        else:
             # Não levantar erro aqui permite ver o print do stdout para debug
             print("Aviso: Tabela 'Analysis of the initial Hamiltonian' não encontrada no output.")