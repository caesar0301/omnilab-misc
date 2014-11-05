library(data.table)
library(ggplot2)

dat <- fread('names001.txt', sep=',')
colnames(dat) <- c("id", "siturl", 'title', 'tag', 'day', 'places', 'people')

dat$day <- as.POSIXct(dat$day, format="%Y-%m-%d")
#spectrum(dat$day)

gg <- ggplot(dat, aes(x=day, group=tag, col=tag)) + theme_bw() +
  geom_freqpoly(aes(y = ..ncount..), binwidth=100000) +
  facet_wrap(~ tag, ncol = 2)
plot(gg)