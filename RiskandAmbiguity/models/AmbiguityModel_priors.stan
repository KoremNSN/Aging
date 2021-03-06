//

data {
  int<lower=1> N; // number of choices
  array[N] int choice;
  array[N] int<lower=0> refProbabilities;
  array[N] int<lower=0> refAmbiguities;
  array[N] real refValues;
  vector[N] lotteryProbabilities;
  vector[N] lotteryAmbiguities;
  array[N] int ID;
  array[N] real lotteryValues;
  int<lower=1> n_sub; // number of participants
  
}



// accepts two parameters 'mu' and 'sigma'.
parameters {
  vector<lower=0>[n_sub] riskTol;
  vector<lower=0>[n_sub] ambTol;
  vector<lower=0>[n_sub] noise;
  real aMu;
  real<lower=0> aSig;
  real bMu;
  real<lower=0> bSig;
  real nMu;
  real<lower=0> nSig;
  

}

transformed parameters {
  vector[N] p;
  vector[N] uRef;
  vector[N] uLotto;
  vector[N] p_inv;
  
  
  for ( i in 1:N ) {
      uLotto[i] = lotteryValues[i]^riskTol[ID[i]] * (lotteryProbabilities[i] - ambTol[ID[i]] * lotteryAmbiguities[i]/2);
      uRef[i] = refValues[i]^riskTol[ID[i]] * (refProbabilities[i] - ambTol[ID[i]] * refAmbiguities[i]/2);
      p[i] = (uLotto[i] - uRef[i]) / noise[ID[i]];
       
  }
 
      p_inv = inv_logit(p);  
      
}

model {
  
  aSig ~ exponential(1);
  aMu ~ lognormal(-0.4, 0.4);
  bSig ~ normal(0, 1);
  bMu ~ normal(0, 0.7);
  nSig ~ exponential(1);
  nMu ~ normal(0, 1);
  
  noise ~ lognormal(nMu, nSig);
  riskTol ~ lognormal(aMu, aSig);
  ambTol ~ normal(bMu, bSig);
  choice ~ binomial(1,p_inv);
}

generated quantities {
  vector[N] log_lik;
  vector[N] y_hat;
  for (j in 1:N) {
    log_lik[j] = normal_lpdf(choice[j] | p_inv[j], 1);
    y_hat[j] = normal_rng(p_inv[j], 1);
    }
}