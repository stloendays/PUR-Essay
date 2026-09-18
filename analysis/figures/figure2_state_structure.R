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
    log_eta = log(viscosity_raw),
    formulation_id = factor(formulation_id, levels = c("E1", "E2", "E3"))
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
rep_labels <- c(
  E1_initial = "E1 initial",
  E1_repeat_day1 = "E1 day-1",
  E2_GJJ = "E2 GJJ",
  E2_ZYX = "E2 ZYX",
  E2_CHH = "E2 CHH",
  E2_ZYX_day1 = "E2 ZYX day-1",
  E3_CHH = "E3 CHH"
)

temp$replicate_id <- factor(temp$replicate_id, levels = rep_order)

# ---------------------------------------------------------------------------
# Statistics used by the figure
# ---------------------------------------------------------------------------

# PCA and pairwise cosine similarity on the raw six-temperature vectors.
wide <- temp |>
  select(replicate_id, temperature_c, viscosity_raw) |>
  pivot_wider(names_from = temperature_c, values_from = viscosity_raw) |>
  arrange(match(replicate_id, rep_order))

mat <- as.matrix(wide[, -1])
pca <- prcomp(mat, center = TRUE, scale. = FALSE)
pc1 <- (pca$sdev[1]^2) / sum(pca$sdev^2)

cosine <- function(a, b) sum(a * b) / sqrt(sum(a^2) * sum(b^2))
cos_vals <- c()
for (i in seq_len(nrow(mat) - 1)) {
  for (j in (i + 1):nrow(mat)) {
    cos_vals <- c(cos_vals, cosine(mat[i, ], mat[j, ]))
  }
}

# Shared-slope vs formulation-specific slope.
m_form_common <- lm(log_eta ~ invT + formulation_id, data = temp)
m_form_interaction <- lm(log_eta ~ invT * formulation_id, data = temp)
a_form <- anova(m_form_common, m_form_interaction)

# Shared-slope vs realization-specific slope.
m_real_common <- lm(log_eta ~ invT + replicate_id, data = temp)
m_real_interaction <- lm(log_eta ~ invT * replicate_id, data = temp)
a_real <- anova(m_real_common, m_real_interaction)

# Formulation-only vs realization-aware level model.
m_form <- lm(log_eta ~ invT + formulation_id, data = temp)
m_state <- lm(log_eta ~ invT + replicate_id, data = temp)
r2_form <- summary(m_form)$r.squared
r2_state <- summary(m_state)$r.squared
rmse_form <- sqrt(mean(residuals(m_form)^2))
rmse_state <- sqrt(mean(residuals(m_state)^2))

# Leave-one-temperature-out interpolation for already observed realizations.
loto <- lapply(sort(unique(temp$temperature_c)), function(tt) {
  train <- filter(temp, temperature_c != tt)
  test <- filter(temp, temperature_c == tt)

  fit_form <- lm(log_eta ~ invT + formulation_id, data = train)
  fit_state <- lm(log_eta ~ invT + replicate_id, data = train)

  data.frame(
    temperature_c = tt,
    observed = test$log_eta,
    pred_form = predict(fit_form, newdata = test),
    pred_state = predict(fit_state, newdata = test)
  )
}) |>
  bind_rows()

loto_rmse_form <- sqrt(mean((loto$pred_form - loto$observed)^2))
loto_rmse_state <- sqrt(mean((loto$pred_state - loto$observed)^2))
loto_reduction <- 1 - loto_rmse_state / loto_rmse_form

# ---------------------------------------------------------------------------
# Panel A: same nominal E2 formulation, large absolute-level spread
# ---------------------------------------------------------------------------

e2 <- temp |>
  filter(formulation_id == "E2")

e2_cols <- c(
  E2_GJJ = "#A9C1CF",
  E2_ZYX = "#6D9FB0",
  E2_CHH = pur_pal[["core"]],
  E2_ZYX_day1 = pur_pal[["state"]]
)

spread <- e2 |>
  filter(temperature_c %in% c(80, 120), replicate_id %in% c("E2_GJJ", "E2_ZYX", "E2_CHH")) |>
  group_by(temperature_c) |>
  summarise(
    ymin = min(viscosity_raw),
    ymax = max(viscosity_raw),
    fold = ymax / ymin,
    .groups = "drop"
  )

pA <- ggplot(e2, aes(temperature_c, viscosity_raw, group = replicate_id, color = replicate_id)) +
  geom_line(linewidth = 0.75) +
  geom_point(size = 1.8, stroke = 0.25) +
  geom_segment(
    data = spread,
    aes(x = temperature_c + 1.3, xend = temperature_c + 1.3, y = ymin, yend = ymax),
    inherit.aes = FALSE,
    color = pur_pal[["drift"]],
    linewidth = 0.45
  ) +
  geom_text(
    data = spread,
    aes(
      x = temperature_c + 2.2,
      y = sqrt(ymin * ymax),
      label = sprintf("%.2fx", fold)
    ),
    inherit.aes = FALSE,
    hjust = 0,
    color = pur_pal[["drift"]],
    fontface = "bold",
    size = 2.7
  ) +
  scale_color_manual(
    values = e2_cols,
    breaks = names(e2_cols),
    labels = rep_labels[names(e2_cols)]
  ) +
  scale_y_log10(labels = label_number(big.mark = ",", accuracy = 1)) +
  scale_x_continuous(breaks = seq(80, 130, 10), limits = c(78, 136)) +
  labs(
    x = "Temperature (\u00B0C)",
    y = "Viscosity (raw unit)",
    color = NULL,
    subtitle = "Same nominal E2 formulation, different experimental realizations"
  ) +
  theme_pur() +
  theme(
    legend.position = c(0.74, 0.78),
    legend.justification = c(0, 1),
    legend.key.height = unit(3.2, "mm"),
    plot.subtitle = element_text(face = "bold")
  )

# ---------------------------------------------------------------------------
# Panel B: anchor-normalized curves collapse onto a shared temperature shape
# ---------------------------------------------------------------------------

norm <- temp |>
  group_by(replicate_id) |>
  mutate(
    anchor_log = log_eta[temperature_c == 110][1],
    log_ratio_110 = log_eta - anchor_log
  ) |>
  ungroup()

norm_summary <- norm |>
  group_by(temperature_c) |>
  summarise(
    mean = mean(log_ratio_110),
    sd = sd(log_ratio_110),
    .groups = "drop"
  )

pB <- ggplot(norm, aes(temperature_c, log_ratio_110, group = replicate_id)) +
  geom_ribbon(
    data = norm_summary,
    aes(x = temperature_c, ymin = mean - sd, ymax = mean + sd),
    inherit.aes = FALSE,
    fill = pur_pal[["state"]],
    alpha = 0.12
  ) +
  geom_line(color = "#A7ADB4", linewidth = 0.55, alpha = 0.80) +
  geom_point(color = "#8E959D", size = 1.25, alpha = 0.82) +
  geom_line(
    data = norm_summary,
    aes(temperature_c, mean),
    inherit.aes = FALSE,
    color = pur_pal[["state"]],
    linewidth = 1.0
  ) +
  geom_point(
    data = norm_summary,
    aes(temperature_c, mean),
    inherit.aes = FALSE,
    color = pur_pal[["state"]],
    size = 1.8
  ) +
  geom_hline(yintercept = 0, linewidth = 0.35, linetype = 2, color = "#777777") +
  annotate(
    "text",
    x = 81,
    y = min(norm$log_ratio_110) + 0.04,
    hjust = 0,
    label = sprintf("PC1 = %.2f%%\nmean cosine = %.5f", 100 * pc1, mean(cos_vals)),
    color = pur_pal[["state"]],
    fontface = "bold",
    size = 2.8
  ) +
  scale_x_continuous(breaks = seq(80, 130, 10)) +
  labs(
    x = "Temperature (\u00B0C)",
    y = expression(log(eta(T) / eta(110 * degree * C))),
    subtitle = "Removing one realization-specific offset reveals a near-common thermal shape"
  ) +
  theme_pur() +
  theme(plot.subtitle = element_text(face = "bold"))

# ---------------------------------------------------------------------------
# Panel C: residual structure after a shared slope + realization intercept
# ---------------------------------------------------------------------------

temp$resid_shared <- residuals(m_real_common)
max_abs <- max(abs(temp$resid_shared))

heat <- temp |>
  mutate(
    replicate_label = factor(
      rep_labels[as.character(replicate_id)],
      levels = rev(rep_labels[rep_order])
    ),
    temp_factor = factor(temperature_c, levels = sort(unique(temperature_c)))
  )

pC <- ggplot(heat, aes(temp_factor, replicate_label, fill = resid_shared)) +
  geom_tile(color = "white", linewidth = 0.75) +
  scale_fill_gradient2(
    low = pur_pal[["core"]],
    mid = "#F7F7F7",
    high = pur_pal[["drift"]],
    midpoint = 0,
    limits = c(-max_abs, max_abs),
    labels = label_number(accuracy = 0.01)
  ) +
  labs(
    x = "Temperature (\u00B0C)",
    y = NULL,
    fill = "log residual",
    subtitle = "Residual map after shared thermal slope + realization-specific level"
  ) +
  theme_pur() +
  theme(
    panel.grid = element_blank(),
    axis.line = element_blank(),
    legend.position = "right",
    plot.subtitle = element_text(face = "bold")
  )

# ---------------------------------------------------------------------------
# Panel D: compact, scale-honest model comparison
# ---------------------------------------------------------------------------

model_table <- data.frame(
  metric = factor(
    c("R\u00B2", "R\u00B2", "Held-temperature\nRMSE (ln \u03B7)", "Held-temperature\nRMSE (ln \u03B7)"),
    levels = c("Held-temperature\nRMSE (ln \u03B7)", "R\u00B2")
  ),
  model = factor(
    c("Formulation-only", "Realization-aware", "Formulation-only", "Realization-aware"),
    levels = c("Formulation-only", "Realization-aware")
  ),
  xpos = c(1, 2, 1, 2),
  value = c(r2_form, r2_state, loto_rmse_form, loto_rmse_state),
  label = c(
    sprintf("%.3f", r2_form),
    sprintf("%.3f", r2_state),
    sprintf("%.3f", loto_rmse_form),
    sprintf("%.3f", loto_rmse_state)
  )
)

arrows <- data.frame(
  metric = factor(
    c("R\u00B2", "Held-temperature\nRMSE (ln \u03B7)"),
    levels = c("Held-temperature\nRMSE (ln \u03B7)", "R\u00B2")
  ),
  x = 1.16,
  xend = 1.84,
  label = c(
    sprintf("+%.3f", r2_state - r2_form),
    sprintf("-%.1f%%", 100 * loto_reduction)
  )
)

pD <- ggplot(model_table, aes(xpos, metric)) +
  geom_segment(
    data = arrows,
    aes(x = x, xend = xend, y = metric, yend = metric),
    inherit.aes = FALSE,
    color = "#A9AFB6",
    linewidth = 0.65,
    arrow = arrow(length = unit(1.5, "mm"), type = "closed")
  ) +
  geom_point(
    aes(fill = model),
    shape = 21,
    size = 9.3,
    color = "white",
    stroke = 0.8
  ) +
  geom_text(aes(label = label), color = "white", fontface = "bold", size = 2.75) +
  geom_text(
    data = arrows,
    aes(x = 1.5, y = metric, label = label),
    inherit.aes = FALSE,
    vjust = -1.15,
    color = pur_pal[["dark"]],
    fontface = "bold",
    size = 2.65
  ) +
  scale_fill_manual(
    values = c(
      "Formulation-only" = pur_pal[["core"]],
      "Realization-aware" = pur_pal[["state"]]
    )
  ) +
  scale_x_continuous(
    breaks = c(1, 2),
    labels = c("Formulation-only", "Realization-aware"),
    limits = c(0.72, 2.28)
  ) +
  labs(
    x = NULL,
    y = NULL,
    fill = NULL,
    subtitle = "Explicit realization state explains level shifts without changing the thermal slope"
  ) +
  theme_pur() +
  theme(
    panel.grid = element_blank(),
    axis.line = element_blank(),
    axis.text.x = element_text(face = "bold"),
    legend.position = "none",
    plot.subtitle = element_text(face = "bold")
  )

# ---------------------------------------------------------------------------
# Assemble and save
# ---------------------------------------------------------------------------

fig2 <- ((pA | pB) / (pC | pD)) +
  plot_layout(heights = c(1.04, 0.96)) +
  plot_annotation(tag_levels = "A") &
  panel_tag_theme

save_pur_figure(
  fig2,
  file.path(out_dir, "Figure2_state_structure"),
  width_mm = 180,
  height_mm = 142
)

stats <- data.frame(
  metric = c(
    "n_realizations",
    "n_temperature_points",
    "pc1_variance_explained_percent",
    "cosine_mean",
    "cosine_min",
    "cosine_max",
    "formulation_slope_interaction_p",
    "realization_slope_interaction_p",
    "formulation_only_R2",
    "realization_aware_R2",
    "formulation_only_in_sample_RMSE_log_eta",
    "realization_aware_in_sample_RMSE_log_eta",
    "formulation_only_LOTO_RMSE_log_eta",
    "realization_aware_LOTO_RMSE_log_eta",
    "LOTO_RMSE_reduction_percent"
  ),
  value = c(
    length(unique(temp$replicate_id)),
    nrow(temp),
    100 * pc1,
    mean(cos_vals),
    min(cos_vals),
    max(cos_vals),
    a_form$\`Pr(>F)\`[2],
    a_real$\`Pr(>F)\`[2],
    r2_form,
    r2_state,
    rmse_form,
    rmse_state,
    loto_rmse_form,
    loto_rmse_state,
    100 * loto_reduction
  )
)

write.csv(stats, file.path(out_dir, "Figure2_state_structure_stats.csv"), row.names = FALSE)
