function out=readData();

%function out=readData();
%read data from excel file 

curr_d=cd;

[filen, path, ifilter]=uigetfile('*.xlsx','Select data file ...');
 
cd(path);
[num, txt, raw]=xlsread(filen);

[rr cc]=size(raw);
vname={'stage';'trnum';'subj';'rating';'stim';'rew'};
for t=1:length(vname)
    if t==1|t==5,
        eval([vname{t},'=raw(2:rr,t);']);
    else 
        eval([vname{t},'=cell2mat(raw(2:rr,t));']);
    end
end

num_stage=[]; 
num_stim=[];
for t=1:length(stage)
    if strcmp(stage{t},'Acq'),  num_stage(t,1)=1;
    else                        num_stage(t,1)=2;
    end
    
    if strcmp(stim{t},'A'),     num_stim(t,1)=1;
    else                        num_stim(t,1)=2;
    end
end

isub=unique(subj);
subj_table=[];
for t=1:length(isub)
    subj_table(t,1)=isub(t);
    subj_table(t,2)=length(find(subj==isub(t)));
    
    for z=1:2
        subj_table(t,z+2)=length(find(subj==isub(t) & num_stage==z));
    end
    
    for z=1:2
        subj_table(t,z+4)=length(find(subj==isub(t) & num_stage==1 & ...
                                      num_stim==z));
        ix=find(subj==isub(t) & num_stage==1 & num_stim==z);
        subj_table(t,z+6)=mean(rew(ix));
        subj_table(t,z+8)=mean(rating(ix));
    end    
    
    for z=1:2
        subj_table(t,z+10)=length(find(subj==isub(t) & num_stage==2 & ...
                                      num_stim==z));
        ix=find(subj==isub(t) & num_stage==2 & num_stim==z);
        subj_table(t,z+12)=mean(rew(ix));
        
        ix=find(subj==isub(t) & num_stage==2 & num_stim==z & ...
                trnum>66);
        subj_table(t,z+14)=mean(rating(ix));
    end   
end

if length(unique(subj_table(:,2)))==1,
    disp(['#trial/subject = ',num2str(unique(subj_table(:,2)))]);
else
    warning('Number of trials is not same for all the subjects!');
end

% plot
figure(1); set(gcf,'color','w'); clf;

ctb=[1 .3 .3;.3 .3 1];

iplot=0;
for t=1:length(isub)
    it=find(subj==isub(t));
    data=[num_stim(it) trnum(it) rating(it) rew(it) num_stage(it)];
    
    iplot=iplot+1;
    subplot(4,1,iplot);
    
    fill([0 0 35 35],[0 9 9 0],[.95 .95 .95],...
        'edgecolor','none'); hold on;
    line([0 70],[5 5],'color',[.3 .3 .3],...
        'linestyle',':','linewidth',2);
    
    for z=1:2
        iz=find(data(:,1)==z);
        
        plot(data(iz,2),data(iz,3),'marker','o','markersize',5,...
            'color',ctb(z,:),'markeredgecolor',ctb(z,:),...
            'markerfacecolor','w','linewidth',1.5);
        hold on;
        
        ix=find(data(:,1)==z & data(:,4)==1);
        plot(data(ix,2),data(ix,3),'marker','o','markersize',8,...
            'markerfacecolor',ctb(z,:),'markeredgecolor',ctb(z,:),...
            'linestyle','none');
        
        for w=1:2
            ix=find(data(:,1)==z & data(:,5)==w);
            if w==1, xl=[0 35];
            else     xl=[36 70];
            end
            line(xl,[mean(data(ix,3)) mean(data(ix,3))],...
                'color',ctb(z,:),'linestyle',':','linewidth',2);
        end
 
    end
    set(gca,'xlim',[0 70],'ylim',[0 10],'box','off','tickdir','out');
    title(['Subject ID = ',num2str(isub(t))]);
    xlabel('trial');
    ylabel('probability rating');
    
    if t<length(isub) & iplot==4, 
        clf;
        iplot=0;
    end
end

out.subj_table=subj_table;
out.stage=num_stage;    %1 acq, 2 rev
out.trnum=trnum;
out.subj=subj;
out.rating=rating;
out.stim=num_stim;      %1 A,  2 B
out.reinforce=rew;


 