load('session_09_47_23_03_2018.mat')


% % 5 second subtraction
% X1 = X(512*5:end, :);
% force1 = force(512*5:end, :);
% delete X;
% delete force;
% X = X1;
% force = force1;

y1 = X(:,1)-X(:,3);
y2 = X(:,2)-X(:,4);
y3 = X(:,5)-X(:,7);
y4 = X(:,6)-X(:,8);

% f1 = force(:, 1);
% f2 = force(:, 2);
% f3 = force(:, 3);
% f4 = force(:, 4);
% 
% 
% f1(f1>5)=0;
% f2(f2>5)=0;
% f3(f3>5)=0;
% f4(f4>5)=0;
% 
% offset = ceil(512*2.5);
% f1 = [zeros(offset, 1); f1/max(f1)];
% f2 = [zeros(offset, 1); f2/max(f2)];
% f3 = [zeros(offset, 1); f3/max(f3)];
% f4 = [zeros(offset, 1); f4/max(f4)];

time = (time_stamps-time_stamps(1));%*time_conversion_factor;
time2 = linspace(1,(1+size(trial_time_stamps,2))*10,size(time_stamps,2));

minLength = min([length(y1), length(force), length(time)]);
y1(minLength+1:end) = [];
y2(minLength+1:end) = [];
y3(minLength+1:end) = [];
y4(minLength+1:end) = [];


force(minLength+1:end) = [];
force(force>20)=0;
% f1(minLength+1:end) = [];
% f2(minLength+1:end) = [];
% f3(minLength+1:end) = [];
% f4(minLength+1:end) = [];

time(minLength+1:end) = [];
time2(minLength+1:end) = [];

time_conversion_factor = size(time_stamps,2)/((1+size(trial_time_stamps,2))*10);

trials = (trial_time_stamps-trial_time_stamps(1)+10);%*time_conversion_factor;
% r12=xcorr(y1,y2);
% r13=xcorr(y1,y3);
% r23=xcorr(y3,y2);

% subplot(3,1,1);
% plot(y1);
% subplot(3,1,2);
% plot(y2);
% subplot(3,1,3);
% plot(y3);

% plt1 = (max(y1)-mean(y1))*f2/5+mean(y1);
% plt2 = (max(y2)-mean(y2))*f2/5+mean(y2);
% plt3 = (max(y3)-mean(y3))*f2/5+mean(y3);

Max=zeros(4,1);
Min=zeros(4,1);
Mean=zeros(4,1);
Norme=zeros(4,1);

for i=1:4
    Max(i)=max(eval(['y' num2str(i)]));
    Min(i)=min(eval(['y' num2str(i)]));
    Mean(i)=mean(eval(['y' num2str(i)]));
    
    if abs(Max(i))>abs(Min(i))
        Norme(i)=Max(i);
    else
        Norme(i)=Min(i);
    end
end


y1_norm=y1/Norme(1);
y2_norm=y2/Norme(2);
y3_norm=y3/Norme(3);
y4_norm=y4/Norme(4);


subplot(5,1,1);
plot(time, y1_norm);
ylabel('EMG signal');
xlabel('Time (s)');
hold on;
for i=(1:length(trials))
    line([trials(i) trials(i)], [min(y1_norm) 1],'Color',[1 0 0]);
end
hold off;

subplot(5,1,2);
plot(time, y2_norm);
ylabel('EMG signal');
xlabel('Time (s)');
hold on;
for i=(1:length(trials))
    line([trials(i) trials(i)], [min(y2_norm) 1],'Color',[1 0 0]);
end
hold off;

subplot(5,1,3);
plot(time, y3_norm);
ylabel('EMG signal');
xlabel('Time (s)');
hold on;
for i=(1:length(trials))
    line([trials(i) trials(i)], [min(y3_norm) 1],'Color',[1 0 0]);
end
hold off;

subplot(5,1,4);
plot(time, y4_norm);
ylabel('EMG signal');
xlabel('Time (s)');
hold on;
for i=(1:length(trials))
    line([trials(i) trials(i)], [min(y4_norm) 1],'Color',[1 0 0]);
end
hold off;

% subplot(4,1,4);
% hold on;
% plot(time, f1,'Color',[0 1 1]);
% plot(time, f2,'Color',[0 1 0]);
% plot(time, f3,'Color',[0 0 1]);
% plot(time, f4,'Color',[1 0 1]);
% for i=(1:length(trials))
%     line([trials(i) trials(i)], [0 1],'Color',[1 0 0]);
% end
% hold off;

subplot(5,1,5);
plot(time, force);
ylabel('Force Intensity');
xlabel('Time (s)');
hold on;
for i=(1:length(trials))
    line([trials(i) trials(i)], [0 20],'Color',[1 0 0]);
end
hold off;
% subplot(3,2,2);
% plot(f1);
% subplot(3,2,4);
% plot(f2);
% subplot(3,2,6);
% plot(f3);