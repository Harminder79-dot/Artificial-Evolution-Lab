TB_PARAMETERS = {

    # ------------------------
    # GRN
    # ------------------------

    "dosR_activation":0.35,
    "sigH_activation":0.20,
    "sigE_activation":0.20,
    "whiB3_activation":0.15,

    "regulator_decay":0.95,
    "regulator_momentum":0.50,

    # ------------------------
    # Functional decoder
    # ------------------------

    "growth_bias":2.0,

    "growth_dosR_weight":-2.0,
    "growth_sigH_weight":-0.8,
    "growth_mprA_weight":-0.5,
    "growth_phoP_weight":0.4,

    "efflux_sigE_weight":2.0,
    "efflux_mprA_weight":0.5,

    # ------------------------
    # Physiology
    # ------------------------

    "metabolism_growth":0.7,
    "metabolism_dosR":0.3,

    "energy_metabolism":0.6,
    "energy_nutrient":0.4,

    "cellwall_base":0.7,
    "cellwall_sigE":0.3,

    "redox_base":0.5,
    "redox_whiB3":0.5,

    # ------------------------
    # Mutation
    # ------------------------

    "edge_mutation_rate":0.05,
    "edge_sigma":0.05,

    "cytokine_resolution": 10,
    "cytokine_diffusion": 0.20,
    "cytokine_decay": 0.01,
    "cytokine_deposit": 1.0

}