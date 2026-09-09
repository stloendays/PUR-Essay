# Figure 5 — deterministic decision-frontier propagation
#
# This is intentionally data-gated. It refuses to render until the exact complete
# PUR_SIM_V1 response table has been frozen by scripts/freeze_frontier_v1.py.
# No mock/schematic output is produced for the manuscript.

source("figures/R/theme_pur.R")

frontier_path <- "results/frontier_v1/frontier_table.csv"
decision_path <- "results/frontier_v1/frontier_v1_decision.json"
manifest_path <- "results/frontier_v1/manifest.json"

missing_inputs <- c(frontier_path, decision_path, manifest_path)[
  !file.exists(c(frontier_path, decision_path, manifest_path))
]
if (length(missing_inputs)) {
  stop(
    "Figure 5 requires frozen PUR-FRONTIER V1 outputs. Missing: ",
    paste(missing_inputs, collapse = ", "),
    ". Restore data/pur_sim_v1/candidates_full.csv and run scripts/freeze_frontier_v1.py first."
  )
}

if (!requireNamespace("jsonlite", quietly = TRUE)) {
  stop("Figure 5 requires R package 'jsonlite'.")
}

tab <- read_csv(frontier_path, show_col_types = FALSE)
decision <- jsonlite::fromJSON(decision_path, simplifyVector = TRUE)
manifest <- jsonlite::fromJSON(manifest_path, simplifyVector = TRUE)

if (!identical(as.character(manifest$gold_status), "GOLD")) {
  stop("Refusing to render publication Figure 5 because frontier manifest gold_status != GOLD.")
}

needed <- c(
  "cid", "blend", "nco_oh", "mdi_fraction", "property_score", "property_rank",
  "feasible_nominal", "nominal_rank", "feasible_robust", "robust_score", "robust_rank"
)
missing_cols <- setdiff(needed, names(tab))
if (length(missing_cols)) stop("frontier_table.csv is missing: ", paste(missing_cols, collapse = ", "))

property_id <- as.character(decision$property_winner)
nominal_id <- as.character(decision$constrained_winner)
robust_id <- as.character(decision$robust_winner)
if (!nzchar(property_id) || !nzchar(nominal_id) || !nzchar(robust_id)) {
  stop("Figure 5 requires non-null L0, L1 and L2 winners in the frozen decision JSON.")
}

winner_rows <- tab %>% filter(cid %in% c(property_id, nominal_id, robust_id))

# A — property score versus the active MDI formulation boundary.
pA <- ggplot(tab, aes(mdi_fraction, property_score)) +
  geom_vline(xintercept = 0.35, linetype = "22", linewidth = 0.50, colour = PUR_COL[["mid"]]) +
  geom_point(aes(alpha = feasible_nominal), size = 1.20, colour = PUR_COL[["light"]]) +
  geom_point(
    data = winner_rows,
    aes(colour = cid),
    size = 2.65,
    alpha = 1
  ) +
  scale_alpha_manual(values = c(`FALSE` = 0.25, `TRUE` = 0.70), guide = "none") +
  scale_colour_manual(
    values = setNames(c(PUR_COL[["T80"]], PUR_COL[["P"]], PUR_COL[["C"]]), c(property_id, nominal_id, robust_id)),
    labels = setNames(c("L0 property", "L1 nominal", "L2 robust"), c(property_id, nominal_id, robust_id))
  ) +
  scale_y_log10(labels = label_number(accuracy = 0.001)) +
  labs(x = "MDI fraction of polyol + MDI", y = "Nominal property objective, J") +
  annotate("text", x = 0.351, y = Inf, label = "35 wt% MDI floor", hjust = 0, vjust = 1.4,
           size = 2.45, colour = PUR_COL[["mid"]]) +
  theme(legend.position = "top", legend.direction = "horizontal", legend.justification = "left")

# B — backward design on the L0 winner's blend.
prop_row <- tab %>% filter(cid == property_id) %>% slice(1)
trajectory <- tab %>% filter(blend == prop_row$blend) %>% arrange(nco_oh)
threshold <- as.numeric(decision$backward_design$continuous_threshold)
reachable_nco <- as.numeric(decision$backward_design$nearest_reachable_grid_value)
reachable_id <- as.character(decision$backward_design$nearest_reachable_candidate_id)

pB <- ggplot(trajectory, aes(nco_oh, mdi_fraction)) +
  geom_hline(yintercept = 0.35, linetype = "22", linewidth = 0.50, colour = PUR_COL[["mid"]]) +
  geom_vline(xintercept = threshold, linetype = "22", linewidth = 0.50, colour = PUR_COL[["T80"]]) +
  geom_line(linewidth = 0.85, colour = PUR_COL[["ink"]]) +
  geom_point(size = 1.75, colour = PUR_COL[["ink"]]) +
  geom_point(data = trajectory %>% filter(cid == property_id), size = 3.0, colour = PUR_COL[["T80"]]) +
  geom_point(data = trajectory %>% filter(cid == reachable_id), size = 3.0, colour = PUR_COL[["C"]]) +
  annotate("text", x = threshold, y = 0.352, label = paste0("continuous threshold = ", sprintf("%.3f", threshold)),
           hjust = -0.04, vjust = 0, size = 2.45, colour = PUR_COL[["T80"]]) +
  annotate("text", x = reachable_nco, y = 0.35, label = paste0("first reachable = ", sprintf("%.1f", reachable_nco)),
           hjust = -0.05, vjust = 1.5, size = 2.45, colour = PUR_COL[["C"]]) +
  scale_x_continuous(breaks = sort(unique(trajectory$nco_oh))) +
  scale_y_continuous(labels = percent_format(accuracy = 1), expand = expansion(mult = c(0.05, 0.10))) +
  labs(x = "NCO:OH", y = "MDI fraction")

# C — nominal-to-robust rank preservation / inversion among robust-eligible candidates.
ranked <- tab %>% filter(!is.na(nominal_rank), !is.na(robust_rank))
if (nrow(ranked) < 2) stop("Need at least two robust-eligible candidates for Figure 5C.")

rho <- suppressWarnings(cor(ranked$nominal_rank, ranked$robust_rank, method = "spearman"))
tau <- suppressWarnings(cor(ranked$nominal_rank, ranked$robust_rank, method = "kendall"))

ord_nom <- ranked %>% arrange(nominal_rank) %>% pull(cid)
ord_rob <- setNames(ranked$robust_rank, ranked$cid)
rob_pos <- unname(ord_rob[ord_nom])
inversions <- 0L
if (length(rob_pos) > 1) {
  for (i in seq_len(length(rob_pos) - 1L)) {
    inversions <- inversions + sum(rob_pos[(i + 1L):length(rob_pos)] < rob_pos[i])
  }
}
total_pairs <- nrow(ranked) * (nrow(ranked) - 1L) / 2L
inv_pct <- if (total_pairs > 0) 100 * inversions / total_pairs else NA_real_

highlight_rank <- ranked %>% filter(cid %in% c(nominal_id, robust_id))
max_rank <- max(c(ranked$nominal_rank, ranked$robust_rank), na.rm = TRUE)

pC <- ggplot(ranked, aes(nominal_rank, robust_rank)) +
  geom_abline(slope = 1, intercept = 0, linetype = "22", linewidth = 0.50, colour = PUR_COL[["mid"]]) +
  geom_point(size = 1.45, alpha = 0.55, colour = PUR_COL[["light"]]) +
  geom_point(data = highlight_rank, aes(colour = cid), size = 2.8, alpha = 1) +
  scale_colour_manual(
    values = setNames(c(PUR_COL[["P"]], PUR_COL[["C"]]), c(nominal_id, robust_id)),
    labels = setNames(c("L1 nominal", "L2 robust"), c(nominal_id, robust_id))
  ) +
  coord_equal() +
  labs(x = "Nominal rank", y = "Robust minimax rank") +
  annotate(
    "text", x = 0.04 * max_rank, y = 0.96 * max_rank,
    label = sprintf("Spearman ρ = %.3f\nKendall τ = %.3f\n%d/%d inversions (%.1f%%)",
                    rho, tau, inversions, as.integer(total_pairs), inv_pct),
    hjust = 0, vjust = 1, size = 2.45, colour = PUR_COL[["ink"]]
  ) +
  theme(legend.position = "top", legend.direction = "horizontal", legend.justification = "left")

fig5 <- (pA | pB | pC) +
  plot_layout(widths = c(1.08, 1.05, 1.10)) +
  plot_annotation(tag_levels = "A")

save_pur_figure(
  fig5,
  "figures/final/Figure5_decision_frontier",
  width_mm = 180,
  height_mm = 82
)
