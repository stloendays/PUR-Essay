# Figure 6 — uncertainty phase diagram, robustness cliff and objective-geometry sensitivity
# Exact, hash-verified PUR_SIM_V1 / FRONTIER-DEPTH V1 outputs only.

source("figures/R/theme_pur.R")

if (!requireNamespace("jsonlite", quietly = TRUE)) stop("Figure 6 requires jsonlite.")

summary <- jsonlite::fromJSON("results/frontier_depth_v1/summary.json", simplifyVector = TRUE)
phase <- read_csv("results/frontier_depth_v1/uncertainty_scale_phase.csv", show_col_types = FALSE)
sweep <- read_csv("results/frontier_depth_v1/uncertainty_scale_sweep.csv", show_col_types = FALSE)
wn <- read_csv("results/frontier_depth_v1/objective_weight_stability_nominal.csv", show_col_types = FALSE)
wr <- read_csv("results/frontier_depth_v1/objective_weight_stability_robust.csv", show_col_types = FALSE)
state <- read_csv("results/frontier_depth_v1/rheology_state_rank.csv", show_col_types = FALSE)
tab <- read_csv("results/frontier_v1/frontier_table.csv", show_col_types = FALSE)

if (nrow(tab) != 928) stop("Figure 6 requires the complete frozen 928-candidate frontier table.")

cross <- as.numeric(summary$uncertainty_scale$L1_L2_score_crossover_roots[1])
cliff <- as.numeric(summary$uncertainty_scale$global_max_broad_scale)

# A — winner phases as the frozen uncertainty radius is scaled.
phase2 <- phase %>%
  mutate(
    winner2 = ifelse(is.na(winner) | winner == "", "No admissible state", winner),
    width = s_hi - s_lo,
    category = case_when(
      winner2 == "WO_INV_0579" ~ "L1 nominal winner",
      winner2 == "WO_INV_0420" ~ "Frozen L2 winner",
      winner2 == "No admissible state" ~ "No robust state",
      TRUE ~ "Other robust phase"
    ),
    label = ifelse(width >= 0.08, sub("WO_INV_0", "", winner2), "")
  )

pA <- ggplot(phase2) +
  geom_rect(aes(xmin = s_lo, xmax = s_hi, ymin = 0.72, ymax = 1.28, fill = category),
            colour = "white", linewidth = 0.35) +
  geom_text(data = phase2 %>% filter(label != ""), aes(x = (s_lo + s_hi) / 2, y = 1, label = label),
            size = 2.15, colour = "white") +
  geom_vline(xintercept = cross, linetype = "22", linewidth = 0.55, colour = PUR_COL[["T80"]]) +
  geom_vline(xintercept = 1, linewidth = 0.52, colour = PUR_COL[["ink"]]) +
  geom_vline(xintercept = cliff, linetype = "22", linewidth = 0.55, colour = PUR_COL[["mid"]]) +
  annotate("text", x = cross + 0.02, y = 1.48, label = sprintf("0579 → 0420\n s = %.3f", cross),
           hjust = 0, size = 2.35, colour = PUR_COL[["T80"]]) +
  annotate("text", x = 1.02, y = 0.52, label = "frozen s = 1", hjust = 0,
           size = 2.35, colour = PUR_COL[["ink"]]) +
  annotate("text", x = cliff + 0.02, y = 1.48, label = sprintf("robustness cliff\n s = %.3f", cliff),
           hjust = 0, size = 2.35, colour = PUR_COL[["mid"]]) +
  scale_fill_manual(values = c(
    "L1 nominal winner" = PUR_COL[["P"]],
    "Frozen L2 winner" = PUR_COL[["C"]],
    "Other robust phase" = PUR_COL[["D"]],
    "No robust state" = PUR_COL[["mid"]]
  )) +
  scale_x_continuous(limits = c(0, 2.2), breaks = seq(0, 2.0, 0.5)) +
  scale_y_continuous(NULL, breaks = NULL, limits = c(0.40, 1.60)) +
  labs(x = "Uncertainty-radius scale, s") +
  theme(legend.position = "bottom", legend.direction = "horizontal",
        legend.justification = "left", axis.line.y = element_blank(), axis.ticks.y = element_blank())

# B — number of robust-admissible candidates collapses to zero at the cliff.
frozen_row <- sweep %>% slice_min(abs(scale - 1), n = 1)
pB <- ggplot(sweep, aes(scale, n_admissible)) +
  geom_area(fill = alpha(PUR_COL[["light"]], 0.55), colour = NA) +
  geom_line(linewidth = 0.90, colour = PUR_COL[["ink"]]) +
  geom_vline(xintercept = 1, linewidth = 0.48, colour = PUR_COL[["ink"]]) +
  geom_vline(xintercept = cliff, linetype = "22", linewidth = 0.55, colour = PUR_COL[["T80"]]) +
  geom_point(data = frozen_row, size = 2.65, colour = PUR_COL[["C"]]) +
  scale_x_continuous(limits = c(0, 2.2), breaks = seq(0, 2.0, 0.5)) +
  scale_y_continuous(limits = c(0, 145), breaks = seq(0, 140, 20), expand = expansion(mult = c(0, 0.03))) +
  labs(x = "Uncertainty-radius scale, s", y = "Robust-admissible candidates") +
  annotate("text", x = 1.03, y = frozen_row$n_admissible + 5,
           label = paste0("s = 1: ", frozen_row$n_admissible), hjust = 0,
           size = 2.45, colour = PUR_COL[["C"]]) +
  annotate("text", x = cliff - 0.03, y = 16, label = "bottleneck: ratio /\nthermal sensitivity",
           hjust = 1, size = 2.35, colour = PUR_COL[["T80"]])

# C — objective-weight basins: nominal optimum is broad; robust optimum shares the frontier.
key_ids <- c("WO_INV_0579", "WO_INV_0420", "WO_INV_0341", "WO_INV_0470", "WO_INV_0404")
collapse_basin <- function(x, stage) {
  x %>%
    mutate(winner2 = ifelse(winner %in% key_ids, winner, "Other")) %>%
    group_by(winner2) %>%
    summarise(fraction = sum(fraction), .groups = "drop") %>%
    mutate(stage = stage)
}
basin <- bind_rows(collapse_basin(wn, "Nominal"), collapse_basin(wr, "Robust minimax")) %>%
  mutate(
    stage = factor(stage, levels = c("Robust minimax", "Nominal")),
    winner2 = factor(winner2, levels = c(key_ids, "Other"))
  )

basin_cols <- c(
  "WO_INV_0579" = PUR_COL[["P"]],
  "WO_INV_0420" = PUR_COL[["C"]],
  "WO_INV_0341" = PUR_COL[["D"]],
  "WO_INV_0470" = PUR_COL[["T80"]],
  "WO_INV_0404" = "#7A6F9B",
  "Other" = PUR_COL[["light"]]
)

pC <- ggplot(basin, aes(stage, fraction, fill = winner2)) +
  geom_col(width = 0.60, colour = "white", linewidth = 0.35) +
  geom_text(aes(label = ifelse(fraction >= 0.05, percent(fraction, accuracy = 1), "")),
            position = position_stack(vjust = 0.5), size = 2.25, colour = "white") +
  coord_flip() +
  scale_fill_manual(values = basin_cols, labels = c(key_ids, "Other")) +
  scale_y_continuous(labels = percent_format(accuracy = 10), limits = c(0, 1), expand = c(0, 0)) +
  labs(x = NULL, y = "Winner fraction across 50,000 weight vectors") +
  theme(legend.position = "bottom", legend.direction = "horizontal", legend.justification = "left")

# D — changing the rheological coordinate system can strongly reorder the robust frontier.
state_join <- tab %>%
  filter(!is.na(robust_rank)) %>%
  select(cid, robust_rank) %>%
  inner_join(state %>% select(cid, state_robust_rank), by = "cid")
state_rho <- suppressWarnings(cor(state_join$robust_rank, state_join$state_robust_rank, method = "spearman"))
key_state <- state_join %>% filter(cid %in% c("WO_INV_0579", "WO_INV_0420", "WO_INV_0404"))

pD <- ggplot(state_join, aes(robust_rank, state_robust_rank)) +
  geom_abline(slope = 1, intercept = 0, linetype = "22", linewidth = 0.50, colour = PUR_COL[["mid"]]) +
  geom_point(size = 1.40, alpha = 0.55, colour = PUR_COL[["light"]]) +
  geom_point(data = key_state, aes(colour = cid), size = 3.0) +
  geom_text(data = key_state,
            aes(label = case_when(
              cid == "WO_INV_0404" ~ "0404: 10 → 1",
              cid == "WO_INV_0420" ~ "0420: 1 → 2",
              TRUE ~ "0579: 6 → 31"
            ), colour = cid),
            nudge_x = 5.0, hjust = 0, size = 2.25, show.legend = FALSE) +
  scale_colour_manual(values = c(
    "WO_INV_0579" = PUR_COL[["P"]],
    "WO_INV_0420" = PUR_COL[["C"]],
    "WO_INV_0404" = "#7A6F9B"
  )) +
  coord_equal(xlim = c(0, 120), ylim = c(0, 120), expand = FALSE) +
  scale_x_continuous(breaks = seq(0, 120, 20)) +
  scale_y_continuous(breaks = seq(0, 120, 20)) +
  labs(x = "Frozen 3-term robust rank", y = "Independent 2-DOF state robust rank") +
  annotate("text", x = 5, y = 115,
           label = sprintf("Spearman ρ = %.3f\ninduced metric eigenvalue ratio = 3:1\nL2: 0420 → 0404", state_rho),
           hjust = 0, vjust = 1, size = 2.30, colour = PUR_COL[["ink"]]) +
  theme(legend.position = "none")

fig6 <- ((pA | pB) / (pC | pD)) +
  plot_layout(heights = c(0.92, 1.08)) +
  plot_annotation(tag_levels = "A")

save_pur_figure(fig6, "figures/final/Figure6_uncertainty_objective_geometry", width_mm = 180, height_mm = 116)
