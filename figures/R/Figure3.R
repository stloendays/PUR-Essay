source("figures/R/theme_pur.R")

eff <- read_csv("data/figures/pnco_family_effects.csv", show_col_types = FALSE) %>%
  mutate(mean_mult = (multiplier_eta80 + multiplier_eta120) / 2) %>%
  arrange(mean_mult) %>%
  mutate(family = factor(family, levels = family))

long <- eff %>%
  select(family, multiplier_eta80, multiplier_eta120) %>%
  pivot_longer(cols = starts_with("multiplier"), names_to = "temperature", values_to = "multiplier") %>%
  mutate(temperature = recode(temperature, multiplier_eta80 = "80 °C", multiplier_eta120 = "120 °C"))

segments <- eff %>%
  transmute(family, xmin = pmin(multiplier_eta80, multiplier_eta120), xmax = pmax(multiplier_eta80, multiplier_eta120))

pA <- ggplot() +
  geom_segment(data = segments, aes(x = xmin, xend = xmax, y = family, yend = family), linewidth = 0.65, colour = PUR_COL[["light"]]) +
  geom_point(data = long, aes(multiplier, family, colour = temperature), size = 2.15) +
  geom_vline(xintercept = 1, linewidth = 0.45, colour = PUR_COL[["ink"]]) +
  scale_colour_manual(values = c("80 °C" = PUR_COL[["T80"]], "120 °C" = PUR_COL[["T120"]])) +
  scale_x_continuous(limits = c(0.64, 1.01), breaks = seq(0.65, 1.00, 0.05), labels = label_number(accuracy = 0.01)) +
  labs(x = "Viscosity multiplier per +1% free NCO", y = NULL) +
  annotate("text", x = 0.665, y = 10.72, label = "Median 80 °C: 0.742", hjust = 0, size = 2.58, colour = PUR_COL[["T80"]]) +
  annotate("text", x = 0.665, y = 9.84, label = "Median 120 °C: 0.783", hjust = 0, size = 2.58, colour = PUR_COL[["T120"]]) +
  theme(
    legend.position = "bottom",
    legend.direction = "horizontal",
    legend.justification = "left",
    plot.margin = margin(5, 4, 2, 5)
  )

pB <- ggplot(eff, aes(slope_Ea_kJmol_per_pctNCO, family)) +
  geom_vline(xintercept = 0, linewidth = 0.45, colour = PUR_COL[["ink"]]) +
  geom_segment(aes(x = 0, xend = slope_Ea_kJmol_per_pctNCO, yend = family), linewidth = 0.80, colour = PUR_COL[["light"]]) +
  geom_point(aes(colour = slope_Ea_kJmol_per_pctNCO < 0), size = 2.25) +
  scale_colour_manual(values = c(`TRUE` = PUR_COL[["C"]], `FALSE` = PUR_COL[["mid"]]), guide = "none") +
  scale_x_continuous(breaks = seq(-3, 0.5, 0.5), expand = expansion(mult = c(0.04, 0.10))) +
  labs(x = expression(Delta*E[a,app]~"per +1% NCO (kJ mol"^{-1}*")"), y = NULL) +
  annotate("text", x = -3.05, y = 10.72, label = "9/11 families decrease", hjust = 0, size = 2.60, colour = PUR_COL[["ink"]])

pC <- ggplot(eff, aes(multiplier_eta120, multiplier_eta80, colour = polyol)) +
  geom_abline(slope = 1, intercept = 0, linetype = "22", linewidth = 0.48, colour = PUR_COL[["mid"]]) +
  geom_point(size = 2.30, alpha = 0.96) +
  scale_colour_manual(values = PUR_COL[c("P", "D", "C")]) +
  coord_cartesian(xlim = c(0.66, 0.97), ylim = c(0.66, 0.97), expand = FALSE) +
  scale_x_continuous(breaks = seq(0.70, 0.95, 0.05)) +
  scale_y_continuous(breaks = seq(0.70, 0.95, 0.05)) +
  labs(x = "120 °C multiplier", y = "80 °C multiplier") +
  annotate("text", x = 0.675, y = 0.955, label = "below diagonal:\nstronger at 80 °C", hjust = 0, vjust = 1, size = 2.30, colour = PUR_COL[["mid"]]) +
  theme(
    legend.position = "top",
    legend.direction = "horizontal",
    legend.justification = "left",
    plot.margin = margin(5, 5, 5, 8)
  )

fig3 <- (pA | pB | pC) +
  plot_layout(widths = c(1.24, 1.16, 1.08)) +
  plot_annotation(tag_levels = "A")

save_pur_figure(fig3, "figures/final/Figure3_free_NCO_coupling", width_mm = 180, height_mm = 82)
