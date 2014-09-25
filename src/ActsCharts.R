library(dplyr)
library(stringr)
library(ggplot2)

bills <- read.csv('./output/billsUK_20140413_170732.csv')
stages <- read.csv('./output/billsUK_stages_20140413_170732.csv')

sbills <- 
  group_by(bills,Session,Sponsor1Inst) %.%
  summarise(size=sum(NumParagraphsTotal,na.rm=T)) %.%
  filter(!is.na(Sponsor1Inst) & Sponsor1Inst!='')

sbills3 <- group_by(bills, Session,BillCat) %.%
  summarise(billscount=n())

qplot(Session,billscount,fill=BillCat,geom='bar',position='stack',data=sbills3)

sbills2 <- summarise(sbills,size=sum(size,na.rm=T))

# qplot(Session, size,data=sbills,geom = 'bar',stat = 'identity',position='dodge') +
#   facet_wrap(~Sponsor1Inst)

qplot(Session,size,stat='sum',data=sbills2,geom='bar')
qplot(Sponsor1Inst,size,data=sbills,geom='bar',position='stack',fill=Session) + coord_flip()
xx <- qplot(Session,size,data=sbills,geom='bar',position='stack',fill=Sponsor1Inst) + coord_flip()

sessionslist <- unique(as.character(sbills$Session))

# Manipulate demonstration
manipulate(qplot(Sponsor1Inst, size, data=sbills[sbills$Session==x.Sess,],geom='bar')+coord_flip(),
           x.Sess=do.call(picker, as.list(sessionslist)))
# the do.call calls the picker function and passes sessionslist as a list of 
# parameters
