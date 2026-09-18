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
sw$replicate_id <- factor(sw$replicate_id, levels = realization_levels)
temps <- sort(unique(sw$temperature_c))

# ---------- leave-one-realization-out one-anchor calibration ----------
pred_list <- list()
k <- 1L

for (held_id in realization_levels) {
  train <- sw |> filter(as.character(replicate_id) != held_id)
  held <- sw |> filter(as.character(replicate_id) == held_id)

  fit <- lm(log_eta ~ invT + replicate_id, data = train)
  beta <- unname(coef(fit)[["invT"]])

  for (anchor_temp in temps) {
    anchor <- held |> filter(temperature_c == anchor_temp)
    alpha_r <- log(anchor$viscosity_raw[1]) - beta * anchor$invT[1]

    targets <- held |> filter(temperature_c != anchor_temp)
    targets$pred_eta <- exp(alpha_r + beta * targets$invT)
    targets$anchor_temp <- anchor_temp
    targets$held_id <- held_id
    targets$beta_train <- beta
    targets$alpha_r <- alpha_r
    targets$mult_error <- exp(abs(log(targets$pred_eta / targets$viscosity_raw)))

    pred_list[[k]] <- targets
    k <- k + 1L
  }
}

pred <- bind_rows(pred_list) |>
  mutate(
    target_temp = temperature_c,
    strict = anchor_temp == 110 & target_temp %in% c(120, 130),
    strict_target = ifelse(strict, paste0(target_temp, " °C strict"), NA_character_)
  )

# ---------- Panel A: graphical calibration, no workflow boxes ----------
held_demo <- "E2_ZYX"
anchor_demo <- 110

train_demo <- sw |> filter(as.character(replicate_id) != held_demo)
held_demo_df <- sw |> filter(as.character(replicate_id) == held_demo)

fit_demo <- lm(log_eta ~ invT + replicate_id, data = train_demo)
beta_demo <- unname(coef(fit_demo)[["invT"]])
anchor_row <- held_demo_df |> filter(temperature_c == anchor_demo)
alpha_demo <- log(anchor_row$viscosity_raw[1]) - beta_demo * anchor_row$invT[1]

demo_pred <- held_demo_df |>
  mutate(pred_eta = exp(alpha_demo + beta_demo * invT))

pA <- ggplot() +
  geom_line(
    data = train_demo,
    aes(temperature_c, viscosity_raw, group = replicate_id),
    colour = PUR_COLORS$grey2, linewidth = 0.75, alpha = 0.95
  ) +
  geom_point(
    data = train_demo,
    aes(temperature_c, viscosity_raw),
    colour = PUR_COLORS$grey2, size = 1.45, alpha = 0.95
  ) +
  geom_line(
    data = demo_pred,
    aes(temperature_c, pred_eta),
    colour = PUR_COLORS$teal, linewidth = 1.45
  ) +
  geom_point(
    data = held_demo_df |> filter(temperature_c != anchor_demo),
    aes(temperature_c, viscosity_raw),
    shape = 21, fill = "white", colour = PUR_COLORS$navy2,
    stroke = 0.9, size = 2.8
  ) +
  geom_point(
    data = anchor_row,
    aes(temperature_c, viscosity_raw),
    shape = 23, fill = PUR_COLORS$orange, colour = "white",
    stroke = 0.8, size = 4.4
  ) +
  geom_vline(xintercept = anchor_demo, linetype = "dotted",
             colour = PUR_COLORS$orange, linewidth = 0.65) +
  annotate(
    "label", x = 82, y = max(train_demo$viscosity_raw) * 0.88,
    label = "training realizations\n(shared thermal direction)",
    hjust = 0, vjust = 1, size = 3.15,
    colour = PUR_COLORS$muted, fill = alpha("white", 0.90),
    label.size = 0
  ) +
  annotate(
    "text", x = 110.8, y = anchor_row$viscosity_raw[1] * 1.12,
    label = "single anchor", hjust = 0,
    colour = PUR_COLORS$orange, fontface = "bold", size = 3.25
  ) +
  annotate(
    "text", x = 129.2, y = tail(demo_pred$pred_eta, 1) * 0.90,
    label = "reconstructed curve", hjust = 1, vjust = 1,
    colour = PUR_COLORS$teal, fontface = "bold", size = 3.25
  ) +
  annotate(
    "label", x = 128.5, y = max(train_demo$viscosity_raw) * 0.88,
    label = "log ηᵣ(T) = β/T + αᵣ\none anchor estimates αᵣ",
    hjust = 1, vjust = 1, size = 3.05,
    colour = PUR_COLORS$ink, fill = alpha("white", 0.94),
    label.size = 0.25, label.padding = grid::unit(0.18, "lines")
  ) +
  scale_x_continuous(breaks = temps) +
  scale_y_log10(labels = label_number(big.mark = ",")) +
  labs(
    title = "One anchor calibrates a held-out realization",
    x = "Temperature (°C)",
    y = "Viscosity (raw unit)"
  ) +
  theme_pur() +
  theme(legend.position = "none")

# ---------- Panel B ----------
strict_cols <- c(
  "120 °C strict" = PUR_COLORS$teal,
  "130 °C strict" = PUR_COLORS$navy
)

pB <- ggplot(pred, aes(viscosity_raw, pred_eta)) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed",
              colour = "#737A82", linewidth = 0.7) +
  geom_point(colour = PUR_COLORS$grey, alpha = 0.38, size = 1.65) +
  geom_point(
    data = pred |> filter(strict),
    aes(colour = strict_target),
    size = 2.7
  ) +
  scale_colour_manual(values = strict_cols, drop = TRUE) +
  scale_x_log10(labels = label_math(10^.x)) +
  scale_y_log10(labels = label_math(10^.x)) +
  coord_fixed() +
  labs(
    title = "One-point predictions stay close to the identity line",
    x = "Observed viscosity",
    y = "One-point reconstructed viscosity"
  ) +
  theme_pur() +
  theme(legend.position = c(0.18, 0.86))

# ---------- Panel C ----------
med <- pred |>
  group_by(anchor_temp) |>
  summarise(median_error = median(mult_error), .groups = "drop")

pC <- ggplot(pred, aes(factor(anchor_temp), mult_error)) +
  geom_hline(yintercept = 1, linetype = "dashed", colour = "#747B82", linewidth = 0.6) +
  geom_violin(
    fill = PUR_COLORS$grey3, colour = PUR_COLORS$grey,
    linewidth = 0.75, width = 0.90, trim = TRUE
  ) +
  geom_jitter(
    width = 0.085, height = 0,
    colour = PUR_COLORS$navy2, alpha = 0.48, size = 1.45
  ) +
  geom_point(
    data = med,
    aes(factor(anchor_temp), median_error),
    inherit.aes = FALSE, shape = 21, fill = PUR_COLORS$teal,
    colour = "white", stroke = 0.75, size = 3.55
  ) +
  scale_x_discrete(labels = function(x) paste0(x, " °C")) +
  coord_cartesian(ylim = c(0.995, 1.395)) +
  labs(
    title = "Calibration quality is stable across anchor temperatures",
    x = "Single measured anchor temperature",
    y = "Multiplicative prediction error"
  ) +
  theme_pur()

# ---------- Panel D ----------
set.seed(20260918)
strict_110 <- pred |>
  filter(anchor_temp == 110, target_temp %in% c(120, 130))

boot_ci <- function(x, B = 20000L) {
  sims <- replicate(B, median(sample(x, length(x), replace = TRUE)))
  c(lo = unname(quantile(sims, 0.025)),
    hi = unname(quantile(sims, 0.975)))
}

summ <- strict_110 |>
  group_by(target_temp) |>
  summarise(
    med = median(mult_error),
    lo = boot_ci(mult_error)[1],
    hi = boot_ci(mult_error)[2],
    .groups = "drop"
  ) |>
  mutate(
    y = ifelse(target_temp == 120, 2, 1),
    label = sprintf("median %.3f×\n95%% bootstrap %.3f–%.3f×", med, lo, hi),
    grp = paste0(target_temp, " °C")
  )

pD <- ggplot(summ) +
  geom_vline(xintercept = 1, linetype = "dashed", colour = "#747B82", linewidth = 0.6) +
  geom_segment(
    aes(x = lo, xend = hi, y = y, yend = y, colour = grp),
    linewidth = 1.25
  ) +
  geom_point(aes(x = med, y = y, fill = grp), shape = 21,
             colour = "white", stroke = 0.9, size = 4.4) +
  geom_text(
    aes(x = hi + 0.0045, y = y, label = label),
    hjust = 0, vjust = 0.5, colour = PUR_COLORS$ink,
    size = 3.25, lineheight = 0.95
  ) +
  scale_colour_manual(values = c("120 °C" = PUR_COLORS$teal, "130 °C" = PUR_COLORS$navy)) +
  scale_fill_manual(values = c("120 °C" = PUR_COLORS$teal, "130 °C" = PUR_COLORS$navy)) +
  scale_y_continuous(
    breaks = c(2, 1), labels = c("120 °C", "130 °C"),
    limits = c(0.72, 2.28)
  ) +
  scale_x_continuous(
    limits = c(0.997, 1.235),
    breaks = seq(1.00, 1.20, 0.05),
    labels = label_number(accuracy = 0.01)
  ) +
  labs(
    title = "Strict 110 °C anchor → hotter-temperature extrapolation",
    x = "Multiplicative error",
    y = NULL
  ) +
  theme_pur() +
  theme(
    legend.position = "none",
    panel.grid.major.y = element_blank()
  )

fig3 <- (pA | pB) / (pC | pD) +
  plot_annotation(tag_levels = "A")

ggsave("figures/r_manuscript/Figure3_one_point_calibration_R.png", fig3,
       width = 14.2, height = 9.7, units = "in", dpi = 320, bg = "white")
ggsave("figures/r_manuscript/Figure3_one_point_calibration_R.pdf", fig3,
       width = 14.2, height = 9.7, units = "in", device = cairo_pdf, bg = "white")
ggsave("figures/r_manuscript/Figure3_one_point_calibration_R.svg", fig3,
       width = 14.2, height = 9.7, units = "in", bg = "white")

save_panel(pA, "figures/r_manuscript/Figure3A_R.png")
save_panel(pB, "figures/r_manuscript/Figure3B_R.png")
save_panel(pC, "figures/r_manuscript/Figure3C_R.png")
save_panel(pD, "figures/r_manuscript/Figure3D_R.png")

cat("Figure 3 rendered from R-only analysis.\n")
cat("Median multiplicative error by anchor temperature:\n")
print(med)
cat("Strict 110 C extrapolation summary:\n")
print(summ[, c("target_temp", "med", "lo", "hi")])
