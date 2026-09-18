suppressPackageStartupMessages({
  library(ggplot2)
  library(scales)
})

PUR_COLORS <- list(
  navy = "#17365D",
  navy2 = "#27496D",
  teal = "#2A8580",
  teal2 = "#5A9E99",
  orange = "#D9773F",
  gold = "#D9A441",
  grey = "#A7B0BA",
  grey2 = "#D6DDE3",
  grey3 = "#EEF2F5",
  grid = "#E5EAF0",
  ink = "#20242A",
  muted = "#5F6770"
)

theme_pur <- function(base_size = 10.5) {
  theme_minimal(base_size = base_size, base_family = "sans") +
    theme(
      plot.title = element_text(
        face = "bold", size = rel(1.22), colour = PUR_COLORS$ink,
        margin = margin(b = 7)
      ),
      plot.subtitle = element_text(
        size = rel(0.92), colour = PUR_COLORS$muted,
        margin = margin(b = 8)
      ),
      axis.title = element_text(size = rel(1.0), colour = PUR_COLORS$ink),
      axis.text = element_text(size = rel(0.90), colour = PUR_COLORS$ink),
      panel.grid.major = element_line(colour = PUR_COLORS$grid, linewidth = 0.45),
      panel.grid.minor = element_blank(),
      legend.title = element_blank(),
      legend.text = element_text(size = rel(0.88), colour = PUR_COLORS$ink),
      plot.tag = element_text(face = "bold", size = rel(1.05), colour = PUR_COLORS$ink),
      plot.tag.position = c(0.00, 1.01),
      plot.margin = margin(8, 10, 8, 8),
      strip.text = element_text(face = "bold", colour = PUR_COLORS$ink),
      strip.background = element_blank()
    )
}

save_panel <- function(plot, filename, width = 6.6, height = 5.0) {
  ggsave(filename, plot, width = width, height = height, units = "in", dpi = 320, bg = "white")
}
