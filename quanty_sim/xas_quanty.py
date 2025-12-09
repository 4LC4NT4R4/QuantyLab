# coding: utf-8

# # Libraries
import os
import subprocess
import shutil
import copy
import pandas as pd
import re
from io import StringIO
from pathlib import Path

# Importação para lidar com recursos do pacote (Templates/Executáveis)
import importlib.resources

# Importação do Jinja
from jinja2 import Environment, PackageLoader, select_autoescape

# Se você renomeou o pacote para 'quantylab', ajuste o nome abaixo. 
# Estou assumindo que o nome do pacote onde este arquivo reside é 'quanty_sim' (baseado no seu setup atual)
PACKAGE_NAME = 'quanty_sim' 

try:
    env = Environment(
        loader=PackageLoader(PACKAGE_NAME, 'Templates'),
        autoescape=False
    )
except ImportError:
    # Fallback caso o pacote não esteja instalado corretamente (ex: rodando script solto)
    # Isso mantém a compatibilidade durante o desenvolvimento
    print("⚠️ Aviso: Carregando Templates via sistema de arquivos (fallback).")
    from jinja2 import FileSystemLoader
    TEMPLATES_DIR = Path(__file__).parent / "Templates"
    env = Environment(loader=FileSystemLoader(str(TEMPLATES_DIR)), autoescape=False)

# # XAS Simulation Class
class XAS_sim():
    def __init__(self, symmetry='Oh', filename='filename'):
        self.filename = filename
        self.symmetry = symmetry
        self.CrystalField = {}
        self.LMCT = {}
        self.MLCT = {}
        self._set_symmetry(self.symmetry)

        self.Parameters = {
            "Energy": {
                "Emin": 768.0,
                "Emax": 808.0,
                "NPoints": 2000,
                "Gaussian": 0.0,
                "Lorentzian": 0.43,
                "Gamma": 0.1,
                
            },
            "Experiment": {
                "Temperature": 10,
                "Absorption": False,
                "CircularDichroic": False,
                "LinearDichroic": False,
                "IsotropicAbsorption": True,
                "SpectraToCalculate": ' ',
                "NConfigurations": 1,
                "SynchronizeHamiltonian": True,
                "NPsis": 120,
                "NPsisAuto": 'true',

                
            },
            "Geometry": {
                "WaveVector": "{0, 0, 1}",
                "Ev": "{0, 1, 0}",
                "Eh": "{1, 0, 0}",
            },
            "Fields": {
                "Bx_i": 0.0, "By_i": 0.0, "Bz_i": 0.0,
                "Bx_f": 0.0, "By_f": 0.0, "Bz_f": 0.0,
                "Hx_i": 0.0, "Hy_i": 0.0, "Hz_i": 0.0,
                "Hx_f": 0.0, "Hy_f": 0.0, "Hz_f": 0.0,
            }
        }


        self.Electrons = {
            'NBosons': 0,
            'NFermions': 16,
            'NElectrons_2p': 6,
            'NElectrons_3d': 7,
            'IndexDn_2p': '{0, 2, 4}',
            'IndexUp_2p': '{1, 3, 5}',
            'IndexDn_3d': '{6, 8, 10, 12, 14}',
            'IndexUp_3d': '{7, 9, 11, 13, 15}',
            'NElectron_L1': 10,
            'IndexDn_L1': '{16, 18, 20, 22, 24}',
            'IndexUp_L1': '{17, 19, 21, 23, 25}',
            'NElectron_L2': 0,
            'IndexDn_L2': '{16, 18, 20, 22, 24}',
            'IndexUp_L2': '{17, 19, 21, 23, 25}'
        }

        self.ScaleFactors={
            'Fk':0.8,
            'Gk':0.8,
            'zeta': 1.0}

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

        self.FinalHamiltonian = {'U_3d_3d_f': 0.0, 'F2_3d_3d_f': 12.3956, 'F4_3d_3d_f': 7.7077,
                                 'U_2p_3d_f' : 0.0,'F2_2p_3d_f' : 7.2601,'G1_2p_3d_f' : 5.3971,
                                 'G3_2p_3d_f' : 3.0687, 'zeta_3d_f': 0.083, 'zeta_2p_f': 9.7475}
            
        self._defaults = {
            'Parameters': copy.deepcopy(self.Parameters),
            'ScaleFactors': copy.deepcopy(self.ScaleFactors),
            'CrystalField': copy.deepcopy(self.CrystalField),
            'LMCT': copy.deepcopy(self.LMCT),
            'MLCT': copy.deepcopy(self.MLCT),
            'HamiltonianTerms': copy.deepcopy(self.HamiltonianTerms),
            'InitialHamiltonian': copy.deepcopy(self.InitialHamiltonian),  # cuidado com o nome aqui também
            'FinalHamiltonian': copy.deepcopy(self.FinalHamiltonian),
            'Electrons': copy.deepcopy(self.Electrons)
        }


        self._verify()


    def _set_symmetry(self, symmetry):
        self.symmetry = symmetry

        if symmetry == 'Oh':
            self.template_name = 'Co2+_Oh_XAS_2p.lua'
            
            self.CrystalField = {
                'tenDq_3d_i': 1.0,
                'tenDq_3d_f': 1.0
            }
            self.LMCT = {
                'Delta_3d_L1_i': 0.0,
                'Delta_3d_L1_f': 0.0,
                'tenDq_L1_i': 0.0,
                'Veg_3d_L1_i': 0.0,
                'Vt2g_3d_L1_i': 0.0,
                'tenDq_L1_f': 0.0,
                'Veg_3d_L1_f': 0.0,
                'Vt2g_3d_L1_f': 0.0
            }
            self.MLCT = {
                'Delta_3d_L2_i': 0.0,
                'Delta_3d_L2_f': 0.0,
                'tenDq_L2_i': 0.0,
                'Veg_3d_L2_i': 0.0,
                'Vt2g_3d_L2_i': 0.0,
                'tenDq_L2_f': 0.0,
                'Veg_3d_L2_f': 0.0,
                'Vt2g_3d_L2_f': 0.0
            }

        elif symmetry == 'D4h':
            self.template_name = 'Co2+_D4h_XAS_2p.lua'
            
            self.CrystalField = {
                'tenDq_3d_i': 1.0,
                'tenDq_3d_f': 1.0,
                'Ds_3d_i': 0.0,
                'Ds_3d_f': 0.0,
                'Dt_3d_i': 0.0,
                'Dt_3d_f': 0.0
            }
            self.LMCT = {
                'Delta_3d_L1_i': 0.0,
                'Delta_3d_L1_f': 0.0,
                'tenDq_L1_i': 0.0,
                'Veg_3d_L1_i': 0.0,
                'Vt2g_3d_L1_i': 0.0,
                'tenDq_L1_f': 0.0,
                'Veg_3d_L1_f': 0.0,
                'Vt2g_3d_L1_f': 0.0,
                'Ds_L1_i': 0.0,
                'Ds_L1_f': 0.0,
                'Dt_L1_i': 0.0,
                'Dt_L1_f': 0.0,
                'Va1g_3d_L1_i': 0.0,
                'Va1g_3d_L1_f': 0.0,
                'Vb1g_3d_L1_i': 0.0,
                'Vb1g_3d_L1_f': 0.0,
                'Vb2g_3d_L1_i': 0.0,
                'Vb2g_3d_L1_f': 0.0
            }
            self.MLCT = {
                'Delta_3d_L2_i': 0.0,
                'Delta_3d_L2_f': 0.0,
                'tenDq_L2_i': 0.0,
                'Veg_3d_L2_i': 0.0,
                'Vt2g_3d_L2_i': 0.0,
                'tenDq_L2_f': 0.0,
                'Veg_3d_L2_f': 0.0,
                'Vt2g_3d_L2_f': 0.0,
                'Ds_L2_i': 0.0,
                'Ds_L2_f': 0.0,
                'Dt_L2_i': 0.0,
                'Dt_L2_f': 0.0,
                'Va1g_3d_L2_i': 0.0,
                'Va1g_3d_L2_f': 0.0,
                'Vb1g_3d_L2_i': 0.0,
                'Vb1g_3d_L2_f': 0.0,
                'Vb2g_3d_L2_i': 0.0,
                'Vb2g_3d_L2_f': 0.0
            }

        else:
            raise ValueError(f"Simetria não suportada: {symmetry}")


    def _synchronize_hamiltonians(self):
        if self.Parameters["Experiment"].get("SynchronizeHamiltonian", False):
            # Synchronize Hamiltonian terms
            for key, value in self.InitialHamiltonian.items():
                if key.endswith("_i"):
                    corresponding_key = key.replace("_i", "_f")
                    if corresponding_key in self.FinalHamiltonian:
                        self.FinalHamiltonian[corresponding_key] = value



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
            ('FinalHamiltonian', self.FinalHamiltonian),
            ('Electrons', self.Electrons)
        ]:
            default_dict = self._defaults.get(name, {})
            changes = {
                k: v for k, v in current_dict.items()
                if default_dict.get(k) != v
            }
            if changes:
                modified[name] = changes
    
        return modified


    def _verify(self):
        """Verifica se os parâmetros estão corretos e ajusta conforme necessário."""
    
        # Cria a lista de tipos de espectros a calcular
        SpecTypes = []
        if self.Parameters['Experiment'].get('Absorption', False):
            SpecTypes.append('Absorption')
        if self.Parameters['Experiment'].get('IsotropicAbsorption', False):
            SpecTypes.append('Isotropic Absorption')
        if self.Parameters['Experiment'].get('CircularDichroic', False):
            SpecTypes.append('Circular Dichroic')
        if self.Parameters['Experiment'].get('LinearDichroic', False):
            SpecTypes.append('Linear Dichroic')
    
        # Define a lista de tipos de espectros para calcular
        self.Parameters['Experiment']['SpectraToCalculate'] = '{' + ", ".join(f'"{Type}"' for Type in SpecTypes) + '}'
    
        # Ajusta a configuração de espectros se necessário
        if self.HamiltonianTerms.get('LmctLigandsHybridizationTerm', 'false') == 'true' or self.HamiltonianTerms.get('MlctLigandsHybridizationTerm', 'false') == 'true':
            self.Parameters['Experiment']['NConfigurations'] = 2

    
        # Ajusta os termos do campo magnético se necessário
        if self.Parameters['Fields'].get('Bz_i', 0.0) != 0.0 or self.Parameters['Fields'].get('Bz_f', 0.0) != 0.0:
            self.HamiltonianTerms['MagneticFieldTerm'] = 'true'

            



    def _verify_hamiltonians(self):
        """Verifica se os Hamiltonianos inicial e final possuem todas as chaves necessárias."""
    
        required_initial_keys = {'U_3d_3d_i', 'F2_3d_3d_i', 'F4_3d_3d_i', 'zeta_3d_i'}
        required_final_keys = {
            'U_3d_3d_f', 'F2_3d_3d_f', 'F4_3d_3d_f', 'U_2p_3d_f', 'F2_2p_3d_f',
            'G1_2p_3d_f', 'G3_2p_3d_f', 'zeta_3d_f', 'zeta_2p_f'
        }
    
        initial_keys = set(self.InitialHamiltonian.keys())
        final_keys = set(self.FinalHamiltonian.keys())
    
        missing_initial = required_initial_keys - initial_keys
        missing_final = required_final_keys - final_keys
    
        extra_initial = initial_keys - required_initial_keys
        extra_final = final_keys - required_final_keys
    
        if missing_initial:
            raise ValueError(f"⚠️ Missing keys in InitialHamiltonian: {missing_initial}")
        if missing_final:
            raise ValueError(f"⚠️ Missing keys in FinalHamiltonian: {missing_final}")
        if extra_initial:
            print(f"🔸 Warning: Unrecognized keys in InitialHamiltonian: {extra_initial}")
        if extra_final:
            print(f"🔸 Warning: Unrecognized keys in FinalHamiltonian: {extra_final}")




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
        print_dict_section("Hamiltoniano Final", self.FinalHamiltonian)
        print_dict_section("Elétrons", self.Electrons)

    def generate_lua_script(self, template_path=None, output_filename="xas_output/input.lua"):
        self._verify()
        self._verify_hamiltonians()
        
        # Nome do template no pacote
        if template_path is None:
            template_path = getattr(self, "template_name", None)
        
        if template_path is None:
            raise ValueError("Nenhum template especificado.")
        
        try:
            # O env já foi configurado lá em cima com PackageLoader
            template = env.get_template(template_path)
        except Exception as e:
            raise FileNotFoundError(f"Erro ao carregar o template '{template_path}': {e}")

        context = {
            "Parameters": self.Parameters,
            "ScaleFactors": self.ScaleFactors,
            "CrystalField": self.CrystalField,
            "LMCT": self.LMCT,
            "MLCT": self.MLCT,
            "HamiltonianTerms": self.HamiltonianTerms,
            "InitialHamiltonian": self.InitialHamiltonian,
            "FinalHamiltonian": self.FinalHamiltonian,
            "Electrons": self.Electrons,
            "filename": self.filename,
        }

        rendered_script = template.render(context)

        # Garante diretório de saída
        output_path = Path(output_filename)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(rendered_script)

    def run_quanty(self, input_filename='input.lua', input_dir='xas_output', output_dir='xas_output', print_output=True):
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