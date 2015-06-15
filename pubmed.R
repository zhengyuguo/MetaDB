library(RISmed)
library(pytools)

author_table=function(pubmed_id) {
  do.call( rbind 
    ,lapply(pubmed_id,function(id){
    res = EUtilsGet(id)
    a=Author(res)[[1]]
    a$PubMed=rep(id,nrow(a))
    a
 }))
}

pub_main=function(pubmed_id) {
  do.call( rbind
    , lapply ( pubmed_id
      , function ( id ) {
        res = EUtilsGet(id)
        t = ArticleTitle(res)
        ab = AbstractText(res)
        j = Title(res)
        jab = ISOAbbreviation(res)
        y = YearPubmed(res)
        c(PubMed=id, Title=t, Abstract=ab, Journal=j, JournalAbbr=jab, Year=y)
      }
      )
    )
}
