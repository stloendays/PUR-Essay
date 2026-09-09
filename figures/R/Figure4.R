source("figures/R/theme_pur.R")

pairs <- read_csv("data/figures/cp_matched_pairs.csv", show_col_types = FALSE)
pat <- read_csv("data/figures/us5932680_interaction.csv", show_col_types = FALSE) %>%
  mutate(
    state = factor(state, levels = c("Low A", "High A")),
    background = factor(background, levels = c("C/D balanced", "D-rich"))
  )

pair_long <- pairs %>%
  select(pair, iso, pNCO, ratio80, ratio120) %>%
  pivot_longer(cols = c(ratio80, ratio120), names_to = "temperature", values_to = "CP_ratio") %>%
  mutate(temperature = factor(recode(temperature, ratio80 = "80 °C", ratio120 = "120 °C"), levels = c("80 °C", "120 °C")))

pA <- ggplot(pair_long, aes(temperature, CP_ratio, group = pair)) +
  geom_line(colour = PUR_COL[["light"]], linewidth = 0.72) +
  geom_point(aes(colour = temperature), size = 2.28) +
  scale_colour_manual(values = c("80 °C" = PUR_COL[["T80"]], "120 °C" = PUR_COL[["T120"]]), guide = "none") +
  scale_y_log10(breaks = c(1.5, 2, 3, 4, 6, 8, 10), labels = label_number(accuracy = 0.1)) +
  labs(x = NULL, y = "Matched C/P viscosity ratio") +
  annotate("text", x = 1.03, y = 9.3, label = "Median: 4.20", hjust = 0, size = 2.62, colour = PUR_COL[["T80"]]) +
  annotate("text", x = 1.60, y = 2.15, label = "Median: 2.06", hjust = 0, size = 2.62, colour = PUR_COL[["T120"]])

pB <- ggplot(pairs, aes(reorder(pair, amplification), amplification, colour = iso)) +
  geom_hline(yintercept = 1, linewidth = 0.45, colour = PUR_COL[["ink"]]) +
  geom_hline(yintercept = median(pairs$amplification), linetype = "22", linewidth = 0.55, colour = PUR_COL[["mid"]]) +
  geom_point(size = 2.28) +
  scale_colour_manual(values = c("44M" = PUR_COL[["C"]], "MLQ" = PUR_COL[["D"]])) +
  coord_flip() +
  scale_y_continuous(limits = c(0.9, 3.45), breaks = c(1, 1.5, 2, 2.5, 3, 3.5)) +
  labs(x = NULL, y = "Low-temperature amplification: (C/P)80 / (C/P)120") +
  annotate("text", x = 1, y = 2.04, label = "Median = 1.99×", hjust = 0, size = 2.60, colour = PUR_COL[["ink"]]) +
  theme(
    legend.position = "top",
    legend.direction = "horizontal",
    legend.justification = "left",
    plot.margin = margin(5, 4, 5, 5)
  )

pC <- ggplot(pat, aes(state, eta130, group = background, colour = background)) +
  geom_line(linewidth = 1.02) +
  geom_point(size = 2.65) +
  geom_text(
    aes(label = paste0(eta130, " Pa·s")),
    nudge_y = 0.85,
    show.legend = FALSE,
    size = 2.50,
    colour = PUR_COL[["ink"]]
  ) +
  scale_colour_manual(values = c("C/D balanced" = PUR_COL[["balanced"]], "D-rich" = PUR_COL[["drich"]])) +
  scale_y_continuous(limits = c(18, 54), breaks = seq(20, 50, 5), expand = expansion(mult = c(0, 0.02))) +
  labs(x = "A/B composition state", y = expression(eta[130]~"(Pa·s)")) +
  annotate("text", x = 1.04, y = 53.0, label = "High-A / Low-A", hjust = 0, size = 2.42, colour = PUR_COL[["ink"]]) +
  annotate("text", x = 1.04, y = 51.0, label = "1.654×  balanced", hjust = 0, size = 2.42, colour = PUR_COL[["balanced"]]) +
  annotate("text", x = 1.04, y = 49.0, label = "1.091×  D-rich", hjust = 0, size = 2.42, colour = PUR_COL[["drich"]]) +
  annotate("text", x = 1.04, y = 47.0, label = "ratio-of-ratios = 1.516", hjust = 0, size = 2.42, colour = PUR_COL[["ink"]]) +
  theme(
    legend.position = "bottom",
    legend.direction = "vertical",
    legend.justification = "left",
    legend.background = element_rect(fill = alpha("white", 0.90), colour = NA),
    plot.margin = margin(5, 5, 5, 7)
  )

fig4 <- (pA | pB | pC) +
  plot_layout(widths = c(0.90, 1.07, 1.28)) +
  plot_annotation(tag_levels = "A")

save_pur_figure(fig4, "figures/final/Figure4_chemistry_amplification_interaction", width_mm = 180, height_mm = 82)
