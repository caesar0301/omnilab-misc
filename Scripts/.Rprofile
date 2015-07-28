## R startup configurations:
## $R_HOME/etc/Rprofile.site > $(pwd)/.Rprofile > ~/.Rprofile
##
## Get $R_HOME:
##    R >: R.home(component = "home")
##

## set permanent CRAN mirror
## Mirrors: https://cran.r-project.org/mirrors.html
local({r <- getOption("repos")
    r["CRAN"] <- "http://cran.rstudio.com/"
    options(repos=r)
})

test.library <- function(pkg) {
    if (! require(pkg))
        install.packages(pkg)
}

sshhh <- function(a.package){
    suppressWarnings(suppressPackageStartupMessages(
        library(a.package, character.only=TRUE)))
}

options(editor="vim")
auto.loads <-c("devtools", "ggplot2")

# test the presence of libraries
test.library(auto.loads)

## devtools::install_github("jalvesaq/colorout")
if(Sys.getenv("TERM") == "xterm-256color")
    if(! require("colorout"))
        devtools::install_github("jalvesaq/colorout")

if(interactive()){
    invisible(sapply(auto.loads, sshhh))
}

message("n*** Successfully loaded .Rprofile ***n")
