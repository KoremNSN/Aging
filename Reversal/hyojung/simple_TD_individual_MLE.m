%function [] = simple_TD_individual_MLE(model_opt);
clear all;
% function []=simple_TD_individual_MLE();
model_opt=0;
maxit=1000000;
maxfit=1000000;
op=optimset('fminsearch');
op.MaxIter=maxit;
op.MaxFunEvals=maxfit;
op.LargeScale='On';

% model_opt
% 0     common, constant learning rate for acquisition and reversal
%       npar=2:   nu, initial V  
% 1     separate, decaying learning rates (common decay rate)
%       npar=4;   nu_A, nu_R, alpha , initial V (Schiller et al., 2008)
% 2     associability
%       npar=4;   alpha, initial V, gamma, kappa (Li et al., 2011)

% initial values for parameters
switch model_opt
    case 0
        ixa=0.5;
        ixb=0;
        [x1,x2]=ndgrid(ixa,ixb);
        ix=[x1(:) x2(:)];       
               
    case 1
        ixa=0.5;
        ixb=0.5;
        ixc=0.5;
        ixd=0;
        [x1,x2,x3,x4]=ndgrid(ixa,ixb,ixc,ixd);
        ix=[x1(:) x2(:) x3(:) x4(:)];  
        
    case 2
        ixa=0.5;
        ixb=0;
        ixc=0.5;
        ixd=0.5;
        [x1,x2,x3,x4]=ndgrid(ixa,ixb,ixc,ixd);
        ix=[x1(:) x2(:) x3(:) x4(:)];         
        
end
npar=size(ix,2);   %number of free parameters

expdata = readData;
% data.stage:       1 Acquisition,  2 Reversal
% data.trnum:       trial number 
% data.subj:        subject ID
% data.rating:      probability rating (0~100)
% data.stim:        1 stim A (CS+ --> CS-), 2 stim B (CS- --> CS+)
% data.reinforce:   0 no reinforcement, 1 reinforcement

global model_data        

outp_mtx = [];
isub = unique(expdata.subj); 
for k=1:length(isub)   %individual subjects
    disp(['subject ID = ',num2str(isub(k))]);
    
    idx=find(expdata.subj == isub(k));
    
    model_data=[expdata.stage(idx) ...
                expdata.stim(idx) ...
                expdata.reinforce(idx) ...
                expdata.rating(idx)];

            
    best_xpar = [];  
    best_mrss = [];
    for m=1:size(ix,1)
        
        switch model_opt
            case 0
                [xpar min_rss eflag output]=...
                    fminsearch(@simple_TD_model_0,ix(m,:),op);
            case 1
                [xpar min_rss eflag output]=...
                    fminsearch(@simple_TD_model_1,ix(m,:),op);
            case 2
                [xpar min_rss eflag output]=...
                    fminsearch(@associability_model,ix(m,:),op);
        end
       
        if   m==1, 
            best_xpar = xpar;
            best_mrss = min_rss;
        else 
             if min_rss < best_mrss,
                best_xpar = xpar;
                best_mrss = min_rss;
             end
         end        
    end
 
    switch model_opt
        case 0
            [best_rss, model_out] = simple_TD_model_0(best_xpar);
        case 1
            [best_rss, model_out] = simple_TD_model_1(best_xpar);
        case 2
            [best_rss, model_out] = associability_model(best_xpar);
    end
    
    nn = size(model_data,1);
    loglike = -nn*(log(sqrt(2*pi*best_rss/nn))+1/2);
    
    outp_mtx(k,:) = [isub(k) best_xpar best_rss loglike];
end
                
                
                
                
                
                
                