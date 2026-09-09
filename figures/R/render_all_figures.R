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

frontier_inputs <- c(
  "results/frontier_v1/frontier_table.csv",
  "results/frontier_v1/frontier_v1_decision.json",
  "results/frontier_v1/manifest.json"
)

if (all(file.exists(frontier_inputs))) {
  source("figures/R/Figure5.R")
  expected <- c(
    expected,
    "figures/final/Figure5_decision_frontier.png",
    "figures/final/Figure5_decision_frontier.pdf",
    "figures/final/Figure5_decision_frontier.svg"
  )
  message("Frozen FRONTIER V1 found; rendered Figure 5.")
} else {
  message("FRONTIER V1 gold not present; Figure 5 intentionally skipped.")
}

missing <- expected[!file.exists(expected)]
if (length(missing)) stop("Missing figure outputs: ", paste(missing, collapse = ", "))
message("Rendered all currently eligible manuscript figures successfully.")
