source("figures/R/theme_pur.R")

fits <- read_csv("data/figures/pugar_andrade_fits.csv", show_col_types = FALSE) %>%
  mutate(polyol = factor(polyol, levels = c("P", "D", "C")))

tgrid <- seq(80, 120, by = 1)
curves <- fits %>%
  select(sample_id, polyol, A, B, eta120) %>%
  tidyr::crossing(temperature_c = tgrid) %>%
  mutate(
    eta_fit = exp(A + B / (temperature_c + 273.15)),
    eta_norm = eta_fit / eta120
  )

med_curves <- curves %>%
  group_by(polyol, temperature_c) %>%
  summarise(eta_norm = median(eta_norm), .groups = "drop")

pA <- ggplot(curves, aes(temperature_c, eta_norm, group = sample_id, colour = polyol)) +
  geom_line(alpha = 0.20, linewidth = 0.40) +
  geom_line(data = med_curves, aes(group = polyol), linewidth = 1.08, alpha = 1) +
  scale_colour_manual(values = PUR_COL[c("P", "D", "C")], labels = c("P", "D", "C")) +
  scale_y_log10(breaks = c(1, 2, 4, 8, 16), labels = label_number(accuracy = 1)) +
  scale_x_continuous(breaks = seq(80, 120, 10), expand = expansion(mult = c(0.01, 0.02))) +
  labs(x = "Temperature (°C)", y = expression(eta[T] / eta[120])) +
  guides(colour = guide_legend(override.aes = list(alpha = 1, linewidth = 1.1))) +
  theme(
    legend.position = c(0.16, 0.19),
    legend.background = element_rect(fill = alpha("white", 0.90), colour = NA),
    legend.key.width = grid::unit(5.5, "mm")
  )

pB <- ggplot(fits, aes(r2, polyol, colour = polyol)) +
  geom_vline(xintercept = 0.98, linetype = "22", linewidth = 0.48, colour = PUR_COL[["mid"]]) +
  geom_jitter(width = 0, height = 0.105, size = 1.75, alpha = 0.92) +
  scale_colour_manual(values = PUR_COL[c("P", "D", "C")]) +
  scale_x_continuous(
    limits = c(0.84, 1.003),
    breaks = c(0.85, 0.90, 0.95, 0.98, 1.00),
    labels = label_number(accuracy = 0.01)
  ) +
  labs(x = expression(Andrade~R^2), y = NULL) +
  annotate("text", x = 0.982, y = 3.32, label = "37/39 ≥ 0.98", hjust = 0, size = 2.65, colour = PUR_COL[["ink"]]) +
  theme(legend.position = "none", plot.margin = margin(4, 6, 7, 5))

pC <- ggplot(fits, aes(polyol, Ea_kJmol, colour = polyol)) +
  geom_boxplot(width = 0.50, outlier.shape = NA, linewidth = 0.52, fill = "white", colour = PUR_COL[["ink"]]) +
  geom_jitter(width = 0.10, size = 1.75, alpha = 0.90) +
  scale_colour_manual(values = PUR_COL[c("P", "D", "C")]) +
  scale_y_continuous(breaks = seq(30, 100, 10), expand = expansion(mult = c(0.03, 0.06))) +
  labs(x = "Polyol code", y = expression(E[a,app]~"(kJ mol"^{-1}*")")) +
  annotate("text", x = 1.02, y = 96.5, label = "Overall median = 51.09", hjust = 0, size = 2.55, colour = PUR_COL[["ink"]]) +
  theme(legend.position = "none", plot.margin = margin(6, 6, 4, 5))

fig2 <- (pA | (pB / pC)) +
  plot_layout(widths = c(1.60, 1.00)) +
  plot_annotation(tag_levels = "A")

save_pur_figure(fig2, "figures/final/Figure2_temperature_Andrade", width_mm = 180, height_mm = 84)
