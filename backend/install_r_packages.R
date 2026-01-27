# Install required R packages for EcoModel Hub
packages <- c("heemod", "flexsurv", "survival", "dplyr", "ggplot2")

for (pkg in packages) {
  if (!require(pkg, character.only = TRUE)) {
    install.packages(pkg, repos = "https://cloud.r-project.org")
  }
}

cat("All packages installed successfully\n")
