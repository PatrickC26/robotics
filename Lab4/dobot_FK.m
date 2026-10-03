%%Dobot kinematic in real-world system

% Author: Yan-Ru (Patrick) Chen
% Date: Sep. 1, 2026

clear all clc

% declare the vars
% the length of each arms
syms a1 a2 a3 b3 a4 a5 b5 
% the angle of the joint in dobotlab
syms J1 J2 J3 

% define each theta with the joint angle (J1-J3)
t0 = J1
t1 = J2
t2 = -J2
t3 = J3 + J2 -J2
t4 = -J3

% given all the actual length
% try a2_val, b5_val -5
a1_val = 0, a2_val = 150, a4_val = 150
a3_val = 25, b3_val = 50 
a5_val = 40,  b5_val = 30
                

% Forward kinematic
H01 = [cos(t0) 0 -sin(t0) 0;...
       sin(t0) 0 cos(t0)  0;...
       0      -1    0     a1;...
       0       0    0      1]
H12= [cos(t1) -sin(t1) 0 a2*sin(t1);...
      sin(t1)  cos(t1) 0 -a2*cos(t1);...
      0         0      1    0;...
      0         0      0    1]
H23= [cos(t2) -sin(t2) 0 a3*sin(t2)+b3*cos(t2);...
      sin(t2)  cos(t2) 0 -a3*cos(t2)+b3*sin(t2);...
      0         0      1    0;...
      0         0      0    1]
H34= [cos(t3) -sin(t3) 0 a4*cos(t3);...
      sin(t3)  cos(t3) 0 a4*sin(t3);...
      0         0      1    0;...
      0         0      0    1]
H45= [cos(t4) -sin(t4) 0 a5*cos(t4)-b5*sin(t4);...
      sin(t4)  cos(t4) 0 a5*sin(t4)+b5*cos(t4);...
      0         0      1    0;...
      0         0      0    1]
H05 = simplify(H01*H12*H23*H34*H45)


%Computing Forward Solution
Px = H05(1,4) % 
Py = H05(2,4) % 
Pz = H05(3,4) % 

J1_val=27/180*pi;
J2_val=52/180*pi;
J3_val=24/180*pi;

% J1_val=1.19/180*pi;
% J2_val=38.80/180*pi;
% J3_val=35.02/180*pi;


% vpa = Variable-precision Arithmetic
% sub = Symbolic substitution
px_new=vpa(subs(Px,[J1,J2,J3, a1, a2, a3, b3, a4, a5, b5],[J1_val,J2_val,J3_val, a1_val, a2_val, a3_val, b3_val, a4_val, a5_val, b5_val]))
py_new=vpa(subs(Py,[J1,J2,J3, a1, a2, a3, b3, a4, a5, b5],[J1_val,J2_val,J3_val, a1_val, a2_val, a3_val, b3_val, a4_val, a5_val, b5_val]))
pz_new=vpa(subs(Pz,[J1,J2,J3, a1, a2, a3, b3, a4, a5, b5],[J1_val,J2_val,J3_val, a1_val, a2_val, a3_val, b3_val, a4_val, a5_val, b5_val]))

H_new = vpa(subs(H05,[ a1, a2, a3, b3, a4, a5, b5],[a1_val, a2_val, a3_val, b3_val, a4_val, a5_val, b5_val]))

H_new = vpa(subs(H_new,[J1,J2,J3],[J1_val,J2_val,J3_val]))