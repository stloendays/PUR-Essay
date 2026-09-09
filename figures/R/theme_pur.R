suppressPackageStartupMessages({
  library(ggplot2)
  library(dplyr)
  library(readr)
  library(tidyr)
  library(patchwork)
  library(scales)
})

PUR_COL <- c(
  P = "#3D5A80",
  D = "#E07A5F",
  C = "#2A9D8F",
  T80 = "#B04A4A",
  T120 = "#3D5A80",
  balanced = "#2A9D8F",
  drich = "#E07A5F",
  ink = "#202020",
  mid = "#6F6F6F",
  light = "#D9D9D9"
)

pur_theme <- function(base_size = 8.5) {
  theme_classic(base_size = base_size, base_family = "sans") +
    theme(
      text = element_text(colour = PUR_COL[["ink"]]),
      axis.title = element_text(size = base_size + 0.5, face = "plain"),
      axis.text = element_text(size = base_size - 0.4, colour = PUR_COL[["ink"]]),
      axis.ticks = element_line(linewidth = 0.35, colour = PUR_COL[["ink"]]),
      axis.line = element_line(linewidth = 0.45, colour = PUR_COL[["ink"]]),
      legend.title = element_blank(),
      legend.text = element_text(size = base_size - 0.5),
      legend.key.height = grid::unit(3.5, "mm"),
      legend.key.width = grid::unit(4.5, "mm"),
      plot.margin = margin(5, 6, 5, 5),
      plot.tag = element_text(face = "bold", size = base_size + 2),
      strip.background = element_blank(),
      strip.text = element_text(face = "bold", size = base_size)
    )
}

theme_set(pur_theme())

save_pur_figure <- function(plot, stem, width_mm = 180, height_mm = 95) {
  dir.create(dirname(stem), recursive = TRUE, showWarnings = FALSE)
  ggsave(paste0(stem, ".png"), plot = plot, width = width_mm, height = height_mm,
         units = "mm", dpi = 600, bg = "white")
  ggsave(paste0(stem, ".pdf"), plot = plot, width = width_mm, height = height_mm,
         units = "mm", device = cairo_pdf, bg = "white")
  ggsave(paste0(stem, ".svg"), plot = plot, width = width_mm, height = height_mm,
         units = "mm", device = svglite::svglite, bg = "white")
}
