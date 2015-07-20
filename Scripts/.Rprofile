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

options(editor="vim")

auto.loads <-c("devtools", "dplyr", "ggplot2")

sshhh <- function(a.package){
    suppressWarnings(suppressPackageStartupMessages(
        library(a.package, character.only=TRUE)))
}

if(interactive()){
    invisible(sapply(auto.loads, sshhh))
}

if(Sys.getenv("TERM") == "xterm-256color")
    library("colorout")

message("n*** Successfully loaded .Rprofile ***n")
