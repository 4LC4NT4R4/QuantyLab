--------------------------------------------------------------------------------
-- Quanty input file generated using Crispy. If you use this file please cite
-- the following reference: http://dx.doi.org/10.5281/zenodo.1008184.
--
-- elements: 3d
-- symmetry: D4h
-- experiment: XAS
-- edge: L2,3 (2p)
--------------------------------------------------------------------------------

--------------------------------------------------------------------------------
-- Set the verbosity of the calculation. For increased verbosity use the values
-- 0x00FF or 0xFFFF.
--------------------------------------------------------------------------------
Verbosity(0x0000)

--------------------------------------------------------------------------------
-- Define the parameters of the calculation.
--------------------------------------------------------------------------------
Temperature = {{Parameters.Experiment.Temperature}} -- Temperature (Kelvin).

NPsis = {{ Parameters.Experiment.NPsis}} -- Number of states to consider in the spectra calculation.
NPsisAuto = {{ Parameters.Experiment.NPsisAuto}} -- Determine the number of state automatically.
NConfigurations = {{ Parameters.Experiment.NConfigurations}} -- Number of configurations.

Emin = {{Parameters.Energy.Emin}} -- Minimum value of the energy range (eV).
Emax = {{Parameters.Energy.Emax}} -- Maximum value of the energy range (eV).
NPoints = {{Parameters.Energy.NPoints}} -- Number of points of the spectra.
ZeroShift = 4.87375 -- Shift that brings the edge or line energy to approximately zero (eV).
ExperimentalShift = 778.1 -- Experimental edge or line energy (eV).
Gaussian = 0.0 -- {{ Parameters.Energy.Gaussian }} -- Gaussian FWHM (eV).
Lorentzian = {{"{"}}{{"{"}}{{Parameters.Energy.Emin}}, {{Parameters.Energy.Lorentzian}}{{"}"}}, {{"{"}}{{Parameters.Energy.Emax}}, {{Parameters.Energy.Lorentzian}}{{"}"}}{{"}"}} -- Lorentzian FWHM (eV).
Gamma = {{ Parameters.Energy.Gamma }} -- Lorentzian FWHM used in the spectra calculation (eV).

WaveVector = {{ Parameters.Geometry.WaveVector }} -- Wave vector.
Ev = {{ Parameters.Geometry.Ev }} -- Vertical polarization.
Eh = {{ Parameters.Geometry.Eh }} -- Horizontal polarization.

SpectraToCalculate = {{Parameters.Experiment.SpectraToCalculate}}  -- Types of spectra to calculate.

DenseBorder = 2000 -- Number of determinants where we switch from dense methods to sparse methods.
ShiftSpectra = true -- If enabled, shift the spectra in the experimental energy range.

Prefix = "{{filename}}" -- File name prefix.

--------------------------------------------------------------------------------
-- Toggle the Hamiltonian terms.
--------------------------------------------------------------------------------
AtomicTerm = {{HamiltonianTerms.AtomicTerm}}
CrystalFieldTerm = {{HamiltonianTerms.CrystalFieldTerm}}
LmctLigandsHybridizationTerm = {{HamiltonianTerms.LmctLigandsHybridizationTerm}}
MlctLigandsHybridizationTerm = {{HamiltonianTerms.MlctLigandsHybridizationTerm}}
MagneticFieldTerm = {{HamiltonianTerms.MagneticFieldTerm}}
ExchangeFieldTerm = {{HamiltonianTerms.ExchangeFieldTerm}}

--------------------------------------------------------------------------------
-- Define the number of electrons, shells, etc.
--------------------------------------------------------------------------------
NBosons = {{Electrons.NBosons}}
NFermions = {{Electrons.NFermions}}


NElectrons_2p = {{Electrons.NElectrons_2p}}
NElectrons_3d = {{Electrons.NElectrons_3d}}

IndexDn_2p = {{Electrons.IndexDn_2p}}
IndexUp_2p = {{Electrons.IndexUp_2p}}
IndexDn_3d = {{Electrons.IndexDn_3d}}
IndexUp_3d = {{Electrons.IndexUp_3d}}

if LmctLigandsHybridizationTerm then
    NFermions = {{Electrons.NFermions+10}}

    NElectrons_L1 = {{Electrons.NElectron_L1}}

    IndexDn_L1 = {{Electrons.IndexDn_L1}}
    IndexUp_L1 = {{Electrons.IndexUp_L1}}
end

if MlctLigandsHybridizationTerm then
    NFermions = {{Electrons.NFermions+10}}

    NElectrons_L2 = {{Electrons.NElectron_L2}}

    IndexDn_L2 = {{Electrons.IndexDn_L2}}
    IndexUp_L2 = {{Electrons.IndexUp_L2}}
end

if LmctLigandsHybridizationTerm and MlctLigandsHybridizationTerm then
    return
end


--------------------------------------------------------------------------------
-- Initialize the Hamiltonians.
--------------------------------------------------------------------------------
H_i = 0
H_f = 0

--------------------------------------------------------------------------------
-- Define the atomic term.
--------------------------------------------------------------------------------
N_2p = NewOperator("Number", NFermions, IndexUp_2p, IndexUp_2p, {1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_2p, IndexDn_2p, {1, 1, 1})

N_3d = NewOperator("Number", NFermions, IndexUp_3d, IndexUp_3d, {1, 1, 1, 1, 1})
     + NewOperator("Number", NFermions, IndexDn_3d, IndexDn_3d, {1, 1, 1, 1, 1})

if AtomicTerm then
    F0_3d_3d = NewOperator("U", NFermions, IndexUp_3d, IndexDn_3d, {1, 0, 0})
    F2_3d_3d = NewOperator("U", NFermions, IndexUp_3d, IndexDn_3d, {0, 1, 0})
    F4_3d_3d = NewOperator("U", NFermions, IndexUp_3d, IndexDn_3d, {0, 0, 1})

    F0_2p_3d = NewOperator("U", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {1, 0}, {0, 0})
    F2_2p_3d = NewOperator("U", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 1}, {0, 0})
    G1_2p_3d = NewOperator("U", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 0}, {1, 0})
    G3_2p_3d = NewOperator("U", NFermions, IndexUp_2p, IndexDn_2p, IndexUp_3d, IndexDn_3d, {0, 0}, {0, 1})

    U_3d_3d_i = {{InitialHamiltonian.U_3d_3d_i}}
    F2_3d_3d_i = {{InitialHamiltonian.F2_3d_3d_i}} * {{ScaleFactors.Fk}}
    F4_3d_3d_i = {{InitialHamiltonian.F4_3d_3d_i}} * {{ScaleFactors.Fk}}
    F0_3d_3d_i = U_3d_3d_i + 2 / 63 * F2_3d_3d_i + 2 / 63 * F4_3d_3d_i

    U_3d_3d_f = {{FinalHamiltonian.U_3d_3d_f}}
    F2_3d_3d_f = {{FinalHamiltonian.F2_3d_3d_f}} * {{ScaleFactors.Fk}}
    F4_3d_3d_f = {{FinalHamiltonian.F4_3d_3d_f}} * {{ScaleFactors.Fk}}
    F0_3d_3d_f = U_3d_3d_f + 2 / 63 * F2_3d_3d_f + 2 / 63 * F4_3d_3d_f
    U_2p_3d_f = {{FinalHamiltonian.U_2p_3d_f}}
    F2_2p_3d_f = {{FinalHamiltonian.F2_2p_3d_f}} * {{ScaleFactors.Fk}}
    G1_2p_3d_f = {{FinalHamiltonian.G1_2p_3d_f}} * {{ScaleFactors.Gk}}
    G3_2p_3d_f = {{FinalHamiltonian.G3_2p_3d_f}} * {{ScaleFactors.Gk}}

    F0_2p_3d_f = U_2p_3d_f + 1 / 15 * G1_2p_3d_f + 3 / 70 * G3_2p_3d_f

    H_i = H_i + Chop(
          F0_3d_3d_i * F0_3d_3d
        + F2_3d_3d_i * F2_3d_3d
        + F4_3d_3d_i * F4_3d_3d)

    H_f = H_f + Chop(
          F0_3d_3d_f * F0_3d_3d
        + F2_3d_3d_f * F2_3d_3d
        + F4_3d_3d_f * F4_3d_3d
        + F0_2p_3d_f * F0_2p_3d
        + F2_2p_3d_f * F2_2p_3d
        + G1_2p_3d_f * G1_2p_3d
        + G3_2p_3d_f * G3_2p_3d)

    ldots_3d = NewOperator("ldots", NFermions, IndexUp_3d, IndexDn_3d)

    ldots_2p = NewOperator("ldots", NFermions, IndexUp_2p, IndexDn_2p)

    zeta_3d_i = {{InitialHamiltonian.zeta_3d_i}} * {{ScaleFactors.zeta}}

    zeta_3d_f = {{FinalHamiltonian.zeta_3d_f}} * {{ScaleFactors.zeta}}
    zeta_2p_f = {{FinalHamiltonian.zeta_2p_f}} * {{ScaleFactors.zeta}}

    H_i = H_i + Chop(
          zeta_3d_i * ldots_3d)

    H_f = H_f + Chop(
          zeta_3d_f * ldots_3d
        + zeta_2p_f * ldots_2p)
end


---------------------------------------------------------------------------------
-- Define the crystal field term.
--------------------------------------------------------------------------------
if  CrystalFieldTerm then
    -- PotentialExpandedOnClm("D4h", 2, {Ea1g, Eb1g, Eb2g, Eeg})
    -- Dq_3d = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm("D4h", 2, { 6,  6, -4, -4}))
    -- Ds_3d = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm("D4h", 2, {-2,  2,  2, -1}))
    -- Dt_3d = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm("D4h", 2, {-6, -1, -1,  4}))

    Akm = {{'{{4, 0, 21}, {4, -4, 1.5 * sqrt(70)}, {4, 4, 1.5 * sqrt(70)}}'}}
    Dq_3d = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, Akm)

    Akm = {{'{{2, 0, -7}}'}}
    Ds_3d = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, Akm)

    Akm = {{'{{4, 0, -21}}'}}
    Dt_3d = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, Akm)

    Dq_3d_i = {{CrystalField.tenDq_3d_i}} / 10.0
    Ds_3d_i = {{CrystalField.Ds_3d_i}}
    Dt_3d_i = {{CrystalField.Dt_3d_i}}

    io.write("Diagonal values of the initial crystal field Hamiltonian:\n")
    io.write("================\n")
    io.write("Irrep.         E\n")
    io.write("================\n")
    io.write(string.format("a1g     %8.3f\n", 6 * Dq_3d_i - 2 * Ds_3d_i - 6 * Dt_3d_i ))
    io.write(string.format("b1g     %8.3f\n", 6 * Dq_3d_i + 2 * Ds_3d_i - Dt_3d_i ))
    io.write(string.format("b2g     %8.3f\n", -4 * Dq_3d_i + 2 * Ds_3d_i - Dt_3d_i ))
    io.write(string.format("eg      %8.3f\n", -4 * Dq_3d_i - Ds_3d_i + 4 * Dt_3d_i))
    io.write("================\n")
    io.write("\n")

    Dq_3d_f = {{CrystalField.tenDq_3d_i}} / 10.0
    Ds_3d_f = {{CrystalField.Ds_3d_f}}
    Dt_3d_f = {{CrystalField.Dt_3d_f}}

    H_i = H_i + Chop(
          Dq_3d_i * Dq_3d
        + Ds_3d_i * Ds_3d
        + Dt_3d_i * Dt_3d)

    H_f = H_f + Chop(
          Dq_3d_f * Dq_3d
        + Ds_3d_f * Ds_3d
        + Dt_3d_f * Dt_3d)
end

--------------------------------------------------------------------------------
-- Define the 3d-ligands hybridization term (LMCT).
--------------------------------------------------------------------------------
if LmctLigandsHybridizationTerm then
    N_L1 = NewOperator("Number", NFermions, IndexUp_L1, IndexUp_L1, {1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L1, IndexDn_L1, {1, 1, 1, 1, 1})

    Delta_3d_L1_i = {{LMCT.Delta_3d_L1_i}}
    E_3d_i = (10 * Delta_3d_L1_i - NElectrons_3d * (19 + NElectrons_3d) * U_3d_3d_i / 2) / (10 + NElectrons_3d)
    E_L1_i = NElectrons_3d * ((1 + NElectrons_3d) * U_3d_3d_i / 2 - Delta_3d_L1_i) / (10 + NElectrons_3d)

    Delta_3d_L1_f = {{LMCT.Delta_3d_L1_f}}
    E_3d_f = (10 * Delta_3d_L1_f - NElectrons_3d * (31 + NElectrons_3d) * U_3d_3d_f / 2 - 90 * U_2p_3d_f) / (16 + NElectrons_3d)
    E_2p_f = (10 * Delta_3d_L1_f + (1 + NElectrons_3d) * (NElectrons_3d * U_3d_3d_f / 2 - (10 + NElectrons_3d) * U_2p_3d_f)) / (16 + NElectrons_3d)
    E_L1_f = ((1 + NElectrons_3d) * (NElectrons_3d * U_3d_3d_f / 2 + 6 * U_2p_3d_f) - (6 + NElectrons_3d) * Delta_3d_L1_f) / (16 + NElectrons_3d)

    H_i = H_i + Chop(
          E_3d_i * N_3d
        + E_L1_i * N_L1)

    H_f = H_f + Chop(
          E_3d_f * N_3d
        + E_2p_f * N_2p
        + E_L1_f * N_L1)

    Dq_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, { 6,  6, -4, -4}))
    Ds_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {-2,  2,  2, -1}))
    Dt_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {-6, -1, -1,  4}))

    Va1g_3d_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))

    Vb1g_3d_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))

    Vb2g_3d_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))
               + NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))

    Veg_3d_L1 = NewOperator("CF", NFermions, IndexUp_L1, IndexDn_L1, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))
              + NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_L1, IndexDn_L1, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))

    Dq_L1_i = {{LMCT.tenDq_L1_i}} / 10.0
    Ds_L1_i = {{LMCT.Ds_L1_i}}
    Dt_L1_i = {{LMCT.Dt_L1_i}}
    Va1g_3d_L1_i = {{LMCT.Va1g_3d_L1_i}}
    Vb1g_3d_L1_i = {{LMCT.Vb1g_3d_L1_i}}
    Vb2g_3d_L1_i = {{LMCT.Vb2g_3d_L1_i}}
    Veg_3d_L1_i = {{LMCT.Veg_3d_L1_i}}

    Dq_L1_f = {{LMCT.tenDq_L1_f}} / 10.0
    Ds_L1_f = {{LMCT.Ds_L1_f}}
    Dt_L1_f = {{LMCT.Dt_L1_f}}
    Va1g_3d_L1_f = {{LMCT.Va1g_3d_L1_f}}
    Vb1g_3d_L1_f = {{LMCT.Vb1g_3d_L1_f}}
    Vb2g_3d_L1_f = {{LMCT.Vb2g_3d_L1_f}}
    Veg_3d_L1_f = {{LMCT.Veg_3d_L1_f}}

    H_i = H_i + Chop(
          Dq_L1_i * Dq_L1
        + Ds_L1_i * Ds_L1
        + Dt_L1_i * Dt_L1
        + Va1g_3d_L1_i * Va1g_3d_L1
        + Vb1g_3d_L1_i * Vb1g_3d_L1
        + Vb2g_3d_L1_i * Vb2g_3d_L1
        + Veg_3d_L1_i  * Veg_3d_L1)

    H_f = H_f + Chop(
          Dq_L1_f * Dq_L1
        + Ds_L1_f * Ds_L1
        + Dt_L1_f * Dt_L1
        + Va1g_3d_L1_f * Va1g_3d_L1
        + Vb1g_3d_L1_f * Vb1g_3d_L1
        + Vb2g_3d_L1_f * Vb2g_3d_L1
        + Veg_3d_L1_f  * Veg_3d_L1)
end

--------------------------------------------------------------------------------
-- Define the 3d-ligands hybridization term (MLCT).
--------------------------------------------------------------------------------
if MlctLigandsHybridizationTerm then
    N_L2 = NewOperator("Number", NFermions, IndexUp_L2, IndexUp_L2, {1, 1, 1, 1, 1})
         + NewOperator("Number", NFermions, IndexDn_L2, IndexDn_L2, {1, 1, 1, 1, 1})

    Delta_3d_L2_i = {{MLCT.Delta_3d_L2_i}}
    E_3d_i = U_3d_3d_i * (-NElectrons_3d + 1) / 2
    E_L2_i = Delta_3d_L2_i + U_3d_3d_i * NElectrons_3d / 2 - U_3d_3d_i / 2

    Delta_3d_L2_f = {{MLCT.Delta_3d_L2_f}}
    E_3d_f = -(U_3d_3d_f * NElectrons_3d^2 + 11 * U_3d_3d_f * NElectrons_3d + 60 * U_2p_3d_f) / (2 * NElectrons_3d + 12)
    E_2p_f = NElectrons_3d * (U_3d_3d_f * NElectrons_3d + U_3d_3d_f - 2 * U_2p_3d_f * NElectrons_3d - 2 * U_2p_3d_f) / (2 * (NElectrons_3d + 6))
    E_L2_f = (2 * Delta_3d_L2_f * NElectrons_3d + 12 * Delta_3d_L2_f + U_3d_3d_f * NElectrons_3d^2 - U_3d_3d_f * NElectrons_3d - 12 * U_3d_3d_f + 12 * U_2p_3d_f * NElectrons_3d + 12 * U_2p_3d_f) / (2 * (NElectrons_3d + 6))

    H_i = H_i + Chop(
          E_3d_i * N_3d
        + E_L2_i * N_L2)

    H_f = H_f + Chop(
          E_3d_f * N_3d
        + E_2p_f * N_2p
        + E_L2_f * N_L2)

    Dq_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, { 6,  6, -4, -4}))
    Ds_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {-2,  2,  2, -1}))
    Dt_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {-6, -1, -1,  4}))

    Va1g_3d_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {1, 0, 0, 0}))

    Vb1g_3d_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))
               + NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {0, 1, 0, 0}))

    Vb2g_3d_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))
               + NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {0, 0, 1, 0}))

    Veg_3d_L2 = NewOperator("CF", NFermions, IndexUp_L2, IndexDn_L2, IndexUp_3d, IndexDn_3d, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))
              + NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_L2, IndexDn_L2, PotentialExpandedOnClm("D4h", 2, {0, 0, 0, 1}))

    Dq_L2_i = {{MLCT.tenDq_L2_i}} / 10.0
    Ds_L2_i = {{MLCT.Ds_L2_i}}
    Dt_L2_i = {{MLCT.Dt_L2_i}}
    Va1g_3d_L2_i = {{MLCT.Va1g_3d_L2_i}}
    Vb1g_3d_L2_i = {{MLCT.Vb1g_3d_L2_i}}
    Vb2g_3d_L2_i = {{MLCT.Vb2g_3d_L2_i}}
    Veg_3d_L2_i = {{MLCT.Veg_3d_L2_i}}

    Dq_L2_f = {{MLCT.tenDq_L2_f}} / 10.0
    Ds_L2_f = {{MLCT.Ds_L2_f}}
    Dt_L2_f = {{MLCT.Dt_L2_f}}
    Va1g_3d_L2_f = {{MLCT.Va1g_3d_L2_f}}
    Vb1g_3d_L2_f = {{MLCT.Vb1g_3d_L2_f}}
    Vb2g_3d_L2_f = {{MLCT.Vb2g_3d_L2_f}}
    Veg_3d_L2_f = {{MLCT.Veg_3d_L2_f}}

    H_i = H_i + Chop(
          Dq_L2_i * Dq_L2
        + Ds_L2_i * Ds_L2
        + Dt_L2_i * Dt_L2
        + Va1g_3d_L2_i * Va1g_3d_L2
        + Vb1g_3d_L2_i * Vb1g_3d_L2
        + Vb2g_3d_L2_i * Vb2g_3d_L2
        + Veg_3d_L2_i  * Veg_3d_L2)

    H_f = H_f + Chop(
          Dq_L2_f * Dq_L2
        + Ds_L2_f * Ds_L2
        + Dt_L2_f * Dt_L2
        + Va1g_3d_L2_f * Va1g_3d_L2
        + Vb1g_3d_L2_f * Vb1g_3d_L2
        + Vb2g_3d_L2_f * Vb2g_3d_L2
        + Veg_3d_L2_f  * Veg_3d_L2)
end


--------------------------------------------------------------------------------
-- Define the magnetic field and exchange field terms.
--------------------------------------------------------------------------------
Sx_3d = NewOperator("Sx", NFermions, IndexUp_3d, IndexDn_3d)
Sy_3d = NewOperator("Sy", NFermions, IndexUp_3d, IndexDn_3d)
Sz_3d = NewOperator("Sz", NFermions, IndexUp_3d, IndexDn_3d)
Ssqr_3d = NewOperator("Ssqr", NFermions, IndexUp_3d, IndexDn_3d)
Splus_3d = NewOperator("Splus", NFermions, IndexUp_3d, IndexDn_3d)
Smin_3d = NewOperator("Smin", NFermions, IndexUp_3d, IndexDn_3d)

Lx_3d = NewOperator("Lx", NFermions, IndexUp_3d, IndexDn_3d)
Ly_3d = NewOperator("Ly", NFermions, IndexUp_3d, IndexDn_3d)
Lz_3d = NewOperator("Lz", NFermions, IndexUp_3d, IndexDn_3d)
Lsqr_3d = NewOperator("Lsqr", NFermions, IndexUp_3d, IndexDn_3d)
Lplus_3d = NewOperator("Lplus", NFermions, IndexUp_3d, IndexDn_3d)
Lmin_3d = NewOperator("Lmin", NFermions, IndexUp_3d, IndexDn_3d)

Jx_3d = NewOperator("Jx", NFermions, IndexUp_3d, IndexDn_3d)
Jy_3d = NewOperator("Jy", NFermions, IndexUp_3d, IndexDn_3d)
Jz_3d = NewOperator("Jz", NFermions, IndexUp_3d, IndexDn_3d)
Jsqr_3d = NewOperator("Jsqr", NFermions, IndexUp_3d, IndexDn_3d)
Jplus_3d = NewOperator("Jplus", NFermions, IndexUp_3d, IndexDn_3d)
Jmin_3d = NewOperator("Jmin", NFermions, IndexUp_3d, IndexDn_3d)

Tx_3d = NewOperator("Tx", NFermions, IndexUp_3d, IndexDn_3d)
Ty_3d = NewOperator("Ty", NFermions, IndexUp_3d, IndexDn_3d)
Tz_3d = NewOperator("Tz", NFermions, IndexUp_3d, IndexDn_3d)

Sx = Sx_3d
Sy = Sy_3d
Sz = Sz_3d

Lx = Lx_3d
Ly = Ly_3d
Lz = Lz_3d

Mx = Lx+2*Sx
My = Ly+2

Jx = Jx_3d
Jy = Jy_3d
Jz = Jz_3d

Tx = Tx_3d
Ty = Ty_3d
Tz = Tz_3d

Ssqr = Sx * Sx + Sy * Sy + Sz * Sz
Lsqr = Lx * Lx + Ly * Ly + Lz * Lz
Jsqr = Jx * Jx + Jy * Jy + Jz * Jz

if MagneticFieldTerm then
    -- The values are in eV, and not Tesla. To convert from Tesla to eV multiply
    -- the value with EnergyUnits.Tesla.value.

    Bx_i = {{Parameters.Fields.Bx_i}}
    By_i = {{Parameters.Fields.By_i}}
    Bz_i = {{Parameters.Fields.Bz_i}}

    Bx_f = {{Parameters.Fields.Bx_f}}
    By_f = {{Parameters.Fields.By_f}}
    Bz_f = {{Parameters.Fields.Bz_f}}

    H_i = H_i + Chop(
          Bx_i * (2 * Sx + Lx)
        + By_i * (2 * Sy + Ly)
        + Bz_i * (2 * Sz + Lz))

    H_f = H_f + Chop(
          Bx_f * (2 * Sx + Lx)
        + By_f * (2 * Sy + Ly)
        + Bz_f * (2 * Sz + Lz))
end

if ExchangeFieldTerm then
    Hx_i = {{Parameters.Fields.Hx_i}}
    Hy_i = {{Parameters.Fields.Hy_i}}
    Hz_i = {{Parameters.Fields.Hz_i}}

    Hx_f = {{Parameters.Fields.Hx_f}}
    Hy_f = {{Parameters.Fields.Hy_f}}
    Hz_f = {{Parameters.Fields.Hz_f}}


    H_i = H_i + Chop(
          Hx_i * Sx
        + Hy_i * Sy
        + Hz_i * Sz)

    H_f = H_f + Chop(
          Hx_f * Sx
        + Hy_f * Sy
        + Hz_f * Sz)
end

--------------------------------------------------------------------------------
-- Define the restrictions and set the number of initial states.
--------------------------------------------------------------------------------

InitialRestrictions = {{'{NFermions, NBosons, {"111111 0000000000", NElectrons_2p, NElectrons_2p},'}}
                                           {{'{"000000 1111111111", NElectrons_3d, NElectrons_3d}}'}}

FinalRestrictions = {{'{NFermions, NBosons, {"111111 0000000000", NElectrons_2p - 1, NElectrons_2p - 1},'}}
                                         {{'{"000000 1111111111", NElectrons_3d + 1, NElectrons_3d + 1}}'}}

CalculationRestrictions = nil

if LmctLigandsHybridizationTerm then
    InitialRestrictions = {{'{NFermions, NBosons, {"111111 0000000000 0000000000", NElectrons_2p, NElectrons_2p},'}}
                                               {{'{"000000 1111111111 0000000000", NElectrons_3d, NElectrons_3d},'}}
                                               {{'{"000000 0000000000 1111111111", NElectrons_L1, NElectrons_L1}}'}}

    FinalRestrictions = {{'{NFermions, NBosons, {"111111 0000000000 0000000000", NElectrons_2p - 1, NElectrons_2p - 1},'}}
                                             {{'{"000000 1111111111 0000000000", NElectrons_3d + 1, NElectrons_3d + 1},'}}
                                             {{'{"000000 0000000000 1111111111", NElectrons_L1, NElectrons_L1}}'}}

    CalculationRestrictions ={{' {NFermions, NBosons, {"000000 0000000000 1111111111", NElectrons_L1 - (NConfigurations - 1), NElectrons_L1}}'}}
end

if MlctLigandsHybridizationTerm then
    InitialRestrictions = {{'{NFermions, NBosons, {"111111 0000000000 0000000000", NElectrons_2p, NElectrons_2p},'}}
                                               {{'{"000000 1111111111 0000000000", NElectrons_3d, NElectrons_3d},'}}
                                               {{'{"000000 0000000000 1111111111", NElectrons_L2, NElectrons_L2}}'}}

    FinalRestrictions = {{'{NFermions, NBosons, {"111111 0000000000 0000000000", NElectrons_2p - 1, NElectrons_2p - 1},'}}
                                             {{'{"000000 1111111111 0000000000", NElectrons_3d + 1, NElectrons_3d + 1},'}}
                                             {{'{"000000 0000000000 1111111111", NElectrons_L2, NElectrons_L2}}'}}

    CalculationRestrictions = {{'{NFermions, NBosons, {"000000 0000000000 1111111111", NElectrons_L2, NElectrons_L2 + (NConfigurations - 1)}}'}}
end


--------------------------------------------------------------------------------
-- Define some helper functions.
--------------------------------------------------------------------------------
function MatrixToOperator(Matrix, StartIndex)
    -- Transform a matrix to an operator.
    local Operator = 0
    for i = 1, #Matrix do
        for j = 1, #Matrix do
            local Weight = Matrix[i][j]
            Operator = Operator + NewOperator("Number", #Matrix + StartIndex, i + StartIndex - 1, j + StartIndex - 1) * Weight
        end
    end
    Operator.Chop()
    return Operator
end

function ValueInTable(Value, Table)
    -- Check if a value is in a table.
    for _, v in ipairs(Table) do
        if Value == v then
            return true
        end
    end
    return false
end

function GetSpectrum(G, Ids, dZ, NOperators, NPsis)
    -- Extract the spectrum corresponding to the operators identified using the
    -- Ids argument. The returned spectrum is a weighted sum, where the weights
    -- are the Boltzmann probabilities.
    --
    -- @param G userdata: Spectrum object as returned by the functions defined in Quanty, i.e. one spectrum
    --                    for each operator and each wavefunction.
    -- @param Ids table: Indexes of the operators that are considered in the returned spectrum.
    -- @param dZ table: Boltzmann prefactors for each of the spectrum in the spectra object.
    -- @param NOperators number: Number of transition operators.
    -- @param NPsis number: Number of wavefunctions.

    if not (type(Ids) == "table") then
        Ids = {{'{Ids}'}}
    end

    local Id = 1
    local dZs = {{'{}'}}

    for i = 1, NOperators do
        for _ = 1, NPsis do
            if ValueInTable(i, Ids) then
                table.insert(dZs, dZ[Id])
            else
                table.insert(dZs, 0)
            end
            Id = Id + 1
        end
    end
    return Spectra.Sum(G, dZs)
end

function SaveSpectrum(G, Filename, Gaussian, Lorentzian, Pcl)
    if Pcl == nil then
        Pcl = 1
    end
    G = -1 / math.pi / Pcl * G
    G.Broaden(Gaussian, Lorentzian)
    G.Print({{'{{"file", Filename .. ".spec"}}'}})
end

function CalculateT(Basis, Eps, K)
    -- Calculate the transition operator in the basis of tesseral harmonics for
    -- an arbitrary polarization and wave-vector (for quadrupole operators).
    --
    -- @param Basis table: Operators forming the basis.
    -- @param Eps table: Cartesian components of the polarization vector.
    -- @param K table: Cartesian components of the wave-vector.

    if #Basis == 3 then
        -- The basis for the dipolar operators must be in the order x, y, z.
        T = Eps[1] * Basis[1]
          + Eps[2] * Basis[2]
          + Eps[3] * Basis[3]
    elseif #Basis == 5 then
        -- The basis for the quadrupolar operators must be in the order xy, xz, yz, x2y2, z2.
        T = (Eps[1] * K[2] + Eps[2] * K[1]) / math.sqrt(3) * Basis[1]
          + (Eps[1] * K[3] + Eps[3] * K[1]) / math.sqrt(3) * Basis[2]
          + (Eps[2] * K[3] + Eps[3] * K[2]) / math.sqrt(3) * Basis[3]
          + (Eps[1] * K[1] - Eps[2] * K[2]) / math.sqrt(3) * Basis[4]
          + (Eps[3] * K[3]) * Basis[5]
    end
    return Chop(T)
end

function DotProduct(a, b)
    return Chop(a[1] * b[1] + a[2] * b[2] + a[3] * b[3])
end

function WavefunctionsAndBoltzmannFactors(H, NPsis, NPsisAuto, Temperature, Threshold, StartRestrictions, CalculationRestrictions)
    -- Calculate the wavefunctions and Boltzmann factors of a Hamiltonian.
    --
    -- @param H userdata: Hamiltonian for which to calculate the wavefunctions.
    -- @param NPsis number: The number of wavefunctions.
    -- @param NPsisAuto boolean: Determine automatically the number of wavefunctions that are populated at the specified
    --                           temperature and within the threshold.
    -- @param Temperature number: The temperature in eV.
    -- @param Threshold number: Threshold used to determine the number of wavefunction in the automatic procedure.
    -- @param StartRestrictions table: Occupancy restrictions at the start of the calculation.
    -- @param CalculationRestrictions table: Occupancy restrictions used during the calculation.
    -- @return table: The calculated wavefunctions.
    -- @return table: The calculated Boltzmann factors.

    if Threshold == nil then
        Threshold = 1e-8
    end

    local dZ = {{'{}'}}
    local Z = 0
    local Psis

    if NPsisAuto == true and NPsis ~= 1 then
        NPsis = 4
        local NPsisIncrement = 8
        local NPsisIsConverged = false

        while not NPsisIsConverged do
            if CalculationRestrictions == nil then
                Psis = Eigensystem(H, StartRestrictions, NPsis)
            else
                Psis = Eigensystem(H, StartRestrictions, NPsis, {{'{{"restrictions", CalculationRestrictions}}'}})
            end

            if not (type(Psis) == "table") then
                Psis = {{'{Psis}'}}
            end

            if E_gs == nil then
                E_gs = Psis[1] * H * Psis[1]
            end

            Z = 0

            for i, Psi in ipairs(Psis) do
                local E = Psi * H * Psi

                if math.abs(E - E_gs) < Threshold ^ 2 then
                    dZ[i] = 1
                else
                    dZ[i] = math.exp(-(E - E_gs) / Temperature)
                end

                Z = Z + dZ[i]

                if dZ[i] / Z < Threshold then
                    i = i - 1
                    NPsisIsConverged = true
                    NPsis = i
                    Psis = {{'{unpack(Psis, 1, i)}'}}
                    dZ = {{'{unpack(dZ, 1, i)}'}}
                    break
                end
            end

            if NPsisIsConverged then
                break
            else
                NPsis = NPsis + NPsisIncrement
            end
        end
    else
        if CalculationRestrictions == nil then
            Psis = Eigensystem(H, StartRestrictions, NPsis)
        else
            Psis = Eigensystem(H, StartRestrictions, NPsis, {{'{{"restrictions", CalculationRestrictions}}'}})
        end

        if not (type(Psis) == "table") then
            Psis = {{'{Psis}'}}
        end

        local E_gs = Psis[1] * H * Psis[1]

        Z = 0

        for i, psi in ipairs(Psis) do
            local E = psi * H * psi

            if math.abs(E - E_gs) < Threshold ^ 2 then
                dZ[i] = 1
            else
                dZ[i] = math.exp(-(E - E_gs) / Temperature)
            end

            Z = Z + dZ[i]
        end
    end

    -- Normalize the Boltzmann factors to unity.
    for i in ipairs(dZ) do
        dZ[i] = dZ[i] / Z
    end

    return Psis, dZ
end

function PrintHamiltonianAnalysis(Psis, Operators, dZ, Header, Footer)
    io.write(Header)
    for i, Psi in ipairs(Psis) do
        io.write(string.format("%5d", i))
        for j, Operator in ipairs(Operators) do
            if j == 1 then
                io.write(string.format("%12.6f", Complex.Re(Psi * Operator * Psi)))
            elseif Operator == "dZ" then
                io.write(string.format("%12.2e", dZ[i]))
            else
                io.write(string.format("%10.4f", Complex.Re(Psi * Operator * Psi)))
            end
        end
        io.write("\n")
    end
    io.write(Footer)
end

function CalculateEnergyDifference(H1, H1Restrictions, H2, H2Restrictions)
    -- Calculate the energy difference between the lowest eigenstates of the two
    -- Hamiltonians.
    --
    -- @param H1 userdata: The first Hamiltonian.
    -- @param H1Restrictions table: Restrictions of the occupation numbers for H1.
    -- @param H2 userdata: The second Hamiltonian.
    -- @param H2Restrictions table: Restrictions of the occupation numbers for H2.

    local E1 = 0.0
    local E2 = 0.0

    if H1 ~= nil and H1Restrictions ~= nil then
        Psis1, _ = WavefunctionsAndBoltzmannFactors(H1, 1, false, 0, nil, H1Restrictions, nil)
        E1 = Psis1[1] * H1 * Psis1[1]
    end

    if H2 ~= nil and H2Restrictions ~= nil then
        Psis2, _ = WavefunctionsAndBoltzmannFactors(H2, 1, false, 0, nil, H2Restrictions, nil)
        E2 = Psis2[1] * H2 * Psis2[1]
    end

    return E1 - E2
end

--------------------------------------------------------------------------------
-- Analyze the initial Hamiltonian.
--------------------------------------------------------------------------------
Temperature = Temperature * EnergyUnits.Kelvin.value

Sk = DotProduct(WaveVector, {{'{Sx, Sy, Sz}'}})
Lk = DotProduct(WaveVector, {{'{Lx, Ly, Lz}'}})
Jk = DotProduct(WaveVector, {{'{Jx, Jy, Jz}'}})
Tk = DotProduct(WaveVector, {{'{Tx, Ty, Tz}'}})

Operators = {{'{H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_3d, N_2p, N_3d, "dZ"}'}}
Header = "Analysis of the %s Hamiltonian:\n"
Header = Header .. "=================================================================================================================================\n"
Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_2p>    <N_3d>          dZ\n"
Header = Header .. "=================================================================================================================================\n"
Footer = "=================================================================================================================================\n"

if LmctLigandsHybridizationTerm then
    Operators = {{'{H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_3d, N_2p, N_3d, N_L1, "dZ"}'}}
    Header = "Analysis of the %s Hamiltonian:\n"
    Header = Header .. "===========================================================================================================================================\n"
    Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_2p>    <N_3d>    <N_L1>          dZ\n"
    Header = Header .. "===========================================================================================================================================\n"
    Footer = "===========================================================================================================================================\n"
end

if MlctLigandsHybridizationTerm then
    Operators = {{'{H_i, Ssqr, Lsqr, Jsqr, Sk, Lk, Jk, Tk, ldots_3d, N_2p, N_3d, N_L2, "dZ"}'}}
    Header = "Analysis of the %s Hamiltonian:\n"
    Header = Header .. "===========================================================================================================================================\n"
    Header = Header .. "State           E     <S^2>     <L^2>     <J^2>      <Sk>      <Lk>      <Jk>      <Tk>     <l.s>    <N_2p>    <N_3d>    <N_L2>          dZ\n"
    Header = Header .. "===========================================================================================================================================\n"
    Footer = "===========================================================================================================================================\n"
end
--------------------------------------------------------------------------------
-- Printers
--------------------------------------------------------------------------------
function print_spin_operators(Sx, Sy, Sz, Ssqr, psi_i, Npsis)
    Header = string.format("%10s %10s %10s %10s %10s", "State", "Sx", "Sy", "Sz", "Ssqr")
    print(Header)
    for i=1, Npsis do
    print(string.format("%10.0f %10.4f  %10.4f  %10.4f %10.4f", i, Complex.Re(psi_i[i] * Sx * psi_i[i]), Complex.Re(psi_i[i] * Sy * psi_i[i]), Complex.Re(psi_i[i] * Sz * psi_i[i]), Complex.Re(psi_i[i] * Ssqr * psi_i[i])))
    end
end


function print_orbital_operators(Lx, Ly, Lz, Lsqr, psi_i, Npsis)
    Header = string.format("%10s %10s %10s %10s %10s", "State", "Lx", "Ly", "Lz", "Lsqr")
    print(Header)
    for i=1, Npsis do
    print(string.format("%10.0f %10.4f  %10.4f  %10.4f %10.4f", i, Complex.Re(psi_i[i] * Lx * psi_i[i]), Complex.Re(psi_i[i] * Ly * psi_i[i]), Complex.Re(psi_i[i] * Lz * psi_i[i]), Complex.Re(psi_i[i] * Lsqr * psi_i[i])))
    end
end

function print_total_operators(Jx, Jy, Jz, Jsqr, psi_i, Npsis)
    Header = string.format("%10s %10s %10s %10s %10s", "State", "Jx", "Jy", "Jz", "Jsqr")
    print(Header)
    for i=1, Npsis do
    print(string.format("%10.0f %10.4f  %10.4f  %10.4f %10.4f", i, Complex.Re(psi_i[i] * Jx * psi_i[i]), Complex.Re(psi_i[i] * Jy * psi_i[i]), Complex.Re(psi_i[i] * Jz * psi_i[i]), Complex.Re(psi_i[i] * Jsqr * psi_i[i])))
    end
end
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
local Psis_i, dZ_i = WavefunctionsAndBoltzmannFactors(H_i, NPsis, NPsisAuto, Temperature, nil, InitialRestrictions, CalculationRestrictions)
PrintHamiltonianAnalysis(Psis_i, Operators, dZ_i, string.format(Header, "initial"), Footer)

-- Stop the calculation if no spectra need to be calculated.
if next(SpectraToCalculate) == nil then
    return
end

--------------------------------------------------------------------------------
-- Calculate and save the spectra.
--------------------------------------------------------------------------------
local t = math.sqrt(1 / 2)

Tx_2p_3d = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_2p, IndexDn_2p, {{'{{1, -1, t}, {1, 1, -t}}'}})
Ty_2p_3d = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_2p, IndexDn_2p, {{'{{1, -1, t * I}, {1, 1, t * I}}'}})
Tz_2p_3d = NewOperator("CF", NFermions, IndexUp_3d, IndexDn_3d, IndexUp_2p, IndexDn_2p, {{'{{1, 0, 1}}'}})

Er = {{'{t * (Eh[1] - I * Ev[1]),'}}
      {{'t * (Eh[2] - I * Ev[2]),'}}
      {{'t * (Eh[3] - I * Ev[3])}'}}

El = {{'{-t * (Eh[1] + I * Ev[1]),'}}
      {{'-t * (Eh[2] + I * Ev[2]),'}}
      {{'-t * (Eh[3] + I * Ev[3])}'}}

local T = {{'{Tx_2p_3d, Ty_2p_3d, Tz_2p_3d}'}}
Tv_2p_3d = CalculateT(T, Ev)
Th_2p_3d = CalculateT(T, Eh)
Tr_2p_3d = CalculateT(T, Er)
Tl_2p_3d = CalculateT(T, El)
Tk_2p_3d = CalculateT(T, WaveVector)

-- Initialize a table with the available spectra and the required operators.
SpectraAndOperators = {
    ["Isotropic Absorption"] = {Tk_2p_3d, Tr_2p_3d, Tl_2p_3d},
    ["Absorption"] = {Tk_2p_3d,},
    ["Circular Dichroic"] = {Tr_2p_3d, Tl_2p_3d},
    ["Linear Dichroic"] = {Tv_2p_3d, Th_2p_3d},
}

-- Create an unordered set with the required operators.
local T_2p_3d = {{'{}'}}
for Spectrum, Operators in pairs(SpectraAndOperators) do
    if ValueInTable(Spectrum, SpectraToCalculate) then
        for _, Operator in pairs(Operators) do
            T_2p_3d[Operator] = true
        end
    end
end

-- Give the operators table the form required by Quanty's functions.
local T = {{'{}'}}
for Operator, _ in pairs(T_2p_3d) do
    table.insert(T, Operator)
end
T_2p_3d = T

if ShiftSpectra then
    Emin = Emin - (ZeroShift + ExperimentalShift)
    Emax = Emax - (ZeroShift + ExperimentalShift)
end

if CalculationRestrictions == nil then
    G_2p_3d = CreateSpectra(H_f, T_2p_3d, Psis_i, {{'{{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"DenseBorder", DenseBorder}}'}})
else
    G_2p_3d = CreateSpectra(H_f, T_2p_3d, Psis_i, {{'{{"Emin", Emin}, {"Emax", Emax}, {"NE", NPoints}, {"Gamma", Gamma}, {"Restrictions", CalculationRestrictions}, {"DenseBorder", DenseBorder}}'}})
end

if ShiftSpectra then
    G_2p_3d.Shift(ZeroShift + ExperimentalShift)
end

-- Create a list with the Boltzmann probabilities for a given operator and wavefunction.
local dZ_2p_3d = {{'{}'}}
for _ in ipairs(T_2p_3d) do
    for j in ipairs(Psis_i) do
        table.insert(dZ_2p_3d, dZ_i[j])
    end
end

local Ids = {{'{}'}}
for k, v in pairs(T_2p_3d) do
    Ids[v] = k
end

-- Subtract the broadening used in the spectra calculations from the Lorentzian table.
for i, _ in ipairs(Lorentzian) do
    -- The FWHM is the second value in each pair.

    Lorentzian[i][2] = Lorentzian[i][2] - Gamma
end

Pcl_2p_3d = 2

for Spectrum, Operators in pairs(SpectraAndOperators) do
    if ValueInTable(Spectrum, SpectraToCalculate) then
        -- Find the indices of the spectrum's operators in the table used during the
        -- calculation (this is unsorted).
        SpectrumIds = {{'{}'}}
        for _, Operator in pairs(Operators) do
            table.insert(SpectrumIds, Ids[Operator])
        end

        if Spectrum == "Isotropic Absorption" then
            Giso = GetSpectrum(G_2p_3d, SpectrumIds, dZ_2p_3d, #T_2p_3d, #Psis_i)
            Giso = Giso / 3
            SaveSpectrum(Giso, Prefix .. "_iso", Gaussian, Lorentzian, Pcl_2p_3d)
        end

        if Spectrum == "Absorption" then
            Gk = GetSpectrum(G_2p_3d, SpectrumIds, dZ_2p_3d, #T_2p_3d, #Psis_i)
            SaveSpectrum(Gk, Prefix .. "_k", Gaussian, Lorentzian, Pcl_2p_3d)
        end

        if Spectrum == "Circular Dichroic" then
            Gr = GetSpectrum(G_2p_3d, SpectrumIds[1], dZ_2p_3d, #T_2p_3d, #Psis_i)
            Gl = GetSpectrum(G_2p_3d, SpectrumIds[2], dZ_2p_3d, #T_2p_3d, #Psis_i)
            SaveSpectrum(Gr, Prefix .. "_r", Gaussian, Lorentzian, Pcl_2p_3d)
            SaveSpectrum(Gl, Prefix .. "_l", Gaussian, Lorentzian, Pcl_2p_3d)
            SaveSpectrum(Gr - Gl, Prefix .. "_cd", Gaussian, Lorentzian)
        end

        if Spectrum == "Linear Dichroic" then
            Gv = GetSpectrum(G_2p_3d, SpectrumIds[1], dZ_2p_3d, #T_2p_3d, #Psis_i)
            Gh = GetSpectrum(G_2p_3d, SpectrumIds[2], dZ_2p_3d, #T_2p_3d, #Psis_i)
            SaveSpectrum(Gv, Prefix .. "_v", Gaussian, Lorentzian, Pcl_2p_3d)
            SaveSpectrum(Gh, Prefix .. "_h", Gaussian, Lorentzian, Pcl_2p_3d)
            SaveSpectrum(Gv - Gh, Prefix .. "_ld", Gaussian, Lorentzian)
        end
    end
end