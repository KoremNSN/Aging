function [RSS, mout] = simple_TD_model_1(xpar);

% function [] = simple_TD_model_0(xpar);
% xpar(1) nu (learning rate) during acquisition
% xpar(2) nu after reversal
% xpar(3) decay of nu
% xpar(4) initial cue value

% constrain the range of parameters
if xpar(1)<0 | xpar(1)>1, RSS = realmax('double'); mout=[];  return; end;
if xpar(2)<0 | xpar(2)>1, RSS = realmax('double'); mout=[];  return; end;
if xpar(3)<0 | xpar(3)>1, RSS = realmax('double'); mout=[];  return; end;
if xpar(4)<0 | xpar(4)>1, RSS = realmax('double'); mout=[];  return; end;    

global model_data
%model_data=[stage stim reinforce rating];

nu_A = xpar(1);
nu_R = xpar(2);
alpha = xpar(3);
CSa_V = xpar(4);  % value of CS+ (-->CS- after reversal)
CSb_V = xpar(4);  % value of CS- (-->CS+ after reversal)

CSa_TD = [];
CSb_TD = [];
CSa_TDs = [];
CSb_TDs = [];

CSa_Vs = [];
CSb_Vs = [];
CSa_r = [];
CSb_r = [];

rx = [];
ry = [];

nu_As = [];
nu_Rs = [];

ntrial=size(model_data,1);
for t=1:ntrial
        
    nu_As = [nu_As;nu_A];
    nu_Rs = [nu_Rs;nu_R];
    
    if model_data(t,2)==1,  %CSa
        % cue-period prediction/probability rating
        CSa_Vs = [CSa_Vs; CSa_V];
        CSa_r = [CSa_r; model_data(t,4)];
        
        rx = [rx; CSa_V];
        ry = [ry; model_data(t,4)];
        
        % value update at the outcome phase
        CSa_TD = model_data(t,3)-CSa_V;  
        
        % separate learning rates for acquisition and reversal stages
        CSa_V = CSa_V + (model_data(t,1)==1)*nu_A*CSa_TD ...
                      + (model_data(t,1)==2)*nu_R*CSa_TD;  
                                 
        CSa_TDs = [CSa_TDs; CSa_TD];
                
    else  %CSb
        % cue-period prediction/probability rating
        CSb_Vs = [CSb_Vs; CSb_V];
        CSb_r = [CSb_r; model_data(t,4)];
        
        rx = [rx; CSb_V];
        ry = [ry; model_data(t,4)];
                
        CSb_TD = model_data(t,3)-CSb_V;  
        CSb_V = CSb_V + (model_data(t,1)==1)*nu_A*CSb_TD ...
                      + (model_data(t,1)==2)*nu_R*CSb_TD;  
                
        CSb_TDs = [CSb_TDs; CSb_TD];
    end
    
    nu_A = (model_data(t,1)==1)*alpha*nu_A + ...
           (model_data(t,1)==2)*nu_A;
    nu_R = (model_data(t,1)==1)*nu_R + ...
           (model_data(t,1)==2)*alpha*nu_R;
end    

[beta, beta_ci, residual, res_ci, rstats] = regress(ry,[ones(size(rx,1),1) rx]);
RSS = sum(residual.^2);  % residual sum of squares;
    
mout.CSa_Vs = CSa_Vs;
mout.CSb_Vs = CSb_Vs;
mout.CSa_Rs = CSa_r;
mout.CSb_Rs = CSb_r;
mout.CSa_TDs = CSa_TDs;
mout.CSb_TDs = CSb_TDs;
mout.nu_As = nu_As;
mout.nu_Rs = nu_Rs;
mout.regx = rx;
mout.regy = ry;
mout.beta = beta;
mout.beta_ci = beta_ci;  %95% interval
mout.residuals = residual;



        