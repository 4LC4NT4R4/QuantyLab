# quanty_sim/readers.py

import re
import pandas as pd
import brixs as br
from pathlib import Path

# XAS readers
def xas_sim(filename):
    """
    Read a spectral data file and return a brixs.Spectrum object.

    Parameters
    ----------
    filename : str or Path
        Path to the file containing the spectrum data.

    Returns
    -------
    brixs.Spectrum
        A Spectrum object with energy values as `x` and intensity values as `z`.
    """
    
    # Garante que lidamos com objetos Path ou string
    filepath = Path(filename)
    
    if not filepath.exists():
        raise FileNotFoundError(f"O arquivo não foi encontrado: {filepath}")

    with filepath.open("r") as f:
        lines = f.readlines()

    # Encontrar onde começam os dados numéricos
    start_idx = None
    for i, line in enumerate(lines):
        if line.strip().startswith("Energy"):
            start_idx = i + 1  # A próxima linha contém os dados
            break

    # Se não encontrou o cabeçalho, LEVANTA ERRO (não apenas print)
    if start_idx is None:
        raise ValueError(f"Formato inválido em {filename}: Cabeçalho 'Energy' não encontrado.")

    try:
        # Criar um DataFrame a partir das linhas numéricas
        data = [line.split() for line in lines[start_idx:] if line.strip()]
        
        if not data:
            raise ValueError("O arquivo contém o cabeçalho, mas não possui dados numéricos abaixo dele.")

        x, y, z = zip(*data)
        x = list(map(float, x))
        # y = list(map(float, y)) # Y arbitrário ignorado
        z = list(map(float, z))
        
        s = br.Spectrum(x, z)
        return s

    except Exception as e:
        raise ValueError(f"Erro ao processar dados numéricos no arquivo {filename}: {e}")


# RIXS Readers
def read_spectra_as_br(filename):
    """
    Read a file containing multiple spectra and return a brixs.Spectra object.

    Parameters
    ----------
    filename : str or Path
        Path to the spectral data file.

    Returns
    -------
    brixs.Spectra
    """
    filepath = Path(filename)

    if not filepath.exists():
        raise FileNotFoundError(f"O arquivo não foi encontrado: {filepath}")

    with filepath.open('r') as file:
        lines = file.readlines()

    if not lines:
        raise ValueError(f"O arquivo {filename} está vazio.")

    # Detect number of spectra
    num_spectra_match = re.search(r"#Spectra:\s+(\d+)", lines[0])
    if not num_spectra_match:
        raise ValueError(f"Cabeçalho inválido em {filename}: Não foi possível encontrar '#Spectra: <n>'.")
    
    n_spectra = int(num_spectra_match.group(1))

    # Find the header line
    header_index = None
    for i, line in enumerate(lines):
        if line.strip().startswith("Energy"):
            header_index = i
            break
    
    if header_index is None:
        raise ValueError(f"Cabeçalho de dados 'Energy' não encontrado em {filename}.")

    # Read the data
    data_lines = lines[header_index + 1:]
    data = []
    for line in data_lines:
        parts = line.strip().split()
        if parts:
            try:
                data.append(list(map(float, parts)))
            except ValueError:
                continue # Pula linhas que não sejam números (ex: linhas vazias no fim)

    if not data:
         raise ValueError(f"Não foram encontrados dados numéricos após o cabeçalho em {filename}.")

    # Build DataFrame
    columns = ["Energy"]
    for i in range(n_spectra):
        columns.extend([f"Re[{i+1}]", f"Im[{i+1}]"])
    
    df = pd.DataFrame(data, columns=columns)

    # Create br.Spectra object
    ss = br.Spectra()
    for i in range(n_spectra):
        # Proteção caso as colunas não existam
        col_name = f"Im[{i+1}]"
        if col_name in df.columns:
            spectrum = br.Spectrum(x=df["Energy"].values, y=df[col_name].values)
            ss.append(spectrum)
        else:
             raise ValueError(f"Coluna esperada {col_name} não encontrada nos dados.")

    return ss


def emap_sim(filename):
    """
    Return a stacked spectra object (Image) from a Quanty-generated spectra file.
    """
    # Reutiliza a função robusta acima
    ss = read_spectra_as_br(filename)
    
    # O método stack_spectra_as_columns retorna um objeto Image/Map do brixs
    Im = ss.stack_spectra_as_columns()
    return Im


def rixs_sim(filename):
    """
    Load a RIXS simulation result and return the first spectrum.
    """
    ss = read_spectra_as_br(filename)
    if len(ss) > 0:
        return ss[0]
    else:
        raise ValueError(f"Nenhum espectro encontrado no arquivo {filename}.")