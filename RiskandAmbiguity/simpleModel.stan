//

data {
  int<lower=1> N; // number of choices
  array[N] int choice;
  array[N] int<lower=0> refProbabilities;
  array[N] real refValues;
  vector[N] lotteryProbabilities;
  array[N] int ID;
  array[N] real lotteryValues;
  int<lower=1> n_sub; // number of participants
  
}


// accepts two parameters 'mu' and 'sigma'.
parameters {
  vector<lower=0>[n_sub] riskTol;
  vector<lower=0>[n_sub] noise;
  real rMu;
  real<lower=0> rSig;
  real nMu;
  real<lower=0> nSig;
  

}

transformed parameters {
  vector[N] p;
  vector[N] uRef;
  vector[N] uLotto;
  vector[N] p_inv;
  
  
  for ( i in 1:N ) {
      uLotto[i] = lotteryValues[i]^riskTol[ID[i]] * lotteryProbabilities[i];
      uRef[i] = refValues[i]^riskTol[ID[i]] * refProbabilities[i];
      p[i] = (uLotto[i] - uRef[i]) / noise[ID[i]];
       
  }
 
      p_inv = inv_logit(p);  
      
}

model {
  
  rSig ~ exponential(1);
  rMu ~ normal(0, 1);
  nSig ~ exponential(1);
  nMu ~ normal(0, 1);
  noise ~ lognormal(nMu, nSig);
  riskTol ~ lognormal(rMu, rSig);
  choice ~ binomial(1,p_inv);
}

generated quantities {
  //array[N] real alphas = lognormal(rMu, rSig);  
}