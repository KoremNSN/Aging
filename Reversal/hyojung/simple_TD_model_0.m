function [RSS, mout] = simple_TD_model_0(xpar);

% function [] = simple_TD_model_0(xpar);
% xpar(1) nu (learning rate)
% xpar(2) initial cue value

% constrain the range of parameters
if xpar(1)<0 | xpar(1)>1, RSS = realmax('double'); mout=[];  return; end;
if xpar(2)<0 | xpar(2)>1, RSS = realmax('double'); mout=[];  return; end;

global model_data
%model_data=[stage stim reinforce rating];

nu = xpar(1);
CSa_V = xpar(2);  % value of CS+ (-->CS- after reversal)
CSb_V = xpar(2);  % value of CS- (-->CS+ after reversal)

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

ntrial=size(model_data,1);
for t=1:ntrial
        
    if model_data(t,2)==1,  %CSa
        % cue-period prediction/probability rating
        CSa_Vs = [CSa_Vs; CSa_V];
        CSa_r = [CSa_r; model_data(t,4)];
        
        rx = [rx; CSa_V];
        ry = [ry; model_data(t,4)];
        
        % value update at the outcome phase
        CSa_TD = model_data(t,3)-CSa_V;  
        CSa_V = CSa_V + nu*CSa_TD;  %value update
                
        CSa_TDs = [CSa_TDs; CSa_TD];
                
    else  %CSb
        % cue-period prediction/probability rating
        CSb_Vs = [CSb_Vs; CSb_V];
        CSb_r = [CSb_r; model_data(t,4)];
        
        rx = [rx; CSb_V];
        ry = [ry; model_data(t,4)];
                
        CSb_TD = model_data(t,3)-CSb_V;  
        CSb_V = CSb_V + nu*CSb_TD;  %value update
                
        CSb_TDs = [CSb_TDs; CSb_TD];
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
mout.regx = rx;
mout.regy = ry;
mout.beta = beta;
mout.beta_ci = beta_ci;  %95% interval
mout.residuals = residual;



        