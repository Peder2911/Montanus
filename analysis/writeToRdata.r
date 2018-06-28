#!/usr/local/bin/rscript

library(magrittr)
library(jsonlite)

library(cowsay)

lines<-readLines('stdin')

# First line contains metadata about the data being analyzed
meta <- unlist(strsplit(lines[1],','))
names(meta) <- c('site','about')
meta <- as.list(meta)

# The rest of the data is in JSON format.
df <- fromJSON(lines[-1])

save(df,file='.data/rdata')

cowsay::say(df[1,'snippet'])
print(names(df))
print(str(df))
