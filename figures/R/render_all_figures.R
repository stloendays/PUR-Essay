options(warn = 1)
source("figures/R/Figure2.R")
source("figures/R/Figure3.R")
source("figures/R/Figure4.R")
expected <- c(
  "figures/final/Figure2_temperature_Andrade.png",
  "figures/final/Figure2_temperature_Andrade.pdf",
  "figures/final/Figure2_temperature_Andrade.svg",
  "figures/final/Figure3_free_NCO_coupling.png",
  "figures/final/Figure3_free_NCO_coupling.pdf",
  "figures/final/Figure3_free_NCO_coupling.svg",
  "figures/final/Figure4_chemistry_amplification_interaction.png",
  "figures/final/Figure4_chemistry_amplification_interaction.pdf",
  "figures/final/Figure4_chemistry_amplification_interaction.svg"
)
missing <- expected[!file.exists(expected)]
if (length(missing)) stop("Missing figure outputs: ", paste(missing, collapse = ", "))
message("Rendered all Figure 2-4 outputs successfully.")
