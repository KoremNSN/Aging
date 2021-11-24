data {
  int<lower=1> N; // number of subjects
  int<lower=1> T; // number of trials              
  int<lower=1, upper=T> Tsubj[N];   // trials per subject              
  real<lower=0> rating[T, N];     
  int<lower=0, upper=1> lambda[T, N];   
  int<lower=1, upper=2> stim[T, N];
}

transformed data {
  vector<lower=0, upper=1>[2] initV;  // initial value for EV
  initV = rep_vector(0.5, 2);
}

parameters {
// Declare all parameters as vectors for vectorizing
  // Hyper(group)-parameters  
  vector[4] mu_p;           
  // increase from 3 --> 4 to add "sigma_er mean"
  vector<lower=0>[4] sigma;
    
  // Subject-level raw parameters (for Matt trick)
  vector[N] A_pr;    // learning rate
  vector[N] alpha_pr;
  vector[N] beta_pr;

  // sigma_er will be the sd of the normal distribution. It is like an
  // inverse temperature --> higher = actual y values are "consistent"
  // with the y-hat values
  vector[N] sigma_er_pr;  
}

transformed parameters {
  // subject-level parameters
  vector<lower=0,upper=1>[N] A;
  vector[N] alpha;
  vector[N] beta;
  vector<lower=0>[N] sigma_er;
  
  for (i in 1:N) {
    A[i] = Phi_approx( mu_p[1]  + sigma[1]  * A_pr[i] );
  }
  // Using non-centered parameterization
  alpha = mu_p[2] + sigma[2] * alpha_pr;  
  beta  = mu_p[3] + sigma[3] * beta_pr;  
  sigma_er = exp(mu_p[4] + sigma[4] * sigma_er_pr);
}

model {
  // Hyperparameters
  mu_p  ~ normal(0, 1); 
  sigma ~ cauchy(0, 5);  
  
  // individual parameters
  A_pr     ~ normal(0, 1);
  alpha_pr ~ normal(0, 1);
  beta_pr  ~ normal(0, 1);
  sigma_er_pr ~ normal(0, 1);

  // subject loop and trial loop
  for (i in 1:N) {
    vector[2] ev; // expected value
    real PE;      // prediction error

    ev = initV;

    for (t in 1:(Tsubj[i])) {        
      rating[t, i] ~ normal(alpha[i] + beta[i] * ev[stim[t,i]], sigma_er[i]);

      // prediction error 
      PE = lambda[t, i] - ev[stim[t,i]];

      // value updating (learning) 
      ev[stim[t, i]] = ev[stim[t, i]] + A[i] * PE; 
    }
  }
}

generated quantities {
  // For group level parameters
  real<lower=0, upper=1> mu_A;
  real mu_alpha;
  real mu_beta;
  real<lower=0> mu_sigma_er;
  
  // For log likelihood calculation
  real log_lik[N]; 

  mu_A = Phi_approx(mu_p[1]);
  mu_alpha = mu_p[2];
  mu_beta  = mu_p[3];
  mu_sigma_er = exp(mu_p[4]);

  { // local section, this saves time and space
    for (i in 1:N) {
      vector[2] ev; // expected value
      real PE;      // prediction error

      // Initialize values
      ev = initV;
      
      log_lik[i] = 0;
      
      for (t in 1:(Tsubj[i])) {
        // compute action probabilities
        log_lik[i] = log_lik[i] + normal_lpdf(rating[t, i] | alpha[i] + beta[i] * ev[stim[t, i]], sigma_er[i]);
        
        // prediction error 
        PE = lambda[t, i] - ev[stim[t, i]];

        // value updating (learning) 
        ev[stim[t, i]] = ev[stim[t, i]] + A[i] * PE; 
      }
    }   
  }
}