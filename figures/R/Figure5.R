source("figures/R/theme_pur.R")

rank_pairs <- read_csv("data/figures/frontier_rank_pairs.csv", show_col_types = FALSE)
backward <- read_csv("data/figures/backward_local_curve.csv", show_col_types = FALSE)
control <- read_csv("data/figures/rank_preservation_control.csv", show_col_types = FALSE)

frontier_cols <- c(
  constrained_winner = PUR_COL[["T80"]],
  robust_winner = PUR_COL[["C"]],
  other = PUR_COL[["light"]]
)

# A — Global rank preservation with a changed decision-frontier winner.
pA <- ggplot(rank_pairs, aes(rank_nom_within_robust, rank_robust_within_robust)) +
  geom_abline(slope = 1, intercept = 0, linetype = "22", linewidth = 0.50, colour = PUR_COL[["mid"]]) +
  geom_point(
    data = filter(rank_pairs, highlight == "other"),
    size = 1.45, alpha = 0.72, colour = PUR_COL[["light"]]
  ) +
  geom_point(
    data = filter(rank_pairs, highlight != "other"),
    aes(colour = highlight), size = 3.0, alpha = 1
  ) +
  scale_colour_manual(values = frontier_cols, guide = "none") +
  scale_x_continuous(breaks = c(1, 20, 40, 60, 80, 100, 117), limits = c(0, 118)) +
  scale_y_continuous(breaks = c(1, 20, 40, 60, 80, 100, 117), limits = c(0, 118)) +
  coord_equal() +
  labs(x = "Nominal rank within robust-admissible set", y = "Worst-case robust rank") +
  annotate("text", x = 63, y = 8,
           label = "Spearman ρ = 0.985\nKendall τ = 0.892\n367 / 6786 inversions (5.41%)",
           hjust = 0, vjust = 0, size = 2.55, colour = PUR_COL[["ink"]]) +
  annotate("text", x = 5.5, y = 9.5, label = "L1 winner", hjust = 0, size = 2.45, colour = PUR_COL[["T80"]]) +
  annotate("text", x = 5.5, y = 2.0, label = "L2 winner", hjust = 0, size = 2.45, colour = PUR_COL[["C"]]) +
  theme(plot.margin = margin(5, 7, 5, 5))

# B — Enlarge only the top of the decision frontier.
top_ids <- rank_pairs %>%
  filter(rank_nom_within_robust <= 8 | rank_robust_within_robust <= 8) %>%
  pull(source_candidate_id)

top_long <- rank_pairs %>%
  filter(source_candidate_id %in% top_ids) %>%
  select(source_candidate_id, highlight, rank_nom_within_robust, rank_robust_within_robust) %>%
  pivot_longer(
    cols = c(rank_nom_within_robust, rank_robust_within_robust),
    names_to = "layer", values_to = "rank"
  ) %>%
  mutate(
    layer = factor(layer,
                   levels = c("rank_nom_within_robust", "rank_robust_within_robust"),
                   labels = c("Nominal", "Robust")),
    line_class = if_else(highlight == "other", "other", highlight)
  )

pB <- ggplot(top_long, aes(layer, rank, group = source_candidate_id, colour = line_class)) +
  geom_line(linewidth = 0.85, alpha = 0.92) +
  geom_point(size = 2.05) +
  scale_colour_manual(values = frontier_cols, guide = "none") +
  scale_y_reverse(limits = c(15.5, 0.5), breaks = 1:15) +
  labs(x = NULL, y = "Rank") +
  annotate("text", x = 1.02, y = 1.0, label = "WO_INV_0579", hjust = 0, vjust = 1.3,
           size = 2.45, colour = PUR_COL[["T80"]]) +
  annotate("text", x = 1.98, y = 1.0, label = "WO_INV_0420", hjust = 1, vjust = 1.3,
           size = 2.45, colour = PUR_COL[["C"]]) +
  annotate("text", x = 1.50, y = 14.3, label = "top-rank reshuffling", hjust = 0.5,
           size = 2.45, colour = PUR_COL[["mid"]]) +
  theme(plot.margin = margin(5, 5, 5, 7))

# C — Backward solution of the active 35 wt% MDI constraint and grid reachability.
backward <- backward %>%
  mutate(point_class = case_when(
    source_candidate_id == "WO_INV_0419" ~ "property_winner",
    source_candidate_id == "WO_INV_0420" ~ "robust_winner",
    TRUE ~ "other"
  ))

pC <- ggplot(backward, aes(nco_oh, mdi_fraction_total)) +
  geom_hline(yintercept = 0.35, linetype = "22", linewidth = 0.60, colour = PUR_COL[["ink"]]) +
  geom_vline(xintercept = 1.771983672436162, linetype = "13", linewidth = 0.55, colour = PUR_COL[["mid"]]) +
  geom_line(linewidth = 0.95, colour = PUR_COL[["mid"]]) +
  geom_point(data = filter(backward, point_class == "other"), size = 1.65, colour = PUR_COL[["light"]]) +
  geom_point(data = filter(backward, point_class == "property_winner"), size = 3.0, colour = PUR_COL[["T80"]]) +
  geom_point(data = filter(backward, point_class == "robust_winner"), size = 3.0, colour = PUR_COL[["C"]]) +
  scale_x_continuous(breaks = seq(1.5, 3.0, 0.3), limits = c(1.48, 3.02)) +
  scale_y_continuous(labels = label_percent(accuracy = 1), breaks = seq(0.30, 0.48, 0.03), limits = c(0.30, 0.485)) +
  labs(x = "NCO:OH at PPG1000/PPG700 = 50/50", y = "MDI fraction of polyol + MDI") +
  annotate("text", x = 2.60, y = 0.354, label = "35 wt% feasibility boundary", hjust = 0.5,
           size = 2.45, colour = PUR_COL[["ink"]]) +
  annotate("text", x = 1.748, y = 0.318, label = "continuous\nthreshold 1.772", hjust = 1,
           size = 2.35, colour = PUR_COL[["mid"]]) +
  annotate("text", x = 1.675, y = 0.337, label = "0419", hjust = 1,
           size = 2.45, colour = PUR_COL[["T80"]]) +
  annotate("text", x = 1.825, y = 0.363, label = "0420\nreachable at 1.8", hjust = 0,
           size = 2.45, colour = PUR_COL[["C"]]) +
  theme(plot.margin = margin(5, 7, 5, 5))

# D — A rank-preservation control in one fixed chemistry family.
pD <- ggplot(control, aes(rn, rr)) +
  geom_abline(slope = 1, intercept = 0, linetype = "22", linewidth = 0.50, colour = PUR_COL[["mid"]]) +
  geom_line(linewidth = 0.85, colour = PUR_COL[["C"]], alpha = 0.65) +
  geom_point(size = 2.35, colour = PUR_COL[["C"]]) +
  geom_text(aes(label = nco_oh), nudge_x = 0.18, nudge_y = -0.18, size = 2.15, colour = PUR_COL[["ink"]]) +
  coord_equal(xlim = c(0.5, 8.7), ylim = c(0.5, 8.7), expand = FALSE) +
  scale_x_continuous(breaks = 1:8) +
  scale_y_continuous(breaks = 1:8) +
  labs(x = "Nominal rank", y = "Robust rank") +
  annotate("text", x = 1.0, y = 8.25,
           label = "PPG1000/PPG700 = 50/50\nNCO:OH 1.8–2.5\nρ = 1.000, τ = 1.000\n0 inversions",
           hjust = 0, vjust = 1, size = 2.45, colour = PUR_COL[["ink"]]) +
  theme(plot.margin = margin(5, 5, 5, 7))

fig5 <- (pA | pB) / (pC | pD) +
  plot_layout(widths = c(1.30, 1.00), heights = c(1.00, 1.02)) +
  plot_annotation(tag_levels = "A")

save_pur_figure(fig5, "figures/final/Figure5_decision_frontier", width_mm = 180, height_mm = 142)
