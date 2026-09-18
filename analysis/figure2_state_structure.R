suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(tidyr)
  library(patchwork)
  library(scales)
})
source("analysis/plot_style.R")

dir.create("figures/r_manuscript", recursive = TRUE, showWarnings = FALSE)

raw <- read.csv(
  "data/prospective_validation/experimental_viscosity_v1.csv",
  stringsAsFactors = FALSE
)

sw <- raw |>
  filter(measurement_type == "temperature_sweep") |>
  mutate(
    temp_K = temperature_c + 273.15,
    invT = 1 / temp_K,
    log_eta = log(viscosity_raw)
  )

realization_levels <- c(
  "E1_initial", "E1_repeat_day1", "E2_GJJ", "E2_ZYX",
  "E2_CHH", "E2_ZYX_day1", "E3_CHH"
)

realization_labels <- c(
  E1_initial = "E1 initial",
  E1_repeat_day1 = "E1 day-1",
  E2_GJJ = "E2 GJJ",
  E2_ZYX = "E2 ZYX",
  E2_CHH = "E2 CHH",
  E2_ZYX_day1 = "E2 ZYX day-1",
  E3_CHH = "E3 CHH"
)

sw <- sw |>
  mutate(replicate_id = factor(replicate_id, levels = realization_levels))

# ---------- statistics ----------
wide <- sw |>
  select(replicate_id, temperature_c, viscosity_raw) |>
  pivot_wider(names_from = temperature_c, values_from = viscosity_raw) |>
  arrange(replicate_id)

mat <- as.matrix(wide[, -1])
pca <- prcomp(mat, center = TRUE, scale. = FALSE)
pc1 <- 100 * summary(pca)$importance[2, 1]

cosine <- function(x, y) sum(x * y) / sqrt(sum(x^2) * sum(y^2))
pair_idx <- combn(seq_len(nrow(mat)), 2)
cos_vals <- apply(pair_idx, 2, function(ii) cosine(mat[ii[1], ], mat[ii[2], ]))
mean_cos <- mean(cos_vals)

fit_real <- lm(log_eta ~ invT + replicate_id, data = sw)
sw$residual_shared <- residuals(fit_real)

fit_form <- lm(log_eta ~ invT + formulation_id, data = sw)
r2_form <- summary(fit_form)$r.squared
r2_real <- summary(fit_real)$r.squared

# held-temperature interpolation RMSE
temps <- sort(unique(sw$temperature_c))
cv_rows <- lapply(temps, function(tt) {
  train <- sw |> filter(temperature_c != tt)
  test <- sw |> filter(temperature_c == tt)

  mf <- lm(log_eta ~ invT + formulation_id, data = train)
  mr <- lm(log_eta ~ invT + replicate_id, data = train)

  data.frame(
    temp = tt,
    model = c("Formulation-only", "Realization-aware"),
    se = c(
      (test$log_eta - predict(mf, newdata = test))^2,
      (test$log_eta - predict(mr, newdata = test))^2
    ) |> I()
  )
})
# compute directly to avoid list-column ambiguity
se_form <- c()
se_real <- c()
for (tt in temps) {
  train <- sw |> filter(temperature_c != tt)
  test <- sw |> filter(temperature_c == tt)
  mf <- lm(log_eta ~ invT + formulation_id, data = train)
  mr <- lm(log_eta ~ invT + replicate_id, data = train)
  se_form <- c(se_form, (test$log_eta - predict(mf, newdata = test))^2)
  se_real <- c(se_real, (test$log_eta - predict(mr, newdata = test))^2)
}
rmse_form <- sqrt(mean(se_form))
rmse_real <- sqrt(mean(se_real))
rmse_reduction <- 100 * (1 - rmse_real / rmse_form)

# ---------- Panel A ----------
e2 <- sw |>
  filter(formulation_id == "E2") |>
  mutate(series = factor(replicate_id, levels = c("E2_GJJ", "E2_ZYX", "E2_CHH", "E2_ZYX_day1")))

e2_cols <- c(
  E2_GJJ = "#A9C2D0",
  E2_ZYX = "#6E9FB2",
  E2_CHH = PUR_COLORS$navy,
  E2_ZYX_day1 = PUR_COLORS$teal
)

y80_gjj <- e2 |> filter(replicate_id == "E2_GJJ", temperature_c == 80) |> pull(viscosity_raw)
y80_chh <- e2 |> filter(replicate_id == "E2_CHH", temperature_c == 80) |> pull(viscosity_raw)
y120_gjj <- e2 |> filter(replicate_id == "E2_GJJ", temperature_c == 120) |> pull(viscosity_raw)
y120_chh <- e2 |> filter(replicate_id == "E2_CHH", temperature_c == 120) |> pull(viscosity_raw)

pA <- ggplot(e2, aes(temperature_c, viscosity_raw, colour = series, group = series)) +
  geom_line(linewidth = 1.05) +
  geom_point(size = 2.45) +
  annotate("segment", x = 81.5, xend = 81.5, y = y80_gjj, yend = y80_chh,
           colour = PUR_COLORS$orange, linewidth = 0.8) +
  annotate("text", x = 82.4, y = sqrt(y80_gjj * y80_chh), label = "2.89×",
           colour = PUR_COLORS$orange, fontface = "bold", hjust = 0, size = 3.35) +
  annotate("segment", x = 121.5, xend = 121.5, y = y120_gjj, yend = y120_chh,
           colour = PUR_COLORS$orange, linewidth = 0.8) +
  annotate("text", x = 122.4, y = sqrt(y120_gjj * y120_chh), label = "3.57×",
           colour = PUR_COLORS$orange, fontface = "bold", hjust = 0, size = 3.35) +
  scale_colour_manual(
    values = e2_cols,
    labels = c("E2 GJJ", "E2 ZYX", "E2 CHH", "E2 ZYX day-1")
  ) +
  scale_y_log10(labels = label_number(big.mark = ",")) +
  scale_x_continuous(breaks = temps) +
  labs(
    title = "Same nominal E2 formulation, different realizations",
    x = "Temperature (°C)",
    y = "Viscosity (raw unit)"
  ) +
  theme_pur() +
  theme(legend.position = c(0.80, 0.84), legend.background = element_blank())

# ---------- Panel B ----------
norm <- sw |>
  group_by(replicate_id) |>
  mutate(
    eta110 = viscosity_raw[temperature_c == 110][1],
    log_rel = log(viscosity_raw / eta110)
  ) |>
  ungroup()

mean_profile <- norm |>
  group_by(temperature_c) |>
  summarise(mean_log_rel = mean(log_rel), .groups = "drop")

pB <- ggplot(norm, aes(temperature_c, log_rel, group = replicate_id)) +
  geom_hline(yintercept = 0, linetype = "dashed", colour = "#7E858D", linewidth = 0.6) +
  geom_line(colour = PUR_COLORS$grey, linewidth = 0.75, alpha = 0.72) +
  geom_point(colour = PUR_COLORS$grey, size = 1.7, alpha = 0.80) +
  geom_line(
    data = mean_profile,
    aes(temperature_c, mean_log_rel, group = 1),
    inherit.aes = FALSE, colour = PUR_COLORS$teal, linewidth = 1.4
  ) +
  geom_point(
    data = mean_profile,
    aes(temperature_c, mean_log_rel),
    inherit.aes = FALSE, colour = PUR_COLORS$teal, size = 2.7
  ) +
  annotate(
    "text", x = 80.7, y = min(norm$log_rel) + 0.06,
    label = sprintf("PC1 = %.2f%%\nmean cosine = %.5f", pc1, mean_cos),
    hjust = 0, vjust = 0, colour = PUR_COLORS$teal,
    fontface = "bold", size = 3.35, lineheight = 0.95
  ) +
  scale_x_continuous(breaks = temps) +
  labs(
    title = "A near-common thermal shape remains after level normalization",
    x = "Temperature (°C)",
    y = expression(log(eta(T)/eta(110*degree*C)))
  ) +
  theme_pur()

# ---------- Panel C ----------
heat <- sw |>
  mutate(
    realization = factor(
      as.character(replicate_id),
      levels = rev(realization_levels),
      labels = rev(realization_labels[realization_levels])
    )
  )

lim <- 0.15
pC <- ggplot(heat, aes(temperature_c, realization, fill = residual_shared)) +
  geom_tile(width = 10.1, height = 1.02) +
  scale_fill_gradient2(
    low = PUR_COLORS$navy, mid = "white", high = "#C94B3B",
    midpoint = 0, limits = c(-lim, lim), oob = squish,
    name = "log residual"
  ) +
  scale_x_continuous(breaks = temps) +
  labs(
    title = "Residuals after shared slope + realization-specific level",
    x = "Temperature (°C)",
    y = NULL
  ) +
  theme_pur() +
  theme(
    panel.grid = element_blank(),
    legend.position = "right",
    legend.title = element_text(size = 9),
    legend.key.height = grid::unit(18, "mm")
  )

# ---------- Panel D ----------
node <- data.frame(
  metric = factor(c("R²", "R²", "Held-temperature\nRMSE (ln η)", "Held-temperature\nRMSE (ln η)"),
                  levels = c("Held-temperature\nRMSE (ln η)", "R²")),
  model = factor(c("Formulation-only", "Realization-aware", "Formulation-only", "Realization-aware"),
                 levels = c("Formulation-only", "Realization-aware")),
  x = c(1, 2, 1, 2),
  value = c(r2_form, r2_real, rmse_form, rmse_real)
)

arrow_df <- data.frame(
  y = c(2, 1),
  x = 1.16,
  xend = 1.84
)

pD <- ggplot() +
  geom_segment(
    data = arrow_df,
    aes(x = x, xend = xend, y = y, yend = y),
    colour = PUR_COLORS$grey, linewidth = 0.9,
    arrow = arrow(length = grid::unit(2.3, "mm"), type = "closed")
  ) +
  geom_point(
    data = node,
    aes(x = x, y = as.numeric(metric), fill = model),
    shape = 21, colour = "white", stroke = 1.2, size = 9.2
  ) +
  geom_text(
    data = node,
    aes(x = x, y = as.numeric(metric), label = sprintf("%.3f", value)),
    colour = "white", fontface = "bold", size = 3.6
  ) +
  annotate("text", x = 1.5, y = 2.28, label = sprintf("+%.3f", r2_real - r2_form),
           fontface = "bold", colour = PUR_COLORS$ink, size = 3.4) +
  annotate("text", x = 1.5, y = 1.28, label = sprintf("−%.1f%%", rmse_reduction),
           fontface = "bold", colour = PUR_COLORS$ink, size = 3.4) +
  scale_fill_manual(values = c("Formulation-only" = PUR_COLORS$navy, "Realization-aware" = PUR_COLORS$teal)) +
  scale_x_continuous(
    breaks = c(1, 2),
    labels = c("Formulation-only", "Realization-aware"),
    limits = c(0.55, 2.45)
  ) +
  scale_y_continuous(
    breaks = c(1, 2),
    labels = c("Held-temperature\nRMSE (ln η)", "R²"),
    limits = c(0.65, 2.42)
  ) +
  labs(
    title = "Explicit realization state explains viscosity-level shifts",
    x = NULL, y = NULL
  ) +
  theme_pur() +
  theme(
    panel.grid = element_blank(),
    legend.position = "none",
    axis.ticks = element_blank()
  )

fig2 <- (pA | pB) / (pC | pD) +
  plot_annotation(tag_levels = "A") +
  plot_layout(guides = "keep")

ggsave("figures/r_manuscript/Figure2_state_structure_R.png", fig2,
       width = 14.2, height = 9.7, units = "in", dpi = 320, bg = "white")
ggsave("figures/r_manuscript/Figure2_state_structure_R.pdf", fig2,
       width = 14.2, height = 9.7, units = "in", device = cairo_pdf, bg = "white")
ggsave("figures/r_manuscript/Figure2_state_structure_R.svg", fig2,
       width = 14.2, height = 9.7, units = "in", bg = "white")

save_panel(pA, "figures/r_manuscript/Figure2A_R.png")
save_panel(pB, "figures/r_manuscript/Figure2B_R.png")
save_panel(pC, "figures/r_manuscript/Figure2C_R.png")
save_panel(pD, "figures/r_manuscript/Figure2D_R.png")

cat(sprintf(
  "Figure 2 rendered. PC1 %.4f%%; mean cosine %.6f; R2 %.5f -> %.5f; held-temp RMSE %.5f -> %.5f\n",
  pc1, mean_cos, r2_form, r2_real, rmse_form, rmse_real
))
