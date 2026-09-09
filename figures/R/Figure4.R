source("figures/R/theme_pur.R")

Rgas <- 8.31446261815324
T80 <- 80 + 273.15
T45 <- 45 + 273.15
T75 <- 75 + 273.15

pairs <- read_csv("data/figures/cp_matched_pairs.csv", show_col_types = FALSE) %>%
  mutate(
    deltaB = delta_Ea * 1000 / Rgas,
    ratio45 = exp(log(ratio80) + deltaB * (1 / T45 - 1 / T80)),
    ratio75 = exp(log(ratio80) + deltaB * (1 / T75 - 1 / T80)),
    amplification_45_75 = ratio45 / ratio75
  )

pat <- read_csv("data/figures/us5932680_interaction.csv", show_col_types = FALSE) %>%
  mutate(
    state = factor(state, levels = c("Low A", "High A")),
    background = factor(background, levels = c("C/D balanced", "D-rich"))
  )

rev <- read_csv("data/figures/us5932680_rank_reversal.csv", show_col_types = FALSE) %>%
  mutate(example = factor(example, levels = c("Example 1", "Example 4")))

pair_long <- pairs %>%
  select(pair, iso, pNCO, ratio45, ratio75) %>%
  pivot_longer(cols = c(ratio45, ratio75), names_to = "temperature", values_to = "CP_ratio") %>%
  mutate(temperature = factor(recode(temperature, ratio45 = "45 °C", ratio75 = "75 °C"),
                              levels = c("45 °C", "75 °C")))

med45 <- median(pairs$ratio45)
med75 <- median(pairs$ratio75)
medamp <- median(pairs$amplification_45_75)

pA <- ggplot(pair_long, aes(temperature, CP_ratio, group = pair)) +
  geom_line(colour = PUR_COL[["light"]], linewidth = 0.72) +
  geom_point(aes(colour = temperature), size = 2.28) +
  scale_colour_manual(values = c("45 °C" = PUR_COL[["T80"]], "75 °C" = PUR_COL[["T120"]]), guide = "none") +
  scale_y_log10(breaks = c(2, 3, 4, 6, 8, 12, 16, 24), labels = label_number(accuracy = 0.1)) +
  labs(x = NULL, y = "Matched C/P viscosity ratio") +
  annotate("text", x = 1.02, y = max(pairs$ratio45) * 0.96,
           label = sprintf("Median: %.2f", med45), hjust = 0, size = 2.62, colour = PUR_COL[["T80"]]) +
  annotate("text", x = 1.58, y = med75 * 0.92,
           label = sprintf("Median: %.2f", med75), hjust = 0, size = 2.62, colour = PUR_COL[["T120"]])

pB <- ggplot(pairs, aes(reorder(pair, amplification_45_75), amplification_45_75, colour = iso)) +
  geom_hline(yintercept = 1, linewidth = 0.45, colour = PUR_COL[["ink"]]) +
  geom_hline(yintercept = medamp, linetype = "22", linewidth = 0.55, colour = PUR_COL[["mid"]]) +
  geom_point(size = 2.28) +
  scale_colour_manual(values = c("44M" = PUR_COL[["C"]], "MLQ" = PUR_COL[["D"]])) +
  coord_flip() +
  scale_y_continuous(expand = expansion(mult = c(0.05, 0.12))) +
  labs(x = NULL, y = "Low-temperature amplification: (C/P)45 / (C/P)75") +
  annotate("text", x = 1, y = medamp * 1.03, label = sprintf("Median = %.2f×", medamp),
           hjust = 0, size = 2.60, colour = PUR_COL[["ink"]]) +
  theme(legend.position = "top", legend.direction = "horizontal", legend.justification = "left")

pC <- ggplot(pat, aes(state, eta130, group = background, colour = background)) +
  geom_line(linewidth = 1.02) +
  geom_point(size = 2.65) +
  geom_text(aes(label = paste0(eta130, " Pa·s")), nudge_y = 0.85,
            show.legend = FALSE, size = 2.42, colour = PUR_COL[["ink"]]) +
  scale_colour_manual(values = c("C/D balanced" = PUR_COL[["balanced"]], "D-rich" = PUR_COL[["drich"]])) +
  scale_y_continuous(limits = c(18, 54), breaks = seq(20, 50, 5), expand = expansion(mult = c(0, 0.02))) +
  labs(x = "A/B composition state", y = expression(eta[130]~"(Pa·s)")) +
  annotate("text", x = 1.04, y = 52.7, label = "effect-size interaction", hjust = 0,
           size = 2.42, colour = PUR_COL[["ink"]]) +
  annotate("text", x = 1.04, y = 50.3, label = "1.654×  balanced", hjust = 0,
           size = 2.42, colour = PUR_COL[["balanced"]]) +
  annotate("text", x = 1.04, y = 47.9, label = "1.091×  D-rich", hjust = 0,
           size = 2.42, colour = PUR_COL[["drich"]]) +
  annotate("text", x = 1.04, y = 45.5, label = "ratio-of-ratios = 1.516", hjust = 0,
           size = 2.42, colour = PUR_COL[["ink"]]) +
  theme(legend.position = "bottom", legend.direction = "horizontal", legend.justification = "left")

pD <- ggplot(rev, aes(temperature_c, eta_pa_s, group = example, colour = example)) +
  geom_line(linewidth = 1.00) +
  geom_point(size = 2.65) +
  geom_text(aes(label = eta_pa_s), nudge_x = 0.7, show.legend = FALSE,
            size = 2.45, colour = PUR_COL[["ink"]]) +
  scale_colour_manual(values = c("Example 1" = PUR_COL[["T80"]], "Example 4" = PUR_COL[["P"]])) +
  scale_x_continuous(breaks = c(90, 110), limits = c(88, 114)) +
  scale_y_log10(breaks = c(50, 60, 100, 200), labels = label_number(accuracy = 1)) +
  labs(x = "Temperature (°C)", y = "Published viscosity (Pa·s)") +
  annotate("text", x = 89, y = 220, label = "190 > 98", hjust = 0,
           size = 2.50, colour = PUR_COL[["ink"]]) +
  annotate("text", x = 106.5, y = 48, label = "55 < 60", hjust = 0,
           size = 2.50, colour = PUR_COL[["ink"]]) +
  theme(legend.position = "bottom", legend.direction = "horizontal", legend.justification = "left")

fig4 <- ((pA | pB) / (pC | pD)) +
  plot_layout(heights = c(1.00, 1.05)) +
  plot_annotation(tag_levels = "A")

save_pur_figure(fig4, "figures/final/Figure4_chemistry_amplification_interaction", width_mm = 180, height_mm = 112)
