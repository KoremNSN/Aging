function [RSS, mout] = associability(xpar);

% function [] = simple_TD_model_0(xpar);
% xpar(1) alpha initial associability 
% xpar(2) V initial associative strength
% xpar(3) gamma weight allocating factor
% xpar(4) kappa scaling factor

% constrain the range of parameters
if xpar(1)<0 | xpar(1)>1, RSS = realmax('double'); mout=[];  return; end;
if xpar(2)<0 | xpar(2)>1, RSS = realmax('double'); mout=[];  return; end;
if xpar(3)<0 | xpar(3)>1, RSS = realmax('double'); mout=[];  return; end;
if xpar(4)<0,             RSS = realmax('double'); mout=[];  return; end;    


global model_data
%model_data=[stage stim reinforce rating];

CSa_alpha = xpar(1);
CSb_alpha = xpar(1);
CSa_V = xpar(2);
CSb_V = xpar(2);
gamma = xpar(3);
kappa = xpar(4);

CSa_TD = [];
CSb_TD = [];
CSa_TDs = [];
CSb_TDs = [];

CSa_alphas =[];
CSb_alphas =[];

CSa_Vs = [];
CSb_Vs = [];

CSa_r = [];
CSb_r = [];

rx = [];
ry = [];

ntrial=size(model_data,1);
for t=1:ntrial
            
    if model_data(t,2)==1,  %CSa
        % cue-period prediction/probability rating
        CSa_Vs = [CSa_Vs; CSa_V];
        CSa_r = [CSa_r; model_data(t,4)];
        CSa_alphas = [CSa_alphas; CSa_alpha];
        
        rx = [rx; CSa_V];
        ry = [ry; model_data(t,4)];
        
        % prediction error at the outcome phase
        CSa_TD = model_data(t,3)-CSa_V;  
        CSa_TDs = [CSa_TDs; CSa_TD];
        
        % value update with prediction error
        nu = (1/(1+exp(-kappa*(CSa_alpha-.5))));
        CSa_V = CSa_V + nu*CSa_TD; 
        
        % associability update
        CSa_alpha = (1-gamma)*CSa_alpha + gamma*abs(CSa_TD);
                                
    else  %CSb
        % cue-period prediction/probability rating
        CSb_Vs = [CSb_Vs; CSb_V];
        CSb_r = [CSb_r; model_data(t,4)];
        CSb_alphas = [CSb_alphas; CSb_alpha];
        
        rx = [rx; CSb_V];
        ry = [ry; model_data(t,4)];
                
        CSb_TD = model_data(t,3)-CSb_V; 
        CSb_TDs = [CSb_TDs; CSb_TD];
                
        % value update
        nu = (1/(1+exp(-kappa*(CSb_alpha-.5))));
        CSb_V = CSb_V + nu*CSb_TD;
        
        % associability update
        CSb_alpha = (1-gamma)*CSb_alpha + gamma*abs(CSb_TD);
                
    end
end    


[beta, beta_ci, residual, res_ci, rstats] = regress(ry,[ones(size(rx,1),1) rx]);
RSS = sum(residual.^2);  % residual sum of squares;
    
mout.CSa_Vs = CSa_Vs;
mout.CSb_Vs = CSb_Vs;
mout.CSa_Rs = CSa_r;
mout.CSb_Rs = CSb_r;
mout.CSa_TDs = CSa_TDs;
mout.CSb_TDs = CSb_TDs;
mout.CSa_alphas = CSa_alphas;
mout.CSb_alphas = CSb_alphas;
mout.regx = rx;
mout.regy = ry;
mout.beta = beta;
mout.beta_ci = beta_ci;  %95% interval
mout.residuals = residual;



        