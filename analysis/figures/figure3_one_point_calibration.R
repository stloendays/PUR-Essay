#!/usr/bin/env Rscript

suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(tidyr)
  library(patchwork)
  library(scales)
  library(grid)
})

source("analysis/figures/theme_pur_paper.R")

input_file <- "data/prospective_validation/experimental_viscosity_v1.csv"
out_dir <- "figures/generated"
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)

raw <- read.csv(input_file, stringsAsFactors = FALSE)
temp <- raw |>
  filter(measurement_type == "temperature_sweep") |>
  mutate(
    temp_k = temperature_c + 273.15,
    invT = 1 / temp_k,
    log_eta = log(viscosity_raw)
  )

rep_order <- c(
  "E1_initial",
  "E1_repeat_day1",
  "E2_GJJ",
  "E2_ZYX",
  "E2_CHH",
  "E2_ZYX_day1",
  "E3_CHH"
)
temp$replicate_id <- factor(temp$replicate_id, levels = rep_order)

# ---------------------------------------------------------------------------
# Leave-one-realization-out, one-point calibration.
# Learn a shared thermal slope from six realizations, measure one anchor point
# in the held-out realization, then reconstruct the other five temperatures.
# ---------------------------------------------------------------------------

fit_one_anchor <- function(anchor_temp) {
  out <- lapply(rep_order, function(rep) {
    train <- temp |> filter(as.character(replicate_id) != rep)
    test <- temp |> filter(as.character(replicate_id) == rep)

    fit <- lm(log_eta ~ invT + replicate_id, data = train)
    slope <- unname(coef(fit)[["invT"]])

    anchor <- test |> filter(temperature_c == anchor_temp)
    alpha <- anchor$log_eta - slope * anchor$invT

    pred <- test |>
      filter(temperature_c != anchor_temp) |>
      mutate(
        anchor_temp = anchor_temp,
        pred_log_eta = alpha + slope * invT,
        pred_eta = exp(pred_log_eta),
        factor_error = exp(abs(pred_log_eta - log_eta)),
        signed_log_error = pred_log_eta - log_eta
      )

    pred
  })
  bind_rows(out)
}

anchors <- sort(unique(temp$temperature_c))
pred_all <- bind_rows(lapply(anchors, fit_one_anchor))

anchor_summary <- pred_all |>
  group_by(anchor_temp) |>
  summarise(
    median_factor_error = median(factor_error),
    mean_factor_error = mean(factor_error),
    rmse_log_eta = sqrt(mean(signed_log_error^2)),
    p90_factor_error = quantile(factor_error, 0.90),
    max_factor_error = max(factor_error),
    .groups = "drop"
  )

# Strict extrapolation panel: use 110 C as the only measured anchor and assess
# the two hotter temperatures, which are both unmeasured at calibration time.
strict <- pred_all |>
  filter(anchor_temp == 110, temperature_c %in% c(120, 130))

set.seed(20260918)
boot_ci <- function(x, nboot = 10000) {
  meds <- replicate(nboot, median(sample(x, length(x), replace = TRUE)))
  c(lo = unname(quantile(meds, 0.025)),
    med = median(x),
    hi = unname(quantile(meds, 0.975)))
}

strict_summary <- strict |>
  group_by(temperature_c) |>
  summarise(
    ci = list(boot_ci(factor_error)),
    geometric_rmse_factor = exp(sqrt(mean(log(factor_error)^2))),
    .groups = "drop"
  ) |>
  mutate(
    lo = vapply(ci, function(x) x[["lo"]], numeric(1)),
    median_factor_error = vapply(ci, function(x) x[["med"]], numeric(1)),
    hi = vapply(ci, function(x) x[["hi"]], numeric(1))
  ) |>
  select(-ci)

# ---------------------------------------------------------------------------
# Panel A: one-point calibration schematic
# ---------------------------------------------------------------------------

box_df <- data.frame(
  xmin = c(0.02, 0.27, 0.53, 0.77),
  xmax = c(0.22, 0.47, 0.72, 0.98),
  ymin = 0.28,
  ymax = 0.72,
  label = c(
    "Learn shared\nthermal shape\ng(T)",
    "Measure one\nanchor point\neta(T0)",
    "Estimate\nrealization offset\nalpha_r",
    "Reconstruct\nunmeasured\ntemperatures"
  ),
  fill = c("core", "evidence", "state", "state")
)

arrow_df <- data.frame(
  x = c(0.225, 0.475, 0.725),
  xend = c(0.265, 0.515, 0.765),
  y = 0.50,
  yend = 0.50
)

pA <- ggplot() +
  geom_rect(
    data = box_df,
    aes(xmin = xmin, xmax = xmax, ymin = ymin, ymax = ymax, fill = fill),
    color = NA,
    alpha = 0.96
  ) +
  geom_text(
    data = box_df,
    aes(x = (xmin + xmax) / 2, y = 0.50, label = label),
    color = "white",
    fontface = "bold",
    lineheight = 0.95,
    size = 2.75
  ) +
  geom_segment(
    data = arrow_df,
    aes(x = x, xend = xend, y = y, yend = yend),
    linewidth = 0.55,
    color = pur_pal[["dark"]],
    arrow = arrow(length = unit(1.7, "mm"), type = "closed")
  ) +
  scale_fill_manual(values = pur_pal) +
  annotate(
    "text", x = 0.50, y = 0.12,
    label = "LOFO protocol: held-out realization contributes only the single anchor measurement",
    color = "#555555", size = 2.6
  ) +
  coord_cartesian(xlim = c(0, 1), ylim = c(0, 1), clip = "off") +
  labs(subtitle = "One measured point locates a new realization on the shared thermal-response family") +
  theme_void(base_family = "sans") +
  theme(
    plot.subtitle = element_text(face = "bold", size = 8.5, color = pur_pal[["dark"]]),
    plot.margin = margin(8, 6, 3, 6)
  )

# ---------------------------------------------------------------------------
# Panel B: observed vs predicted parity
# Show all LOFO one-anchor predictions in light gray and the strict 110->120/130
# extrapolation in semantic colors.
# ---------------------------------------------------------------------------

parity_bg <- pred_all |>
  mutate(kind = "All LOFO reconstructions")

strict_plot <- strict |>
  mutate(
    target = factor(
      paste0(temperature_c, " C"),
      levels = c("120 C", "130 C")
    )
  )

lim_lo <- min(c(parity_bg$viscosity_raw, parity_bg$pred_eta)) * 0.86
lim_hi <- max(c(parity_bg$viscosity_raw, parity_bg$pred_eta)) * 1.15

pB <- ggplot() +
  geom_abline(intercept = 0, slope = 1, color = "#777777", linewidth = 0.45, linetype = 2) +
  geom_point(
    data = parity_bg,
    aes(viscosity_raw, pred_eta),
    color = pur_pal[["naive"]],
    alpha = 0.24,
    size = 1.15
  ) +
  geom_point(
    data = strict_plot,
    aes(viscosity_raw, pred_eta, fill = target),
    shape = 21,
    color = "white",
    stroke = 0.45,
    size = 3.1
  ) +
  scale_fill_manual(
    values = c("120 C" = pur_pal[["state"]], "130 C" = pur_pal[["core"]])
  ) +
  scale_x_log10(labels = label_number(big.mark = ",", accuracy = 1)) +
  scale_y_log10(labels = label_number(big.mark = ",", accuracy = 1)) +
  coord_equal(xlim = c(lim_lo, lim_hi), ylim = c(lim_lo, lim_hi)) +
  labs(
    x = "Observed viscosity",
    y = "One-point reconstructed viscosity",
    fill = "Strict target",
    subtitle = "Predictions remain close to the identity line across held-out realizations"
  ) +
  theme_pur() +
  theme(
    legend.position = c(0.05, 0.94),
    legend.justification = c(0, 1),
    plot.subtitle = element_text(face = "bold")
  )

# ---------------------------------------------------------------------------
# Panel C: anchor-temperature robustness without bar charts
# violin + jitter + median point for multiplicative error.
# ---------------------------------------------------------------------------

pred_all <- pred_all |>
  mutate(anchor_label = factor(paste0(anchor_temp, " C"), levels = paste0(anchors, " C")))

pC <- ggplot(pred_all, aes(anchor_label, factor_error)) +
  geom_violin(
    fill = pur_pal[["light"]],
    color = "#A7ADB4",
    linewidth = 0.35,
    scale = "width",
    trim = FALSE
  ) +
  geom_jitter(
    width = 0.10,
    height = 0,
    size = 1.05,
    alpha = 0.48,
    color = pur_pal[["core"]]
  ) +
  stat_summary(
    fun = median,
    geom = "point",
    shape = 21,
    size = 3.0,
    fill = pur_pal[["state"]],
    color = "white",
    stroke = 0.55
  ) +
  geom_hline(yintercept = 1, linewidth = 0.35, color = "#777777", linetype = 2) +
  scale_y_continuous(
    labels = function(x) sprintf("%.2fx", x),
    expand = expansion(mult = c(0.03, 0.08))
  ) +
  labs(
    x = "Single measured anchor temperature",
    y = "Multiplicative prediction error",
    subtitle = "Calibration quality is stable across the available anchor temperatures"
  ) +
  theme_pur() +
  theme(plot.subtitle = element_text(face = "bold"))

# ---------------------------------------------------------------------------
# Panel D: strict extrapolation forest plot
# ---------------------------------------------------------------------------

strict_summary <- strict_summary |>
  mutate(target = factor(paste0(temperature_c, " C"), levels = c("130 C", "120 C")))

pD <- ggplot(strict_summary, aes(median_factor_error, target)) +
  geom_vline(xintercept = 1, linewidth = 0.35, color = "#777777", linetype = 2) +
  geom_errorbarh(
    aes(xmin = lo, xmax = hi, color = target),
    height = 0.12,
    linewidth = 0.85
  ) +
  geom_point(
    aes(fill = target),
    shape = 21,
    size = 4.5,
    color = "white",
    stroke = 0.65
  ) +
  geom_text(
    aes(
      x = hi + 0.008,
      label = sprintf("median %.3fx\n95%% bootstrap %.3f-%.3fx", median_factor_error, lo, hi)
    ),
    hjust = 0,
    size = 2.45,
    color = pur_pal[["dark"]],
    lineheight = 0.92
  ) +
  scale_color_manual(
    values = c("120 C" = pur_pal[["state"]], "130 C" = pur_pal[["core"]]),
    guide = "none"
  ) +
  scale_fill_manual(
    values = c("120 C" = pur_pal[["state"]], "130 C" = pur_pal[["core"]]),
    guide = "none"
  ) +
  scale_x_continuous(
    limits = c(0.995, max(strict_summary$hi) + 0.115),
    labels = function(x) sprintf("%.2fx", x)
  ) +
  labs(
    x = "Multiplicative error",
    y = NULL,
    subtitle = "Strict test: one 110 C anchor extrapolated to hotter temperatures"
  ) +
  theme_pur() +
  theme(
    panel.grid.major.y = element_blank(),
    plot.subtitle = element_text(face = "bold")
  )

# ---------------------------------------------------------------------------
# Assemble and save
# ---------------------------------------------------------------------------

fig3 <- ((pA | pB) / (pC | pD)) +
  plot_layout(heights = c(0.88, 1.12)) +
  plot_annotation(tag_levels = "A") &
  panel_tag_theme

save_pur_figure(
  fig3,
  file.path(out_dir, "Figure3_one_point_calibration"),
  width_mm = 180,
  height_mm = 140
)

write.csv(anchor_summary, file.path(out_dir, "Figure3_anchor_summary.csv"), row.names = FALSE)
write.csv(strict_summary, file.path(out_dir, "Figure3_strict_extrapolation_summary.csv"), row.names = FALSE)
write.csv(
  strict |>
    select(replicate_id, anchor_temp, temperature_c, viscosity_raw, pred_eta, factor_error),
  file.path(out_dir, "Figure3_strict_extrapolation_predictions.csv"),
  row.names = FALSE
)
