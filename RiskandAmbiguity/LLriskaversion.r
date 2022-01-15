library(bbmle)

# LogLikelihood function
LL <- function(intercept, alpha, beta, gamma){
  uRef = 5 ** alpha
  uLotto = (lotteryProbabilities - beta *(ambiguity/2)) * lotteryValues ** alpha
  R = choice - 1/(1+exp(gamma * (uRef-uLotto)))
  R = suppressWarnings(dnorm(R, log = TRUE))
  -sum(R)
}


db <- read.csv('mon.csv')
db_all = data.frame()
subs <- unique(db$sub)

for (s in subs){
  df <- subset(db, sub == s)
  lotteryProbabilities <- df$risk
  ambiguity <- df$ambiguity
  lotteryValues <- df$value
  choice <- df$choice
  valid <- df$catch
  validBin <- df$catch < 6
  
  
  fit <- mle2(LL, start = list(alpha = 1, beta = 1, gamma =1), method="L-BFGS-B", lower = c(alpha = 0, beta = -2, -Inf), upper = c(alpha = 2, beta = 2, Inf))
  LLcoef <- coef(fit)
  temp = data.frame()
  temp = data.frame(s, valid, validBin,
                    alpha <- LLcoef[1], beta <- LLcoef[2], gamma <- LLcoef[3])
  
  db_all <- rbind(db_all, temp)
}
write.csv(db_all, 'LL_alpha_beta.csv')
