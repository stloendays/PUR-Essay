source("figures/R/theme_pur.R")

Rgas <- 8.31446261815324
T80 <- 80 + 273.15
T45 <- 45 + 273.15
T75 <- 75 + 273.15

eff <- read_csv("data/figures/pnco_family_effects.csv", show_col_types = FALSE) %>%
  mutate(
    dB_dNCO = slope_Ea_kJmol_per_pctNCO * 1000 / Rgas,
    slope_log10_eta45 = slope_log10_eta80 + dB_dNCO / log(10) * (1 / T45 - 1 / T80),
    slope_log10_eta75 = slope_log10_eta80 + dB_dNCO / log(10) * (1 / T75 - 1 / T80),
    multiplier_eta45 = 10^slope_log10_eta45,
    multiplier_eta75 = 10^slope_log10_eta75,
    mean_mult = (multiplier_eta45 + multiplier_eta75) / 2
  ) %>%
  arrange(mean_mult) %>%
  mutate(family = factor(family, levels = family))

long <- eff %>%
  select(family, multiplier_eta45, multiplier_eta75) %>%
  pivot_longer(cols = starts_with("multiplier"), names_to = "temperature", values_to = "multiplier") %>%
  mutate(temperature = recode(temperature, multiplier_eta45 = "45 °C", multiplier_eta75 = "75 °C"))

segments <- eff %>%
  transmute(family, xmin = pmin(multiplier_eta45, multiplier_eta75), xmax = pmax(multiplier_eta45, multiplier_eta75))

m45 <- median(eff$multiplier_eta45)
m75 <- median(eff$multiplier_eta75)

pA <- ggplot() +
  geom_segment(data = segments, aes(x = xmin, xend = xmax, y = family, yend = family),
               linewidth = 0.65, colour = PUR_COL[["light"]]) +
  geom_point(data = long, aes(multiplier, family, colour = temperature), size = 2.15) +
  geom_vline(xintercept = 1, linewidth = 0.45, colour = PUR_COL[["ink"]]) +
  scale_colour_manual(values = c("45 °C" = PUR_COL[["T80"]], "75 °C" = PUR_COL[["T120"]])) +
  scale_x_continuous(limits = c(0.57, 1.01), breaks = seq(0.60, 1.00, 0.05), labels = label_number(accuracy = 0.01)) +
  labs(x = "Viscosity multiplier per +1 wt%-point free NCO", y = NULL) +
  annotate("text", x = 0.585, y = 10.72, label = sprintf("Median 45 °C: %.3f", m45), hjust = 0,
           size = 2.58, colour = PUR_COL[["T80"]]) +
  annotate("text", x = 0.585, y = 9.84, label = sprintf("Median 75 °C: %.3f", m75), hjust = 0,
           size = 2.58, colour = PUR_COL[["T120"]]) +
  theme(
    legend.position = "bottom",
    legend.direction = "horizontal",
    legend.justification = "left",
    plot.margin = margin(5, 4, 2, 5)
  )

pB <- ggplot(eff, aes(slope_Ea_kJmol_per_pctNCO, family)) +
  geom_vline(xintercept = 0, linewidth = 0.45, colour = PUR_COL[["ink"]]) +
  geom_segment(aes(x = 0, xend = slope_Ea_kJmol_per_pctNCO, yend = family),
               linewidth = 0.80, colour = PUR_COL[["light"]]) +
  geom_point(aes(colour = slope_Ea_kJmol_per_pctNCO < 0), size = 2.25) +
  scale_colour_manual(values = c(`TRUE` = PUR_COL[["C"]], `FALSE` = PUR_COL[["mid"]]), guide = "none") +
  scale_x_continuous(breaks = seq(-3, 0.5, 0.5), expand = expansion(mult = c(0.04, 0.10))) +
  labs(x = expression(Delta*E[a,app]~"per +1 wt%-point NCO (kJ mol"^{-1}*")"), y = NULL) +
  annotate("text", x = -3.05, y = 10.72, label = "9/11 families decrease", hjust = 0,
           size = 2.60, colour = PUR_COL[["ink"]])

pC <- ggplot(eff, aes(multiplier_eta75, multiplier_eta45, colour = polyol)) +
  geom_abline(slope = 1, intercept = 0, linetype = "22", linewidth = 0.48, colour = PUR_COL[["mid"]]) +
  geom_point(size = 2.30, alpha = 0.96) +
  scale_colour_manual(values = PUR_COL[c("P", "D", "C")]) +
  coord_cartesian(xlim = c(0.58, 0.98), ylim = c(0.58, 0.98), expand = FALSE) +
  scale_x_continuous(breaks = seq(0.60, 0.95, 0.05)) +
  scale_y_continuous(breaks = seq(0.60, 0.95, 0.05)) +
  labs(x = "75 °C multiplier", y = "45 °C multiplier") +
  annotate("text", x = 0.595, y = 0.962, label = "below diagonal:\nstronger at lower T", hjust = 0, vjust = 1,
           size = 2.30, colour = PUR_COL[["mid"]]) +
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
