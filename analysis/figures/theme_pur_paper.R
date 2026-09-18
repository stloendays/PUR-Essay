# Shared visual system for PUR manuscript figures.
# Keep semantic colors stable across figures.

pur_pal <- c(
  core = "#1F3A5F",
  state = "#2A7F7F",
  drift = "#C46A3A",
  evidence = "#D9A441",
  agent = "#7A5C8E",
  naive = "#9AA0A6",
  random = "#D8DCE3",
  dark = "#222222",
  light = "#F5F7FA"
)

theme_pur <- function(base_size = 8.5) {
  ggplot2::theme_minimal(base_family = "sans", base_size = base_size) +
    ggplot2::theme(
      text = ggplot2::element_text(color = pur_pal[["dark"]]),
      plot.title = ggplot2::element_text(face = "bold", size = base_size + 1.2, hjust = 0),
      plot.subtitle = ggplot2::element_text(size = base_size, color = "#4A4A4A", hjust = 0),
      axis.title = ggplot2::element_text(size = base_size),
      axis.text = ggplot2::element_text(size = base_size - 0.6, color = "#333333"),
      panel.grid.major = ggplot2::element_line(color = "#E5E9F0", linewidth = 0.28),
      panel.grid.minor = ggplot2::element_blank(),
      axis.line = ggplot2::element_line(color = "#4D4D4D", linewidth = 0.32),
      legend.title = ggplot2::element_text(size = base_size - 0.2),
      legend.text = ggplot2::element_text(size = base_size - 0.5),
      legend.background = ggplot2::element_blank(),
      legend.key = ggplot2::element_blank(),
      strip.text = ggplot2::element_text(face = "bold", size = base_size - 0.2),
      strip.background = ggplot2::element_rect(fill = pur_pal[["light"]], color = NA),
      plot.margin = ggplot2::margin(5, 6, 5, 6)
    )
}

panel_tag_theme <- ggplot2::theme(
  plot.tag = ggplot2::element_text(face = "bold", size = 11, color = pur_pal[["dark"]]),
  plot.tag.position = c(0.01, 0.99)
)

save_pur_figure <- function(plot, stem, width_mm = 180, height_mm = 140) {
  dir.create(dirname(stem), recursive = TRUE, showWarnings = FALSE)
  ggplot2::ggsave(
    paste0(stem, ".pdf"),
    plot = plot,
    width = width_mm,
    height = height_mm,
    units = "mm",
    device = grDevices::cairo_pdf,
    bg = "white"
  )
  ggplot2::ggsave(
    paste0(stem, ".png"),
    plot = plot,
    width = width_mm,
    height = height_mm,
    units = "mm",
    dpi = 600,
    bg = "white"
  )
}
