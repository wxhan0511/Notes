#pragma once
#ifdef __cplusplus
extern "C"{
#endif
typedef int(*MF)(int);typedef void(*WF)(int,int,int,int,unsigned char);
int GammaTuning(const char*id,int g,const int*lv,const int*reg,int*o);
int GammaTuning_EnhancePoint(int i,int gy,int t,int c1,int c2,int c3,unsigned char sn,MF m,WF w,int*o1,int*o2,int*o3,unsigned char*os);
#ifdef __cplusplus
}
#endif