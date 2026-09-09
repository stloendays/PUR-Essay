# Figure 5 — constraint-induced decision phase transition and rank inversion
# Exact, hash-verified PUR_SIM_V1 / PUR-FRONTIER V1 outputs only.

source("figures/R/theme_pur.R")

if (!requireNamespace("jsonlite", quietly = TRUE)) stop("Figure 5 requires jsonlite.")

tab <- read_csv("results/frontier_v1/frontier_table.csv", show_col_types = FALSE)
decision <- jsonlite::fromJSON("results/frontier_v1/frontier_v1_decision.json", simplifyVector = TRUE)
manifest <- jsonlite::fromJSON("results/frontier_v1/manifest.json", simplifyVector = TRUE)
metrics <- jsonlite::fromJSON("results/frontier_v1/ranking_metrics.json", simplifyVector = TRUE)
control <- jsonlite::fromJSON("results/frontier_v1/rank_preservation_control_summary.json", simplifyVector = TRUE)
phase_nom <- read_csv("results/frontier_depth_v1/mdi_floor_phase_nominal.csv", show_col_types = FALSE)
phase_rob <- read_csv("results/frontier_depth_v1/mdi_floor_phase_robust.csv", show_col_types = FALSE)

if (!identical(as.character(manifest$gold_status), "GOLD")) {
  stop("Refusing to render Figure 5 because PUR-FRONTIER V1 is not GOLD.")
}
if (nrow(tab) != 928) stop("Figure 5 requires the complete 928-candidate frontier table.")

property_id <- as.character(decision$property_winner)
nominal_id <- as.character(decision$constrained_winner)
robust_id <- as.character(decision$robust_winner)
ids <- c(property_id, nominal_id, robust_id)
key <- tab %>% filter(cid %in% ids)

# A — a tiny property optimum sits on the wrong side of the formulation boundary.
pA <- ggplot(tab, aes(mdi_fraction * 100, property_score)) +
  geom_point(size = 1.00, alpha = 0.22, colour = PUR_COL[["light"]]) +
  geom_point(data = tab %>% filter(feasible_nominal), size = 1.10, alpha = 0.45,
             colour = PUR_COL[["P"]]) +
  geom_vline(xintercept = 35, linetype = "22", linewidth = 0.55, colour = PUR_COL[["mid"]]) +
  geom_segment(
    data = key %>% filter(cid == property_id),
    aes(x = mdi_fraction * 100, y = property_score,
        xend = (key %>% filter(cid == robust_id) %>% pull(mdi_fraction)) * 100,
        yend = (key %>% filter(cid == robust_id) %>% pull(property_score))),
    inherit.aes = FALSE, linetype = "22", linewidth = 0.55, colour = PUR_COL[["T80"]],
    arrow = grid::arrow(length = grid::unit(1.4, "mm"), type = "closed")
  ) +
  geom_point(data = key, aes(colour = cid), size = 2.75, alpha = 1) +
  scale_colour_manual(
    values = setNames(c(PUR_COL[["T80"]], PUR_COL[["P"]], PUR_COL[["C"]]), ids),
    labels = setNames(c("L0 property", "L1 constrained", "L2 robust"), ids)
  ) +
  scale_y_continuous(trans = pseudo_log_trans(base = 10), labels = label_number(accuracy = 0.001)) +
  scale_x_continuous(limits = c(25, 51), breaks = seq(25, 50, 5)) +
  labs(x = "MDI fraction of polyol + MDI (%)", y = "Nominal property objective, J") +
  annotate("text", x = 35.25, y = Inf, label = "frozen 35% floor", hjust = 0, vjust = 1.4,
           size = 2.45, colour = PUR_COL[["mid"]]) +
  annotate("text", x = 34.05, y = 6.0e-05, label = "0419\n34.06%", hjust = 1.08, vjust = 0.5,
           size = 2.30, colour = PUR_COL[["T80"]]) +
  annotate("text", x = 36.2, y = 1.8e-04,
           label = "backward feasibility:\nNCO:OH 1.772 → grid 1.8", hjust = 0,
           size = 2.25, colour = PUR_COL[["ink"]]) +
  theme(legend.position = "top", legend.direction = "horizontal", legend.justification = "left")

# B — changing only the MDI floor generates a sequence of decision phases.
phase <- bind_rows(
  phase_nom %>% mutate(layer = "Nominal", y = 2),
  phase_rob %>% mutate(layer = "Robust", y = 1)
) %>%
  mutate(
    xmin = 100 * floor_lo,
    xmax = 100 * floor_hi_inclusive,
    width = xmax - xmin,
    label = ifelse(width >= 0.55, sub("WO_INV_0", "", winner), "")
  )

pB <- ggplot(phase) +
  geom_rect(aes(xmin = xmin, xmax = xmax, ymin = y - 0.28, ymax = y + 0.28, fill = layer),
            colour = "white", linewidth = 0.35) +
  geom_text(data = phase %>% filter(label != ""), aes(x = (xmin + xmax) / 2, y = y, label = label),
            size = 2.05, colour = "white") +
  geom_vline(xintercept = 35, linetype = "22", linewidth = 0.60, colour = PUR_COL[["ink"]]) +
  annotate("text", x = 35.12, y = 2.48, label = "current floor", hjust = 0,
           size = 2.35, colour = PUR_COL[["ink"]]) +
  scale_fill_manual(values = c("Nominal" = PUR_COL[["P"]], "Robust" = PUR_COL[["C"]])) +
  scale_y_continuous(breaks = c(1, 2), labels = c("Robust", "Nominal"), limits = c(0.55, 2.55)) +
  scale_x_continuous(limits = c(30, 40), breaks = seq(30, 40, 2)) +
  labs(x = "Assumed MDI lower bound (%)", y = NULL) +
  theme(legend.position = "none", axis.ticks.y = element_blank(), axis.line.y = element_blank())

# C — global ranks remain similar while the decision-critical top order changes.
ranked <- tab %>% filter(!is.na(nominal_rank), !is.na(robust_rank))
highlight <- ranked %>% filter(cid %in% c(nominal_id, robust_id))

pC <- ggplot(ranked, aes(nominal_rank, robust_rank)) +
  geom_abline(slope = 1, intercept = 0, linetype = "22", linewidth = 0.50, colour = PUR_COL[["mid"]]) +
  geom_point(size = 1.42, alpha = 0.55, colour = PUR_COL[["light"]]) +
  geom_point(data = highlight, aes(colour = cid), size = 3.0, alpha = 1) +
  geom_text(data = highlight,
            aes(label = ifelse(cid == nominal_id, "0579: 1 → 6", "0420: 4 → 1"), colour = cid),
            nudge_x = 5.0, nudge_y = 1.8, hjust = 0, size = 2.35, show.legend = FALSE) +
  scale_colour_manual(values = setNames(c(PUR_COL[["P"]], PUR_COL[["C"]]), c(nominal_id, robust_id))) +
  coord_equal(xlim = c(0, 120), ylim = c(0, 120), expand = FALSE) +
  scale_x_continuous(breaks = seq(0, 120, 20)) +
  scale_y_continuous(breaks = seq(0, 120, 20)) +
  labs(x = "Nominal rank", y = "Robust minimax rank") +
  annotate(
    "text", x = 5, y = 115,
    label = sprintf("ρ = %.3f; τ = %.3f\n%d/%d inversions (%.1f%%)\nTop-1 inversion",
                    metrics$spearman_rho, metrics$kendall_tau,
                    metrics$pairwise_inversions, metrics$total_pairs,
                    100 * metrics$inversion_fraction),
    hjust = 0, vjust = 1, size = 2.40, colour = PUR_COL[["ink"]]
  ) +
  annotate(
    "text", x = 60, y = 12,
    label = sprintf("rank-preservation control:\n%s, τ = %.1f, %d/%d inversions",
                    control$blend, control$kendall_tau,
                    control$pairwise_inversions, control$total_pairs),
    hjust = 0, vjust = 0, size = 2.20, colour = PUR_COL[["mid"]]
  ) +
  theme(legend.position = "none")

fig5 <- (pA | pB | pC) +
  plot_layout(widths = c(1.10, 1.08, 1.12)) +
  plot_annotation(tag_levels = "A")

save_pur_figure(fig5, "figures/final/Figure5_decision_frontier", width_mm = 180, height_mm = 84)
