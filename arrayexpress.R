library(jsonlite)
library(RCurl)
arrayexpress=function(accessions){
  lapply(accessions, function(acc) {
    j = fromJSON(getURL(paste0(c('http://www.ebi.ac.uk/arrayexpress/json/v2/experiments/',acc),collapse='')))
    c(acc, j$experiments$experiment$name, j$experiments$experiment$description$text)
  })
}
